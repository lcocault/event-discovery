"""Main program to generate family data."""

from collections import Counter
from models.family import Family
from extractors.family_generator import FamilyGenerator
from models.person import SocialCategory, Religiosity
from location_assigner import LocationAssigner
from models.location import Position
import sys
import os


def generate_families(count: int = 1000) -> list[Family]:
    """
    Generate a specified number of Family instances with proper child distribution.
    
    Child distribution:
    - 40% of families have no children
    - 20% of families have 1 child
    - 25% of families have 2 children
    - 10% of families have 3 children
    - 5% of families have 4 children
    
    Args:
        count: Number of families to generate (default: 1000)
    
    Returns:
        List of Family instances
    """
    generator = FamilyGenerator()
    return generator.generate_families(count)


def analyze_families(families: list[Family]) -> None:
    """Analyze and display statistics about the generated families."""
    # Count families by number of children
    child_counts = {}
    total_people = 0
    all_people = []
    
    for family in families:
        num_children = family.num_children
        child_counts[num_children] = child_counts.get(num_children, 0) + 1
        total_people += family.total_members
        
        # Collect all people for social category analysis
        all_people.extend(family.parents)
        all_people.extend(family.children)
    
    print(f"\nFamily Analysis ({len(families)} families, {total_people} total people):")
    print("=" * 60)
    
    # Display distribution
    for child_count in sorted(child_counts.keys()):
        count = child_counts[child_count]
        percentage = (count / len(families)) * 100
        print(f"Families with {child_count} children: {count:4d} ({percentage:5.1f}%)")
    
    # Expected vs actual distribution
    expected_distribution = {
        0: 40.0,  # 40% no children
        1: 20.0,  # 20% 1 child
        2: 25.0,  # 25% 2 children
        3: 10.0,  # 10% 3 children
        4: 5.0,   # 5% 4 children
    }
    
    print("\nExpected vs Actual Distribution:")
    print("=" * 60)
    print(f"{'Children':<10} {'Expected':<10} {'Actual':<10} {'Difference':<12}")
    print("-" * 60)
    
    for child_count in range(5):
        expected = expected_distribution.get(child_count, 0.0)
        actual_count = child_counts.get(child_count, 0)
        actual = (actual_count / len(families)) * 100
        difference = actual - expected
        
        print(f"{child_count:<10} {expected:<10.1f}% {actual:<10.1f}% {difference:+5.1f}%")
    
    # Social category analysis
    social_categories = Counter(person.social_category for person in all_people)
    
    print(f"\nSocial Category Distribution ({len(all_people)} people):")
    print("=" * 60)
    
    # English category names for display
    category_names = {
        SocialCategory.FARMERS: "Farmers",
        SocialCategory.ARTISANS_MERCHANTS_ENTREPRENEURS: "Artisans, Merchants, Entrepreneurs",
        SocialCategory.EXECUTIVES_HIGHER_INTELLECTUAL_PROFESSIONS: "Executives and Higher Intellectual Professions",
        SocialCategory.INTERMEDIATE_PROFESSIONS: "Intermediate Professions",
        SocialCategory.EMPLOYEES: "Employees",
        SocialCategory.WORKERS: "Workers",
        SocialCategory.RETIREES: "Retirees",
        SocialCategory.INACTIVE: "Other Inactive Persons"
    }
    
    for category in SocialCategory:
        count = social_categories[category]
        percentage = (count / len(all_people)) * 100
        english_name = category_names[category]
        print(f"{english_name:<45}: {count:4d} ({percentage:5.1f}%)")
    
    # Additional analysis for adults (15+) to match INSEE data
    adults_15_plus = [person for person in all_people if person.age >= 15]
    if adults_15_plus:
        adult_social_categories = Counter(person.social_category for person in adults_15_plus)
        
        print(f"\nSocial Category Distribution - Adults 15+ only ({len(adults_15_plus)} people):")
        print("=" * 60)
        print("(This matches INSEE demographic data for comparison)")
        print("-" * 60)
        
        for category in SocialCategory:
            count = adult_social_categories[category]
            percentage = (count / len(adults_15_plus)) * 100
            english_name = category_names[category]
            print(f"{english_name:<45}: {count:4d} ({percentage:5.1f}%)")
    
    # Breakdown of inactive category by age
    inactive_people = [person for person in all_people if person.social_category == SocialCategory.INACTIVE]
    inactive_children = [person for person in inactive_people if person.age < 15]
    inactive_adults = [person for person in inactive_people if person.age >= 15]
    
    print(f"\nInactive Category Breakdown:")
    print("=" * 60)
    print(f"Children under 15: {len(inactive_children):4d} ({len(inactive_children)/len(all_people)*100:5.1f}% of total population)")
    print(f"Adults 15+:        {len(inactive_adults):4d} ({len(inactive_adults)/len(all_people)*100:5.1f}% of total population)")
    if adults_15_plus:
        print(f"                           ({len(inactive_adults)/len(adults_15_plus)*100:5.1f}% of adults 15+)")
    
    # Age distribution analysis
    ages = [person.age for person in all_people]
    print(f"\nAge Distribution:")
    print("=" * 60)
    print(f"Average age: {sum(ages) / len(ages):.1f} years")
    print(f"Youngest: {min(ages)} years")
    print(f"Oldest: {max(ages)} years")
    
    # Age groups
    age_groups = {
        "0-14 (Children)": len([age for age in ages if 0 <= age <= 14]),
        "15-24 (Young adults)": len([age for age in ages if 15 <= age <= 24]),
        "25-61 (Working adults)": len([age for age in ages if 25 <= age <= 61]),
        "62+ (Pre-retirement/Seniors)": len([age for age in ages if age >= 62])
    }
    
    for group, count in age_groups.items():
        percentage = (count / len(ages)) * 100
        print(f"{group:<20}: {count:4d} ({percentage:5.1f}%)")
    
    # Religiosity analysis
    religiosity_counts = Counter(family.religiosity for family in families)
    
    print(f"\nReligiosity Distribution ({len(families)} families):")
    print("=" * 60)
    
    # Religiosity names for display
    religiosity_names = {
        Religiosity.VERY_RELIGIOUS: "Very Religious",
        Religiosity.MODERATE_RELIGIOUS: "Moderate Religious Activity",
        Religiosity.OCCASIONAL_RELIGIOUS: "Occasional Religious Activity",
        Religiosity.NO_RELIGION: "No Religion"
    }
    
    for religiosity in Religiosity:
        count = religiosity_counts[religiosity]
        percentage = (count / len(families)) * 100
        name = religiosity_names[religiosity]
        print(f"{name:<35}: {count:4d} ({percentage:5.1f}%)")
    
    # Expected vs actual religiosity distribution
    expected_religiosity = {
        Religiosity.VERY_RELIGIOUS: 5.0,      # 5% very religious
        Religiosity.MODERATE_RELIGIOUS: 10.0, # 10% moderate
        Religiosity.OCCASIONAL_RELIGIOUS: 30.0, # 30% occasional
        Religiosity.NO_RELIGION: 55.0,        # 55% no religion
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


def main():
    """Main program entry point."""
    # Accept file path argument
    if len(sys.argv) > 1:
        family_file = sys.argv[1]
    else:
        family_file = "families.json"
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
            "toulouse_educational_institutions.geojson",
            "toulouse_hospitality_venues.geojson"
        )
        for family in families:
            assigner.assign_locations_to_family(family)
        print("✓ Locations assigned to all families.")

        print(f"Saving families to {family_file}...")
        generator.save_families(families, family_file)
        print(f"✓ Families saved to {family_file}")

    # Verify location assignment
    missing_home = sum(1 for fam in families if not fam.home_position)
    missing_work = sum(1 for fam in families for p in fam.parents if not p.work_location)
    missing_school = sum(1 for fam in families for c in fam.children if not c.school_location)
    print(f"Location assignment check: {missing_home} families missing home, {missing_work} parents missing work, {missing_school} children missing school location.")
    if missing_home or missing_work or missing_school:
        print("WARNING: Some locations were not assigned. Check assignment logic and input data.")

    # Print assignment stats summary
    print("\nLocation Assignment Summary:")
    print(f"Families missing home: {missing_home}")
    print(f"Parents missing work: {missing_work}")
    print(f"Children missing school: {missing_school}")
    print("(If any value above is nonzero, check assignment logic and input data)")

    # Display first 5 families as examples
    print("\nFirst 5 families:")
    for i, family in enumerate(families[:5]):
        print(f"{i+1}. {family}")
        for j, parent in enumerate(family.parents):
            print(f"   Parent {j+1}: {parent}")
        for j, child in enumerate(family.children):
            print(f"   Child {j+1}: {child}")

    # Analyze family distribution
    analyze_families(families)

    # Verify all families have unique IDs
    unique_ids = set(family.family_id for family in families)
    print(f"\nVerification: {len(unique_ids)} unique family IDs out of {len(families)} families")

    if len(unique_ids) == len(families):
        print("✓ All families have unique identifiers")
    else:
        print("✗ Some families have duplicate identifiers")

    # Trigger event generation and save events if a second argument is provided
    if len(sys.argv) > 2:
        event_file = sys.argv[2]
        print(f"Generating events and saving to {event_file}...")
        from extractors.event_generator import EventGenerator
        event_generator = EventGenerator(families)
        event_generator.generate_events()
        event_generator.save_events(event_file)
        print(f"✓ Events saved to {event_file}")


if __name__ == "__main__":
    main()