import base64
import io
from typing import Any, Dict, List, Union

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from .base import LLMClient
from ..config.models import ProviderConfig
from ..core.exceptions import LLMApiException, ConfigurationException
from ..core.logging import get_logger

logger = get_logger(__name__)

MessageContentPart = Union[Dict[str, str], Dict[str, Any]]


class OpenRouterClient(LLMClient):
    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        api_key = (self.config.api_key or "").strip()
        if not api_key or api_key.endswith("_PLACEHOLDER"):
            import os
            api_key = os.getenv("OPENROUTER_API_KEY", "").strip()
        if not api_key:
            raise ConfigurationException("OpenRouter API key missing. Set it in DB provider config or OPENROUTER_API_KEY env var.")
        # OpenRouter provides an OpenAI-compatible API
        # Trailing slash is important so relative paths like "embeddings" join to "/api/v1/embeddings"
        self.base_url = "https://openrouter.ai/api/v1/"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "HTTP-Referer": "https://cosolvent.app",
            "X-Title": "Cosolvent",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "Cosolvent-Orchestrator/1.0 (+https://cosolvent.app)",
            # Some proxies/CDNs prefer the standard header as well
            "Referer": "https://cosolvent.app",
        }
        # Single shared async client
        self._client = httpx.AsyncClient(base_url=self.base_url, headers=self.headers, timeout=60, follow_redirects=False)

    async def _post(self, path: str, json: Dict[str, Any]) -> Dict[str, Any]:
        # Ensure relative path join to base_url (avoid leading '/')
        safe_path = path.lstrip('/')
        resp = await self._client.post(safe_path, json=json)
        # Detect unexpected redirects to HTML pages (website login/landing)
        if 300 <= resp.status_code < 400:
            loc = resp.headers.get("location")
            raise LLMApiException(self.config.name, Exception(f"Unexpected redirect ({resp.status_code}) to {loc} for {safe_path}"))
        if resp.status_code >= 400:
            raise LLMApiException(self.config.name, Exception(f"HTTP {resp.status_code}: {resp.text[:500]}"))
        ct = (resp.headers.get("content-type") or "").lower()
        # Some providers occasionally mislabel or send blank-but-JSON-typed bodies; guard strictly.
        if "application/json" not in ct:
            body = resp.text[:500] if hasattr(resp, "text") else "<no body>"
            raise LLMApiException(self.config.name, Exception(f"Non-JSON response from OpenRouter ({ct}). Body: {body}"))
        text_body = resp.text if hasattr(resp, "text") else ""
        if text_body is None or text_body.strip() == "":
            raise LLMApiException(self.config.name, Exception("Empty JSON response body from OpenRouter (whitespace-only)."))
        try:
            return resp.json()
        except Exception as json_err:
            # Include headers and a snippet of the body for diagnostics
            snippet = text_body[:500]
            raise LLMApiException(self.config.name, Exception(f"Failed to parse JSON response (ct={ct}): {json_err}. Body: {snippet}"))

    @retry(reraise=True, stop=stop_after_attempt(2), wait=wait_exponential(multiplier=1, min=1, max=5))
    async def create_embedding(self, input_texts: List[str], dimensions: int | None = None, **kwargs: Any) -> List[List[float]]:
        # Some providers misbehave when dimensions is included. Omit to use the model default (e.g., 1536 for text-embedding-3-small).
        # For maximum compatibility with OpenAI schema, always send a list of inputs.
        input_payload: Any = list(input_texts)
        payload: Dict[str, Any] = {"model": self.config.model, "input": input_payload, "encoding_format": "float"}
        # Intentionally not including 'dimensions' to maximize compatibility across OpenRouter providers.
        payload.update({k: v for k, v in kwargs.items() if v is not None})
        data = await self._post("/embeddings", json=payload)
        # Validate expected shape: { data: [ { embedding: [...] }, ... ] }
        if not isinstance(data, dict) or not isinstance(data.get("data"), list):
            raise LLMApiException(self.config.name, Exception(f"Unexpected embeddings response shape: keys={list(data.keys()) if isinstance(data, dict) else type(data)}"))
        try:
            return [item["embedding"] for item in data.get("data", [])]
        except Exception as e:
            raise LLMApiException(self.config.name, Exception(f"Embeddings missing 'embedding' field: {e}. First item: {data.get('data')[0] if data.get('data') else None}"))

    def _build_messages(self, prompt: str, image_bytes: bytes | None) -> List[Dict[str, Any]]:
        parts: List[MessageContentPart] = [{"type": "text", "text": prompt}]
        if image_bytes:
            b64 = base64.b64encode(image_bytes).decode("utf-8")
            parts.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{b64}"}
            })
        return [{"role": "user", "content": parts}]  # multimodal message per Chat Completions schema

    @retry(reraise=True, stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def call_model(self, prompt: str, **kwargs: Any) -> str:
        logger.info(f"Calling OpenRouter model '{self.config.model}'")
        image_bytes: bytes | None = kwargs.pop("image_bytes", None)
        payload = {
            "model": self.config.model,
            "messages": self._build_messages(prompt, image_bytes),
        }
        payload.update({k: v for k, v in kwargs.items() if v is not None})
        try:
            data = await self._post("/chat/completions", json=payload)
            content = data.get("choices", [{}])[0].get("message", {}).get("content")
            if not content:
                raise LLMApiException(self.config.name, Exception("No content in response"))
            return content
        except Exception as e:
            logger.error(f"OpenRouter call failed: {e}")
            raise LLMApiException(self.config.name, e)

    async def call_vision_model(self, prompt: str, image_bytes: bytes, **kwargs: Any) -> str:
        return await self.call_model(prompt, image_bytes=image_bytes, **kwargs)

    @retry(reraise=True, stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def call_stt_model(self, audio_bytes: bytes, filename: str = "audio.mp3", **kwargs: Any) -> str:
        # OpenRouter doesn't offer Whisper; route via regular prompt if configured for ASR, else raise
        raise ConfigurationException("Speech-to-text via OpenRouter is not supported in this implementation")
