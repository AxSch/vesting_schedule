from datetime import date
from decimal import Decimal

import pytest

from models.event import Event, EventType


class TestEventModel:
    def test_create_valid_vest_event(self):
        event = Event(
            event_type=EventType.VEST,
            employee_id="E001",
            employee_name="Alice Smith",
            award_id="ISO-001",
            event_date=date(2020, 1, 1),
            quantity=Decimal("1000")
        )


        assert event.event_type == EventType.VEST
        assert event.employee_id == "E001"
        assert event.employee_name == "Alice Smith"
        assert event.award_id == "ISO-001"
        assert event.event_date == date(2020, 1, 1)
        assert event.quantity == Decimal("1000")

    def test_create_cancel_event(self):
        event = Event(
            event_type=EventType.CANCEL,
            employee_id="E001",
            employee_name="Alice Smith",
            award_id="ISO-001",
            event_date=date(2020, 1, 1),
            quantity=Decimal("1000")
        )


        assert event.event_type == EventType.CANCEL
        assert event.employee_id == "E001"
        assert event.employee_name == "Alice Smith"
        assert event.award_id == "ISO-001"
        assert event.event_date == date(2020, 1, 1)
        assert event.quantity == Decimal("1000")

    def test_invalid_event_type(self):
        with pytest.raises(ValueError):
            Event(
                event_type="INVALID",
                employee_id="E001",
                employee_name="Alice Smith",
                award_id="ISO-001",
                event_date=date(2020, 1, 1),
                quantity=Decimal("1000")
            )

    def test_zero_quantity(self):
        with pytest.raises(ValueError):
            Event(
                event_type=EventType.VEST,
                employee_id="E001",
                employee_name="Alice Smith",
                award_id="ISO-001",
                event_date=date(2020, 1, 1),
                quantity=Decimal("0")
            )

    def test_negative_quantity(self):
        with pytest.raises(ValueError):
            Event(
                event_type=EventType.VEST,
                employee_id="E001",
                employee_name="Alice Smith",
                award_id="ISO-001",
                event_date=date(2020, 1, 1),
                quantity=Decimal("-10")
            )

    def test_fractional_quantity(self):
        event = Event(
            event_type=EventType.VEST,
            employee_id="E001",
            employee_name="Alice Smith",
            award_id="ISO-001",
            event_date=date(2020, 1, 1),
            quantity=Decimal("10.501")
        )

        assert event.quantity == Decimal("10.501")
