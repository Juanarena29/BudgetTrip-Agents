from datetime import date
from typing import Literal

from pydantic import BaseModel, Field, model_validator

from budgettrip.domain.entities import RequirementsTurn, TripRequest
from budgettrip.interfaces.api.schemas.trip_dto import MAX_TRIP_DAYS


class ChatMessageDTO(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=4000)


class ChatRequestDTO(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    history: list[ChatMessageDTO] = Field(default_factory=list, max_length=50)
    session_id: str | None = Field(default=None, max_length=64)


class TripPreviewDTO(BaseModel):
    origin: str = Field(min_length=1, max_length=200)
    destination: str = Field(min_length=1, max_length=200)
    start_date: date
    end_date: date
    budget_limit: float = Field(gt=0, le=1_000_000)
    preferences: list[str] = Field(default_factory=list, max_length=20)

    @model_validator(mode="after")
    def validate_dates(self) -> "TripPreviewDTO":
        if self.end_date <= self.start_date:
            raise ValueError("end_date must be after start_date")
        trip_days = (self.end_date - self.start_date).days
        if trip_days > MAX_TRIP_DAYS:
            raise ValueError(f"Trip cannot exceed {MAX_TRIP_DAYS} days")
        return self

    @classmethod
    def from_domain(cls, trip: TripRequest) -> "TripPreviewDTO":
        return cls(
            origin=trip.origin,
            destination=trip.destination,
            start_date=trip.start_date,
            end_date=trip.end_date,
            budget_limit=trip.budget_limit,
            preferences=trip.preferences,
        )

    def to_domain(self) -> TripRequest:
        return TripRequest(
            origin=self.origin,
            destination=self.destination,
            start_date=self.start_date,
            end_date=self.end_date,
            budget_limit=self.budget_limit,
            preferences=self.preferences,
        )


class ConfirmTripRequestDTO(BaseModel):
    trip: TripPreviewDTO
    send_email: bool = False


class ChatResponseDTO(BaseModel):
    session_id: str
    assistant_message: str
    complete: bool
    missing_fields: list[str]
    trip: TripPreviewDTO | None = None

    @classmethod
    def from_requirements_turn(
        cls,
        turn: RequirementsTurn,
        session_id: str,
    ) -> "ChatResponseDTO":
        trip_request = turn.to_trip_request()
        return cls(
            session_id=session_id,
            assistant_message=turn.assistant_message,
            complete=turn.complete,
            missing_fields=turn.missing_fields,
            trip=TripPreviewDTO.from_domain(trip_request) if trip_request else None,
        )
