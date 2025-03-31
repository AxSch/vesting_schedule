import decimal
from datetime import date
from decimal import Decimal
from typing import List, Annotated

from pydantic import BaseModel, Field, field_validator

from models.event import Event


class Award(BaseModel):
    award_id: str
    employee_id: str
    employee_name: str
    vested_events: Annotated[List[Event], Field(default_factory=list)]
    cancelled_events: Annotated[List[Event], Field(default_factory=list)]

    @field_validator('award_id', 'employee_id', 'employee_name', mode="after")
    @classmethod
    def validate_non_empty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Field cannot be empty")
        return value

    def add_vested_event(self, event: Event) -> None:
        self.vested_events.append(event)

    def add_cancelled_event(self, event: Event) -> None:
        self.cancelled_events.append(event)

    def total_vested_shares(self, target_date: date, precision: int = 0) -> Decimal:
        quantities = [
            event.quantity
            for event in sorted(self.vested_events, key=lambda e: e.event_date)
            if event.event_date <= target_date
        ]
        total_sum = sum(quantities, Decimal('0'))

        if precision > 0:
            return total_sum.quantize(Decimal(f'0.{"0" * precision}'), rounding=decimal.ROUND_DOWN)
        if total_sum % 1 != 0:
            return total_sum
        else:
            return total_sum.to_integral_exact(rounding=decimal.ROUND_DOWN)

    def total_cancelled_shares(self, target_date: date, precision: int = 0) -> Decimal:
        quantities = [
            event.quantity
            for event in sorted(self.cancelled_events, key=lambda e: e.event_date)
            if event.event_date <= target_date
        ]
        total_sum = sum(quantities, Decimal('0'))

        if precision > 0:
            return total_sum.quantize(Decimal(f'0.{"0" * precision}'), rounding=decimal.ROUND_DOWN)
        if total_sum % 1 != 0:
            return total_sum
        else:
            return total_sum.to_integral_exact(rounding=decimal.ROUND_DOWN)

    def net_vested_shares(self, target_date: date, precision: int = 0) -> Decimal:
        total_vested_shares = self.total_vested_shares(target_date, precision)
        total_cancelled_shares = self.total_cancelled_shares(target_date, precision)

        cancelled = min(total_vested_shares, total_cancelled_shares)
        net_vested = total_vested_shares - cancelled

        if precision > 0:
            return net_vested.quantize(Decimal(f'0.{"0" * precision}'), rounding=decimal.ROUND_DOWN)
        return net_vested.to_integral_exact(rounding=decimal.ROUND_DOWN)
