"""Dispatcher of REST API calls to the event service."""

from .event_repository import EventRepository
from .event import Event
from fastapi import HTTPException
from api.stubs.event.models import Event as JsonEvent


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
            start_time=evt.start_time,
            end_time=evt.end_time,
        )

    async def get_events_around(
        self, latitude: float, longitude: float, time: str
    ) -> list[JsonEvent]:
        from datetime import datetime
        from math import radians, cos, sin, sqrt, atan2

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

        try:
            query_time = datetime.fromisoformat(time)
        except Exception:
            raise HTTPException(
                status_code=400, detail="Invalid time format. Use ISO 8601."
            )

        results = []
        for evt in self.repository.get_all_events():
            # Check if event is within 5km radius
            dist = haversine(latitude, longitude, evt.latitude, evt.longitude)
            if dist > 5:
                continue
            # Check if event overlaps with query time
            if evt.start_time and evt.end_time:
                try:
                    start = datetime.fromisoformat(evt.start_time)
                    end = datetime.fromisoformat(evt.end_time)
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
