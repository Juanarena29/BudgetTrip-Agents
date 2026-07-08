from agents import function_tool

from budgettrip.application.ports.budget_port import BudgetCalculator
from budgettrip.domain.entities import Itinerary
from budgettrip.infrastructure.tools.budget_logic import compute_budget


@function_tool(name_override="calculate_budget")
def calculate_budget(itinerary: Itinerary, budget_limit: float) -> Itinerary:
    """Calcula totales de presupuesto de forma determinística a partir de los cost_items."""
    return compute_budget(itinerary, budget_limit)


class CalculateBudgetTool(BudgetCalculator):
    def calculate(self, itinerary: Itinerary, budget_limit: float) -> Itinerary:
        return compute_budget(itinerary, budget_limit)
