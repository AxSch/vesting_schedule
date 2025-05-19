from abc import ABC, abstractmethod
from datetime import date
from decimal import Decimal


class IAwardCalculatorService(ABC):

    @abstractmethod
    def calculate_vested_shares(self, award_id: str, target_date: date) -> Decimal:
        ...

    @abstractmethod
    def calculate_cancelled_shares(self, award_id: str, target_date: date) -> Decimal:
        ...

    @abstractmethod
    def calculate_performance_events(self, award_id: str, target_date: date) -> Decimal:
        ...

    @abstractmethod
    def calculate_net_vested_shares(self, award_id: str, target_date: date) -> Decimal:
        ...
