import pytest
from models.employee import Employee
from models.award import Award


class TestEmployeeModel:
    def test_valid_employee(self):
        employee = Employee(
            employee_id="E001",
            name="Alice Smith",
            awards={}
        )

        assert employee.employee_id == "E001"
        assert employee.name == "Alice Smith"
        assert employee.awards == {}

    def test_add_award(self):
        employee = Employee(
            employee_id="E001",
            name="Alice Smith",
            awards = {}
        )

        award_one = Award(
            award_id="ISO-001",
            employee_id="E001",
            employee_name="Alice Smith",
            cancelled_events=[],
            vested_events=[]
        )

        award_two = Award(
            award_id="ISO-002",
            employee_id="E001",
            employee_name="Alice Smith",
            cancelled_events=[],
            vested_events=[]
        )

        employee.add_award(award_one)
        employee.add_award(award_two)

        assert len(employee.awards) == 2
        assert employee.awards["ISO-001"] == award_one
        assert employee.awards["ISO-002"] == award_two

    def test_add_award_with_same_id(self):
        employee = Employee(
            employee_id="E001",
            name="Alice Smith",
            awards={}
        )

        award_one = Award(
            award_id="ISO-001",
            employee_id="E001",
            employee_name="Alice Smith",
            cancelled_events=[],
            vested_events=[]
        )

        award_two = Award(
            award_id="ISO-001",
            employee_id="E001",
            employee_name="Alice Smith",
            cancelled_events=[],
            vested_events=[]
        )

        employee.add_award(award_one)
        employee.add_award(award_two)

        assert len(employee.awards) == 1
        assert employee.awards["ISO-001"] == award_two

    def test_get_sorted_awards(self):
        employee = Employee(
            employee_id="E001",
            name="Alice Smith",
            awards = {}
        )

        award_three = Award(
            award_id="ISO-003",
            employee_id="E001",
            employee_name="Alice Smith",
            cancelled_events=[],
            vested_events=[]
        )

        award_one = Award(
            award_id="ISO-001",
            employee_id="E001",
            employee_name="Alice Smith",
            cancelled_events=[],
            vested_events=[]
        )

        award_two = Award(
            award_id="ISO-002",
            employee_id="E001",
            employee_name="Alice Smith",
            cancelled_events=[],
            vested_events=[]
        )

        employee.add_award(award_three)
        employee.add_award(award_one)
        employee.add_award(award_two)

        sorted_awards = employee.get_sorted_awards()

        assert len(sorted_awards) == 3
        assert sorted_awards[0].award_id == "ISO-001"
        assert sorted_awards[1].award_id == "ISO-002"
        assert sorted_awards[2].award_id == "ISO-003"
