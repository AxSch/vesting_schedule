from exceptions.vesting_exception import VestingValidationError
from interfaces.event_processor import IEventProcessor
from models.award import Award
from models.event import EventType, Event

@IEventProcessor.register(EventType.VEST)
class VestEventProcessor(IEventProcessor):
    def validate(self, event: Event, award: Award) -> None:
        if event.quantity <= 0:
            raise VestingValidationError(
                f"Vest quantity must be positive, got {event.quantity}"
            )

    def process(self, event: Event, award: Award) -> None:
        self.validate(event, award)
        award.add_vested_event(event)


@IEventProcessor.register(EventType.CANCEL)
class CancelEventProcessor(IEventProcessor):
    def validate(self, event: Event, award: Award) -> None:
        vested_to_date = award.total_vested_shares(event.event_date)
        cancelled_to_date = award.total_cancelled_shares(event.event_date)
        net_vested = vested_to_date - cancelled_to_date

        if event.quantity > net_vested or net_vested <= 0:
            raise VestingValidationError(f"Cannot cancel more shares than vested.")

    def process(self, event: Event, award: Award) -> None:
        self.validate(event, award)
        award.add_cancelled_event(event)


@IEventProcessor.register(EventType.PERFORMANCE)
class PerformanceBonusEventProcessor(IEventProcessor):
    def validate(self, event: Event, award: Award) -> None:
        if event.quantity <= 0:
            raise VestingValidationError(
                f"Performance bonus must be positive, got {event.quantity}"
            )

    def process(self, event: Event, award: Award) -> None:
        self.validate(event, award)
        award.add_performance_event(event)


def create_event_processor(event_type: EventType) -> IEventProcessor:
    processor_class = IEventProcessor.get_processor(event_type)
    return processor_class()
