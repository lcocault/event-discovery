import pytest
from event.event_dispatcher import EventDispatcher
from event.event import Event
from fastapi import HTTPException


class FakeEventRepository:
    def get_event(self, event_id: str):
        if event_id == "valid_id":
            return Event(
                id="valid_id",
                name="Test Event",
                start_time="2025-11-01T10:00:00Z",
                end_time="2025-11-01T12:00:00Z",
                latitude=42.0,
                longitude=1.5,
            )
        return None


@pytest.mark.asyncio
async def test_get_event_event_id_found():
    # GIVEN: An EventDispatcher with a fake repository returning a valid event
    repository = FakeEventRepository()
    dispatcher = EventDispatcher(repository)

    # WHEN: The method is called with a valid event ID
    event_id = "valid_id"
    result = await dispatcher.get_events_event_id(event_id)

    # THEN: The result should be an Event with matching details
    assert result.id == "valid_id"
    assert result.name == "Test Event"


@pytest.mark.asyncio
async def test_get_event_event_id_not_found():
    # GIVEN: An EventDispatcher with a fake repository returning None
    repository = FakeEventRepository()
    dispatcher = EventDispatcher(repository)

    # WHEN: The method is called with an invalid event ID
    event_id = "invalid_id"

    # THEN: An HTTPException should be raised
    with pytest.raises(HTTPException) as exc_info:
        await dispatcher.get_events_event_id(event_id)

    assert exc_info.value.status_code == 404
    assert "Event with ID invalid_id not found" in str(exc_info.value)
