"""Simple in-memory repository for Event objects."""

from typing import Dict, List, Optional
from .event import Event


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
