import decimal
from datetime import date
from decimal import Decimal
from typing import List, Annotated

from pydantic import BaseModel, Field

from models.event import Event


class Award(BaseModel):
    award_id: str
    employee_id: str
    employee_name: str
    vested_events: Annotated[List[Event], Field(default_factory=list)]
    cancelled_events: Annotated[List[Event], Field(default_factory=list)]

    def total_vested_shares(self, target_date: date, precision: int = 0) -> Decimal:
        quantities = []
        for event in self.vested_events:
            if event.event_date <= target_date:
                 quantities.append(event.quantity)
        total_sum = Decimal(sum(quantities))

        if precision > 0:
            return total_sum.quantize(Decimal(f'0.{"0" * precision}'))
        return total_sum.to_integral_exact(rounding=decimal.ROUND_DOWN)
