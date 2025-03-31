from abc import ABC, abstractmethod
from typing import Type, Dict, TypeVar, Callable
from typing_extensions import ClassVar

from exceptions.vesting_exception import VestingValidationError
from models.award import Award
from models.event import EventType, Event

T = TypeVar('T', bound='EventProcessor')

class EventProcessor(ABC):
    _registry: ClassVar[Dict[EventType, Type['EventProcessor']]] = {}

    @classmethod
    def register(cls, event_type: EventType) -> Callable[[Type[T]], Type[T]]:
        def inner(processor_class: Type[T]) -> Type[T]:
            cls._registry[event_type] = processor_class
            return processor_class
        return inner

    @classmethod
    def get_processor(cls, event_type: EventType) -> Type['EventProcessor']:
        if event_type not in cls._registry:
            raise ValueError(f"No processor registered for event type: {event_type}")
        return cls._registry[event_type]

    @abstractmethod
    def process(self, event: Event, award: Award) -> None:
        pass

    @abstractmethod
    def validate(self, event: Event, award: Award) -> None:
        pass

@EventProcessor.register(EventType.VEST)
class VestEventProcessor(EventProcessor):
    def validate(self, event: Event, award: Award) -> None:
        if event.quantity <= 0:
            raise VestingValidationError(
                f"Vest quantity must be positive, got {event.quantity}"
            )

    def process(self, event: Event, award: Award) -> None:
        self.validate(event, award)
        award.add_vested_event(event)


@EventProcessor.register(EventType.CANCEL)
class CancelEventProcessor(EventProcessor):
    def validate(self, event: Event, award: Award) -> None:
        vested_to_date = award.total_vested_shares(event.event_date)
        cancelled_to_date = award.total_cancelled_shares(event.event_date)
        net_vested = vested_to_date - cancelled_to_date

        if event.quantity > net_vested or net_vested <= 0:
            raise VestingValidationError(f"Cannot cancel more shares than vested.")

    def process(self, event: Event, award: Award) -> None:
        self.validate(event, award)
        award.add_cancelled_event(event)


def create_event_processor(event_type: EventType) -> EventProcessor:
    processor_class = EventProcessor.get_processor(event_type)
    return processor_class()
