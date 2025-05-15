from datetime import date
from decimal import Decimal

from interfaces.award_calculator_service import IAwardCalculatorService
from interfaces.award_event_store import IAwardEventStore
from interfaces.vesting_calculator import IVestingCalculator
from models.award_event_store import AwardEventStore
from models.event import EventType
from utils.vesting_calculator import DefaultVestingCalculator


class AwardCalculatorService(IAwardCalculatorService):
    def __init__(self):
        self.award_event_store: IAwardEventStore = AwardEventStore()
        self.calculator: IVestingCalculator = DefaultVestingCalculator()


    def calculate_vested_shares(self, award_id: str, target_date: date) -> Decimal:
        events = self.award_event_store.get_all_award_events(award_id, EventType.VEST)
        return self.calculator.calculate_vested_shares(events, target_date)

    def calculate_cancelled_shares(self, award_id: str, target_date: date) -> Decimal:
        events = self.award_event_store.get_all_award_events(award_id, EventType.CANCEL)
        return self.calculator.calculate_cancelled_shares(events, target_date)

    def calculate_performance_events(self, award_id: str, target_date: date) -> Decimal:
        events = self.award_event_store.get_all_award_events(award_id, EventType.PERFORMANCE)
        return self.calculator.calculate_performance_bonus(events, target_date)

    def calculate_net_vested_shares(self, award_id: str, target_date: date) -> Decimal:
        vested_shares = self.calculate_vested_shares(award_id, target_date)
        cancelled_shares = self.calculate_cancelled_shares(award_id, target_date)
        cancelled_amount = min(vested_shares, cancelled_shares)

        return vested_shares - cancelled_amount
