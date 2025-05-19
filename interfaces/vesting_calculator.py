from abc import ABC, abstractmethod
from datetime import date
from decimal import Decimal
from typing import List

from models.event import Event


class IVestingCalculator(ABC):

    @abstractmethod
    def calculate_vested_shares(self, events: List[Event], target_date: date) -> Decimal:
        ...

    @abstractmethod
    def calculate_cancelled_shares(self, events: List[Event], target_date: date) -> Decimal:
        ...

    @abstractmethod
    def calculate_performance_bonus(self, events: List[Event], target_date: date) -> Decimal:
        ...
