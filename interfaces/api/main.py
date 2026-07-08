from fastapi import FastAPI
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi import _rate_limit_exceeded_handler

from budgettrip.infrastructure.config import get_settings
from budgettrip.interfaces.api.routers.chat_router import router as chat_router
from budgettrip.interfaces.api.routers.trip_router import router as trip_router
from budgettrip.interfaces.api.security.cors import configure_cors
from budgettrip.interfaces.api.security.rate_limit import limiter
from budgettrip.interfaces.api.storage.requirements_session_store import InMemoryRequirementsSessionStore
from budgettrip.interfaces.api.storage.trip_store import InMemoryTripStore


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="BudgetTrip API", version="0.1.0")
    app.state.limiter = limiter
    app.state.trip_store = InMemoryTripStore()
    app.state.requirements_session_store = InMemoryRequirementsSessionStore()
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)

    configure_cors(app, settings.allowed_origins)
    app.include_router(chat_router)
    app.include_router(trip_router)

    @app.get("/api/v1/health")
    async def healthcheck() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
