from datetime import date
from decimal import Decimal
from models.event import Event, EventType
from utils.vesting_calculator import DefaultVestingCalculator


class TestVestingCalculator:
    def test_calculate_vested_shares(self):
        calculator = DefaultVestingCalculator()
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
                event_type=EventType.VEST,
                employee_id="E001",
                employee_name="Alice Smith",
                award_id="ISO-001",
                event_date=date(2021, 1, 1),
                quantity=Decimal(2000)
            )
        ]
        target_date = date(2020, 6, 1)

        vested_shares = calculator.calculate_vested_shares(events, target_date)

        assert vested_shares == Decimal(1000)

    def test_calculate_cancelled_shares(self):
        calculator = DefaultVestingCalculator()
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
                event_type=EventType.CANCEL,
                employee_id="E001",
                employee_name="Alice Smith",
                award_id="ISO-002",
                event_date=date(2020, 3, 1),
                quantity=Decimal(200)
            )
        ]
        target_date = date(2020, 6, 1)

        cancelled_shares = calculator.calculate_cancelled_shares(events, target_date)

        assert cancelled_shares == Decimal(200)

    def test_calculate_performance_bonus(self):
        calculator = DefaultVestingCalculator()
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
                event_date=date(2020, 3, 1),
                quantity=Decimal(2)
            )
        ]
        target_date = date(2020, 6, 1)

        performance_bonus = calculator.calculate_performance_bonus(events, target_date)

        assert performance_bonus == Decimal(2)

    def test_calculate_vested_shares_outside_of_target_date(self):
        calculator = DefaultVestingCalculator()
        events = [
            Event(
                event_type=EventType.VEST,
                employee_id="E001",
                employee_name="Alice Smith",
                award_id="ISO-001",
                event_date=date(2021, 7, 1),
                quantity=Decimal(1000)
            )
        ]
        target_date = date(2021, 6, 1)

        vested_shares = calculator.calculate_vested_shares(events, target_date)

        assert vested_shares == Decimal(0)

    def test_calculate_cancelled_shares_outside_of_target_date(self):
        calculator = DefaultVestingCalculator()
        events = [
            Event(
                event_type=EventType.CANCEL,
                employee_id="E001",
                employee_name="Alice Smith",
                award_id="ISO-001",
                event_date=date(2021, 1, 1),
                quantity=Decimal(1000)
            )
        ]
        target_date = date(2020, 6, 1)

        cancelled_shares = calculator.calculate_cancelled_shares(events, target_date)

        assert cancelled_shares == Decimal(0)

    def test_calculate_performance_bonus_outside_of_target_date(self):
        calculator = DefaultVestingCalculator()
        events = [
            Event(
                event_type=EventType.PERFORMANCE,
                employee_id="E001",
                employee_name="Alice Smith",
                award_id="ISO-001",
                event_date=date(2021, 1, 1),
                quantity=Decimal(1.5)
            ),
            Event(
                event_type=EventType.PERFORMANCE,
                employee_id="E001",
                employee_name="Alice Smith",
                award_id="ISO-001",
                event_date=date(2020, 1, 1),
                quantity=Decimal(0.5)
            )
        ]
        target_date = date(2020, 6, 1)

        performance_bonus = calculator.calculate_performance_bonus(events, target_date)

        assert performance_bonus == Decimal(0.5)
