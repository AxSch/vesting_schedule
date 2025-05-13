from collections import defaultdict
from datetime import date
from decimal import Decimal
from typing import Dict, List, Tuple, DefaultDict, Set, Optional
from threading import RLock

from exceptions.vesting_exception import VestingValidationError
from models.award import Award
from models.employee import Employee
from models.event import Event
from utils.decimal_utils import format_decimal
from processors.event_processor import create_event_processor
from utils.concurrency_utils import parallel_map

_service_lock = RLock()

class VestingService:
    def __init__(self, use_parallel: bool = True, max_workers: int = None):
        self.employees: Dict[str, Employee] = {}
        self._lock: Optional[RLock] = _service_lock
        self._schedule_cache: DefaultDict[Tuple[date, int], List] = defaultdict(list)
        self._cache_valid: bool = True
        self._processed_events: Set[Tuple] = set()
        self.use_parallel = use_parallel
        self.max_workers = max_workers

    def __getstate__(self):
        state = self.__dict__.copy()
        state['_lock'] = None
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self._lock = _service_lock

    def _invalidate_cache(self):
        self._cache_valid = False
        self._schedule_cache.clear()

    def _create_event_key(self, event: Event) -> Tuple:
        return (event.event_type, event.employee_id, event.award_id,
                event.event_date, float(event.quantity))

    def _ensure_employee_and_award(self, event: Event) -> Award:
        with self._lock:
            if event.employee_id not in self.employees:
                self.employees[event.employee_id] = Employee(
                    employee_id=event.employee_id,
                    name=event.employee_name,
                    awards={}
                )

            employee = self.employees[event.employee_id]

            if event.award_id not in employee.awards:
                employee.awards[event.award_id] = Award(
                    award_id=event.award_id,
                    employee_id=event.employee_id,
                    employee_name=event.employee_name,
                    vested_events=[],
                    cancelled_events=[],
                    performance_events=[]
                )
            return employee.awards[event.award_id]

    def _initialize_employees_and_awards(self, events: List[Event]) -> None:
        unique_combinations = set()

        for event in events:
            if (event.employee_id, event.award_id) not in unique_combinations:
                self._ensure_employee_and_award(event)
                unique_combinations.add((event.employee_id, event.award_id))

    def _process_event(self, event: Event) -> None:
            award = self._ensure_employee_and_award(event)
            processor = create_event_processor(event.event_type)

            try:
                processor.validate(event, award)
                processor.process(event, award)
            except VestingValidationError as e:
                raise VestingValidationError(
                    f"Validation error processing {event.event_type} event for "
                    f"employee {event.employee_id}, award {event.award_id}: {str(e)}"
                )

    def _process_award_events(self, events_group: Tuple[str, List[Event]]):
        award_key, events = events_group

        for event in sorted(events, key=lambda e: e.event_date):
            try:
                self._process_event(event)
            except Exception as error:
                raise VestingValidationError(f"Award event can't be processed: {error} ")
        return award_key

    def process_events(self, events: List[Event]) -> None:
        if not events:
            return

        self._invalidate_cache()
        sorted_events = sorted(events, key=lambda e: e.event_date)

        if self.use_parallel:
            self._initialize_employees_and_awards(sorted_events)

            award_events = defaultdict(list)
            for event in sorted_events:
                event_key = self._create_event_key(event)
                if event_key in self._processed_events:
                    continue

                key = (event.employee_id, event.award_id)
                award_events[key].append(event)
                self._processed_events.add(event_key)

            if self.max_workers is not None and self.max_workers <= 0:
                self.max_workers = None

            try:
                parallel_map(
                    self._process_award_events,
                    list(award_events.items()),
                    max_workers=self.max_workers
                )
            except Exception as error:
                raise VestingValidationError(error)
        else:
            for event in sorted_events:
                event_key = self._create_event_key(event)

                if event_key in self._processed_events:
                    continue

                self._process_event(event)
                self._processed_events.add(event_key)

    def get_vesting_schedule(self, target_date: date, precision: int = 0) -> List[Tuple[str, str, str, Decimal]]:
        with self._lock:
            cache_key = (target_date, precision)

            if self._cache_valid and cache_key in self._schedule_cache:
                return self._schedule_cache[cache_key]

        result = []
        for employee_id in sorted(self.employees.keys()):
            employee = self.employees[employee_id]

            for award_id in sorted(employee.awards.keys()):
                award = employee.awards[award_id]
                net_vested = award.net_vested_shares(target_date, precision)
                net_vested = format_decimal(net_vested, precision)

                result.append((employee_id, employee.name, award_id, net_vested))

        with self._lock:
            self._schedule_cache[cache_key] = result
            self._cache_valid = True
        return result
