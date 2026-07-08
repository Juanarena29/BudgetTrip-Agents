from budgettrip.application.ports.progress_port import ProgressReporter
from budgettrip.application.ports.tracing_port import TracingProvider
from budgettrip.application.use_cases.plan_trip_use_case import PlanTripUseCase
from budgettrip.infrastructure.agents_sdk.planner_agent import PlannerAgent
from budgettrip.infrastructure.agents_sdk.requirements_agent import RequirementsAgent
from budgettrip.infrastructure.agents_sdk.search_agent import SearchAgent
from budgettrip.infrastructure.agents_sdk.tracing import OpenAITracingProvider
from budgettrip.infrastructure.agents_sdk.writer_agent import WriterAgent
from budgettrip.infrastructure.config import Settings, get_settings
from budgettrip.infrastructure.notifications import build_email_sender
from budgettrip.infrastructure.notifications.ics_exporter import IcsExporter
from budgettrip.infrastructure.tools.calculate_budget_tool import CalculateBudgetTool


def build_requirements_agent(settings: Settings | None = None) -> RequirementsAgent:
    return RequirementsAgent(settings=settings or get_settings())


def build_plan_trip_use_case(
    settings: Settings | None = None,
    reporter: ProgressReporter | None = None,
    tracer: TracingProvider | None = None,
) -> PlanTripUseCase:
    resolved_settings = settings or get_settings()

    return PlanTripUseCase(
        planner=PlannerAgent(settings=resolved_settings),
        searcher=SearchAgent(settings=resolved_settings),
        writer=WriterAgent(settings=resolved_settings),
        budget_calc=CalculateBudgetTool(),
        email_sender=build_email_sender(resolved_settings),
        calendar_exporter=IcsExporter(),
        reporter=reporter,
        tracer=tracer or OpenAITracingProvider(),
    )
