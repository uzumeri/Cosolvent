from ..config.models import AppConfig, ClientConfig
from typing import Optional, Any
from pydantic import BaseModel

def mask_value(val: Any) -> Any:
    if isinstance(val, str):
        n = len(val)
        if n <= 8:
            return '*' * n
        return val[:4] + '*' * (n - 8) + val[-4:]
    return val

def mask_sensitive_fields(obj: Any) -> Any:
    """
    Recursively mask sensitive fields (like api_key, secret, token) in dicts, lists, and pydantic models.
    """
    if isinstance(obj, BaseModel):
        data = obj.model_dump()
        return obj.__class__(**mask_sensitive_fields(data))
    elif isinstance(obj, dict):
        masked = {}
        for k, v in obj.items():
            if k.lower() in {"api_key", "apikey", "token", "secret", "password"} and isinstance(v, str):
                masked[k] = mask_value(v)
            else:
                masked[k] = mask_sensitive_fields(v)
        return masked
    elif isinstance(obj, list):
        return [mask_sensitive_fields(i) for i in obj]
    return obj

def mask_providers_api_keys(cfg: AppConfig) -> AppConfig:
    """Return AppConfig with provider api_key partially masked."""
    def _mask_key(key: Optional[str]) -> Optional[str]:
        if not key:
            return None
        n = len(key)
        if n <= 8:
            return '*' * n
        return key[:4] + '*' * (n - 8) + key[-4:]

    masked_clients = {}
    for client_name, client_config in cfg.clients.items():
        masked_providers = {}
        for name, pc in client_config.providers.items():
            masked_providers[name] = pc.copy(update={"api_key": _mask_key(pc.api_key)})
        masked_clients[client_name] = ClientConfig(providers=masked_providers)

    return cfg.copy(update={"clients": masked_clients})
