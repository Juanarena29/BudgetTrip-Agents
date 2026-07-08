from datetime import datetime

from ics import Calendar, Event

from budgettrip.application.ports.notifier_port import CalendarExporter
from budgettrip.domain.entities import DayPlan, Itinerary


def _day_description(day: DayPlan) -> str:
    activities = "\n".join(f"- {activity}" for activity in day.activities)
    costs = "\n".join(
        f"- {item.description} ({item.category}): ${item.estimated_cost:.2f}"
        for item in day.cost_items
    )
    parts = [day.summary]
    if activities:
        parts.append(f"Actividades:\n{activities}")
    if costs:
        parts.append(f"Costos:\n{costs}")
    parts.append(f"Total del día: ${day.day_total:.2f}")
    return "\n\n".join(parts)


class IcsExporter(CalendarExporter):
    def export(self, itinerary: Itinerary) -> bytes:
        calendar = Calendar()
        calendar.creator = "BudgetTrip"

        for day in itinerary.days:
            event = Event()
            event.name = f"{itinerary.destination} — Día {day.day}"
            event.begin = datetime.combine(day.date, datetime.min.time())
            event.make_all_day()
            event.description = _day_description(day)
            calendar.events.add(event)

        return calendar.serialize().encode("utf-8")
