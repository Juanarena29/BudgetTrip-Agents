from datetime import date

from pydantic import BaseModel, Field, model_validator

from budgettrip.domain.entities import Itinerary, TripRequest

MAX_TRIP_DAYS = 30


class TripRequestDTO(BaseModel):
    origin: str = Field(min_length=1, max_length=200)
    destination: str = Field(min_length=1, max_length=200)
    start_date: date
    end_date: date
    budget_limit: float = Field(gt=0, le=1_000_000)
    preferences: list[str] = Field(default_factory=list, max_length=20)

    @model_validator(mode="after")
    def validate_dates(self) -> "TripRequestDTO":
        if self.end_date <= self.start_date:
            raise ValueError("end_date must be after start_date")
        trip_days = (self.end_date - self.start_date).days
        if trip_days > MAX_TRIP_DAYS:
            raise ValueError(f"Trip cannot exceed {MAX_TRIP_DAYS} days")
        return self

    def to_domain(self) -> TripRequest:
        return TripRequest(
            origin=self.origin,
            destination=self.destination,
            start_date=self.start_date,
            end_date=self.end_date,
            budget_limit=self.budget_limit,
            preferences=self.preferences,
        )


class CreateTripRequestDTO(TripRequestDTO):
    send_email: bool = True


class CostItemDTO(BaseModel):
    day: int
    category: str
    description: str
    estimated_cost: float


class DayPlanDTO(BaseModel):
    day: int
    date: date
    summary: str
    activities: list[str]
    cost_items: list[CostItemDTO]
    day_total: float


class ItineraryResponseDTO(BaseModel):
    destination: str
    days: list[DayPlanDTO]
    total_cost: float
    over_budget: bool
    budget_difference: float
    short_summary: str

    @classmethod
    def from_domain(cls, itinerary: Itinerary) -> "ItineraryResponseDTO":
        return cls(
            destination=itinerary.destination,
            days=[DayPlanDTO.model_validate(day.model_dump()) for day in itinerary.days],
            total_cost=itinerary.total_cost,
            over_budget=itinerary.over_budget,
            budget_difference=itinerary.budget_difference,
            short_summary=itinerary.short_summary,
        )


class TripCreatedResponseDTO(BaseModel):
    id: str
    itinerary: ItineraryResponseDTO

