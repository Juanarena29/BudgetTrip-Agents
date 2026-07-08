from agents import Agent, Runner

from budgettrip.application.ports.planner_port import PlannerProvider
from budgettrip.domain.entities import SearchPlan, TripRequest
from budgettrip.domain.exceptions import PlanningError
from budgettrip.infrastructure.agents_sdk.instructions import PLANNER_INSTRUCTIONS
from budgettrip.infrastructure.config import Settings, get_settings


class PlannerAgent(PlannerProvider):
    def __init__(
        self,
        settings: Settings | None = None,
        model_name: str | None = None,
        how_many_searches: int | None = None,
    ) -> None:
        self._settings = settings or get_settings()
        self._how_many_searches = how_many_searches or self._settings.how_many_searches
        self._agent = Agent(
            name="Trip Planner",
            instructions=PLANNER_INSTRUCTIONS,
            model=model_name or self._settings.model_name,
            output_type=SearchPlan,
        )

    async def plan_searches(self, trip: TripRequest) -> SearchPlan:
        if not self._settings.openai_api_key:
            raise PlanningError("OPENAI_API_KEY no está configurada")

        preferences = ", ".join(trip.preferences) if trip.preferences else "ninguna"
        input_message = (
            f"Planificá exactamente {self._how_many_searches} búsquedas web para este viaje.\n"
            f"Origen: {trip.origin}\n"
            f"Destino: {trip.destination}\n"
            f"Fecha inicio: {trip.start_date.isoformat()}\n"
            f"Fecha fin: {trip.end_date.isoformat()}\n"
            f"Presupuesto total: USD {trip.budget_limit:.2f}\n"
            f"Preferencias: {preferences}"
        )

        result = await Runner.run(self._agent, input_message)
        plan = result.final_output
        if not isinstance(plan, SearchPlan):
            raise PlanningError("El planner no devolvió un SearchPlan válido")
        return plan
