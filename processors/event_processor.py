from datetime import date
from typing import Optional

from exceptions.vesting_exception import VestingValidationError
from interfaces.award_calculator_service import IAwardCalculatorService
from interfaces.award_event_store import IAwardEventStore
from interfaces.event_processor import IEventProcessor
from models.event import EventType, Event

@IEventProcessor.register(EventType.VEST)
class VestEventProcessor(IEventProcessor):
    async def validate_event(self, event: Event, calculation_service: IAwardCalculatorService, target_date: Optional[date] = None) -> None:
        if event.quantity <= 0:
            raise VestingValidationError(
                f"Vest quantity must be positive, got {event.quantity}"
            )

    async def process_event(self, event: Event, event_store: IAwardEventStore) -> None:
        event_store.add_award_event(event)


@IEventProcessor.register(EventType.CANCEL)
class CancelEventProcessor(IEventProcessor):
    async def validate_event(self, event: Event, calculation_service: IAwardCalculatorService, target_date: Optional[date] = None) -> None:
        if target_date is None:
            raise VestingValidationError("Cannot cancel event without a target date.")

        validation_date = max(event.event_date, target_date)

        vested_to_date = calculation_service.calculate_vested_shares(event.award_id, validation_date)
        cancelled_to_date = calculation_service.calculate_cancelled_shares(event.award_id, validation_date)
        net_vested = vested_to_date - cancelled_to_date

        if event.quantity > net_vested or net_vested <= 0:
            raise VestingValidationError(
                f"Cannot cancel more shares than vested. Available: {net_vested}, Attempting to cancel: {event.quantity}")

    async def process_event(self, event: Event, event_store: IAwardEventStore) -> None:
        event_store.add_award_event(event)


@IEventProcessor.register(EventType.PERFORMANCE)
class PerformanceBonusEventProcessor(IEventProcessor):
    async def validate_event(self, event: Event, calculation_service: IAwardCalculatorService, target_date: Optional[date] = None) -> None:
        if target_date is None:
            raise VestingValidationError("Cannot cancel event without a target date.")

        if event.quantity <= 0:
            raise VestingValidationError(
                f"Performance bonus must be positive, got {event.quantity}"
            )

    async def process_event(self, event: Event, event_store: IAwardEventStore) -> None:
        event_store.add_award_event(event)


def create_event_processor(event_type: EventType) -> IEventProcessor:
    processor_class = IEventProcessor.get_processor(event_type)
    return processor_class()
