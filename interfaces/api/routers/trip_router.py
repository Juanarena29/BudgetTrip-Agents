from fastapi import APIRouter, Depends, HTTPException, Request, WebSocket, status

from budgettrip.infrastructure.factory import build_plan_trip_use_case
from budgettrip.infrastructure.notifications.websocket_reporter import WebSocketReporter
from budgettrip.interfaces.api.dependencies import (
    get_settings_dep,
    get_trip_store,
    verify_api_key,
)
from budgettrip.interfaces.api.schemas.trip_dto import (
    CreateTripRequestDTO,
    ItineraryResponseDTO,
    TripCreatedResponseDTO,
)
from budgettrip.interfaces.api.security.api_key_auth import validate_api_key
from budgettrip.interfaces.api.security.rate_limit import limiter
from budgettrip.interfaces.api.storage.trip_store import InMemoryTripStore

router = APIRouter(prefix="/api/v1", tags=["trips"])


@router.post("/trips", response_model=TripCreatedResponseDTO)
@limiter.limit("10/minute")
async def create_trip(
    request: Request,
    payload: CreateTripRequestDTO,
    _: None = Depends(verify_api_key),
    trip_store: InMemoryTripStore = Depends(get_trip_store),
) -> TripCreatedResponseDTO:
    use_case = build_plan_trip_use_case()
    itinerary = await use_case.execute(
        payload.to_domain(),
        send_email=payload.send_email,
    )
    trip_id = trip_store.save(itinerary)
    return TripCreatedResponseDTO(
        id=trip_id,
        itinerary=ItineraryResponseDTO.from_domain(itinerary),
    )


@router.get("/trips/{trip_id}", response_model=ItineraryResponseDTO)
async def get_trip(
    trip_id: str,
    _: None = Depends(verify_api_key),
    trip_store: InMemoryTripStore = Depends(get_trip_store),
) -> ItineraryResponseDTO:
    itinerary = trip_store.get(trip_id)
    if itinerary is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found",
        )
    return ItineraryResponseDTO.from_domain(itinerary)


@router.websocket("/trips/stream")
async def trip_stream(websocket: WebSocket) -> None:
    settings = get_settings_dep()
    await websocket.accept()

    if not settings.api_secret_key or not validate_api_key(
        websocket.query_params.get("api_key"),
        settings.api_secret_key,
    ):
        await websocket.close(code=4401)
        return

    try:
        data = await websocket.receive_json()
        payload = CreateTripRequestDTO.model_validate(data)
    except Exception:
        await websocket.close(code=4400)
        return

    reporter = WebSocketReporter(websocket)
    use_case = build_plan_trip_use_case(reporter=reporter)

    try:
        itinerary = await use_case.execute(
            payload.to_domain(),
            send_email=payload.send_email,
        )
        await websocket.send_json(
            {
                "status": "done",
                "itinerary": ItineraryResponseDTO.from_domain(itinerary).model_dump(mode="json"),
            }
        )
    except Exception as exc:
        await websocket.send_json({"status": "error", "detail": str(exc)})
    finally:
        await websocket.close()
