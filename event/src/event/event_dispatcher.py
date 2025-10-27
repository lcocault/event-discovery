"""Dispatcher of REST API calls to the event service."""

from .event_repository import EventRepository
from .event import Event
from fastapi import HTTPException
from api.stubs.event.models import Event as JsonEvent
from math import radians, cos, sin, sqrt, atan2


class EventDispatcher:
    def __init__(self, repository: EventRepository) -> None:
        self.repository = repository

    async def get_events_event_id(self, event_id: str) -> JsonEvent:
        evt: Event | None = self.repository.get_event(event_id)
        if evt is None:
            raise HTTPException(
                status_code=404, detail=f"Event with ID {event_id} not found"
            )
        return JsonEvent(
            id=evt.id,
            name=evt.name,
            latitude=evt.latitude,
            longitude=evt.longitude,
            start_time=evt.start_time if evt.start_time else None,
            end_time=evt.end_time if evt.end_time else None,
        )

    async def get_events_around(
        self, latitude: float, longitude: float, time
    ) -> list[JsonEvent]:
        def haversine(lat1, lon1, lat2, lon2):
            R = 6371  # Earth radius in km
            dlat = radians(lat2 - lat1)
            dlon = radians(lon2 - lon1)
            a = (
                sin(dlat / 2) ** 2
                + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
            )
            c = 2 * atan2(sqrt(a), sqrt(1 - a))
            return R * c

        query_time = time  # Already a datetime object

        results = []
        for evt in self.repository.get_all_events():
            # Check if event is within 500 m radius
            dist = haversine(latitude, longitude, evt.latitude, evt.longitude)
            if dist > 0.5:
                continue
            # Check if event overlaps with query time
            if evt.start_time and evt.end_time:
                try:
                    start = evt.start_time
                    end = evt.end_time
                except Exception:
                    continue
                if not (start <= query_time <= end):
                    continue
            results.append(
                JsonEvent(
                    id=evt.id,
                    name=evt.name,
                    latitude=evt.latitude,
                    longitude=evt.longitude,
                    start_time=evt.start_time,
                    end_time=evt.end_time,
                )
            )
        return results
