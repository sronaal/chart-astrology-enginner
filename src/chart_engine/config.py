from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

class Setting(BaseSettings):
    ephemeris_path: Path = Path("/data/ephemeris")
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Setting()