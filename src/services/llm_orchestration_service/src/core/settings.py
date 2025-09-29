from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class AppSettings(BaseSettings):
    database_url: str = "postgresql://cosolvent:cosolvent@postgres:5432/cosolvent"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> AppSettings:
    return AppSettings()
