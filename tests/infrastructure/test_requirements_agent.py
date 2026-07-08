from datetime import date
from unittest.mock import AsyncMock, patch

import pytest

from budgettrip.domain.entities import RequirementsTurn
from budgettrip.infrastructure.agents_sdk.requirements_agent import RequirementsAgent
from budgettrip.infrastructure.config import Settings


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
        how_many_searches=8,
        model_name="gpt-5.4-mini",
    )


@pytest.mark.asyncio
async def test_requirements_agent_asks_for_missing_origin(settings: Settings):
    incomplete = RequirementsTurn(
        complete=False,
        missing_fields=["origin", "start_date", "end_date", "budget_limit"],
        assistant_message="¿Desde dónde vas a salir?",
        destination="Barcelona",
        preferences=["gastronomía"],
    )
    mock_result = AsyncMock()
    mock_result.final_output = incomplete

    with patch(
        "budgettrip.infrastructure.agents_sdk.requirements_agent.Runner.run",
        new_callable=AsyncMock,
        return_value=mock_result,
    ) as run_mock:
        agent = RequirementsAgent(settings=settings)
        turn = await agent.process_message("Quiero 3 días en Barcelona, me gusta la gastronomía")

    assert turn.complete is False
    assert "origin" in turn.missing_fields
    assert turn.destination == "Barcelona"
    assert turn.to_trip_request() is None
    assert "Usuario:" in run_mock.await_args.args[1]


@pytest.mark.asyncio
async def test_requirements_agent_includes_previous_state_in_prompt(settings: Settings):
    previous = RequirementsTurn(
        complete=False,
        missing_fields=["budget_limit"],
        assistant_message="¿Cuál es tu presupuesto?",
        origin="Buenos Aires",
        destination="Londres",
        start_date=date(2027, 2, 1),
        end_date=date(2027, 2, 8),
    )
    updated = RequirementsTurn(
        complete=False,
        missing_fields=["preferences"],
        assistant_message="¿Qué te gusta hacer?",
        origin="Buenos Aires",
        destination="Londres",
        start_date=date(2027, 2, 1),
        end_date=date(2027, 2, 8),
        budget_limit=2500.0,
        preferences_asked=False,
    )
    mock_result = AsyncMock()
    mock_result.final_output = updated

    with patch(
        "budgettrip.infrastructure.agents_sdk.requirements_agent.Runner.run",
        new_callable=AsyncMock,
        return_value=mock_result,
    ) as run_mock:
        agent = RequirementsAgent(settings=settings)
        turn = await agent.process_message(
            "Tengo 2500 USD",
            previous_state=previous,
        )

    prompt = run_mock.await_args.args[1]
    assert "Estado actual conocido" in prompt
    assert "Buenos Aires" in prompt
    assert turn.budget_limit == 2500.0


@pytest.mark.asyncio
async def test_requirements_agent_returns_trip_request_when_complete(settings: Settings):
    complete = RequirementsTurn(
        complete=True,
        missing_fields=[],
        assistant_message="Perfecto, tengo todo. ¿Confirmás?",
        origin="Buenos Aires, Argentina",
        destination="Barcelona",
        start_date=date(2026, 8, 1),
        end_date=date(2026, 8, 3),
        budget_limit=2000.0,
        preferences=["gastronomía"],
        preferences_asked=True,
    )
    mock_result = AsyncMock()
    mock_result.final_output = complete

    with patch(
        "budgettrip.infrastructure.agents_sdk.requirements_agent.Runner.run",
        new_callable=AsyncMock,
        return_value=mock_result,
    ):
        agent = RequirementsAgent(settings=settings)
        turn = await agent.process_message(
            "Salgo de Buenos Aires, 1 al 3 de agosto, presupuesto 2000 USD",
            history=[("assistant", "¿Desde dónde salís?")],
        )

    trip = turn.to_trip_request()
    assert trip is not None
    assert trip.origin == "Buenos Aires, Argentina"
    assert trip.destination == "Barcelona"
