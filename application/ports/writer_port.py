from typing import Protocol

from budgettrip.domain.entities import Itinerary, TripRequest


class WriterProvider(Protocol):
    async def write_itinerary(
        self,
        trip: TripRequest,
        research: list[str],
        previous_draft: Itinerary | None = None,
        feedback: str | None = None,
    ) -> Itinerary: ...
