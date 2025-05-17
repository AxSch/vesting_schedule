from datetime import date
from decimal import Decimal
from unittest.mock import Mock

from models.event import Event, EventType
from services.award_calculator_service import AwardCalculatorService
from interfaces.award_event_store import IAwardEventStore
from interfaces.vesting_calculator import IVestingCalculator


class TestAwardCalculatorServiceIntegration:
    def setup_method(self):
        self.mock_award_event_store = Mock(spec=IAwardEventStore)
        self.mock_calculator = Mock(spec=IVestingCalculator)

        self.service = AwardCalculatorService(
            award_event_store=self.mock_award_event_store,
            use_numba_calculator=False
        )

        self.service.calculator = self.mock_calculator

    def test_calculate_vested_shares(self):
        # Setup test data
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
        award_id = "ISO-001"
        expected_result = Decimal(1300)

        # Configure mocks
        self.mock_award_event_store.get_all_award_events.return_value = events
        self.mock_calculator.calculate_vested_shares.return_value = expected_result

        # Call the method under test
        result = self.service.calculate_vested_shares(award_id, target_date)

        # Verify the result and mock interactions
        assert result == expected_result
        self.mock_award_event_store.get_all_award_events.assert_called_once_with(award_id, EventType.VEST)
        self.mock_calculator.calculate_vested_shares.assert_called_once_with(events, target_date)

    def test_calculate_cancelled_shares(self):
        # Setup test data
        events = [
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
        award_id = "ISO-001"
        expected_result = Decimal(300)

        # Configure mocks
        self.mock_award_event_store.get_all_award_events.return_value = events
        self.mock_calculator.calculate_cancelled_shares.return_value = expected_result

        # Call the method under test
        result = self.service.calculate_cancelled_shares(award_id, target_date)

        # Verify the result and mock interactions
        assert result == expected_result
        self.mock_award_event_store.get_all_award_events.assert_called_once_with(award_id, EventType.CANCEL)
        self.mock_calculator.calculate_cancelled_shares.assert_called_once_with(events, target_date)

    def test_calculate_performance_events(self):
        # Setup test data
        events = [
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
        award_id = "ISO-001"
        expected_result = Decimal(3)

        # Configure mocks
        self.mock_award_event_store.get_all_award_events.return_value = events
        self.mock_calculator.calculate_performance_bonus.return_value = expected_result

        # Call the method under test
        result = self.service.calculate_performance_events(award_id, target_date)

        # Verify the result and mock interactions
        assert result == expected_result
        self.mock_award_event_store.get_all_award_events.assert_called_once_with(award_id, EventType.PERFORMANCE)
        self.mock_calculator.calculate_performance_bonus.assert_called_once_with(events, target_date)

    def test_calculate_net_vested_shares(self):
        target_date = date(2022, 1, 1)
        award_id = "ISO-001"
        vested_shares = Decimal(1000)
        cancelled_shares = Decimal(300)
        expected_result = Decimal(700)

        service_with_mocked_methods = AwardCalculatorService(
            award_event_store=self.mock_award_event_store,
            use_numba_calculator=False
        )
        service_with_mocked_methods.calculate_vested_shares = Mock(return_value=vested_shares)
        service_with_mocked_methods.calculate_cancelled_shares = Mock(return_value=cancelled_shares)

        result = service_with_mocked_methods.calculate_net_vested_shares(award_id, target_date)

        assert result == expected_result
        service_with_mocked_methods.calculate_vested_shares.assert_called_once_with(award_id, target_date)
        service_with_mocked_methods.calculate_cancelled_shares.assert_called_once_with(award_id, target_date)

    def test_non_existent_award_id(self):
        target_date = date(2022, 1, 1)
        award_id = "NON-EXISTENT-ID"
        expected_result = Decimal(0)

        self.mock_award_event_store.get_all_award_events.return_value = []
        self.mock_calculator.calculate_vested_shares.return_value = expected_result

        result = self.service.calculate_vested_shares(award_id, target_date)

        assert result == expected_result
        self.mock_award_event_store.get_all_award_events.assert_called_once_with(award_id, EventType.VEST)
        self.mock_calculator.calculate_vested_shares.assert_called_once_with([], target_date)

    def test_empty_event_list(self):
        target_date = date(2022, 1, 1)
        award_id = "ISO-001"
        expected_result = Decimal(0)

        self.mock_award_event_store.get_all_award_events.return_value = []
        self.mock_calculator.calculate_cancelled_shares.return_value = expected_result

        result = self.service.calculate_cancelled_shares(award_id, target_date)

        assert result == expected_result
        self.mock_award_event_store.get_all_award_events.assert_called_once_with(award_id, EventType.CANCEL)
        self.mock_calculator.calculate_cancelled_shares.assert_called_once_with([], target_date)

    def test_target_date_before_events(self):
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
        award_id = "ISO-001"
        expected_result = Decimal(0)
        self.mock_award_event_store.get_all_award_events.return_value = events
        self.mock_calculator.calculate_vested_shares.return_value = expected_result

        result = self.service.calculate_vested_shares(award_id, target_date)

        assert result == expected_result
        self.mock_award_event_store.get_all_award_events.assert_called_once_with(award_id, EventType.VEST)
        self.mock_calculator.calculate_vested_shares.assert_called_once_with(events, target_date)

    def test_future_events(self):
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
        award_id = "ISO-001"
        expected_result = Decimal(1000)
        self.mock_award_event_store.get_all_award_events.return_value = events
        self.mock_calculator.calculate_vested_shares.return_value = expected_result

        result = self.service.calculate_vested_shares(award_id, target_date)

        assert result == expected_result
        self.mock_award_event_store.get_all_award_events.assert_called_once_with(award_id, EventType.VEST)
        self.mock_calculator.calculate_vested_shares.assert_called_once_with(events, target_date)

    def test_cancellations_greater_than_vested(self):
        target_date = date(2022, 1, 1)
        award_id = "ISO-001"
        vested_shares = Decimal(1000)
        cancelled_shares = Decimal(2000)
        expected_result = Decimal(0)
        service_with_mocked_methods = AwardCalculatorService(
            award_event_store=self.mock_award_event_store,
            use_numba_calculator=False
        )
        service_with_mocked_methods.calculate_vested_shares = Mock(return_value=vested_shares)
        service_with_mocked_methods.calculate_cancelled_shares = Mock(return_value=cancelled_shares)

        result = service_with_mocked_methods.calculate_net_vested_shares(award_id, target_date)

        assert result == expected_result
        service_with_mocked_methods.calculate_vested_shares.assert_called_once_with(award_id, target_date)
        service_with_mocked_methods.calculate_cancelled_shares.assert_called_once_with(award_id, target_date)

    def test_performance_events_with_no_events(self):
        target_date = date(2022, 1, 1)
        award_id = "ISO-001"
        expected_result = Decimal(1)
        self.mock_award_event_store.get_all_award_events.return_value = []
        self.mock_calculator.calculate_performance_bonus.return_value = expected_result

        result = self.service.calculate_performance_events(award_id, target_date)

        assert result == expected_result
        self.mock_award_event_store.get_all_award_events.assert_called_once_with(award_id, EventType.PERFORMANCE)
        self.mock_calculator.calculate_performance_bonus.assert_called_once_with([], target_date)
