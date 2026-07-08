from datetime import date
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

from budgettrip.application.use_cases.plan_trip_use_case import PlanTripUseCase
from budgettrip.domain.entities import CostItem, DayPlan, Itinerary, SearchItem, SearchPlan, TripRequest
from budgettrip.infrastructure.tools.calculate_budget_tool import CalculateBudgetTool


@pytest.mark.asyncio
async def test_execute_exports_calendar_when_path_provided(tmp_path: Path):
    itinerary = Itinerary(
        destination="Madrid",
        days=[
            DayPlan(
                day=1,
                date=date(2026, 9, 1),
                summary="Centro",
                activities=["Plaza Mayor"],
                cost_items=[
                    CostItem(day=1, category="food", description="Tapas", estimated_cost=25.0)
                ],
                day_total=25.0,
            )
        ],
        total_cost=25.0,
        over_budget=False,
        budget_difference=0.0,
        short_summary="Escapada",
    )
    calendar_exporter = MagicMock()
    calendar_exporter.export = MagicMock(return_value=b"BEGIN:VCALENDAR")

    planner = AsyncMock()
    planner.plan_searches = AsyncMock(
        return_value=SearchPlan(
            searches=[SearchItem(category="clima", reason="Clima", query="clima Madrid")]
        )
    )
    searcher = AsyncMock()
    searcher.search = AsyncMock(return_value="soleado")
    writer = AsyncMock()
    writer.write_itinerary = AsyncMock(return_value=itinerary)

    use_case = PlanTripUseCase(
        planner=planner,
        searcher=searcher,
        writer=writer,
        budget_calc=CalculateBudgetTool(),
        email_sender=MagicMock(),
        calendar_exporter=calendar_exporter,
    )

    export_path = tmp_path / "trip.ics"
    await use_case.execute(
        TripRequest(
            origin="Buenos Aires, Argentina",
            destination="Madrid",
            start_date=date(2026, 9, 1),
            end_date=date(2026, 9, 1),
            budget_limit=500.0,
        ),
        send_email=False,
        export_calendar_path=export_path,
    )

    calendar_exporter.export.assert_called_once()
    assert export_path.read_bytes() == b"BEGIN:VCALENDAR"
