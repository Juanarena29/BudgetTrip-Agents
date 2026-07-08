from datetime import date
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from budgettrip.domain.entities import CostItem, DayPlan, Itinerary
from budgettrip.interfaces.api.main import create_app
from budgettrip.interfaces.api.storage.trip_store import InMemoryTripStore


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


@pytest.fixture
def sample_itinerary() -> Itinerary:
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


def test_healthcheck_no_auth_required(client: TestClient):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_trip_requires_api_key(client: TestClient):
    response = client.post(
        "/api/v1/trips",
        json={
            "destination": "Barcelona",
            "start_date": "2026-08-01",
            "end_date": "2026-08-03",
            "budget_limit": 1200,
        },
    )
    assert response.status_code == 401


@patch("budgettrip.interfaces.api.routers.trip_router.build_plan_trip_use_case")
def test_create_trip_returns_itinerary(
    mock_build: AsyncMock,
    client: TestClient,
    api_key: str,
    sample_itinerary: Itinerary,
):
    mock_use_case = AsyncMock()
    mock_use_case.execute = AsyncMock(return_value=sample_itinerary)
    mock_build.return_value = mock_use_case

    response = client.post(
        "/api/v1/trips",
        headers={"X-API-Key": api_key},
        json={
            "origin": "Buenos Aires, Argentina",
            "destination": "Barcelona",
            "start_date": "2026-08-01",
            "end_date": "2026-08-03",
            "budget_limit": 1200,
            "send_email": False,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["itinerary"]["destination"] == "Barcelona"
    assert data["itinerary"]["total_cost"] == 20.0
    mock_use_case.execute.assert_awaited_once()


def test_get_trip_returns_saved_itinerary(
    client: TestClient,
    api_key: str,
    sample_itinerary: Itinerary,
):
    store = client.app.state.trip_store
    trip_id = store.save(sample_itinerary)

    response = client.get(f"/api/v1/trips/{trip_id}", headers={"X-API-Key": api_key})

    assert response.status_code == 200
    assert response.json()["destination"] == "Barcelona"


def test_get_trip_not_found(client: TestClient, api_key: str):
    response = client.get("/api/v1/trips/nonexistent", headers={"X-API-Key": api_key})
    assert response.status_code == 404


def test_create_trip_rejects_invalid_dates(client: TestClient, api_key: str):
    response = client.post(
        "/api/v1/trips",
        headers={"X-API-Key": api_key},
        json={
            "origin": "Buenos Aires, Argentina",
            "destination": "Barcelona",
            "start_date": "2026-08-03",
            "end_date": "2026-08-01",
            "budget_limit": 1200,
        },
    )
    assert response.status_code == 422


def test_trip_store_generates_unique_ids(sample_itinerary: Itinerary):
    store = InMemoryTripStore()
    id_a = store.save(sample_itinerary)
    id_b = store.save(sample_itinerary)
    assert id_a != id_b
    assert store.get(id_a) == sample_itinerary
