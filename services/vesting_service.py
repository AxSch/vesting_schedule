from datetime import date
from decimal import Decimal
from typing import Dict, List, Tuple

from exceptions.vesting_exception import VestingValidationError
from models.award import Award
from models.employee import Employee
from models.event import Event, EventType


class VestingService:
    def __init__(self):
        self.employees: Dict[str, Employee] = {}

    def process_events(self, events: List[Event]) -> None:
        self._initialize_employees_and_awards(events)

        sorted_events = sorted(events, key=lambda event: (event.event_date, event.employee_id, event.award_id))

        for event in sorted_events:
            self._process_event(event)

    def _initialize_employees_and_awards(self, events: List[Event]) -> None:
        for event in events:
            if event.employee_id not in self.employees:
                self.employees[event.employee_id] = Employee(
                    employee_id=event.employee_id,
                    name=event.employee_name,
                    awards={}
                )

            employee = self.employees[event.employee_id]
            if event.award_id not in employee.awards:
                employee.awards[event.award_id] = Award(
                    award_id=event.award_id,
                    employee_id=event.employee_id,
                    employee_name=event.employee_name,
                    vested_events=[],
                    cancelled_events=[]
                )

    def _process_event(self, event: Event) -> None:
        employee = self.employees[event.employee_id]
        award = employee.awards[event.award_id]

        if event.event_type != EventType.VEST:
            vested_to_date = award.total_vested_shares(event.event_date)
            cancelled_to_date = award.total_cancelled_shares(event.event_date)

            if cancelled_to_date + event.quantity > vested_to_date:
                raise VestingValidationError(f"Cannot cancel more shares than vested.")

            award.add_cancelled_event(event)
        else:
            award.add_vested_event(event)

    def get_vesting_schedule(self, target_date: date, precision: int = 0) -> List[Tuple[str, str, str, Decimal]]:
        result = []

        def format_decimal(value: Decimal, prec: int) -> Decimal:
            if prec > 0:
                return value.quantize(Decimal(f'0.{"0" * prec}'))
            return value.to_integral_value()

        for employee_id in sorted(self.employees.keys()):
            employee = self.employees[employee_id]

            for award_id in sorted(employee.awards.keys()):
                award = employee.awards[award_id]
                net_vested = format_decimal(award.net_vested_shares(target_date, precision), precision)

                result.append((employee_id, employee.name, award_id, net_vested))

        return result
