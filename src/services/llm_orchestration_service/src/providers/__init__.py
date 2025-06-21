# providers/__init__.py
from typing import Dict, Type
from .base import LLMClient
from .openai_client import OpenAIClient
from ..config.models import ProviderConfig, ClientName
from ..core.exceptions import ProviderNotFoundException

# Registry of available provider clients
_provider_clients: Dict[ClientName, Type[LLMClient]] = {
    ClientName.OPENAI: OpenAIClient,
}

# Cache for instantiated clients to reuse them
_client_instances: Dict[str, LLMClient] = {}

async def get_client(client_name: ClientName, config: ProviderConfig) -> LLMClient:
    """
    Factory function to get an initialized LLM client instance.
    Caches instances to avoid re-initializing on every call.
    """
    instance_key = f"{client_name.value}_{config.name}"

    if instance_key in _client_instances:
        # TODO: Add logic to check if config has changed and re-initialize if necessary
        return _client_instances[instance_key]

    if client_name not in _provider_clients:
        raise ProviderNotFoundException(client_name.value)

    client_class = _provider_clients[client_name]
    # Pass the specific provider_config to the client constructor
    instance = client_class(config=config)
    _client_instances[instance_key] = instance
    return instance

def register_provider(name: str, client_class: Type[LLMClient]):
    """Allows dynamic registration of new providers."""
    # This function might need adjustment if used with the new Enum-based client names
    pass

# Example of how services might get a client:
# from ..config.store import get_config
# from . import get_client
# async def some_service_function():
#     app_config = await get_config()
#     # Assuming 'translate' service uses 'openai' provider as per AppConfig
#     service_conf = app_config.services["translate"]
#     provider_conf = app_config.providers[service_conf.provider]
#     client = await get_client(service_conf.provider, provider_conf)
#     # Now use the client
