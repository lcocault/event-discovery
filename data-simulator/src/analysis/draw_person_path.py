import sys
import json
import pandas as pd
import geopandas as gpd
import logging
from typing import List, Dict

# Set up logger
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger("draw_person_path")


# Helper to load family data (assume JSON)
def load_family(family_path: str) -> Dict:
    with open(family_path, "r") as f:
        return json.load(f)


# Helper to load events data (Parquet file)
def load_events(events_path: str) -> List[Dict]:
    df = gpd.read_parquet(events_path)
    # Convert DataFrame to list of dicts, geometry as shapely objects
    return df.to_dict(orient="records")


# Extract home and work/school positions for a person
def get_person_locations(families: List[Dict], person_id: str):
    home = None
    work_school = None
    for family in families:
        for member in family.get("parents", []) + family.get("children", []):
            if member.get("person_id") == person_id:
                home = family.get("home_position")
                # Try work_location for parents, school_location for children
                work_school = member.get("work_location") or member.get(
                    "school_location"
                )
                return home, work_school
    return home, work_school


# Extract events for a person
def get_person_events(events_data: List[Dict], person_id: str) -> List[Dict]:
    return [e for e in events_data if e.get("person_id") == person_id]


# Build GeoJSON feature
def build_kml(home, work_school, events):
    # Extract coordinates from geometry column
    positions = []
    for e in events:
        geom = e.get("geometry")
        if geom and hasattr(geom, "x") and hasattr(geom, "y"):
            positions.append((geom.x, geom.y))
        elif geom and isinstance(geom, str) and geom.startswith("POINT"):
            coords = geom.replace("POINT", "").replace("(", "").replace(")", "").split()
            positions.append((float(coords[0]), float(coords[1])))

    kml = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<kml xmlns="http://www.opengis.net/kml/2.2">',
        "  <Document>",
        "    <name>Person Path</name>",
        "    <Placemark>",
        "      <name>Path</name>",
        "      <LineString>",
        "        <coordinates>",
    ]
    for x, y in positions:
        kml.append(f"{x},{y},0 ")
    kml += ["        </coordinates>", "      </LineString>", "    </Placemark>"]
    # Home placemark
    if home:
        kml += [
            "    <Placemark>",
            "      <name>Home</name>",
            f'      <Point><coordinates>{home["longitude"]},{home["latitude"]},0</coordinates></Point>',
            "    </Placemark>",
        ]
    # Work/school placemark
    if work_school:
        kml += [
            "    <Placemark>",
            "      <name>Work/School</name>",
            f'      <Point><coordinates>{work_school["longitude"]},{work_school["latitude"]},0</coordinates></Point>',
            "    </Placemark>",
        ]
    kml += ["  </Document>", "</kml>"]
    return "\n".join(kml)


if __name__ == "__main__":
    if len(sys.argv) != 4:
        logger.error(
            "Usage: draw_person_path.py <family_file> <events_file> <person_id>"
        )
        sys.exit(1)
    family_file = sys.argv[1]
    events_file = sys.argv[2]
    person_id = sys.argv[3]
    families = load_family(family_file)
    events_data = load_events(events_file)
    home, work_school = get_person_locations(families, person_id)
    person_events = get_person_events(events_data, person_id)
    kml = build_kml(home, work_school, person_events)
    logger.info(kml)
