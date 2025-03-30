from datetime import date
from decimal import Decimal

from pydantic import BaseModel, field_validator
from enum import StrEnum


class EventType(StrEnum):
    VEST = "VEST"
    CANCEL = "CANCEL"


class Event(BaseModel):
    event_type: EventType
    employee_id: str
    employee_name: str
    award_id: str
    event_date: date
    quantity: Decimal

    @field_validator('quantity', mode="after")
    @classmethod
    def ensure_positive(cls, value):
        if value <= 0:
            raise ValueError("Quantity must be positive")
        return value
