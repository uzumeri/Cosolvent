# services/metadata_extraction.py
from ..config.store import get_config
from ..providers import get_client as get_llm_provider_client
from ..config.models import AppConfig, ServiceConfig, ProviderConfig
from ..core.logging import get_logger
from fastapi import UploadFile
import mimetypes
import asyncio

logger = get_logger(__name__)

# Placeholder for a function that would convert image to text (e.g., using an OCR or image-to-text model)
async def image_to_text(file_content: bytes, provider_config: ProviderConfig, llm_client) -> str:
    logger.info("Attempting to convert image to text (placeholder).")
    # In a real implementation, you would use a specific model/service for this.
    # This might involve another call to an LLM or a specialized vision service.
    # For now, this is a placeholder.
    # Example: return await llm_client.call_model(prompt="Describe this image.", image_bytes=file_content)
    # This depends heavily on the capabilities of the chosen llm_client and provider_config.
    if provider_config.model:
        # This is a conceptual example; actual VLM call would encode image bytes in the message content.
        # The `call_model` is already able to handle multimodal inputs for compatible providers.
        # For now, we simulate this by returning a descriptive string.
        logger.warning("Image-to-text placeholder used. Implement a proper VLM call if needed.")
        return "[Placeholder: Textual description of an image that was processed by a vision model]"
    return "[Placeholder image content as text: a cat sitting on a mat]"

# Placeholder for a function that would convert audio/video to text (Speech-to-Text)
async def speech_to_text(file_content: bytes, provider_config: ProviderConfig, llm_client) -> str:
    logger.info("Attempting to convert speech to text (placeholder).")
    # Use a specific STT model/service if available (e.g., Whisper via another provider)
    # Example: return await llm_client.call_stt_model(audio_bytes=file_content)
    # This also depends on the llm_client supporting such calls or using a separate client.
    if provider_config.model:
        logger.warning("Speech-to-text placeholder used. Implement a proper STT call if needed.")
        return "[Placeholder: Transcribed text from an audio/video file using a speech-to-text model like Whisper]"
    return "[Placeholder audio content as text: Hello world, this is a test.]"

async def extract_textual_metadata_from_file(file: UploadFile, service_name: str = "metadata_extraction") -> str:
    logger.info(f"Metadata extraction service called for file: {file.filename}, type: {file.content_type}")
    app_config: AppConfig = await get_config()

    service_cfg: ServiceConfig = app_config.services.get(service_name)
    if not service_cfg:
        logger.error(f"Service configuration for '{service_name}' not found.")
        raise ValueError(f"Service '{service_name}' is not configured.")

    opts = service_cfg.options or {}
    file_content = await file.read()
    text_content_for_llm = ""

    mime_type = file.content_type
    if not mime_type and file.filename:
        mime_type, _ = mimetypes.guess_type(file.filename)

    proc_cfg = {}
    client_cfg = app_config.clients[service_cfg.client]
    if mime_type:
        if mime_type.startswith("image/"):
            logger.info(f"Processing image file: {file.filename}")
            proc_cfg = opts.get("image_processing", {})
            vlm_provider = proc_cfg.get("vlm_provider")
            if vlm_provider and vlm_provider in client_cfg.providers:
                vlm_provider_cfg = client_cfg.providers[vlm_provider]
                vlm_client = await get_llm_provider_client(service_cfg.client, vlm_provider_cfg)
                vlm_template = proc_cfg.get("vlm_prompt_template", "")
                vlm_params = proc_cfg.get("vlm_params", {})
                vlm_prompt = vlm_template.format(file_name=file.filename)
                text_content_for_llm = await vlm_client.call_model(vlm_prompt, image_bytes=file_content, **vlm_params)
            else:
                text_content_for_llm = "[Placeholder: VLM provider not configured]"

    if not text_content_for_llm:
        logger.warning("No text content was extracted from the file. Cannot proceed.")
        return "{}"

    logger.info("Extracted text content, now calling LLM for metadata extraction.")

    metadata_llm_provider_name = proc_cfg.get("metadata_llm_provider") or service_cfg.provider
    metadata_llm_provider_cfg = client_cfg.providers.get(metadata_llm_provider_name)
    if not metadata_llm_provider_cfg:
        raise ValueError(f"Provider '{metadata_llm_provider_name}' for metadata extraction is not configured.")

    metadata_llm_client = await get_llm_provider_client(service_cfg.client, metadata_llm_provider_cfg)
    metadata_llm_template = proc_cfg.get("metadata_llm_prompt_template", "{text}")
    final_prompt = metadata_llm_template.format(vlm_output=text_content_for_llm, file_name=file.filename)
    metadata_llm_params = proc_cfg.get("metadata_llm_params", {})

    metadata_response = await metadata_llm_client.call_model(final_prompt, **metadata_llm_params)
    
    logger.info("Successfully extracted metadata.")
    return metadata_response
