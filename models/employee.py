from typing import Dict, Annotated, List

from pydantic import BaseModel, Field

from models.award import Award


class Employee(BaseModel):
    employee_id: str
    name: str
    awards: Annotated[Dict[str, Award], Field(default_factory=dict)]

    def add_award(self, award: Award) -> None:
        self.awards[award.award_id] = award

    def get_sorted_awards(self) -> List[Award]:
        sorted_awards = []
        for key, award in sorted(self.awards.items()):
            sorted_awards.append(award)

        return sorted_awards
