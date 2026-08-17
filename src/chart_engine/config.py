from pathlib import Path

from pydantic_settings import BaseSettings

class Setting(BaseSettings):
    ephemeris_path: Path = Path("/data/ephemeris")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Setting()