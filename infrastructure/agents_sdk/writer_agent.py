from agents import Agent, Runner

from budgettrip.application.ports.writer_port import WriterProvider
from budgettrip.domain.entities import Itinerary, TripRequest
from budgettrip.domain.exceptions import PlanningError
from budgettrip.infrastructure.agents_sdk.instructions import WRITER_INSTRUCTIONS
from budgettrip.infrastructure.config import Settings, get_settings


class WriterAgent(WriterProvider):
    def __init__(self, settings: Settings | None = None, model_name: str | None = None) -> None:
        self._settings = settings or get_settings()
        self._agent = Agent(
            name="Itinerary Writer",
            instructions=WRITER_INSTRUCTIONS,
            model=model_name or self._settings.model_name,
            output_type=Itinerary,
        )

    async def write_itinerary(
        self,
        trip: TripRequest,
        research: list[str],
        previous_draft: Itinerary | None = None,
        feedback: str | None = None,
    ) -> Itinerary:
        if not self._settings.openai_api_key:
            raise PlanningError("OPENAI_API_KEY no está configurada")

        trip_days = (trip.end_date - trip.start_date).days + 1
        preferences = ", ".join(trip.preferences) if trip.preferences else "ninguna"
        research_block = "\n\n".join(
            f"--- Investigación {index} ---\n{content}"
            for index, content in enumerate(research, start=1)
        )

        if previous_draft is None:
            input_message = (
                f"Destino: {trip.destination}\n"
                f"Fecha inicio: {trip.start_date.isoformat()}\n"
                f"Fecha fin: {trip.end_date.isoformat()}\n"
                f"Días del viaje: {trip_days}\n"
                f"Presupuesto total: USD {trip.budget_limit:.2f}\n"
                f"Preferencias: {preferences}\n\n"
                f"Investigación:\n{research_block}"
            )
        else:
            input_message = (
                f"Destino: {trip.destination}\n"
                f"Fecha inicio: {trip.start_date.isoformat()}\n"
                f"Fecha fin: {trip.end_date.isoformat()}\n"
                f"Días del viaje: {trip_days}\n"
                f"Presupuesto total: USD {trip.budget_limit:.2f}\n"
                f"Preferencias: {preferences}\n\n"
                f"Borrador anterior (excedió presupuesto): {previous_draft.model_dump_json()}\n"
                f"Feedback: {feedback}\n"
                f"Ajustá el itinerario para cumplir el presupuesto, manteniendo la mayor "
                f"calidad posible del viaje.\n\n"
                f"Investigación:\n{research_block}"
            )

        result = await Runner.run(self._agent, input_message)
        itinerary = result.final_output
        if not isinstance(itinerary, Itinerary):
            raise PlanningError("El writer no devolvió un Itinerary válido")

        if itinerary.destination != trip.destination:
            itinerary = itinerary.model_copy(update={"destination": trip.destination})
        return itinerary
