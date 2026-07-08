from fastapi import APIRouter, Depends, Request

from budgettrip.infrastructure.factory import build_plan_trip_use_case, build_requirements_agent
from budgettrip.interfaces.api.dependencies import (
    get_requirements_session_store,
    get_trip_store,
    verify_api_key,
)
from budgettrip.interfaces.api.schemas.chat_dto import (
    ChatRequestDTO,
    ChatResponseDTO,
    ConfirmTripRequestDTO,
)
from budgettrip.interfaces.api.schemas.trip_dto import ItineraryResponseDTO, TripCreatedResponseDTO
from budgettrip.interfaces.api.security.rate_limit import limiter
from budgettrip.interfaces.api.storage.requirements_session_store import InMemoryRequirementsSessionStore
from budgettrip.interfaces.api.storage.trip_store import InMemoryTripStore

router = APIRouter(prefix="/api/v1/chat", tags=["chat"])


@router.post("", response_model=ChatResponseDTO)
@limiter.limit("30/minute")
async def chat_requirements(
    request: Request,
    payload: ChatRequestDTO,
    _: None = Depends(verify_api_key),
    session_store: InMemoryRequirementsSessionStore = Depends(get_requirements_session_store),
) -> ChatResponseDTO:
    agent = build_requirements_agent()
    session_id = payload.session_id or session_store.create_session_id()
    previous_state = session_store.get(session_id) if payload.session_id else None
    history = [(message.role, message.content) for message in payload.history]
    turn = await agent.process_message(
        payload.message,
        history=history or None,
        previous_state=previous_state,
    )
    session_store.save(session_id, turn)
    return ChatResponseDTO.from_requirements_turn(turn, session_id=session_id)


@router.post("/confirm", response_model=TripCreatedResponseDTO)
@limiter.limit("10/minute")
async def confirm_and_plan_trip(
    request: Request,
    payload: ConfirmTripRequestDTO,
    _: None = Depends(verify_api_key),
    trip_store: InMemoryTripStore = Depends(get_trip_store),
) -> TripCreatedResponseDTO:
    use_case = build_plan_trip_use_case()
    itinerary = await use_case.execute(
        payload.trip.to_domain(),
        send_email=payload.send_email,
    )
    trip_id = trip_store.save(itinerary)
    return TripCreatedResponseDTO(
        id=trip_id,
        itinerary=ItineraryResponseDTO.from_domain(itinerary),
    )
