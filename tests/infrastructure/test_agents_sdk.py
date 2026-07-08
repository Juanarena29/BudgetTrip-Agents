from unittest.mock import AsyncMock, patch

import pytest

from budgettrip.domain.entities import SearchItem, SearchPlan, TripRequest
from budgettrip.domain.exceptions import PlanningError
from budgettrip.infrastructure.agents_sdk.planner_agent import PlannerAgent
from budgettrip.infrastructure.agents_sdk.search_agent import SearchAgent
from budgettrip.infrastructure.agents_sdk.writer_agent import WriterAgent
from budgettrip.infrastructure.config import Settings
from datetime import date

from budgettrip.domain.entities import CostItem, DayPlan, Itinerary


def _itinerary_with_total(total: float, destination: str = "Lisboa") -> Itinerary:
    return Itinerary(
        destination=destination,
        days=[
            DayPlan(
                day=1,
                date=date(2026, 10, 1),
                summary="Día 1",
                activities=["Tour"],
                cost_items=[
                    CostItem(
                        day=1,
                        category="activity",
                        description="Tour",
                        estimated_cost=total,
                    )
                ],
                day_total=0.0,
            )
        ],
        total_cost=0.0,
        over_budget=False,
        budget_difference=0.0,
        short_summary="Resumen",
    )


@pytest.fixture
def settings() -> Settings:
    return Settings(
        openai_api_key="test-key",
        api_secret_key="secret",
        allowed_origins=["http://localhost:3000"],
        smtp_host="",
        smtp_port=587,
        smtp_user="",
        smtp_password="",
        how_many_searches=2,
        model_name="gpt-5.4-mini",
    )


@pytest.fixture
def trip() -> TripRequest:
    from datetime import date

    return TripRequest(
        origin="Buenos Aires, Argentina",
        destination="Lisboa",
        start_date=date(2026, 10, 1),
        end_date=date(2026, 10, 3),
        budget_limit=800.0,
        preferences=["historia"],
    )


@pytest.mark.asyncio
async def test_planner_agent_returns_search_plan(settings: Settings, trip: TripRequest):
    expected_plan = SearchPlan(
        searches=[
            SearchItem(category="clima", reason="Clima", query="clima Lisboa octubre"),
            SearchItem(category="vuelos", reason="Vuelos", query="vuelos a Lisboa"),
        ]
    )
    mock_result = AsyncMock()
    mock_result.final_output = expected_plan

    with patch(
        "budgettrip.infrastructure.agents_sdk.planner_agent.Runner.run",
        new_callable=AsyncMock,
        return_value=mock_result,
    ):
        agent = PlannerAgent(settings=settings)
        plan = await agent.plan_searches(trip)

    assert plan == expected_plan


@pytest.mark.asyncio
async def test_search_agent_returns_research_text(settings: Settings):
    item = SearchItem(category="clima", reason="Clima", query="clima Lisboa")
    mock_result = AsyncMock()
    mock_result.final_output = "Soleado, 22°C"

    with patch(
        "budgettrip.infrastructure.agents_sdk.search_agent.Runner.run",
        new_callable=AsyncMock,
        return_value=mock_result,
    ):
        agent = SearchAgent(settings=settings)
        result = await agent.search(item)

    assert result == "Soleado, 22°C"


@pytest.mark.asyncio
async def test_writer_agent_builds_initial_prompt(settings: Settings, trip: TripRequest):
    itinerary = _itinerary_with_total(300.0, destination="Lisboa")
    mock_result = AsyncMock()
    mock_result.final_output = itinerary

    with patch(
        "budgettrip.infrastructure.agents_sdk.writer_agent.Runner.run",
        new_callable=AsyncMock,
        return_value=mock_result,
    ) as run_mock:
        agent = WriterAgent(settings=settings)
        result = await agent.write_itinerary(trip, ["research a", "research b"])

    assert result.destination == "Lisboa"
    input_message = run_mock.await_args.args[1]
    assert "Destino: Lisboa" in input_message
    assert "Días del viaje: 3" in input_message
    assert "research a" in input_message


@pytest.mark.asyncio
async def test_writer_agent_includes_previous_draft_on_retry(settings: Settings, trip: TripRequest):
    draft = _itinerary_with_total(900.0, destination="Lisboa")
    adjusted = _itinerary_with_total(700.0, destination="Lisboa")

    mock_result = AsyncMock()
    mock_result.final_output = adjusted

    with patch(
        "budgettrip.infrastructure.agents_sdk.writer_agent.Runner.run",
        new_callable=AsyncMock,
        return_value=mock_result,
    ) as run_mock:
        agent = WriterAgent(settings=settings)
        result = await agent.write_itinerary(
            trip,
            ["research"],
            previous_draft=draft,
            feedback="Recortá costos",
        )

    assert result.days[0].cost_items[0].estimated_cost == 700.0
    input_message = run_mock.await_args.args[1]
    assert "Borrador anterior" in input_message
    assert "Recortá costos" in input_message


@pytest.mark.asyncio
async def test_planner_agent_requires_api_key(trip: TripRequest):
    settings = Settings(
        openai_api_key="",
        api_secret_key="",
        allowed_origins=[],
        smtp_host="",
        smtp_port=587,
        smtp_user="",
        smtp_password="",
        how_many_searches=2,
        model_name="gpt-5.4-mini",
    )
    agent = PlannerAgent(settings=settings)

    with pytest.raises(PlanningError, match="OPENAI_API_KEY"):
        await agent.plan_searches(trip)
