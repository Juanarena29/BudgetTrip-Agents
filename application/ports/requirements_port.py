from typing import Protocol

from budgettrip.domain.entities import RequirementsTurn


class RequirementsCollectorProvider(Protocol):
    async def process_message(
        self,
        user_message: str,
        history: list[tuple[str, str]] | None = None,
        previous_state: RequirementsTurn | None = None,
    ) -> RequirementsTurn: ...
