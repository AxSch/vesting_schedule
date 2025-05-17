from abc import ABC, abstractmethod
from typing import Optional

from models.employee import EmployeeRecord


class IEmployeeRegistry(ABC):

    @abstractmethod
    def register_employee(self, employee_id: str, name: str) -> None:
        ...

    @abstractmethod
    def register_award(self, employee_id: str, award_id: str) -> None:
        ...

    @abstractmethod
    def get_employee(self, employee_id: str) -> Optional[EmployeeRecord]:
        ...

    @abstractmethod
    def get_all_employee_ids(self) -> list[str]:
        ...
