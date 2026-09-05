import logging
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Setting(BaseSettings):
    ephemeris_path: Path = Path("/data/ephemeris")
    database_url: str = "postgresql://astrogyia:astrogyia@localhost:5432/astrogyia"
    jwt_secret_key: str  # Required: set JWT_SECRET_KEY env var
    allowed_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]
    log_level: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Setting()

# Configure logging — reset tokens only appear at DEBUG level
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
