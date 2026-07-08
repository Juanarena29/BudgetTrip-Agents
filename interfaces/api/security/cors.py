from fastapi.middleware.cors import CORSMiddleware
from starlette.applications import Starlette


def configure_cors(app: Starlette, allowed_origins: list[str]) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
