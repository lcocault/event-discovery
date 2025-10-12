import sys
import os
import random
from typing import List, Tuple
from collections import Counter
from simulation.location_assigner import LocationAssigner
from models.family import Family
from models.person import Person, Gender, SocialCategory, Religiosity


"""Family generation utilities with child distribution logic."""


class FamilyGenerator:
    """Generates families with specified child distribution."""

    def __init__(self):
        """Initialize the family generator with child distribution probabilities."""
        # Child distribution: 40% no children, 20% 1 child, 25% 2 children, 10% 3 children, 5% 4 children
        self.child_distribution = [
            (0, 0.40),  # 40% - no children
            (1, 0.20),  # 20% - 1 child
            (2, 0.25),  # 25% - 2 children
            (3, 0.10),  # 10% - 3 children
            (4, 0.05),  # 5% - 4 children
        ]

        # Religiosity distribution: 5% very religious, 10% moderate, 30% occasional, 55% no religion
        self.religiosity_distribution = [
            (Religiosity.VERY_RELIGIOUS, 0.05),  # 5% very religious
            (Religiosity.MODERATE_RELIGIOUS, 0.10),  # 10% moderate religious
            (Religiosity.OCCASIONAL_RELIGIOUS, 0.30),  # 30% occasional religious
            (Religiosity.NO_RELIGION, 0.55),  # 55% no religion
        ]

    def _get_random_child_count(self) -> int:
        """Determine number of children based on distribution probabilities."""
        rand_val = random.random()
        cumulative_prob = 0.0

        for child_count, probability in self.child_distribution:
            cumulative_prob += probability
            if rand_val <= cumulative_prob:
                return child_count

        # Fallback (should not reach here with valid probabilities)
        return 0

    def _get_random_religiosity(self) -> Religiosity:
        """Determine religiosity level based on distribution probabilities."""
        rand_val = random.random()
        cumulative_prob = 0.0

        for religiosity, probability in self.religiosity_distribution:
            cumulative_prob += probability
            if rand_val <= cumulative_prob:
                return religiosity

        # Fallback (should not reach here with valid probabilities)
        return Religiosity.NO_RELIGION

    def _get_social_category_for_age(self, age: int) -> SocialCategory:
        """
        Determine social category based on age and realistic French demographic distribution.

        Uses INSEE data for population 15+ years:
        - Farmers: ~1.5%
        - Artisans/Merchants/Entrepreneurs: ~3.5%
        - Executives/Higher Intellectual: ~10.5%
        - Intermediate Professions: ~14.5%
        - Employees: ~15.5%
        - Workers: ~11.5%
        - Retirees: ~26.5%
        - Other Inactive: ~16.5%

        Args:
            age: Age of the person

        Returns:
            SocialCategory enum value
        """
        # Children under 15: inactive
        if age < 15:
            return SocialCategory.INACTIVE

        # Young people (15-17): mostly inactive (students) with some early workers
        elif age < 18:
            return random.choices(
                [
                    SocialCategory.INACTIVE,
                    SocialCategory.EMPLOYEES,
                    SocialCategory.WORKERS,
                ],
                weights=[0.85, 0.10, 0.05],  # 85% inactive, 10% employees, 5% workers
            )[0]

        # Young adults (18-24): mix of inactive (students) and entry-level positions
        elif age < 25:
            return random.choices(
                [
                    SocialCategory.INACTIVE,
                    SocialCategory.EMPLOYEES,
                    SocialCategory.WORKERS,
                ],
                weights=[0.50, 0.35, 0.15],  # 50% inactive, 35% employees, 15% workers
            )[0]

        # Adults (25-61): active professional categories based on INSEE data
        elif age < 62:
            return random.choices(
                [
                    SocialCategory.FARMERS,
                    SocialCategory.ARTISANS_MERCHANTS_ENTREPRENEURS,
                    SocialCategory.EXECUTIVES_HIGHER_INTELLECTUAL_PROFESSIONS,
                    SocialCategory.INTERMEDIATE_PROFESSIONS,
                    SocialCategory.EMPLOYEES,
                    SocialCategory.WORKERS,
                    SocialCategory.INACTIVE,
                ],
                weights=[
                    1.5,  # 1.5% farmers
                    3.5,  # 3.5% artisans/merchants/entrepreneurs
                    10.5,  # 10.5% executives/higher intellectual
                    14.5,  # 14.5% intermediate professions
                    15.5,  # 15.5% employees
                    11.5,  # 11.5% workers
                    43.5,  # 43.5% inactive (includes unemployed, students, homemakers, etc.)
                ],
            )[0]

        # Pre-retirement and seniors (62+): mostly retirees with some still active
        else:
            return random.choices(
                [
                    SocialCategory.RETIREES,
                    SocialCategory.INACTIVE,
                    SocialCategory.EXECUTIVES_HIGHER_INTELLECTUAL_PROFESSIONS,
                    SocialCategory.INTERMEDIATE_PROFESSIONS,
                    SocialCategory.EMPLOYEES,
                ],
                weights=[
                    0.75,  # 75% retirees
                    0.15,  # 15% inactive
                    0.04,  # 4% still working executives
                    0.03,  # 3% still working intermediate
                    0.03,  # 3% still working employees
                ],
            )[0]

    def _generate_person(self, min_age: int = 0, max_age: int = 100) -> Person:
        """Generate a random person with random gender, age, and social category."""
        gender = random.choice(list(Gender))
        age = random.randint(min_age, max_age)
        social_category = self._get_social_category_for_age(age)
        return Person(gender=gender, age=age, social_category=social_category)

    def _generate_parents(self) -> List[Person]:
        """Generate parents for a family (typically 2 adults)."""
        # Generate 2 parents (adults aged 25-75)
        # 90% chance: age difference < 5 years
        if random.random() < 0.9:
            age1 = random.randint(25, 75)
            # Pick age2 within 5 years of age1, but still in [25, 75]
            min_age2 = max(25, age1 - 4)
            max_age2 = min(75, age1 + 4)
            age2 = random.randint(min_age2, max_age2)
            parent1 = self._generate_person(min_age=age1, max_age=age1)
            parent2 = self._generate_person(min_age=age2, max_age=age2)
        else:
            # 10% chance: any ages 25-75
            parent1 = self._generate_person(min_age=25, max_age=75)
            parent2 = self._generate_person(min_age=25, max_age=75)
        return [parent1, parent2]

    def _generate_children(self, count: int) -> List[Person]:
        """Generate children for a family."""
        children = []
        for _ in range(count):
            # Children aged 0-17
            child = self._generate_person(min_age=0, max_age=17)
            children.append(child)
        return children

    def _generate_parents_and_children(
        self, child_count: int
    ) -> Tuple[List[Person], List[Person]]:
        """
        Generate parents and children so that the age difference between the older parent and youngest child
        is always between 20 and 45, and generally around 30.
        """
        # If there are children, set youngest child's age so that parent-child age difference is 20-45 (centered at 30)
        if child_count > 0:
            # Pick age difference: normal distribution centered at 30, clipped to [20, 45]
            import random

            diff = int(min(45, max(20, random.gauss(30, 5))))
            # Youngest child age
            youngest_child_age = random.randint(0, 17)
            # Older parent age
            older_parent_age = youngest_child_age + diff
            older_parent_age = min(75, max(25, older_parent_age))
            # Other parent age within 5 years
            min_other = max(25, older_parent_age - 4)
            max_other = min(75, older_parent_age + 4)
            other_parent_age = random.randint(min_other, max_other)
            # Generate parents
            parent1 = self._generate_person(
                min_age=older_parent_age, max_age=older_parent_age
            )
            parent2 = self._generate_person(
                min_age=other_parent_age, max_age=other_parent_age
            )
            # Generate children
            children = [
                self._generate_person(
                    min_age=youngest_child_age, max_age=youngest_child_age
                )
            ]
            # Remaining children: ages 0-17, but not younger than youngest_child_age
            for _ in range(child_count - 1):
                age = random.randint(youngest_child_age, 17)
                children.append(self._generate_person(min_age=age, max_age=age))
            return [parent1, parent2], children
        else:
            # No children: parents as before
            parents = self._generate_parents()
            return parents, []

    def generate_family(self) -> Family:
        """Generate a single family with random parents and children based on distribution."""
        # Determine family religiosity and social category
        religiosity = self._get_random_religiosity()
        # Assign social category based on the older parent (or random adult if no children)
        parents = self._generate_parents()
        family = Family(religiosity=religiosity)
        for parent in parents:
            family.add_parent(parent)
        child_count = self._get_random_child_count()
        if child_count > 0:
            children = self._generate_children(child_count)
            family.add_children(children)
        return family

    def generate_families(self, count: int) -> List[Family]:
        """Generate multiple families with the specified child distribution."""
        families = []
        for _ in range(count):
            family = self.generate_family()
            families.append(family)
        return families

    def save_families(self, families: List[Family], file_path: str):
        """Save families to a JSON file."""
        import json
        # Position import not needed here, already imported at top

        def family_to_dict(family: Family):
            return {
                "family_id": family.family_id,
                "religiosity": family.religiosity.value if family.religiosity else None,
                "home_position": {
                    "latitude": family.home_position.latitude
                    if family.home_position
                    else None,
                    "longitude": family.home_position.longitude
                    if family.home_position
                    else None,
                },
                "parents": [
                    {
                        "person_id": p.person_id,
                        "gender": p.gender.value,
                        "age": p.age,
                        "social_category": p.social_category.value
                        if p.social_category
                        else None,
                        "work_location": {
                            "name": p.work_location.name if p.work_location else None,
                            "type": p.work_location.location_type.value
                            if p.work_location
                            else None,
                            "latitude": p.work_location.position.latitude
                            if p.work_location
                            else None,
                            "longitude": p.work_location.position.longitude
                            if p.work_location
                            else None,
                        }
                        if p.work_location
                        else None,
                    }
                    for p in family.parents
                ],
                "children": [
                    {
                        "person_id": c.person_id,
                        "gender": c.gender.value,
                        "age": c.age,
                        "social_category": c.social_category.value
                        if c.social_category
                        else None,
                        "school_location": {
                            "name": c.school_location.name
                            if c.school_location
                            else None,
                            "type": c.school_location.location_type.value
                            if c.school_location
                            else None,
                            "latitude": c.school_location.position.latitude
                            if c.school_location
                            else None,
                            "longitude": c.school_location.position.longitude
                            if c.school_location
                            else None,
                        }
                        if c.school_location
                        else None,
                    }
                    for c in family.children
                ],
            }

        data = [family_to_dict(fam) for fam in families]
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def load_families(self, file_path: str) -> List[Family]:
        """Load families from a JSON file."""
        import json
        from models.location import Coordinates, Location, LocationType
        from models.person import Gender, SocialCategory, Person, Religiosity

        families = []
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        for fam_dict in data:
            religiosity = (
                Religiosity(fam_dict["religiosity"])
                if fam_dict["religiosity"]
                else None
            )
            family = Family(
                family_id=fam_dict["family_id"],
                religiosity=religiosity,
            )
            # Home position
            hp = fam_dict.get("home_position")
            if hp and hp["latitude"] is not None and hp["longitude"] is not None:
                family.home_position = Coordinates(hp["latitude"], hp["longitude"])
            # Parents
            for p in fam_dict["parents"]:
                gender = Gender(p["gender"])
                age = p["age"]
                social_category = (
                    SocialCategory(p["social_category"])
                    if p.get("social_category")
                    else None
                )
                person = Person(
                    gender=gender,
                    age=age,
                    social_category=social_category,
                    person_id=p["person_id"],
                )
                wl = p.get("work_location")
                if wl and wl["name"]:
                    person.work_location = Location(
                        name=wl["name"],
                        location_type=LocationType(wl["type"]),
                        position=Coordinates(wl["latitude"], wl["longitude"]),
                        additional_info={},
                    )
                family.add_parent(person)
            # Children
            for c in fam_dict["children"]:
                gender = Gender(c["gender"])
                age = c["age"]
                social_category = (
                    SocialCategory(c["social_category"])
                    if c.get("social_category")
                    else None
                )
                person = Person(
                    gender=gender,
                    age=age,
                    social_category=social_category,
                    person_id=c["person_id"],
                )
                sl = c.get("school_location")
                if sl and sl["name"]:
                    person.school_location = Location(
                        name=sl["name"],
                        location_type=LocationType(sl["type"]),
                        position=Coordinates(sl["latitude"], sl["longitude"]),
                        additional_info={},
                    )
                family.add_child(person)
            families.append(family)
        return families


