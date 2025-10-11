import argparse
import pandas as pd
import sys


def load_events(events_file):
    try:
        return pd.read_parquet(events_file)
    except Exception as e:
        print(f"Error loading events file: {e}")
        sys.exit(1)


def global_stats(df):
    print("Global Event Statistics:")
    print(f"Total events: {len(df)}")
    if "person_id" in df.columns:
        print(f"Unique persons: {df['person_id'].nunique()}")
    if "location_id" in df.columns:
        print(f"Unique locations: {df['location_id'].nunique()}")
    if "event_type" in df.columns:
        print("Event types:")
        print(df["event_type"].value_counts())


def person_stats(df, person):
    if "person_id" not in df.columns:
        print("No person_id column in events file.")
        return
    person_df = df[df["person_id"] == person]
    if person_df.empty:
        print(f"No events found for person: {person}")
        return
    print(f"Statistics for person {person}:")
    print(f"Total events: {len(person_df)}")
    if "event_type" in person_df.columns:
        print("Event types:")
        print(person_df["event_type"].value_counts())
    # Group by position (geometry or lat/lon columns)
    if "geometry" in person_df.columns:
        from shapely import wkb, wkt

        def geom_to_lonlat(g):
            try:
                # If already a shapely geometry
                if hasattr(g, "x") and hasattr(g, "y"):
                    return (g.x, g.y)
                # If WKB bytes
                if isinstance(g, (bytes, bytearray)):
                    geom = wkb.loads(g)
                    return (geom.x, geom.y)
                # If WKT string
                if isinstance(g, str) and g.strip().startswith("POINT"):
                    geom = wkt.loads(g)
                    return (geom.x, geom.y)
            except Exception:
                pass
            return str(g)

        pos_series = person_df["geometry"].apply(geom_to_lonlat)
    elif "latitude" in person_df.columns and "longitude" in person_df.columns:
        pos_series = person_df.apply(
            lambda row: f"({row['latitude']}, {row['longitude']})", axis=1
        )
    else:
        pos_series = None

    if pos_series is not None:
        print(f"Unique positions visited: {pos_series.nunique()}")
        pos_counts = pos_series.value_counts(normalize=True) * 100
        print("Position breakdown (percentage of events):")
        for pos, pct in pos_counts.items():
            print(f"  {pos}: {pct:.2f}%")


def location_stats(df, location):
    if "location_id" not in df.columns:
        print("No location_id column in events file.")
        return
    location_df = df[df["location_id"] == location]
    if location_df.empty:
        print(f"No events found for location: {location}")
        return
    print(f"Statistics for location {location}:")
    print(f"Total events: {len(location_df)}")
    if "event_type" in location_df.columns:
        print("Event types:")
        print(location_df["event_type"].value_counts())
    if "person_id" in location_df.columns:
        print(f"Unique persons: {location_df['person_id'].nunique()}")


def main():
    parser = argparse.ArgumentParser(description="Show statistics about events.")
    parser.add_argument("events_file", help="Path to events file (parquet)")
    parser.add_argument("--person", help="Person ID to filter statistics", default=None)
    parser.add_argument(
        "--location", help="Location ID to filter statistics", default=None
    )
    args = parser.parse_args()

    df = load_events(args.events_file)

    if args.person:
        person_stats(df, args.person)
    elif args.location:
        location_stats(df, args.location)
    else:
        global_stats(df)


if __name__ == "__main__":
    main()
