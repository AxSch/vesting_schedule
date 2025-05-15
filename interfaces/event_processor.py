from abc import ABC, abstractmethod
from typing import Callable, Dict, ClassVar, Type, Self

from interfaces.award_calculator_service import IAwardCalculatorService
from interfaces.award_event_store import IAwardEventStore
from models.event import EventType, Event


class IEventProcessor(ABC):
    _registry: ClassVar[Dict[EventType, Type[Self]]] = {}

    @classmethod
    def register(cls, event_type: EventType) -> Callable[[Type[Self]], Type[Self]]:
        def inner(processor_class: Type[Self]) -> Type[Self]:
            cls._registry[event_type] = processor_class
            return processor_class
        return inner

    @classmethod
    def get_processor(cls, event_type: EventType) -> Type[Self]:
        if event_type not in cls._registry:
            raise ValueError(f"No processor registered for event type: {event_type}")
        return cls._registry[event_type]

    @abstractmethod
    def process(self, event: Event, event_store: IAwardEventStore) -> None:
        ...

    @abstractmethod
    def validate(self, event: Event, calculation_service: IAwardCalculatorService) -> None:
        ...
