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
            raise HTTPException(status_code=404, detail=f"Event with ID {event_id} not found")
        return JsonEvent(
            id=evt.id,
            name=evt.name,
            latitude=evt.latitude,
            longitude=evt.longitude,
            start_time=evt.start_time,
            end_time=evt.end_time,
        )
