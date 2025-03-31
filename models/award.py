from datetime import date
from decimal import Decimal
from typing import List, Annotated, Dict, Tuple
from threading import RLock

from pydantic import BaseModel, Field, field_validator

from models.event import Event
from utils.vesting_calculator import VestingCalculator, DefaultVestingCalculator

_award_lock = RLock()

class Award(BaseModel):
    award_id: str
    employee_id: str
    employee_name: str
    vested_events: Annotated[List[Event], Field(default_factory=list)]
    cancelled_events: Annotated[List[Event], Field(default_factory=list)]
    _vesting_cache: Dict[Tuple[date, int], Decimal] = None
    _cancellation_cache: Dict[Tuple[date, int], Decimal] = None
    _net_vesting_cache: Dict[Tuple[date, int], Decimal] = None
    _is_cache_valid: bool = True
    _calculation_lock: RLock = None
    _calculator: VestingCalculator = DefaultVestingCalculator()

    def __init__(self, **data):
        super().__init__(**data)
        self._calculation_lock = _award_lock
        self._vesting_cache = {}
        self._cancellation_cache = {}
        self._net_vesting_cache = {}

    def __getstate__(self):
        state = self.__dict__.copy()
        state['_calculation_lock'] = None
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self._calculation_lock = _award_lock

    @field_validator('award_id', 'employee_id', 'employee_name', mode="after")
    @classmethod
    def validate_non_empty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Field cannot be empty")
        return value

    def set_calculator(self, calculator: VestingCalculator) -> None:
        self._calculator = calculator
        self._invalidate_cache()

    def add_vested_event(self, event: Event) -> None:
        with self._calculation_lock:
            self.vested_events.append(event)
            self._invalidate_cache()

    def add_cancelled_event(self, event: Event) -> None:
        with self._calculation_lock:
            self.cancelled_events.append(event)
            self._invalidate_cache()

    def _invalidate_cache(self) -> None:
        with self._calculation_lock:
            self._is_cache_valid = False
            if self._vesting_cache is not None:
                self._vesting_cache.clear()
            if self._cancellation_cache is not None:
                self._cancellation_cache.clear()
            if self._net_vesting_cache is not None:
                self._net_vesting_cache.clear()

    def total_vested_shares(self, target_date: date, precision: int = 0) -> Decimal:
        with self._calculation_lock:
            cache_key = (target_date, precision)

            if self._is_cache_valid and cache_key in self._vesting_cache:
                return self._vesting_cache[cache_key]

            result = self._calculator.calculate_vested_shares( self.vested_events, target_date)

            self._vesting_cache[cache_key] = result
            return result

    def total_cancelled_shares(self, target_date: date, precision: int = 0) -> Decimal:
        with self._calculation_lock:
            cache_key = (target_date, precision)

            if self._is_cache_valid and cache_key in self._cancellation_cache:
                return self._cancellation_cache[cache_key]

            result = self._calculator.calculate_cancelled_shares(self.cancelled_events, target_date)

            self._cancellation_cache[cache_key] = result
            return result

    def net_vested_shares(self, target_date: date, precision: int = 0) -> Decimal:
        with self._calculation_lock:
            cache_key = (target_date, precision)

            if self._is_cache_valid and cache_key in self._net_vesting_cache:
                return self._net_vesting_cache[cache_key]

            total_vested_shares = self.total_vested_shares(target_date, precision)
            total_cancelled_shares = self.total_cancelled_shares(target_date, precision)

            cancelled = min(total_vested_shares, total_cancelled_shares)
            net_vested = total_vested_shares - cancelled

            self._net_vesting_cache[cache_key] = net_vested
            return net_vested
