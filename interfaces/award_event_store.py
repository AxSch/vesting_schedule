from abc import ABC, abstractmethod
from typing import List

from models.event import Event, EventType


class IAwardEventStore(ABC):

    @abstractmethod
    def add_award_event(self, event: Event) -> None:
        ...

    @abstractmethod
    def get_all_award_events(self, award_id: str, event_type: EventType) -> List[Event]:
        ...

    @abstractmethod
    def get_all_award_ids(self) -> List[str]:
        ...
