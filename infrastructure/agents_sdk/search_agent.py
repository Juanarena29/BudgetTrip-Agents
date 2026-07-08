from agents import Agent, Runner, WebSearchTool

from budgettrip.application.ports.search_port import SearchProvider
from budgettrip.domain.entities import SearchItem
from budgettrip.domain.exceptions import PlanningError
from budgettrip.infrastructure.agents_sdk.instructions import SEARCH_INSTRUCTIONS
from budgettrip.infrastructure.config import Settings, get_settings


class SearchAgent(SearchProvider):
    def __init__(self, settings: Settings | None = None, model_name: str | None = None) -> None:
        self._settings = settings or get_settings()
        self._agent = Agent(
            name="Travel Researcher",
            instructions=SEARCH_INSTRUCTIONS,
            model=model_name or self._settings.model_name,
            tools=[WebSearchTool(search_context_size="medium")],
        )

    async def search(self, item: SearchItem) -> str:
        if not self._settings.openai_api_key:
            raise PlanningError("OPENAI_API_KEY no está configurada")

        input_message = (
            f"Categoría: {item.category}\n"
            f"Motivo: {item.reason}\n"
            f"Consulta: {item.query}"
        )
        result = await Runner.run(self._agent, input_message)
        return str(result.final_output)
