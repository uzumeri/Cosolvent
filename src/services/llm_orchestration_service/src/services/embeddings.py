from typing import List
import hashlib
import random
import os

from ..config.store import get_config
from ..providers import get_client as get_llm_provider_client
from ..config.models import AppConfig, ServiceConfig, ProviderConfig
from ..core.logging import get_logger

logger = get_logger(__name__)


async def create_embedding(text: str, service_name: str = "embeddings") -> List[float]:
    """
    Generate an embedding vector for the given text using the configured provider for the embeddings service.
    """
    app_config: AppConfig = await get_config()

    if service_name not in app_config.services:
        logger.error(f"Service configuration for '{service_name}' not found.")
        raise ValueError(f"Service '{service_name}' is not configured. Please add it to config.json.")

    service_cfg: ServiceConfig = app_config.services[service_name]
    client_cfg = app_config.clients.get(service_cfg.client)
    if not client_cfg:
        raise ValueError(f"Client '{service_cfg.client}' is not configured.")

    provider_cfg: ProviderConfig | None = client_cfg.providers.get(service_cfg.provider)
    if not provider_cfg:
        raise ValueError(f"Provider '{service_cfg.provider}' is not configured.")

    opts = service_cfg.options or {}
    llm_params = (opts.get("llm_params") or {})
    # dimensions may be provided in options.llm_params.dimensions
    dimensions = llm_params.get("dimensions")

    def _fallback_vec(txt: str, dim_hint: int | None) -> List[float]:
        dim = int(dim_hint or 1536)
        seed_int = int(hashlib.sha256(txt.encode('utf-8')).hexdigest(), 16) % (2**31 - 1)
        rng = random.Random(seed_int)
        vec = [rng.uniform(-1.0, 1.0) for _ in range(dim)]
        norm = sum(x*x for x in vec) ** 0.5 or 1.0
        return [x / norm for x in vec]

    mode = (os.getenv("EMBEDDINGS_MODE") or "fallback").lower()
    if mode != "provider":
        # Immediate deterministic fallback mode
        logger.info(f"EMBEDDINGS_MODE={mode}. Returning deterministic fallback embedding.")
        return _fallback_vec(text, dimensions)

    try:
        client = await get_llm_provider_client(service_cfg.client, provider_cfg)
        vectors = await client.create_embedding([text], dimensions=dimensions)
        if not vectors:
            raise ValueError("No embedding returned from provider")
        return vectors[0]
    except Exception as e:
        logger.warning("Provider embeddings failed; falling back to deterministic vector: %s", e)
        return _fallback_vec(text, dimensions)
