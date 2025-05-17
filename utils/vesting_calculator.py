from datetime import date
from decimal import Decimal
from typing import List

from interfaces.vesting_calculator import IVestingCalculator
from models.event import Event, EventType
from utils.decimal_utils import decimal_sum

class DefaultVestingCalculator(IVestingCalculator):
    def calculate_vested_shares(self, events: List[Event], target_date: date) -> Decimal:
        quantities = [
            event.quantity
            for event in sorted(events, key=lambda event: event.event_date)
            if event.event_date <= target_date and event.event_type == EventType.VEST
        ]

        return decimal_sum(quantities)

    def calculate_cancelled_shares(self, events: List[Event], target_date: date) -> Decimal:
        quantities = [
            event.quantity
            for event in sorted(events, key=lambda event: event.event_date)
            if event.event_date <= target_date and event.event_type == EventType.CANCEL
        ]
        return decimal_sum(quantities)

    def calculate_performance_bonus(self, events: List[Event], target_date: date) -> Decimal:
        total_performance_events = [
            event.quantity
            for event in sorted(events, key=lambda event: event.event_date)
            if event.event_date <= target_date and event.event_type == EventType.PERFORMANCE
        ]
        result = sum(total_performance_events)
        if result > 0:
            return Decimal(result)
        return Decimal(1)
