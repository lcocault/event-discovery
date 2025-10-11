import shapely.wkb
import argparse
import pandas as pd
import logging
from models.location_repository import LocationRepository

# Set up logger
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger("person_location_categories")


def geom_to_latlon(g):
    try:
        geom = shapely.wkb.loads(g)
        return (round(geom.y, 6), round(geom.x, 6))
    except Exception:
        return (None, None)


def main():
    parser = argparse.ArgumentParser(
        description="Show all locations in a person's events, with categories."
    )
    parser.add_argument("--person", required=True, help="Person ID to analyze")
    args = parser.parse_args()
    person_id = args.person

    # Load events
    events = pd.read_parquet("events.parquet")
    person_events = events[events["person_id"] == person_id].copy()
    person_events["latlon"] = person_events["geometry"].apply(geom_to_latlon)
    unique_coords = set(person_events["latlon"])

    # Load all locations from the repository
    repo = LocationRepository()
    repo.add_locations_from_geojson("data/toulouse_churches.geojson")
    repo.add_locations_from_geojson("data/toulouse_entertainment_venues.geojson")
    repo.add_locations_from_geojson("data/toulouse_hospitality_venues.geojson")
    repo.add_locations_from_geojson("data/toulouse_work_places.geojson")
    repo.add_locations_from_geojson("data/toulouse_educational_institutions.geojson")

    # Build a mapping from coordinates to (name, type)
    coord_to_info = {}
    for loc in repo.get_all_locations():
        lat, lon = round(loc.position.latitude, 6), round(loc.position.longitude, 6)
        coord_to_info[(lat, lon)] = (loc.name, loc.location_type.value)

    # Display all unique locations in the person's events
    logger.info("Locations in person events:")
    for coord in unique_coords:
        info = coord_to_info.get(coord, None)
        if info:
            logger.info(f"{coord}: {info[0]} [{info[1]}]")
        else:
            logger.info(f"{coord}: Home [Home]")


if __name__ == "__main__":
    main()
