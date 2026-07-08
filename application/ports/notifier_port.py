from typing import Protocol

from budgettrip.domain.entities import Itinerary


class EmailSender(Protocol):
    def send(self, subject: str, html_body: str) -> None: ...


class CalendarExporter(Protocol):
    def export(self, itinerary: Itinerary) -> bytes: ...
