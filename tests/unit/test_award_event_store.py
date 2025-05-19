from datetime import date
from decimal import Decimal

import pytest

from repositories.award_event_store import AwardEventStore
from models.event import EventType, Event


class TestAwardEventStore:
    def test_add_award_event(self):
        store = AwardEventStore()
        event = Event(
            event_type=EventType.VEST,
            employee_id="E001",
            employee_name="Alice Smith",
            award_id="ISO-001",
            event_date=date(2020, 1, 1),
            quantity=Decimal(1000)
        )

        store.add_award_event(event)

        assert len(store.events_collections) == 1
        assert len(store.events_collections[event.award_id][event.event_type]) == 1
        assert store.events_collections[event.award_id][event.event_type][0] == event


    def test_get_all_award_event(self):
        store = AwardEventStore()
        events = [
            Event(
                event_type=EventType.VEST,
                employee_id="E001",
                employee_name="Alice Smith",
                award_id="ISO-001",
                event_date=date(2020, 1, 1),
                quantity=Decimal(1000)
            ),
            Event(
                event_type=EventType.PERFORMANCE,
                employee_id="E001",
                employee_name="Alice Smith",
                award_id="ISO-002",
                event_date=date(2020, 1, 1),
                quantity=Decimal(1.5)
            )
        ]

        for event in events:
            store.add_award_event(event)
        result = store.get_all_award_events("ISO-002", EventType.PERFORMANCE)

        assert len(store.events_collections) == 2
        assert len(result) == 1
        assert events[1] in result


    def test_get_all_award_ids(self):
        store = AwardEventStore()
        events = [
            Event(
                event_type=EventType.VEST,
                employee_id="E001",
                employee_name="Alice Smith",
                award_id="ISO-001",
                event_date=date(2020, 1, 1),
                quantity=Decimal(1000)
            ),
            Event(
                event_type=EventType.PERFORMANCE,
                employee_id="E001",
                employee_name="Alice Smith",
                award_id="ISO-003",
                event_date=date(2020, 1, 1),
                quantity=Decimal(1)
            )
        ]

        for events in events:
            store.add_award_event(events)
        result = store.get_all_award_ids()

        assert len(store.events_collections) == 2
        assert len(result) == 2
        assert "ISO-001" in result
        assert "ISO-003" in result

    def test_add_none_event(self):
        store = AwardEventStore()

        with pytest.raises(AttributeError):
            store.add_award_event(None)

    def test_add_invalid_event_type(self):
        store = AwardEventStore()
        invalid_event = {"event_type": "VEST", "award_id": "ISO-001"}

        with pytest.raises(AttributeError):
            store.add_award_event(invalid_event)

    def test_get_non_existent_award_id(self):
        store = AwardEventStore()
        result = store.get_all_award_events("nonexistent-id", EventType.VEST)

        assert result == []

    def test_get_none_event_type(self):
        store = AwardEventStore()

        with pytest.raises(KeyError):
            store.get_all_award_events("ISO-001", None)

    def test_get_no_events_for_type(self):
        store = AwardEventStore()
        event = Event(
            event_type=EventType.VEST,
            employee_id="E001",
            employee_name="Alice Smith",
            award_id="ISO-001",
            event_date=date(2020, 1, 1),
            quantity=Decimal(1000)
        )

        store.add_award_event(event)
        result = store.get_all_award_events("ISO-001", EventType.CANCEL)

        assert result == []
