from datetime import date
from decimal import Decimal

from models.event import Event, EventType
from services.award_calculator_service import AwardCalculatorService


class TestAwardCalculatorServiceIntegration:
    def test_calculate_vested_shares(self):
        service = AwardCalculatorService()
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
                quantity=Decimal(300)
            )
        ]
        target_date = date(2022, 1, 1)

        for event in events:
            service.award_event_store.add_award_event(event)
        result = service.calculate_vested_shares("ISO-001", target_date)

        assert result == Decimal(1300)

    def test_calculate_cancelled_shares(self):
        service = AwardCalculatorService()
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
                award_id="ISO-001",
                event_date=date(2021, 1, 1),
                quantity=Decimal(300)
            )
        ]
        target_date = date(2022, 1, 1)

        for event in events:
            service.award_event_store.add_award_event(event)
        result = service.calculate_cancelled_shares("ISO-001", target_date)

        assert result == Decimal(300)

    def test_calculate_performance_events(self):
        service = AwardCalculatorService()
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
                award_id="ISO-001",
                event_date=date(2021, 1, 1),
                quantity=Decimal(300)
            ),
            Event(
                event_type=EventType.PERFORMANCE,
                employee_id="E001",
                employee_name="Alice Smith",
                award_id="ISO-001",
                event_date=date(2021, 1, 1),
                quantity=Decimal(3)
            )
        ]
        target_date = date(2022, 1, 1)

        for event in events:
            service.award_event_store.add_award_event(event)
        result = service.calculate_performance_events("ISO-001", target_date)

        assert result == Decimal(3)

    def test_calculate_net_vested_shares(self):
        service = AwardCalculatorService()
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
                award_id="ISO-001",
                event_date=date(2021, 1, 1),
                quantity=Decimal(300)
            )
        ]
        target_date = date(2022, 1, 1)

        for event in events:
            service.award_event_store.add_award_event(event)
        result = service.calculate_net_vested_shares("ISO-001", target_date)

        assert result == Decimal(700)

    def test_non_existent_award_id(self):
        service = AwardCalculatorService()
        target_date = date(2022, 1, 1)

        result = service.calculate_vested_shares("NON-EXISTENT-ID", target_date)

        assert result == Decimal(0)

    def test_empty_event_list(self):
        service = AwardCalculatorService()
        events = [
            Event(
                event_type=EventType.VEST,
                employee_id="E001",
                employee_name="Alice Smith",
                award_id="ISO-001",
                event_date=date(2020, 1, 1),
                quantity=Decimal(1000)
            )
        ]
        target_date = date(2022, 1, 1)

        for event in events:
            service.award_event_store.add_award_event(event)
        result = service.calculate_cancelled_shares("ISO-001", target_date)

        assert result == Decimal(0)

    def test_target_date_before_events(self):
        service = AwardCalculatorService()
        events = [
            Event(
                event_type=EventType.VEST,
                employee_id="E001",
                employee_name="Alice Smith",
                award_id="ISO-001",
                event_date=date(2020, 1, 1),
                quantity=Decimal(1000)
            )
        ]
        target_date = date(2019, 1, 1)

        for event in events:
            service.award_event_store.add_award_event(event)
        result = service.calculate_vested_shares("ISO-001", target_date)

        assert result == Decimal(0)

    def test_future_events(self):
        service = AwardCalculatorService()
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
                event_date=date(2022, 1, 1),
                quantity=Decimal(500)
            )
        ]
        target_date = date(2021, 1, 1)

        for event in events:
            service.award_event_store.add_award_event(event)
        result = service.calculate_vested_shares("ISO-001", target_date)

        assert result == Decimal(1000)

    def test_cancellations_greater_than_vested(self):
        service = AwardCalculatorService()
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
                award_id="ISO-001",
                event_date=date(2021, 1, 1),
                quantity=Decimal(2000)
            )
        ]
        target_date = date(2022, 1, 1)

        for event in events:
            service.award_event_store.add_award_event(event)
        result = service.calculate_net_vested_shares("ISO-001", target_date)

        assert result == Decimal(0)

    def test_performance_events_with_no_events(self):
        service = AwardCalculatorService()
        target_date = date(2022, 1, 1)

        result = service.calculate_performance_events("ISO-001", target_date)

        assert result == Decimal(1)
