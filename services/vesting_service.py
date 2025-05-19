import asyncio
from datetime import date
from decimal import Decimal
from typing import Dict, List, Tuple

from exceptions.vesting_exception import VestingValidationError
from interfaces.award_calculator_service import IAwardCalculatorService
from interfaces.award_event_store import IAwardEventStore
from repositories.employee_registry import EmployeeRegistry
from interfaces.employee_registry import IEmployeeRegistry
from repositories.award_event_store import AwardEventStore
from models.event import Event
from services.award_calculator_service import AwardCalculatorService
from processors.event_processor import create_event_processor

class VestingService:
    def __init__(self, target_date: date, max_workers: int = 100, use_numba_calculator: bool = False):
        self.event_store: IAwardEventStore = AwardEventStore()
        self.calculation_service: IAwardCalculatorService = AwardCalculatorService(self.event_store, use_numba_calculator)
        self.target_date: date = target_date
        self.max_workers: int = max_workers
        self.employee_registry: IEmployeeRegistry = EmployeeRegistry()
        self._schedule_cache: Dict[Tuple[date, int], List[Tuple[str, str, str, Decimal]]] = {}

    async def process_events(self, events: List[Event]) -> None:
        if not events:
            return

        self._schedule_cache.clear()

        award_events = {}
        for event in sorted(events, key=lambda e: e.event_date):
            key = (event.employee_id, event.award_id)
            award_events.setdefault(key, []).append(event)

        semaphore = asyncio.Semaphore(self.max_workers)

        for key, events_list in award_events.items():
            await self.process_award_events(semaphore, events_list)

    async def process_award_events(self, semaphore: asyncio.Semaphore, events: List[Event]) -> None:
        async with semaphore:
            for event in events:
                processor = create_event_processor(event.event_type)
                try:
                    await processor.validate_event(event, self.calculation_service, self.target_date)
                    await processor.process_event(event, self.event_store)

                    self.employee_registry.register_employee(event.employee_id, event.employee_name)
                    self.employee_registry.register_award(event.employee_id, event.award_id)
                except Exception:
                    raise VestingValidationError(f"Error processing event: {event}")


    def get_vesting_schedule(self, precision: int = 0) -> List[Tuple[str, str, str, Decimal]]:
        cache_key = (self.target_date, precision)
        if cache_key in self._schedule_cache:
            return self._schedule_cache[cache_key]

        result = []
        for employee_id in self.employee_registry.get_all_employee_ids():
            employee = self.employee_registry.get_employee(employee_id)
            if not employee:
                continue

            for award_id in sorted(employee.awards):
                vested_shares = self.calculation_service.calculate_vested_shares(award_id, self.target_date)
                cancelled_shares = self.calculation_service.calculate_cancelled_shares(award_id, self.target_date)
                performance_bonus = self.calculation_service.calculate_performance_events(award_id, self.target_date)

                cancelled_amount = min(vested_shares, cancelled_shares)
                net_vested = (vested_shares - cancelled_amount) * performance_bonus
                result.append((employee_id, employee.name, award_id, net_vested))

        self._schedule_cache[cache_key] = result
        return result
