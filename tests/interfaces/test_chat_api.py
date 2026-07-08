from datetime import date
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from budgettrip.domain.entities import CostItem, DayPlan, Itinerary, RequirementsTurn
from budgettrip.interfaces.api.main import create_app


def _sample_itinerary() -> Itinerary:
    return Itinerary(
        destination="Barcelona",
        days=[
            DayPlan(
                day=1,
                date=date(2026, 8, 1),
                summary="Gótico",
                activities=["Catedral"],
                cost_items=[
                    CostItem(
                        day=1,
                        category="activity",
                        description="Entrada",
                        estimated_cost=20.0,
                    )
                ],
                day_total=20.0,
            )
        ],
        total_cost=20.0,
        over_budget=False,
        budget_difference=-1180.0,
        short_summary="Fin de semana",
    )


@pytest.fixture
def api_key(monkeypatch: pytest.MonkeyPatch) -> str:
    monkeypatch.setenv("API_SECRET_KEY", "test-secret-key")
    get_settings = __import__(
        "budgettrip.infrastructure.config", fromlist=["get_settings"]
    ).get_settings
    get_settings.cache_clear()
    return "test-secret-key"


@pytest.fixture
def client(api_key: str) -> TestClient:
    return TestClient(create_app())


def test_chat_requires_api_key(client: TestClient):
    response = client.post(
        "/api/v1/chat",
        json={"message": "Quiero ir a Barcelona"},
    )
    assert response.status_code == 401


@patch("budgettrip.interfaces.api.routers.chat_router.build_requirements_agent")
def test_chat_returns_assistant_message(
    mock_build: AsyncMock,
    client: TestClient,
    api_key: str,
):
    mock_agent = AsyncMock()
    mock_agent.process_message = AsyncMock(
        return_value=RequirementsTurn(
            complete=False,
            missing_fields=["origin", "start_date", "end_date", "budget_limit"],
            assistant_message="¿Desde dónde vas a salir?",
            destination="Barcelona",
            preferences=["gastronomía"],
        )
    )
    mock_build.return_value = mock_agent

    response = client.post(
        "/api/v1/chat",
        headers={"X-API-Key": api_key},
        json={
            "message": "Quiero 3 días en Barcelona, me gusta la gastronomía",
            "history": [],
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["complete"] is False
    assert data["assistant_message"] == "¿Desde dónde vas a salir?"
    assert "origin" in data["missing_fields"]
    assert data["trip"] is None
    assert "session_id" in data
    mock_agent.process_message.assert_awaited_once_with(
        "Quiero 3 días en Barcelona, me gusta la gastronomía",
        history=None,
        previous_state=None,
    )


@patch("budgettrip.interfaces.api.routers.chat_router.build_requirements_agent")
def test_chat_returns_trip_preview_when_complete(
    mock_build: AsyncMock,
    client: TestClient,
    api_key: str,
):
    mock_agent = AsyncMock()
    mock_agent.process_message = AsyncMock(
        return_value=RequirementsTurn(
            complete=True,
            missing_fields=[],
            assistant_message="Perfecto, tengo todo listo.",
            origin="Buenos Aires, Argentina",
            destination="Barcelona",
            start_date=date(2026, 8, 1),
            end_date=date(2026, 8, 3),
            budget_limit=2000.0,
            preferences=["gastronomía"],
            preferences_asked=True,
        )
    )
    mock_build.return_value = mock_agent

    response = client.post(
        "/api/v1/chat",
        headers={"X-API-Key": api_key},
        json={
            "message": "Salgo de Buenos Aires, presupuesto 2000 USD",
            "history": [
                {"role": "assistant", "content": "¿Desde dónde salís?"},
                {"role": "user", "content": "Barcelona del 1 al 3 de agosto"},
            ],
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["complete"] is True
    assert data["trip"]["origin"] == "Buenos Aires, Argentina"
    assert data["trip"]["destination"] == "Barcelona"
    mock_agent.process_message.assert_awaited_once_with(
        "Salgo de Buenos Aires, presupuesto 2000 USD",
        history=[
            ("assistant", "¿Desde dónde salís?"),
            ("user", "Barcelona del 1 al 3 de agosto"),
        ],
        previous_state=None,
    )


@patch("budgettrip.interfaces.api.routers.chat_router.build_requirements_agent")
def test_chat_reuses_session_state(
    mock_build: AsyncMock,
    client: TestClient,
    api_key: str,
):
    mock_agent = AsyncMock()
    first_turn = RequirementsTurn(
        complete=False,
        missing_fields=["budget_limit"],
        assistant_message="¿Cuál es tu presupuesto?",
        origin="Buenos Aires",
        destination="Londres",
        start_date=date(2027, 2, 1),
        end_date=date(2027, 2, 8),
    )
    second_turn = RequirementsTurn(
        complete=True,
        missing_fields=[],
        assistant_message="Perfecto, confirmá para planificar.",
        origin="Buenos Aires",
        destination="Londres",
        start_date=date(2027, 2, 1),
        end_date=date(2027, 2, 8),
        budget_limit=2500.0,
        preferences=[],
        preferences_asked=True,
    )
    mock_agent.process_message = AsyncMock(side_effect=[first_turn, second_turn])
    mock_build.return_value = mock_agent

    first_response = client.post(
        "/api/v1/chat",
        headers={"X-API-Key": api_key},
        json={"message": "Quiero ir a Londres desde Buenos Aires", "history": []},
    )
    assert first_response.status_code == 200
    session_id = first_response.json()["session_id"]

    second_response = client.post(
        "/api/v1/chat",
        headers={"X-API-Key": api_key},
        json={
            "message": "2500 USD, sin preferencias",
            "history": [],
            "session_id": session_id,
        },
    )
    assert second_response.status_code == 200
    assert second_response.json()["complete"] is True
    mock_agent.process_message.assert_any_await(
        "2500 USD, sin preferencias",
        history=None,
        previous_state=first_turn,
    )


def test_confirm_requires_api_key(client: TestClient):
    response = client.post(
        "/api/v1/chat/confirm",
        json={
            "trip": {
                "origin": "Buenos Aires, Argentina",
                "destination": "Barcelona",
                "start_date": "2026-08-01",
                "end_date": "2026-08-03",
                "budget_limit": 2000,
            },
            "send_email": False,
        },
    )
    assert response.status_code == 401


@patch("budgettrip.interfaces.api.routers.chat_router.build_plan_trip_use_case")
def test_confirm_starts_planning(
    mock_build: AsyncMock,
    client: TestClient,
    api_key: str,
):
    mock_use_case = AsyncMock()
    mock_use_case.execute = AsyncMock(return_value=_sample_itinerary())
    mock_build.return_value = mock_use_case

    response = client.post(
        "/api/v1/chat/confirm",
        headers={"X-API-Key": api_key},
        json={
            "trip": {
                "origin": "Buenos Aires, Argentina",
                "destination": "Barcelona",
                "start_date": "2026-08-01",
                "end_date": "2026-08-03",
                "budget_limit": 2000,
                "preferences": ["gastronomía"],
            },
            "send_email": False,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["itinerary"]["destination"] == "Barcelona"
    mock_use_case.execute.assert_awaited_once()
