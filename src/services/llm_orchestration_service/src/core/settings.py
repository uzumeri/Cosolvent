from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class AppSettings(BaseSettings):
    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_db: str = "llm_orchestration"
    mongodb_collection: str = "config"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

@lru_cache
def get_settings() -> AppSettings:
    return AppSettings()
