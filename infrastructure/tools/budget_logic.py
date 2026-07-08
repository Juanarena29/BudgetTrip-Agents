from budgettrip.domain.entities import Itinerary


def compute_budget(itinerary: Itinerary, budget_limit: float) -> Itinerary:
    updated_days = []
    for day in itinerary.days:
        day_total = sum(item.estimated_cost for item in day.cost_items)
        updated_days.append(day.model_copy(update={"day_total": day_total}))

    total_cost = sum(day.day_total for day in updated_days)
    budget_difference = total_cost - budget_limit

    return itinerary.model_copy(
        update={
            "days": updated_days,
            "total_cost": total_cost,
            "over_budget": total_cost > budget_limit,
            "budget_difference": budget_difference,
        }
    )
