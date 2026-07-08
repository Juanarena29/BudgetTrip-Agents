from datetime import date
from unittest.mock import AsyncMock, MagicMock

import pytest

from budgettrip.application.use_cases.plan_trip_use_case import PlanTripUseCase
from budgettrip.domain.entities import (
    CostItem,
    DayPlan,
    Itinerary,
    SearchItem,
    SearchPlan,
    TripRequest,
)
from budgettrip.infrastructure.tools.budget_logic import compute_budget
from budgettrip.infrastructure.tools.calculate_budget_tool import CalculateBudgetTool


@pytest.fixture
def trip() -> TripRequest:
    return TripRequest(
        origin="Buenos Aires, Argentina",
        destination="Barcelona",
        start_date=date(2026, 8, 1),
        end_date=date(2026, 8, 3),
        budget_limit=500.0,
        preferences=["gastronomía"],
    )


@pytest.fixture
def search_plan() -> SearchPlan:
    return SearchPlan(
        searches=[
            SearchItem(category="clima", reason="Clima", query="clima Barcelona agosto"),
            SearchItem(category="vuelos", reason="Vuelos", query="vuelos a Barcelona"),
        ]
    )


def _itinerary_with_total(total: float) -> Itinerary:
    return Itinerary(
        destination="Barcelona",
        days=[
            DayPlan(
                day=1,
                date=date(2026, 8, 1),
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


class FakeReporter:
    def __init__(self) -> None:
        self.messages: list[str] = []

    async def report(self, message: str) -> None:
        self.messages.append(message)


def _build_use_case(
    *,
    search_plan: SearchPlan,
    search_results: list[str],
    writer_side_effect: list[Itinerary],
    email_sender: MagicMock | None = None,
    reporter: FakeReporter | None = None,
) -> PlanTripUseCase:
    planner = AsyncMock()
    planner.plan_searches = AsyncMock(return_value=search_plan)

    searcher = AsyncMock()
    searcher.search = AsyncMock(side_effect=search_results)

    writer = AsyncMock()
    writer.write_itinerary = AsyncMock(side_effect=writer_side_effect)

    return PlanTripUseCase(
        planner=planner,
        searcher=searcher,
        writer=writer,
        budget_calc=CalculateBudgetTool(),
        email_sender=email_sender or MagicMock(),
        reporter=reporter,
    )


@pytest.mark.asyncio
async def test_execute_happy_path_within_budget(trip: TripRequest, search_plan: SearchPlan):
    itinerary = _itinerary_with_total(400.0)
    reporter = FakeReporter()
    email_sender = MagicMock()

    use_case = _build_use_case(
        search_plan=search_plan,
        search_results=["clima ok", "vuelos ok"],
        writer_side_effect=[itinerary],
        email_sender=email_sender,
        reporter=reporter,
    )

    result = await use_case.execute(trip)

    assert result.over_budget is False
    assert result.total_cost == 400.0
    email_sender.send.assert_called_once()
    assert email_sender.send.call_args.kwargs["subject"] == "Itinerario: Barcelona"
    assert use_case.writer.write_itinerary.await_count == 1
    assert "Listo." in reporter.messages


@pytest.mark.asyncio
async def test_execute_retries_with_previous_draft_and_feedback(
    trip: TripRequest, search_plan: SearchPlan
):
    over_budget = _itinerary_with_total(700.0)
    adjusted = _itinerary_with_total(450.0)
    email_sender = MagicMock()

    use_case = _build_use_case(
        search_plan=search_plan,
        search_results=["a", "b"],
        writer_side_effect=[over_budget, adjusted],
        email_sender=email_sender,
    )

    result = await use_case.execute(trip)

    assert result.total_cost == 450.0
    assert result.over_budget is False
    use_case.writer.write_itinerary.assert_any_call(
        trip,
        ["a", "b"],
        previous_draft=compute_budget(over_budget, trip.budget_limit),
        feedback="Excediste el presupuesto por $200.00. Recortá costos.",
    )


@pytest.mark.asyncio
async def test_execute_stops_after_max_retries_still_over_budget(
    trip: TripRequest, search_plan: SearchPlan
):
    over_budget = _itinerary_with_total(700.0)

    use_case = _build_use_case(
        search_plan=search_plan,
        search_results=["a", "b"],
        writer_side_effect=[over_budget, over_budget, over_budget],
    )

    result = await use_case.execute(trip)

    assert use_case.writer.write_itinerary.await_count == 3
    assert result.over_budget is True
    assert result.total_cost == 700.0


@pytest.mark.asyncio
async def test_execute_skips_email_when_disabled(trip: TripRequest, search_plan: SearchPlan):
    itinerary = _itinerary_with_total(300.0)
    email_sender = MagicMock()

    use_case = _build_use_case(
        search_plan=search_plan,
        search_results=["a", "b"],
        writer_side_effect=[itinerary],
        email_sender=email_sender,
    )

    await use_case.execute(trip, send_email=False)

    email_sender.send.assert_not_called()


@pytest.mark.asyncio
async def test_execute_reports_search_progress(trip: TripRequest, search_plan: SearchPlan):
    reporter = FakeReporter()

    use_case = _build_use_case(
        search_plan=search_plan,
        search_results=["a", "b"],
        writer_side_effect=[_itinerary_with_total(100.0)],
        reporter=reporter,
    )

    await use_case.execute(trip, send_email=False)

    assert reporter.messages == [
        "Planificando búsquedas...",
        "Buscando información (0/2)...",
        "Buscando información (1/2)...",
        "Buscando información (2/2)...",
        "Escribiendo itinerario...",
        "Calculando presupuesto...",
        "Listo.",
    ]
