import uuid

from budgettrip.domain.entities import RequirementsTurn


class InMemoryRequirementsSessionStore:
    def __init__(self) -> None:
        self._sessions: dict[str, RequirementsTurn] = {}

    def create_session_id(self) -> str:
        return str(uuid.uuid4())

    def get(self, session_id: str) -> RequirementsTurn | None:
        return self._sessions.get(session_id)

    def save(self, session_id: str, turn: RequirementsTurn) -> None:
        self._sessions[session_id] = turn
