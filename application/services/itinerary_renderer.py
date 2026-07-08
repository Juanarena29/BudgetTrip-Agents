from html import escape

from budgettrip.domain.entities import Itinerary


def render_itinerary_html(itinerary: Itinerary) -> str:
    days_html = []
    for day in itinerary.days:
        costs = "".join(
            f"<li>{escape(item.description)} ({escape(item.category)}): "
            f"${item.estimated_cost:.2f}</li>"
            for item in day.cost_items
        )
        activities = "".join(f"<li>{escape(activity)}</li>" for activity in day.activities)
        days_html.append(
            f"<section>"
            f"<h2>Día {day.day} — {day.date.isoformat()}</h2>"
            f"<p>{escape(day.summary)}</p>"
            f"<h3>Actividades</h3><ul>{activities}</ul>"
            f"<h3>Costos</h3><ul>{costs}</ul>"
            f"<p><strong>Total del día:</strong> ${day.day_total:.2f}</p>"
            f"</section>"
        )

    status = (
        f"<p style='color:red;'><strong>Presupuesto excedido</strong> "
        f"por ${itinerary.budget_difference:.2f}</p>"
        if itinerary.over_budget
        else "<p style='color:green;'><strong>Dentro del presupuesto</strong></p>"
    )

    return (
        f"<html><body>"
        f"<h1>Itinerario: {escape(itinerary.destination)}</h1>"
        f"<p>{escape(itinerary.short_summary)}</p>"
        f"{status}"
        f"<p><strong>Costo total:</strong> ${itinerary.total_cost:.2f}</p>"
        f"{''.join(days_html)}"
        f"</body></html>"
    )
