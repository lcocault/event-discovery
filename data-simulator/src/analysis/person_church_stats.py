import pandas as pd
import shapely.wkb
import json

person_id = "3344076f-0aa3-442c-b7f2-cb35e709f7b1"
# Load events
events = pd.read_parquet("events.parquet")
person_events = events[events["person_id"] == person_id]
# Load churches
with open("data/toulouse_churches.geojson") as f:
    churches = json.load(f)["features"]
church_coords = set(
    (
        round(f["geometry"]["coordinates"][1], 6),
        round(f["geometry"]["coordinates"][0], 6),
    )
    for f in churches
)


def geom_to_latlon(g):
    try:
        geom = shapely.wkb.loads(g)
        return (round(geom.y, 6), round(geom.x, 6))
    except Exception:
        return (None, None)


person_events = person_events.copy()
person_events["latlon"] = person_events["geometry"].apply(geom_to_latlon)
church_events = person_events[
    person_events["latlon"].apply(lambda x: x in church_coords)
]
print(f"Total events for person: {len(person_events)}")
print(f"Church events for person: {len(church_events)}")
if not church_events.empty:
    print("Sample church event coordinates:", church_events["latlon"].unique()[:5])
else:
    print("No church events found for this person.")
