from collections import defaultdict
from typing import Dict, List

from interfaces.award_event_store import IAwardEventStore
from models.event import EventType, Event


class AwardEventStore(IAwardEventStore):
    def __init__(self):
        self.events_collections: Dict[str, Dict[EventType, List[Event]]] = defaultdict(lambda: {
            EventType.VEST: [],
            EventType.CANCEL: [],
            EventType.PERFORMANCE: []
        })

    def add_award_event(self, award_id: str, event: Event) -> None:
        self.events_collections[award_id][event.event_type].append(event)

    def get_all_award_events(self, award_id: str, event_type: EventType) -> List[Event]:
        return sorted(self.events_collections[award_id][event_type], key=lambda e: e.event_date)

    def get_all_award_ids(self) -> List[str]:
        return sorted(self.events_collections.keys())