# --- Script entry point logic from main.py ---
def analyze_families(families: list[Family]):
    """Analyze and display statistics about the generated families."""
    child_counts: dict[int, int] = {}
    total_people = 0
    all_people = []
    for family in families:
        num_children = len(family.children)
        child_counts[num_children] = child_counts.get(num_children, 0) + 1
        total_people += family.total_members
        all_people.extend(family.parents)
        all_people.extend(family.children)
    print(f"\nFamily Analysis ({len(families)} families, {total_people} total people):")
    print("=" * 60)
    for child_count in sorted(child_counts.keys()):
        count = child_counts[child_count]
        percentage = (count / len(families)) * 100
        print(f"Families with {child_count} children: {count:4d} ({percentage:5.1f}%)")
    expected_distribution = {0: 40.0, 1: 20.0, 2: 25.0, 3: 10.0, 4: 5.0}
    print("\nExpected vs Actual Distribution:")
    print("=" * 60)
    print(f"{'Children':<10} {'Expected':<10} {'Actual':<10} {'Difference':<12}")
    print("-" * 60)
    for child_count in range(5):
        expected = expected_distribution.get(child_count, 0.0)
        actual_count = child_counts.get(child_count, 0)
        actual = (actual_count / len(families)) * 100
        difference = actual - expected
        print(
            f"{child_count:<10} {expected:<10.1f}% {actual:<10.1f}% {difference:+5.1f}%"
        )
    social_categories = Counter(
        person.social_category
        for person in all_people
        if person.social_category is not None
    )
    print(f"\nSocial Category Distribution ({len(all_people)} people):")
    print("=" * 60)
    category_names = {
        SocialCategory.FARMERS: "Farmers",
        SocialCategory.ARTISANS_MERCHANTS_ENTREPRENEURS: "Artisans, Merchants, Entrepreneurs",
        SocialCategory.EXECUTIVES_HIGHER_INTELLECTUAL_PROFESSIONS: "Executives and Higher Intellectual Professions",
        SocialCategory.INTERMEDIATE_PROFESSIONS: "Intermediate Professions",
        SocialCategory.EMPLOYEES: "Employees",
        SocialCategory.WORKERS: "Workers",
        SocialCategory.RETIREES: "Retirees",
        SocialCategory.INACTIVE: "Other Inactive Persons",
    }
    for category in SocialCategory:
        count = social_categories[category]
        percentage = (count / len(all_people)) * 100
        english_name = category_names[category]
        print(f"{english_name:<45}: {count:4d} ({percentage:5.1f}%)")
    adults_15_plus = [person for person in all_people if person.age >= 15]
    if adults_15_plus:
        adult_social_categories = Counter(
            person.social_category
            for person in adults_15_plus
            if person.social_category is not None
        )
        print(
            f"\nSocial Category Distribution - Adults 15+ only ({len(adults_15_plus)} people):"
        )
        print("=" * 60)
        print("(This matches INSEE demographic data for comparison)")
        print("-" * 60)
        for category in SocialCategory:
            count = adult_social_categories[category]
            percentage = (count / len(adults_15_plus)) * 100
            english_name = category_names[category]
            print(f"{english_name:<45}: {count:4d} ({percentage:5.1f}%)")
    inactive_people = [
        person
        for person in all_people
        if person.social_category == SocialCategory.INACTIVE
    ]
    inactive_children = [person for person in inactive_people if person.age < 15]
    inactive_adults = [person for person in inactive_people if person.age >= 15]
    print("\nInactive Category Breakdown:")
    print("=" * 60)
    print(
        f"Children under 15: {len(inactive_children):4d} ({len(inactive_children)/len(all_people)*100:5.1f}% of total population)"
    )
    print(
        f"Adults 15+:        {len(inactive_adults):4d} ({len(inactive_adults)/len(all_people)*100:5.1f}% of total population)"
    )
    if adults_15_plus:
        print(
            f"                           ({len(inactive_adults)/len(adults_15_plus)*100:5.1f}% of adults 15+)"
        )
    ages = [person.age for person in all_people]
    print("\nAge Distribution:")
    print("=" * 60)
    print(f"Average age: {sum(ages) / len(ages):.1f} years")
    print(f"Youngest: {min(ages)} years")
    print(f"Oldest: {max(ages)} years")
    age_groups = {
        "0-14 (Children)": len([age for age in ages if 0 <= age <= 14]),
        "15-24 (Young adults)": len([age for age in ages if 15 <= age <= 24]),
        "25-61 (Working adults)": len([age for age in ages if 25 <= age <= 61]),
        "62+ (Pre-retirement/Seniors)": len([age for age in ages if age >= 62]),
    }
    for group, count in age_groups.items():
        percentage = (count / len(ages)) * 100
        print(f"{group:<20}: {count:4d} ({percentage:5.1f}%)")
    religiosity_counts = Counter(family.religiosity for family in families)
    print(f"\nReligiosity Distribution ({len(families)} families):")
    print("=" * 60)
    religiosity_names = {
        Religiosity.VERY_RELIGIOUS: "Very Religious",
        Religiosity.MODERATE_RELIGIOUS: "Moderate Religious Activity",
        Religiosity.OCCASIONAL_RELIGIOUS: "Occasional Religious Activity",
        Religiosity.NO_RELIGION: "No Religion",
    }
    for religiosity in Religiosity:
        count = religiosity_counts[religiosity]
        percentage = (count / len(families)) * 100
        name = religiosity_names[religiosity]
        print(f"{name:<35}: {count:4d} ({percentage:5.1f}%)")
    expected_religiosity = {
        Religiosity.VERY_RELIGIOUS: 5.0,
        Religiosity.MODERATE_RELIGIOUS: 10.0,
        Religiosity.OCCASIONAL_RELIGIOUS: 30.0,
        Religiosity.NO_RELIGION: 55.0,
    }
    print("\nExpected vs Actual Religiosity Distribution:")
    print("=" * 60)
    print(f"{'Religiosity':<35} {'Expected':<10} {'Actual':<10} {'Difference':<12}")
    print("-" * 60)
    for religiosity in Religiosity:
        expected = expected_religiosity[religiosity]
        actual_count = religiosity_counts[religiosity]
        actual = (actual_count / len(families)) * 100
        difference = actual - expected
        name = religiosity_names[religiosity]
        print(f"{name:<35} {expected:<10.1f}% {actual:<10.1f}% {difference:+5.1f}%")


