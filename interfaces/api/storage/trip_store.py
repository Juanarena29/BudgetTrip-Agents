import uuid

from budgettrip.domain.entities import Itinerary


class InMemoryTripStore:
    def __init__(self) -> None:
        self._trips: dict[str, Itinerary] = {}

    def save(self, itinerary: Itinerary) -> str:
        trip_id = str(uuid.uuid4())
        self._trips[trip_id] = itinerary
        return trip_id

    def get(self, trip_id: str) -> Itinerary | None:
        return self._trips.get(trip_id)
