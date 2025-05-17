from datetime import date
from decimal import Decimal
from typing import List

import numpy as np
from numba import njit, prange

from interfaces.vesting_calculator import IVestingCalculator
from models.event import Event
from utils.decimal_utils import decimal_sum

@njit
def filter_by_date_numba(dates_array: np.array, target_date_ordinal: int):
    result = np.zeros(len(dates_array), dtype=np.bool_)
    for i in range(len(dates_array)):
        result[i] = dates_array[i] <= target_date_ordinal
    return result


@njit(parallel=True)
def filter_by_date_parallel(dates_array: np.array, target_date_ordinal: int, threshold=10000):
    if len(dates_array) < threshold:
        return filter_by_date_numba(dates_array, target_date_ordinal)

    result = np.zeros(len(dates_array), dtype=np.bool_)
    for i in prange(len(dates_array)):
        result[i] = dates_array[i] <= target_date_ordinal
    return result

class NumbaVestingCalculator(IVestingCalculator):
    def __init__(self, parallel_threshold: int = 500) -> None:
        self.parallel_threshold = parallel_threshold

    def _filter_events_by_date(self, events: List[Event], target_date: date) -> List[Event]:
        sorted_events = sorted(events, key=lambda event: event.event_date)

        if not sorted_events:
            return []

        dates_array = np.array([event.event_date.toordinal() for event in sorted_events])
        target_date_ordinal = target_date.toordinal()

        if len(sorted_events) >= self.parallel_threshold:
            mask = filter_by_date_parallel(dates_array, target_date_ordinal)
        else:
            mask = filter_by_date_numba(dates_array, target_date_ordinal)

        return [sorted_events[i] for i in range(len(sorted_events)) if mask[i]]

    def calculate_vested_shares(self, events: List[Event], target_date: date) -> Decimal:
        filtered_events = self._filter_events_by_date(events, target_date)
        quantities = [event.quantity for event in filtered_events]
        return decimal_sum(quantities)

    def calculate_cancelled_shares(self, events: List[Event], target_date: date) -> Decimal:
        filtered_events = self._filter_events_by_date(events, target_date)
        quantities = [event.quantity for event in filtered_events]
        return decimal_sum(quantities)

    def calculate_performance_bonus(self, events: List[Event], target_date: date) -> Decimal:
        filtered_events = self._filter_events_by_date(events, target_date)
        total_performance_events = [event.quantity for event in filtered_events]
        result = sum(total_performance_events)

        if result > 0:
            return Decimal(result)
        return Decimal(1)
