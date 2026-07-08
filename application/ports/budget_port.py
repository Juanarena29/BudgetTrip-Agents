from typing import Protocol

from budgettrip.domain.entities import Itinerary


class BudgetCalculator(Protocol):
    def calculate(self, itinerary: Itinerary, budget_limit: float) -> Itinerary: ...
