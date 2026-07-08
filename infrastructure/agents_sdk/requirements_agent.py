import json

from agents import Agent, Runner

from budgettrip.application.ports.requirements_port import RequirementsCollectorProvider
from budgettrip.domain.entities import RequirementsTurn
from budgettrip.domain.exceptions import PlanningError
from budgettrip.infrastructure.agents_sdk.instructions import REQUIREMENTS_INSTRUCTIONS
from budgettrip.infrastructure.config import Settings, get_settings

_STATE_FIELDS = (
    "origin",
    "destination",
    "start_date",
    "end_date",
    "budget_limit",
    "preferences",
    "preferences_asked",
    "complete",
    "missing_fields",
)


class RequirementsAgent(RequirementsCollectorProvider):
    def __init__(
        self,
        settings: Settings | None = None,
        model_name: str | None = None,
    ) -> None:
        self._settings = settings or get_settings()
        self._agent = Agent(
            name="Trip Requirements Collector",
            instructions=REQUIREMENTS_INSTRUCTIONS,
            model=model_name or self._settings.model_name,
            output_type=RequirementsTurn,
        )

    async def process_message(
        self,
        user_message: str,
        history: list[tuple[str, str]] | None = None,
        previous_state: RequirementsTurn | None = None,
    ) -> RequirementsTurn:
        if not self._settings.openai_api_key:
            raise PlanningError("OPENAI_API_KEY no está configurada")

        input_message = self._build_input(user_message, history, previous_state)
        result = await Runner.run(self._agent, input_message)
        turn = result.final_output
        if not isinstance(turn, RequirementsTurn):
            raise PlanningError("El requirements agent no devolvió un RequirementsTurn válido")
        return self._merge_with_previous_state(previous_state, turn)

    @staticmethod
    def _build_input(
        user_message: str,
        history: list[tuple[str, str]] | None,
        previous_state: RequirementsTurn | None,
    ) -> str:
        lines: list[str] = []

        if previous_state is not None:
            state_payload = previous_state.model_dump(mode="json")
            lines.append("Estado actual conocido (actualizalo, no lo borres sin motivo):")
            lines.append(json.dumps(state_payload, ensure_ascii=False, indent=2))
            lines.append("")

        lines.append("Conversación hasta ahora:")
        if history:
            for role, content in history:
                lines.append(f"{role}: {content}")
        else:
            lines.append("(sin mensajes previos)")
        lines.append(f"Usuario: {user_message}")
        lines.append(
            "Actualizá el estado de los requisitos del viaje y respondé con RequirementsTurn."
        )
        return "\n".join(lines)

    @staticmethod
    def _merge_with_previous_state(
        previous_state: RequirementsTurn | None,
        turn: RequirementsTurn,
    ) -> RequirementsTurn:
        if previous_state is None:
            return turn

        updates: dict[str, object] = {}
        for field in _STATE_FIELDS:
            previous_value = getattr(previous_state, field)
            current_value = getattr(turn, field)
            if previous_value in (None, [], False) or current_value not in (None, [], False):
                continue
            updates[field] = previous_value

        if previous_state.preferences_asked:
            updates["preferences_asked"] = True

        if not updates:
            return turn
        return turn.model_copy(update=updates)
