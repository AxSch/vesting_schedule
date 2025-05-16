from typing import Optional, Set, Dict

from interfaces.employee_registry import IEmployeeRegistry
from models.employee import EmployeeRecord


class EmployeeRegistry(IEmployeeRegistry):
    def __init__(self):
        self._employees: Dict[str, EmployeeRecord] = {}

    def register_employee(self, employee_id: str, name: str) -> None:
        if employee_id not in self._employees:
            self._employees[employee_id] = EmployeeRecord(employee_id=employee_id, name=name)
        else:
            self._employees[employee_id].name = name

    def register_award(self, employee_id: str, award_id: str) -> None:
        if employee_id in self._employees:
            self._employees[employee_id].awards.add(award_id)

    def get_employee(self, employee_id: str) -> Optional[EmployeeRecord]:
        return self._employees.get(employee_id)

    def get_all_employee_ids(self) -> list[str]:
        return sorted(self._employees.keys())

    def get_employee_awards(self, employee_id: str) -> Set[str]:
        if employee_id in self._employees:
            return self._employees[employee_id].awards
        return set()
