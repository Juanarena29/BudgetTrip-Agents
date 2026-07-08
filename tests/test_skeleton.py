import pytest


def test_domain_entities_import():
    from budgettrip.domain.entities import Itinerary, TripRequest

    assert TripRequest is not None
    assert Itinerary is not None


def test_application_ports_import():
    from budgettrip.application.ports import (
        BudgetCalculator,
        PlannerProvider,
        ProgressReporter,
        SearchProvider,
        WriterProvider,
    )

    assert all(
        port is not None
        for port in (
            PlannerProvider,
            SearchProvider,
            WriterProvider,
            BudgetCalculator,
            ProgressReporter,
        )
    )


def test_plan_trip_use_case_is_instantiable():
    from budgettrip.application.use_cases.plan_trip_use_case import PlanTripUseCase
    from budgettrip.infrastructure.agents_sdk.planner_agent import PlannerAgent
    from budgettrip.infrastructure.agents_sdk.search_agent import SearchAgent
    from budgettrip.infrastructure.agents_sdk.writer_agent import WriterAgent
    from budgettrip.infrastructure.notifications.null_email_sender import NullEmailSender
    from budgettrip.infrastructure.tools.calculate_budget_tool import CalculateBudgetTool

    use_case = PlanTripUseCase(
        planner=PlannerAgent(),
        searcher=SearchAgent(),
        writer=WriterAgent(),
        budget_calc=CalculateBudgetTool(),
        email_sender=NullEmailSender(),
    )
    assert use_case.reporter is not None


def test_fastapi_app_health_route_exists():
    from fastapi.testclient import TestClient

    from budgettrip.interfaces.api.main import app

    client = TestClient(app)
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
