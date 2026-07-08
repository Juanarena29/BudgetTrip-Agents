import asyncio
from pathlib import Path

from budgettrip.application.ports.budget_port import BudgetCalculator
from budgettrip.application.ports.notifier_port import CalendarExporter, EmailSender
from budgettrip.application.ports.planner_port import PlannerProvider
from budgettrip.application.ports.progress_port import NoOpReporter, ProgressReporter
from budgettrip.application.ports.search_port import SearchProvider
from budgettrip.application.ports.tracing_port import NoOpTracer, TracingProvider
from budgettrip.application.ports.writer_port import WriterProvider
from budgettrip.application.services.itinerary_renderer import render_itinerary_html
from budgettrip.domain.entities import Itinerary, TripRequest

MAX_BUDGET_RETRIES = 2


class PlanTripUseCase:
    def __init__(
        self,
        planner: PlannerProvider,
        searcher: SearchProvider,
        writer: WriterProvider,
        budget_calc: BudgetCalculator,
        email_sender: EmailSender,
        calendar_exporter: CalendarExporter | None = None,
        reporter: ProgressReporter | None = None,
        tracer: TracingProvider | None = None,
    ) -> None:
        self.planner = planner
        self.searcher = searcher
        self.writer = writer
        self.budget_calc = budget_calc
        self.email_sender = email_sender
        self.calendar_exporter = calendar_exporter
        self.reporter = reporter or NoOpReporter()
        self.tracer = tracer or NoOpTracer()

    async def execute(
        self,
        trip: TripRequest,
        send_email: bool = True,
        export_calendar_path: Path | None = None,
    ) -> Itinerary:
        with self.tracer.trace(f"Trip planning: {trip.destination}"):
            await self.reporter.report("Planificando búsquedas...")
            plan = await self.planner.plan_searches(trip)

            total_searches = len(plan.searches)
            await self.reporter.report(f"Buscando información (0/{total_searches})...")
            research: list[str] = []
            for index, item in enumerate(plan.searches, start=1):
                result = await self.searcher.search(item)
                research.append(result)
                await self.reporter.report(f"Buscando información ({index}/{total_searches})...")

            await self.reporter.report("Escribiendo itinerario...")
            itinerary = await self.writer.write_itinerary(trip, research)

            await self.reporter.report("Calculando presupuesto...")
            itinerary = self.budget_calc.calculate(itinerary, trip.budget_limit)

            retries = 0
            while itinerary.over_budget and retries < MAX_BUDGET_RETRIES:
                await self.reporter.report("Presupuesto excedido, ajustando itinerario...")
                feedback = (
                    f"Excediste el presupuesto por ${itinerary.budget_difference:.2f}. "
                    f"Recortá costos."
                )
                itinerary = await self.writer.write_itinerary(
                    trip,
                    research,
                    previous_draft=itinerary,
                    feedback=feedback,
                )
                itinerary = self.budget_calc.calculate(itinerary, trip.budget_limit)
                retries += 1

            if send_email:
                await self.reporter.report("Enviando email...")
                await asyncio.to_thread(
                    self.email_sender.send,
                    subject=f"Itinerario: {trip.destination}",
                    html_body=render_itinerary_html(itinerary),
                )

            if export_calendar_path is not None and self.calendar_exporter is not None:
                await self.reporter.report("Generando calendario...")
                calendar_bytes = await asyncio.to_thread(
                    self.calendar_exporter.export,
                    itinerary,
                )
                export_calendar_path.write_bytes(calendar_bytes)

            await self.reporter.report("Listo.")
            return itinerary
