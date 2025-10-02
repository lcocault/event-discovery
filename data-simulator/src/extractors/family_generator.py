"""Family generation utilities with child distribution logic."""

import random
from typing import List, Tuple
from models.family import Family
from models.person import Person, Gender, SocialCategory, Religiosity


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
        """Generate a random person with random gender and age."""
        gender = random.choice(list(Gender))
        age = random.randint(min_age, max_age)
        return Person(gender=gender, age=age)

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
            import math

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
        parent_ages = [p.age for p in parents]
        if parent_ages:
            social_category = self._get_social_category_for_age(max(parent_ages))
        else:
            social_category = SocialCategory.INACTIVE
        family = Family(religiosity=religiosity, social_category=social_category)
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
        from models.location import Position

        def family_to_dict(family: Family):
            return {
                "family_id": family.family_id,
                "religiosity": family.religiosity.value if family.religiosity else None,
                "social_category": family.social_category.value
                if family.social_category
                else None,
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
        from models.location import Position, Location, LocationType
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
            social_category = (
                SocialCategory(fam_dict["social_category"])
                if fam_dict.get("social_category")
                else None
            )
            family = Family(
                family_id=fam_dict["family_id"],
                religiosity=religiosity,
                social_category=social_category,
            )
            # Home position
            hp = fam_dict.get("home_position")
            if hp and hp["latitude"] is not None and hp["longitude"] is not None:
                family.home_position = Position(hp["latitude"], hp["longitude"])
            # Parents
            for p in fam_dict["parents"]:
                gender = Gender(p["gender"])
                age = p["age"]
                person = Person(gender=gender, age=age, person_id=p["person_id"])
                wl = p.get("work_location")
                if wl and wl["name"]:
                    person.work_location = Location(
                        name=wl["name"],
                        location_type=LocationType(wl["type"]),
                        position=Position(wl["latitude"], wl["longitude"]),
                        additional_info={},
                    )
                family.add_parent(person)
            # Children
            for c in fam_dict["children"]:
                gender = Gender(c["gender"])
                age = c["age"]
                person = Person(gender=gender, age=age, person_id=c["person_id"])
                sl = c.get("school_location")
                if sl and sl["name"]:
                    person.school_location = Location(
                        name=sl["name"],
                        location_type=LocationType(sl["type"]),
                        position=Position(sl["latitude"], sl["longitude"]),
                        additional_info={},
                    )
                family.add_child(person)
            families.append(family)
        return families
