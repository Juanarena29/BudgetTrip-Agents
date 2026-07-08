from datetime import date

import pytest

from budgettrip.domain.entities import CostItem, DayPlan, Itinerary
from budgettrip.infrastructure.tools.budget_logic import compute_budget


def _make_itinerary(*day_costs: list[float]) -> Itinerary:
    days = []
    for index, costs in enumerate(day_costs, start=1):
        cost_items = [
            CostItem(day=index, category="activity", description=f"Item {item_index}", estimated_cost=cost)
            for item_index, cost in enumerate(costs, start=1)
        ]
        days.append(
            DayPlan(
                day=index,
                date=date(2026, 7, index),
                summary=f"Día {index}",
                activities=["Visita"],
                cost_items=cost_items,
                day_total=0.0,
            )
        )
    return Itinerary(
        destination="Buenos Aires",
        days=days,
        total_cost=0.0,
        over_budget=False,
        budget_difference=0.0,
        short_summary="Viaje corto",
    )


def test_compute_budget_sums_cost_items_and_day_totals():
    itinerary = _make_itinerary([100.0, 50.0], [75.25, 24.75])

    result = compute_budget(itinerary, budget_limit=300.0)

    assert result.days[0].day_total == 150.0
    assert result.days[1].day_total == 100.0
    assert result.total_cost == 250.0
    assert result.over_budget is False
    assert result.budget_difference == pytest.approx(-50.0)


def test_compute_budget_marks_over_budget():
    itinerary = _make_itinerary([200.0, 200.0])

    result = compute_budget(itinerary, budget_limit=300.0)

    assert result.total_cost == 400.0
    assert result.over_budget is True
    assert result.budget_difference == pytest.approx(100.0)


def test_compute_budget_overrides_incorrect_llm_day_totals():
    itinerary = _make_itinerary([100.0])
    itinerary.days[0].day_total = 999.0

    result = compute_budget(itinerary, budget_limit=500.0)

    assert result.days[0].day_total == 100.0
    assert result.total_cost == 100.0


def test_calculate_budget_tool_delegates_to_compute_budget():
    from budgettrip.infrastructure.tools.calculate_budget_tool import CalculateBudgetTool

    itinerary = _make_itinerary([120.0, 80.0])
    tool = CalculateBudgetTool()

    result = tool.calculate(itinerary, budget_limit=150.0)

    assert result.total_cost == 200.0
    assert result.over_budget is True
