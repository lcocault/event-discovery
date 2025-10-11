import pandas as pd
import shapely.wkb
import json
import numpy as np

# Load events
events = pd.read_parquet("events.parquet")


# Load churches
def load_church_coords():
    with open("data/toulouse_churches.geojson") as f:
        churches = json.load(f)["features"]
    return set(
        (
            round(feat["geometry"]["coordinates"][1], 6),
            round(feat["geometry"]["coordinates"][0], 6),
        )
        for feat in churches
    )


church_coords = load_church_coords()


def geom_to_latlon(g):
    try:
        geom = shapely.wkb.loads(g)
        return (round(geom.y, 6), round(geom.x, 6))
    except Exception:
        return (np.nan, np.nan)


events["latlon"] = events["geometry"].apply(geom_to_latlon)
church_event_count = events["latlon"].apply(lambda x: x in church_coords).sum()
print(f"Church events: {church_event_count}")
