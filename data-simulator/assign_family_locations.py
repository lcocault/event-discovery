#!/usr/bin/env python3
"""
Family Location Assignment Demo

This script generates test families and assigns them home positions, 
schools for children, and work locations for adults.
"""

import sys
import json
from pathlib import Path
from typing import List, Dict

# Add src to Python path
src_dir = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_dir))

from models.family import Family
from models.person import Person
from extractors.family_generator import FamilyGenerator
from location_assigner import LocationAssigner


def generate_test_families(count: int = 50) -> List[Family]:
    """Generate test families for location assignment."""
    print(f"Generating {count} test families...")
    
    generator = FamilyGenerator()
    families = generator.generate_families(count)
    
    print(f"✓ Generated {len(families)} families")
    
    # Show some statistics
    total_people = sum(family.total_members for family in families)
    children_count = sum(len(family.children) for family in families)
    adults_count = sum(len(family.parents) for family in families)
    
    print(f"  - Total people: {total_people}")
    print(f"  - Adults: {adults_count}")
    print(f"  - Children: {children_count}")
    
    return families


def assign_locations_to_families(families: List[Family]) -> bool:
    """Assign locations to all families."""
    print(f"\nAssigning locations to {len(families)} families...")
    
    # Initialize the location assigner with GeoJSON files
    educational_geojson = "toulouse_educational_institutions.geojson"
    hospitality_geojson = "toulouse_hospitality_venues.geojson"
    
    if not Path(educational_geojson).exists():
        print(f"❌ Error: {educational_geojson} not found")
        print("Please run the educational extraction script first:")
        print("python src/extract_educational.py")
        return False
    
    if not Path(hospitality_geojson).exists():
        print(f"❌ Error: {hospitality_geojson} not found") 
        print("Please run the hospitality extraction script first:")
        print("python src/extract_hospitality.py")
        return False
    
    try:
        assigner = LocationAssigner(educational_geojson, hospitality_geojson)
        
        print(f"✓ Loaded {len(assigner.educational_locations)} educational institutions")
        print(f"✓ Loaded {len(assigner.work_locations)} work locations")
        
        # Show school types available
        school_counts = {}
        for school_type, schools in assigner.schools_by_type.items():
            school_counts[school_type.value] = len(schools)
        
        print("  School types available:")
        for school_type, count in sorted(school_counts.items()):
            print(f"    - {school_type.title()}: {count}")
        
        # Assign locations to each family (modifies family objects in place)
        for i, family in enumerate(families):
            assigner.assign_locations_to_family(family)
            
            if (i + 1) % 10 == 0:
                print(f"  Processed {i + 1}/{len(families)} families...")
        
        print(f"✓ Location assignment completed for all families")
        return True
        
    except Exception as e:
        print(f"❌ Error during location assignment: {e}")
        import traceback
        traceback.print_exc()
        return False


def show_assignment_examples(families: List[Family], count: int = 5):
    """Show examples of location assignments."""
    print(f"\nShowing {count} example family assignments:")
    print("=" * 80)
    
    for i, family in enumerate(families[:count]):
        if not family.home_position:
            continue
            
        home_pos = family.home_position
        
        print(f"\nFamily {i+1}: {family.family_id[:8]}...")
        print(f"  Home: ({home_pos.latitude:.6f}, {home_pos.longitude:.6f})")
        print(f"  Members: {len(family.parents)} parents, {len(family.children)} children")
        
        # Show children and their schools
        if family.children:
            print("  Children & Schools:")
            for child in family.children:
                if child.school_location:
                    distance = LocationAssigner.calculate_distance(home_pos, child.school_location.position)
                    print(f"    - {child.gender.value.title()}, age {child.age}: {child.school_location.name} ({child.school_location.location_type.value}) - {distance:.2f}km")
                else:
                    print(f"    - {child.gender.value.title()}, age {child.age}: No suitable school found")
        
        # Show adults and their work locations
        if family.parents:
            print("  Adults & Work:")
            for parent in family.parents:
                if parent.work_location:
                    distance = LocationAssigner.calculate_distance(home_pos, parent.work_location.position)
                    print(f"    - {parent.gender.value.title()}, age {parent.age} ({parent.social_category.value}): {parent.work_location.name} ({parent.work_location.location_type.value}) - {distance:.2f}km")
                else:
                    print(f"    - {parent.gender.value.title()}, age {parent.age} ({parent.social_category.value}): UNEMPLOYED")


