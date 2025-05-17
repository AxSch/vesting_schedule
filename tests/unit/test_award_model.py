from datetime import date
from decimal import Decimal

import pytest
from pydantic import ValidationError

from models.award import Award
from models.event import Event, EventType


class TestAwardModel:
    def test_valid_award(self):
        award = Award(
            award_id="ISO-001",
            employee_id="E001",
            employee_name="Alice Smith"
        )

        assert award.award_id == "ISO-001"
        assert award.employee_id == "E001"
        assert award.employee_name == "Alice Smith"

    def test_invalid_award(self):
        with pytest.raises(ValidationError):
            Award(
                award_id="",
                employee_id="E001",
                employee_name="Alice Smith",
            )
