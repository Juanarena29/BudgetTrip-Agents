import argparse
import asyncio
import json
import sys
from datetime import date
from pathlib import Path

from budgettrip.domain.entities import TripRequest
from budgettrip.infrastructure.factory import build_plan_trip_use_case


class ConsoleReporter:
    async def report(self, message: str) -> None:
        print(f"[progress] {message}")


def _parse_date(value: str) -> date:
    return date.fromisoformat(value)


async def _run(args: argparse.Namespace) -> int:
    trip = TripRequest(
        origin=args.origin,
        destination=args.destination,
        start_date=_parse_date(args.start_date),
        end_date=_parse_date(args.end_date),
        budget_limit=args.budget,
        preferences=args.preferences,
    )

    use_case = build_plan_trip_use_case(reporter=ConsoleReporter())
    export_path = Path(args.export_ics) if args.export_ics else None
    itinerary = await use_case.execute(
        trip,
        send_email=args.send_email,
        export_calendar_path=export_path,
    )

    print(json.dumps(itinerary.model_dump(mode="json"), indent=2, ensure_ascii=False))
    if export_path:
        print(f"[info] Calendario exportado a {export_path}", file=sys.stderr)
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description="Genera un itinerario con BudgetTrip")
    parser.add_argument("--origin", required=True, help="Ciudad/país de salida")
    parser.add_argument("--destination", required=True, help="Destino del viaje")
    parser.add_argument("--start-date", required=True, help="Fecha inicio YYYY-MM-DD")
    parser.add_argument("--end-date", required=True, help="Fecha fin YYYY-MM-DD")
    parser.add_argument("--budget", type=float, required=True, help="Presupuesto en USD")
    parser.add_argument(
        "--preferences",
        nargs="*",
        default=[],
        help="Preferencias del viajero",
    )
    parser.add_argument(
        "--send-email",
        action="store_true",
        help="Enviar email al finalizar (requiere SMTP configurado)",
    )
    parser.add_argument(
        "--export-ics",
        metavar="PATH",
        help="Exportar itinerario como archivo .ics",
    )
    args = parser.parse_args()

    try:
        raise SystemExit(asyncio.run(_run(args)))
    except KeyboardInterrupt:
        raise SystemExit(130) from None
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
