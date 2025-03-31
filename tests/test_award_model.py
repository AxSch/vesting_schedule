from datetime import date
from decimal import Decimal

import pytest
from pydantic import ValidationError

from models.award import Award
from models.event import Event, EventType


class TestAwardModel:
    def test_valid_award(self):
        award = Award(
            award_id="ISO-001",
            employee_id="E001",
            employee_name="Alice Smith",
            cancelled_events=[],
            vested_events=[]
        )

        assert award.award_id == "ISO-001"
        assert award.employee_id == "E001"
        assert award.employee_name == "Alice Smith"

    def test_invalid_award(self):
        with pytest.raises(ValidationError):
            Award(
                award_id="",
                employee_id="E001",
                employee_name="Alice Smith",
                cancelled_events=[],
                vested_events=[]
            )

    def test_add_vested_event(self):
        award = Award(
            award_id="ISO-001",
            employee_id="E001",
            employee_name="Alice Smith",
            cancelled_events = [],
            vested_events = []
        )

        event = Event(
            event_type=EventType.VEST,
            employee_id="E001",
            employee_name="Alice Smith",
            award_id="ISO-001",
            event_date=date(2020, 1, 1),
            quantity=Decimal("1000")
        )

        award.add_vested_event(event)

        assert len(award.vested_events) == 1
        assert award.vested_events[0] == event

    def test_add_cancelled_event(self):
        award = Award(
            award_id="ISO-001",
            employee_id="E001",
            employee_name="Alice Smith",
            cancelled_events=[],
            vested_events=[]
        )

        event = Event(
            event_type=EventType.CANCEL,
            employee_id="E001",
            employee_name="Alice Smith",
            award_id="ISO-001",
            event_date=date(2020, 1, 1),
            quantity=Decimal("1000")
        )

        award.add_cancelled_event(event)

        assert len(award.cancelled_events) == 1
        assert award.cancelled_events[0] == event

    def test_total_vested_shares_single_event(self):
        award = Award(
            award_id="ISO-001",
            employee_id="E001",
            employee_name="Alice Smith",
            cancelled_events=[],
            vested_events=[]
        )

        event = Event(
            event_type=EventType.VEST,
            employee_id="E001",
            employee_name="Alice Smith",
            award_id="ISO-001",
            event_date=date(2020, 1, 1),
            quantity=Decimal("1000")
        )

        award.add_vested_event(event)

        assert award.total_vested_shares(date(2019, 12, 31)) == Decimal("0")
        assert award.total_vested_shares(date(2020, 1, 1)) == Decimal("1000")
        assert award.total_vested_shares(date(2020, 2, 1)) == Decimal("1000")

    def test_total_vested_shares_with_multiple_events(self):
        award = Award(
            award_id="ISO-001",
            employee_id="E001",
            employee_name="Alice Smith",
            cancelled_events=[],
            vested_events=[]
        )

        event_one = Event(
            event_type=EventType.VEST,
            employee_id="E001",
            employee_name="Alice Smith",
            award_id="ISO-001",
            event_date=date(2020, 1, 1),
            quantity=Decimal("1000")
        )

        event_two = Event(
            event_type=EventType.VEST,
            employee_id="E001",
            employee_name="Alice Smith",
            award_id="ISO-001",
            event_date=date(2020, 2, 1),
            quantity=Decimal("50.450")
        )

        award.add_vested_event(event_one)
        award.add_vested_event(event_two)

        assert award.total_vested_shares(date(2019, 12, 31)) == Decimal("0")
        assert award.total_vested_shares(date(2020, 1, 15)) == Decimal("1000")
        assert award.total_vested_shares(date(2020, 2, 15)) == Decimal("1050.450")

    def test_total_cancelled_shares(self):
        award = Award(
            award_id="ISO-001",
            employee_id="E001",
            employee_name="Alice Smith",
            cancelled_events=[],
            vested_events=[]
        )

        event_one = Event(
            event_type=EventType.CANCEL,
            employee_id="E001",
            employee_name="Alice Smith",
            award_id="ISO-001",
            event_date=date(2020, 2, 1),
            quantity=Decimal("1000")
        )

        event_two = Event(
            event_type=EventType.CANCEL,
            employee_id="E001",
            employee_name="Alice Smith",
            award_id="ISO-001",
            event_date=date(2020, 3, 1),
            quantity=Decimal("200")
        )

        award.add_cancelled_event(event_one)
        award.add_cancelled_event(event_two)

        assert award.total_cancelled_shares(date(2020, 1, 31)) == Decimal("0")
        assert award.total_cancelled_shares(date(2020, 2, 15)) == Decimal("1000")
        assert award.total_cancelled_shares(date(2020, 3, 15)) == Decimal("1200")

    def test_net_vested_shares(self):
        award = Award(
            award_id="ISO-001",
            employee_id="E001",
            employee_name="Alice Smith",
            cancelled_events=[],
            vested_events=[]
        )

        vest_event_one = Event(
            event_type=EventType.VEST,
            employee_id="E001",
            employee_name="Alice Smith",
            award_id="ISO-001",
            event_date=date(2020, 1, 1),
            quantity=Decimal("1000")
        )

        vest_event_two = Event(
            event_type=EventType.VEST,
            employee_id="E001",
            employee_name="Alice Smith",
            award_id="ISO-001",
            event_date=date(2020, 2, 20),
            quantity=Decimal("2560.50")
        )

        cancel_event_one = Event(
            event_type=EventType.CANCEL,
            employee_id="E001",
            employee_name="Alice Smith",
            award_id="ISO-001",
            event_date=date(2020, 2, 1),
            quantity=Decimal("500")
        )

        cancel_event_two = Event(
            event_type=EventType.CANCEL,
            employee_id="E001",
            employee_name="Alice Smith",
            award_id="ISO-001",
            event_date=date(2020, 3, 1),
            quantity=Decimal("240.56")
        )

        award.add_vested_event(vest_event_one)
        award.add_vested_event(vest_event_two)
        award.add_cancelled_event(cancel_event_one)
        award.add_cancelled_event(cancel_event_two)

        assert award.net_vested_shares(date(2019, 12, 31)) == Decimal("0")
        assert award.net_vested_shares(date(2020, 1, 15)) == Decimal("1000")
        assert award.net_vested_shares(date(2020, 2, 15)) == Decimal("500")
        assert award.net_vested_shares(date(2020, 3, 15)) == Decimal("2819.94")

    def test_net_vested_shares_with_precision(self):
        award = Award(
            award_id="ISO-001",
            employee_id="E001",
            employee_name="Alice Smith",
            cancelled_events=[],
            vested_events=[]
        )
        vest_event = Event(
            event_type=EventType.VEST,
            employee_id="E001",
            employee_name="Alice Smith",
            award_id="ISO-001",
            event_date=date(2020, 1, 1),
            quantity=Decimal("1000.567")
        )

        cancel_event = Event(
            event_type=EventType.CANCEL,
            employee_id="E001",
            employee_name="Alice Smith",
            award_id="ISO-001",
            event_date=date(2020, 2, 1),
            quantity=Decimal("300.123")
        )

        award.add_vested_event(vest_event)
        award.add_cancelled_event(cancel_event)

        assert award.net_vested_shares(date(2020, 3, 1), 0) == Decimal("700.444")
        assert award.net_vested_shares(date(2020, 3, 1), 1) == Decimal("700.444")
        assert award.net_vested_shares(date(2020, 3, 1), 2) == Decimal("700.444")
        assert award.net_vested_shares(date(2020, 3, 1), 3) == Decimal("700.444")

    def test_cancelled_is_more_than_vested(self):
        award = Award(
            award_id="ISO-001",
            employee_id="E001",
            employee_name="Alice Smith",
            cancelled_events=[],
            vested_events=[]
        )

        vest_event = Event(
            event_type=EventType.VEST,
            employee_id="E001",
            employee_name="Alice Smith",
            award_id="ISO-001",
            event_date=date(2020, 1, 1),
            quantity=Decimal("1000")
        )

        cancel_event = Event(
            event_type=EventType.CANCEL,
            employee_id="E001",
            employee_name="Alice Smith",
            award_id="ISO-001",
            event_date=date(2020, 2, 1),
            quantity=Decimal("1500")
        )

        award.add_vested_event(vest_event)
        award.add_cancelled_event(cancel_event)

        assert award.net_vested_shares(date(2020, 3, 1)) == Decimal("0")
