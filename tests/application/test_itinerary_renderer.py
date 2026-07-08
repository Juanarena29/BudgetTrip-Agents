from datetime import date

from budgettrip.application.services.itinerary_renderer import render_itinerary_html
from budgettrip.domain.entities import CostItem, DayPlan, Itinerary


def test_render_itinerary_html_includes_destination_and_total():
    itinerary = Itinerary(
        destination="Madrid",
        days=[
            DayPlan(
                day=1,
                date=date(2026, 9, 1),
                summary="Centro histórico",
                activities=["Plaza Mayor"],
                cost_items=[
                    CostItem(day=1, category="food", description="Tapas", estimated_cost=30.0)
                ],
                day_total=30.0,
            )
        ],
        total_cost=30.0,
        over_budget=False,
        budget_difference=-70.0,
        short_summary="Escapada de fin de semana",
    )

    html = render_itinerary_html(itinerary)

    assert "Madrid" in html
    assert "Escapada de fin de semana" in html
    assert "Dentro del presupuesto" in html
    assert "$30.00" in html
