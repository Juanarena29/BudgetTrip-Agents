from dataclasses import dataclass
from functools import lru_cache

from dotenv import load_dotenv
import os

load_dotenv()


@dataclass(frozen=True)
class Settings:
    openai_api_key: str
    api_secret_key: str
    allowed_origins: list[str]
    smtp_host: str
    smtp_port: int
    smtp_user: str
    smtp_password: str
    how_many_searches: int
    model_name: str


@lru_cache
def get_settings() -> Settings:
    return Settings(
        openai_api_key=os.getenv("OPENAI_API_KEY", ""),
        api_secret_key=os.getenv("API_SECRET_KEY", ""),
        allowed_origins=[
            origin.strip()
            for origin in os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
            if origin.strip()
        ],
        smtp_host=os.getenv("SMTP_HOST", ""),
        smtp_port=int(os.getenv("SMTP_PORT", "587")),
        smtp_user=os.getenv("SMTP_USER", ""),
        smtp_password=os.getenv("SMTP_PASSWORD", ""),
        how_many_searches=int(os.getenv("HOW_MANY_SEARCHES", "8")),
        model_name=os.getenv("MODEL_NAME", "gpt-5.4-mini"),
    )
