from datetime import date
from decimal import Decimal
import pytest

from models.event import Event, EventType
from services.vesting_service import VestingService
from exceptions.vesting_exception import VestingValidationError

class TestVestingService:
    def test_process_vest_events(self):
        service = VestingService()

        events = [
            Event(
                event_type=EventType.VEST,
                employee_id="E001",
                employee_name="Alice Smith",
                award_id="ISO-001",
                event_date=date(2020, 1, 1),
                quantity=Decimal("1000")
            ),
            Event(
                event_type=EventType.VEST,
                employee_id="E001",
                employee_name="Alice Smith",
                award_id="ISO-001",
                event_date=date(2020, 2, 1),
                quantity=Decimal("500")
            )
        ]

        service.process_events(events)

        assert len(service.employees) == 1
        assert "E001" in service.employees

        employee = service.employees["E001"]
        assert employee.employee_id == "E001"
        assert employee.name == "Alice Smith"
        assert len(employee.awards) == 1
        assert "ISO-001" in employee.awards

        award = employee.awards["ISO-001"]
        assert award.award_id == "ISO-001"
        assert award.employee_id == "E001"
        assert award.employee_name == "Alice Smith"
        assert len(award.vested_events) == 2
        assert len(award.cancelled_events) == 0

        assert award.vested_events[0].quantity == Decimal("1000")
        assert award.vested_events[1].quantity == Decimal("500")

    def test_process_cancel_events(self):
        service = VestingService()

        events = [
            Event(
                event_type=EventType.VEST,
                employee_id="E001",
                employee_name="Alice Smith",
                award_id="ISO-001",
                event_date=date(2020, 1, 1),
                quantity=Decimal("1000")
            ),
            Event(
                event_type=EventType.CANCEL,
                employee_id="E001",
                employee_name="Alice Smith",
                award_id="ISO-001",
                event_date=date(2020, 2, 1),
                quantity=Decimal("300")
            )
        ]

        service.process_events(events)
        employee = service.employees["E001"]
        award = employee.awards["ISO-001"]

        assert len(award.vested_events) == 1
        assert len(award.cancelled_events) == 1
        assert award.vested_events[0].quantity == Decimal("1000")
        assert award.cancelled_events[0].quantity == Decimal("300")

    def test_process_cancel_more_than_vested(self):
        service = VestingService()

        events = [
            Event(
                event_type=EventType.VEST,
                employee_id="E001",
                employee_name="Alice Smith",
                award_id="ISO-001",
                event_date=date(2020, 1, 1),
                quantity=Decimal("1000")
            ),
            Event(
                event_type=EventType.CANCEL,
                employee_id="E001",
                employee_name="Alice Smith",
                award_id="ISO-001",
                event_date=date(2020, 2, 1),
                quantity=Decimal("1500")
            )
        ]

        with pytest.raises(VestingValidationError, match="Cannot cancel more shares than vested"):
            service.process_events(events)

    def test_get_vesting_schedule(self):
        service = VestingService()

        events = [
            Event(
                event_type=EventType.VEST,
                employee_id="E001",
                employee_name="Alice Smith",
                award_id="ISO-001",
                event_date=date(2020, 1, 1),
                quantity=Decimal("1000")
            ),
            Event(
                event_type=EventType.VEST,
                employee_id="E001",
                employee_name="Alice Smith",
                award_id="ISO-002",
                event_date=date(2020, 3, 1),
                quantity=Decimal("300")
            ),
            Event(
                event_type=EventType.VEST,
                employee_id="E001",
                employee_name="Alice Smith",
                award_id="ISO-002",
                event_date=date(2020, 4, 1),
                quantity=Decimal("500")
            ),
            Event(
                event_type=EventType.VEST,
                employee_id="E002",
                employee_name="John Small",
                award_id="NSO-001",
                event_date=date(2020, 1, 2),
                quantity=Decimal("100")
            ),
            Event(
                event_type=EventType.VEST,
                employee_id="E002",
                employee_name="John Small",
                award_id="NSO-001",
                event_date=date(2020, 3, 2),
                quantity=Decimal("300")
            ),
        ]

        service.process_events(events)
        target_date = date(2020, 4, 1)
        schedule = service.get_vesting_schedule(target_date)

        assert len(schedule) == 3
        assert schedule[0] == ("E001", "Alice Smith", "ISO-001", Decimal("1000"))
        assert schedule[1] == ("E001", "Alice Smith", "ISO-002", Decimal("800"))
        assert schedule[2] == ("E002", "John Small", "NSO-001", Decimal("400"))

    def test_get_vesting_schedule_with_cancel(self):
        service = VestingService()

        events = [
            Event(
                event_type=EventType.VEST,
                employee_id="E001",
                employee_name="Alice Smith",
                award_id="ISO-001",
                event_date=date(2020, 1, 1),
                quantity=Decimal("1000")
            ),
            Event(
                event_type=EventType.CANCEL,
                employee_id="E001",
                employee_name="Alice Smith",
                award_id="ISO-001",
                event_date=date(2021, 2, 1),
                quantity=Decimal("300")
            )
        ]

        service.process_events(events)
        target_date = date(2021, 3, 1)
        schedule = service.get_vesting_schedule(target_date)

        assert len(schedule) == 1
        assert schedule[0] == ("E001", "Alice Smith", "ISO-001", Decimal("700"))
