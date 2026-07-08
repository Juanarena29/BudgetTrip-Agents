from fastapi import Depends, Header, HTTPException, Request, status

from budgettrip.infrastructure.config import Settings, get_settings
from budgettrip.interfaces.api.security.api_key_auth import validate_api_key
from budgettrip.interfaces.api.storage.requirements_session_store import InMemoryRequirementsSessionStore
from budgettrip.interfaces.api.storage.trip_store import InMemoryTripStore


def get_settings_dep() -> Settings:
    return get_settings()


async def verify_api_key(
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    settings: Settings = Depends(get_settings_dep),
) -> None:
    if not settings.api_secret_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="API key authentication is not configured",
        )
    if not validate_api_key(x_api_key, settings.api_secret_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )


def get_trip_store(request: Request) -> InMemoryTripStore:
    return request.app.state.trip_store


def get_requirements_session_store(request: Request) -> InMemoryRequirementsSessionStore:
    return request.app.state.requirements_session_store
