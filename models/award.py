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
