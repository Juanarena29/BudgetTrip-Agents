from budgettrip.application.ports.tracing_port import NoOpTracer


def test_noop_tracer_returns_usable_context_manager():
    tracer = NoOpTracer()

    with tracer.trace("some trace name"):
        pass


def test_plan_trip_use_case_defaults_to_noop_tracer():
    from unittest.mock import AsyncMock, MagicMock

    from budgettrip.application.ports.tracing_port import NoOpTracer
    from budgettrip.application.use_cases.plan_trip_use_case import PlanTripUseCase

    use_case = PlanTripUseCase(
        planner=AsyncMock(),
        searcher=AsyncMock(),
        writer=AsyncMock(),
        budget_calc=MagicMock(),
        email_sender=MagicMock(),
    )

    assert isinstance(use_case.tracer, NoOpTracer)