def show_assignment_statistics(families: List[Family]):
    """Show detailed statistics about location assignments."""
    print("\n" + "=" * 80)
    print("LOCATION ASSIGNMENT STATISTICS")
    print("=" * 80)
    
    if not families:
        print("No families to analyze")
        return
    
    # Use LocationAssigner to get statistics
    assigner = LocationAssigner(
        "toulouse_educational_institutions.geojson",
        "toulouse_hospitality_venues.geojson"  
    )
    stats = assigner.get_assignment_statistics(families)
    
    # Count children, adults, and employment by gender
    total_children = sum(len(family.children) for family in families)
    total_adults = sum(len(family.parents) for family in families)
    
    # Count adults by gender and employment status
    male_adults = 0
    female_adults = 0
    employed_males = 0
    employed_females = 0
    
    for family in families:
        for parent in family.parents:
            if parent.gender.value.lower() == 'male':
                male_adults += 1
                if parent.work_location:
                    employed_males += 1
            elif parent.gender.value.lower() == 'female':
                female_adults += 1
                if parent.work_location:
                    employed_females += 1
    
    print(f"Total families processed: {stats['total_families']}")
    print(f"Total people: {total_children + total_adults}")
    print(f"  - Children: {total_children}")
    print(f"  - Adults: {total_adults}")
    
    print(f"\nSchool Assignments:")
    print(f"  - Children with schools: {stats['children_with_schools']}")
    print(f"  - Children without schools: {total_children - stats['children_with_schools']}")
    if total_children > 0:
        assignment_rate = (stats['children_with_schools'] / total_children) * 100
        print(f"  - Assignment rate: {assignment_rate:.1f}%")
    
    if stats.get('avg_school_distance'):
        print(f"  - Average distance to school: {stats['avg_school_distance']}km")
    
    print(f"\nWork Assignments:")
    print(f"  - Adults with work: {stats['adults_with_work']}")
    print(f"  - Adults without work: {total_adults - stats['adults_with_work']}")
    if total_adults > 0:
        assignment_rate = (stats['adults_with_work'] / total_adults) * 100
        print(f"  - Overall employment rate: {assignment_rate:.1f}%")
    
    # Show employment by gender
    print(f"\nEmployment by Gender:")
    if male_adults > 0:
        male_employment_rate = (employed_males / male_adults) * 100
        print(f"  - Male adults: {male_adults} (employed: {employed_males}, rate: {male_employment_rate:.1f}%)")
    else:
        print(f"  - Male adults: 0")
    
    if female_adults > 0:
        female_employment_rate = (employed_females / female_adults) * 100
        print(f"  - Female adults: {female_adults} (employed: {employed_females}, rate: {female_employment_rate:.1f}%)")
    else:
        print(f"  - Female adults: 0")
    
    if stats.get('avg_work_distance'):
        print(f"  - Average distance to work: {stats['avg_work_distance']}km")
    
    # Show school type distribution
    if stats['school_type_distribution']:
        print(f"\nSchool Type Distribution:")
        for school_type, count in sorted(stats['school_type_distribution'].items()):
            print(f"  - {school_type.title()}: {count}")
    
    # Show work type distribution
    if stats['work_type_distribution']:
        print(f"\nWork Type Distribution:")
        for work_type, count in sorted(stats['work_type_distribution'].items()):
            print(f"  - {work_type.title()}: {count}")


def export_assignments_to_json(families: List[Family], output_file: str = "family_location_assignments.json"):
    """Export family and location data to JSON for further analysis."""
    print(f"\nExporting assignments to {output_file}...")
    
    export_data = {
        "metadata": {
            "total_families": len(families),
            "generation_timestamp": "2024-09-21"
        },
        "families": []
    }
    
    for family in families:
        if not family.home_position:
            continue  # Skip families without home positions
            
        family_data = {
            "family_id": family.family_id,
            "religiosity": family.religiosity.value if family.religiosity else None,
            "home_position": {
                "latitude": family.home_position.latitude,
                "longitude": family.home_position.longitude
            },
            "parents": [],
            "children": []
        }
        
        # Add parents with work info
        for parent in family.parents:
            parent_data = {
                "person_id": parent.person_id,
                "gender": parent.gender.value,
                "age": parent.age,
                "social_category": parent.social_category.value,
                "work": None
            }
            
            if parent.work_location:
                distance = LocationAssigner.calculate_distance(family.home_position, parent.work_location.position)
                parent_data["work"] = {
                    "location_id": parent.work_location.location_id,
                    "name": parent.work_location.name,
                    "type": parent.work_location.location_type.value,
                    "position": {
                        "latitude": parent.work_location.position.latitude,
                        "longitude": parent.work_location.position.longitude
                    },
                    "distance_km": round(distance, 2)
                }
            
            family_data["parents"].append(parent_data)
        
        # Add children with school info
        for child in family.children:
            child_data = {
                "person_id": child.person_id,
                "gender": child.gender.value,
                "age": child.age,
                "social_category": child.social_category.value,
                "school": None
            }
            
            if child.school_location:
                distance = LocationAssigner.calculate_distance(family.home_position, child.school_location.position)
                child_data["school"] = {
                    "location_id": child.school_location.location_id,
                    "name": child.school_location.name,
                    "type": child.school_location.location_type.value,
                    "position": {
                        "latitude": child.school_location.position.latitude,
                        "longitude": child.school_location.position.longitude
                    },
                    "distance_km": round(distance, 2)
                }
            
            family_data["children"].append(child_data)
        
        export_data["families"].append(family_data)
    
    # Write to JSON file
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Successfully exported {len(export_data['families'])} families to {output_file}")
        print(f"  File size: {Path(output_file).stat().st_size / 1024:.1f} KB")
        
    except Exception as e:
        print(f"❌ Error exporting to JSON: {e}")


def main():
    """Main function to demonstrate family location assignment."""
    print("FAMILY LOCATION ASSIGNMENT DEMO")
    print("=" * 80)
    
    # Step 1: Generate test families
    families = generate_test_families(50)  # Generate 50 test families
    if not families:
        return 1
    
    # Step 2: Assign locations (modifies family objects in place)
    success = assign_locations_to_families(families)
    if not success:
        return 1
    
    # Step 3: Show examples
    show_assignment_examples(families)
    
    # Step 4: Show statistics
    show_assignment_statistics(families)
    
    # Step 5: Export to JSON
    export_assignments_to_json(families)
    
    print("\n" + "=" * 80)
    print("✓ Family location assignment demo completed successfully!")
    print("=" * 80)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())