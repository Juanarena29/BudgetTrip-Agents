from typing import Protocol

from budgettrip.domain.entities import SearchPlan, TripRequest


class PlannerProvider(Protocol):
    async def plan_searches(self, trip: TripRequest) -> SearchPlan: ...