if __name__ == "__main__":
    # Accept file path argument
    if len(sys.argv) > 1:
        family_file = sys.argv[1]
    else:
        family_file = "data/families.json"
    print(f"Using family file: {family_file}")
    generator = FamilyGenerator()
    if os.path.exists(family_file):
        print(f"Loading families from {family_file}...")
        families = generator.load_families(family_file)
        print(f"Loaded {len(families)} families from file.")
    else:
        print("Generating 1000 families with realistic characteristics distribution...")
        families = generator.generate_families(1000)
        print(f"Successfully generated {len(families)} families.")
        # Assign home, work, and school locations to each family
        assigner = LocationAssigner(
            "data/toulouse_locations_of_interest.geojson"
        )
        for family in families:
            assigner.assign_locations_to_family(family)
        print("✓ Locations assigned to all families.")
        print(f"Saving families to {family_file}...")
        generator.save_families(families, family_file)
        print(f"✓ Families saved to {family_file}")
    # Verify location assignment
    missing_home = sum(1 for fam in families if not fam.home_position)
    missing_work = sum(
        1 for fam in families for p in fam.parents if not p.work_location
    )
    missing_school = sum(
        1 for fam in families for c in fam.children if not c.school_location
    )
    print(
        f"Location assignment check: {missing_home} families missing home, {missing_work} parents missing work, {missing_school} children missing school location."
    )
    if missing_home or missing_work or missing_school:
        print(
            "WARNING: Some locations were not assigned. Check assignment logic and input data."
        )
    print("\nLocation Assignment Summary:")
    print(f"Families missing home: {missing_home}")
    print(f"Parents missing work: {missing_work}")
    print(f"Children missing school: {missing_school}")
    print("(If any value above is nonzero, check assignment logic and input data)")
    print("\nFirst 5 families:")
    for i, family in enumerate(families[:5]):
        print(f"{i+1}. {family}")
        for j, parent in enumerate(family.parents):
            print(f"   Parent {j+1}: {parent}")
        for j, child in enumerate(family.children):
            print(f"   Child {j+1}: {child}")
    analyze_families(families)
    unique_ids = set(family.family_id for family in families)
    print(
        f"\nVerification: {len(unique_ids)} unique family IDs out of {len(families)} families"
    )
    if len(unique_ids) == len(families):
        print("✓ All families have unique identifiers")
    else:
        print("✗ Some families have duplicate identifiers")
