from pydantic import BaseModel, field_validator


class Award(BaseModel):
    award_id: str
    employee_id: str
    employee_name: str

    @field_validator('award_id', 'employee_id', 'employee_name', mode="after")
    @classmethod
    def validate_non_empty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Field cannot be empty")
        return value
