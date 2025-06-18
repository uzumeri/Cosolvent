# services/profile_generation.py
import json
from ..config.store import get_config
from ..providers import get_client as get_llm_provider_client
from ..config.models import AppConfig, ServiceConfig, ProviderConfig, ExporterProfileSchema, ImporterProfileSchema, ProfileType
from ..core.logging import get_logger
from typing import List, Dict, Any

logger = get_logger(__name__)

async def generate_structured_profile(texts: List[str], service_name: str = "profile_generation", profile_type: str = "exporter") -> Dict[str, Any]:
    logger.info(f"Profile generation service called with {len(texts)} text inputs for service '{service_name}' and profile_type '{profile_type}'.")
    app_config: AppConfig = await get_config()

    if service_name not in app_config.services:
        logger.error(f"Service configuration for '{service_name}' not found.")
        raise ValueError(f"Service '{service_name}' is not configured.")

    service_cfg: ServiceConfig = app_config.services[service_name]
    provider_cfg: ProviderConfig = app_config.clients[service_cfg.client].providers[service_cfg.provider]
    client = await get_llm_provider_client(service_cfg.client, provider_cfg)

    # Prepare options
    opts = service_cfg.options or {}
    # Concatenate input texts
    combined_text = "\n\n---\n\n".join(texts)
    # Respect max_input_text_length if provided
    max_len = opts.get("max_input_text_length", 3000)
    if len(combined_text) > max_len:
        logger.warning(f"Combined text length ({len(combined_text)}) exceeds limit ({max_len}). Truncating.")
        combined_text = combined_text[:max_len]

    # Select schema based on profile_type
    if profile_type == ProfileType.EXPORTER:
        schema_model = ExporterProfileSchema
    elif profile_type == ProfileType.IMPORTER:
        schema_model = ImporterProfileSchema
    else:
        logger.error(f"Invalid profile_type: {profile_type}")
        return {"error": "Invalid profile_type", "details": profile_type}
    schema_description = json.dumps(schema_model.schema(), indent=2)

    # Build prompt using configured template or default
    prompt_tpl = opts.get("prompt_template")
    if prompt_tpl:
        try:
            prompt = prompt_tpl.format(profile_schema=schema_description, texts_concatenated=combined_text)
        except Exception:
            logger.warning("Failed to format prompt_template for profile_generation; using default prompt.")
            prompt = f"JSON Schema:\n{schema_description}\nTexts:\n{combined_text}\nExtract JSON Profile:"
    else:
        prompt = (
            f"You are an expert data extractor. Based on the following text segments, please extract information "
            f"and structure it according to the JSON schema provided below. Only return a valid JSON object "
            f"that conforms to this schema. If certain information is not found, use null or omit the field if appropriate "
            f"according to the schema's requirements (e.g., if not required).\n\n"
            f"JSON Schema to follow:\n{schema_description}\n\n"
            f"Text segments to analyze:\n{combined_text}\n\n"
            f"Extracted JSON Profile:"
        )

    # Extract LLM parameters
    llm_params = opts.get("llm_params", {})
    raw_llm_output = await client.call_model(prompt, **llm_params)
    logger.info(f"Raw LLM output for profile generation: {raw_llm_output[:100]}...")

    try:
        cleaned_output = raw_llm_output.strip()
        if cleaned_output.startswith("```json"):
            cleaned_output = cleaned_output[7:]
        if cleaned_output.startswith("```"):
            cleaned_output = cleaned_output[3:]
        if cleaned_output.endswith("```"):
            cleaned_output = cleaned_output[:-3]
        profile_json = json.loads(cleaned_output.strip())
        profile_obj = schema_model.parse_obj(profile_json)
        logger.info("Profile generation successful and parsed to schema model.")
        return profile_obj.dict()
    except Exception as e:
        logger.error(f"Failed to parse or validate LLM output as profile schema: {e}")
        return {
            "error": "Failed to parse or validate LLM output as profile schema.",
            "details": str(e),
            "raw_output": raw_llm_output
        }

