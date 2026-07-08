from fastapi import HTTPException, Request, status


def validate_api_key(api_key: str | None, expected_key: str) -> bool:
    return bool(api_key) and api_key == expected_key


async def require_api_key(request: Request, expected_key: str) -> None:
    api_key = request.headers.get("X-API-Key")
    if not validate_api_key(api_key, expected_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )
