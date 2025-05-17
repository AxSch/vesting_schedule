from typing import Set

from pydantic import BaseModel, Field

class EmployeeRecord(BaseModel):
    employee_id: str
    name: str
    awards: Set[str] = Field(default_factory=set)
