from functools import lru_cache
try:
    from src.core.config import settings as _shared_settings
except Exception:
    class _Shim:
        DATABASE_URL = "postgresql://cosolvent:cosolvent@postgres:5432/cosolvent"
    _shared_settings = _Shim()  


class AppSettings:
    def __init__(self):
        self.database_url: str = getattr(_shared_settings, "DATABASE_URL", "postgresql://cosolvent:cosolvent@postgres:5432/cosolvent")


@lru_cache
def get_settings() -> AppSettings:
    return AppSettings()
