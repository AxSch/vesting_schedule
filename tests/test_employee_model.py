from models.employee import EmployeeRecord


class TestEmployeeRecordModel:
    def test_valid_employee(self):
        employee = EmployeeRecord(
            employee_id="E001",
            name="Alice Smith",
            awards={'ISO_011', 'NSO_011'}
        )

        assert employee.employee_id == "E001"
        assert employee.name == "Alice Smith"
        assert employee.awards == {'ISO_011', 'NSO_011'}
