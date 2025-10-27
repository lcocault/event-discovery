"""Simple in-memory repository for Event objects."""

from typing import Dict, List, Optional
from .event import Event
import json
from datetime import datetime, timezone


class EventRepository:
    def __init__(self) -> None:
        self._events: Dict[str, Event] = {}

    def add_event(self, event: Event) -> None:
        if event.id and event.id not in self._events:
            self._events[event.id] = event

    def add_events(self, events: List[Event]) -> None:
        for e in events:
            self.add_event(e)

    def get_event(self, event_id: str) -> Optional[Event]:
        return self._events.get(event_id)

    def get_all_events(self) -> List[Event]:
        return list(self._events.values())

    def clear(self) -> None:
        self._events.clear()

    def __len__(self) -> int:
        return len(self._events)

    def __repr__(self) -> str:
        return f"EventRepository(events={len(self._events)})"

    def load_events_from_locations_geojson(self, geojson_path: str) -> None:
        DEFAULT_HOURS = {
            "theatre": ("18:00", "23:00"),
            "museum": ("10:00", "18:00"),
            "work_place": ("08:00", "19:00"),
            "restaurant": ("12:00", "22:00"),
            "entertainment": ("18:00", "01:00"),
            "default": ("09:00", "18:00"),
        }
        with open(geojson_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        for feature in data.get("features", []):
            props = feature.get("properties", {})
            coords = feature.get("geometry", {}).get("coordinates", [None, None])
            name = props.get("name", "Unknown")
            location_type = props.get("location_type", "default")
            opening_hours = props.get("opening_hours")
            # Parse opening_hours if available, else use default
            if (
                opening_hours
                and isinstance(opening_hours, str)
                and "24/7" in opening_hours
            ):
                start_time, end_time = "00:00", "23:59"
            elif opening_hours and isinstance(opening_hours, str):
                # Simple parser for 'HH:MM-HH:MM' format
                import re

                match = re.match(r"(\d{2}:\d{2})-(\d{2}:\d{2})", opening_hours)
                if match:
                    start_time, end_time = match.groups()
                else:
                    start_time, end_time = DEFAULT_HOURS.get(
                        location_type, DEFAULT_HOURS["default"]
                    )
            else:
                start_time, end_time = DEFAULT_HOURS.get(
                    location_type, DEFAULT_HOURS["default"]
                )
            # Use today's date for event, ensure offset-aware (UTC)
            today = datetime.now(timezone.utc).date().isoformat()
            start_dt = datetime.fromisoformat(f"{today}T{start_time}+00:00")
            end_dt = datetime.fromisoformat(f"{today}T{end_time}+00:00")
            evt = Event.create(
                name=name,
                latitude=coords[1],
                longitude=coords[0],
                start_time=start_dt,
                end_time=end_dt,
                metadata=props,
            )
            self.add_event(evt)
