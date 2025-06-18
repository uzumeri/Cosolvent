# routes/config.py
from fastapi import APIRouter, HTTPException, Path, Body
from ..config.models import AppConfig, ClientConfig, ProviderConfig, ClientName, ServiceConfig # Use .. to go up one level to src, then to config
from ..config import store as config_store # Use .. to go up one level to src, then to config
from ..core.logging import get_logger
from fastapi.responses import JSONResponse
from ..utils.service_utils import mask_sensitive_fields

router = APIRouter()
logger = get_logger(__name__)

@router.get("", response_model=AppConfig)
async def read_config_endpoint(): # Renamed to avoid conflict with imported `config` module
    """Returns the full AppConfig tree.
    Credentials in ProviderConfig should ideally be masked if sensitive.
    This example does not implement masking.
    """
    logger.info("GET /config endpoint called")
    try:
        current_config = await config_store.get_all()
        return mask_sensitive_fields(current_config)
    except Exception as e:
        logger.exception("Error reading configuration")
        raise HTTPException(status_code=500, detail=f"Error reading configuration: {e}")

@router.put("", response_model=AppConfig)
async def update_config_endpoint(new_config: AppConfig): # Renamed to avoid conflict
    """
    Accepts a new AppConfig document, enabling on-the-fly updates.
    """
    logger.info("PUT /config endpoint called")
    try:
        updated_config = await config_store.update(new_config)
        logger.info("Configuration updated successfully.")
        return mask_sensitive_fields(updated_config)
    except Exception as e:
        logger.exception("Error updating configuration")
        raise HTTPException(status_code=500, detail=f"Error updating configuration: {e}")

@router.patch("", response_model=AppConfig)
async def patch_config_endpoint(patch_data: dict):
    """
    Partially update the AppConfig by merging provided fields.
    """
    logger.info("PATCH /config endpoint called")
    try:
        updated_config = await config_store.patch_config(patch_data)
        logger.info("Configuration patched successfully.")
        return mask_sensitive_fields(updated_config)
    except Exception as e:
        logger.exception("Error patching configuration")
        raise HTTPException(status_code=500, detail=f"Error patching configuration: {e}")

@router.get("/clients", response_model=list[ClientName])
async def list_clients():
    """List available clients (enum-based, no CRUD)."""
    return list(ClientName)

@router.get("/clients/{client}/providers", response_model=dict)
async def list_providers(client: ClientName = Path(...)):
    cfg = await config_store.get_all()
    if client not in cfg.clients:
        raise HTTPException(status_code=404, detail="Client not found")
    return mask_sensitive_fields(cfg.clients[client].providers)

@router.post("/clients/{client}/providers", response_model=ProviderConfig)
async def create_provider(client: ClientName, provider: ProviderConfig):
    cfg = await config_store.get_all()
    if client not in cfg.clients:
        raise HTTPException(status_code=404, detail="Client not found")
    if provider.name in cfg.clients[client].providers:
        raise HTTPException(status_code=400, detail="Provider already exists")
    cfg.clients[client].providers[provider.name] = provider
    await config_store.update(cfg)
    return mask_sensitive_fields(provider)

@router.get("/clients/{client}/providers/{provider}", response_model=ProviderConfig)
async def get_provider(client: ClientName, provider: str):
    cfg = await config_store.get_all()
    if client not in cfg.clients:
        raise HTTPException(status_code=404, detail="Client not found")
    prov = cfg.clients[client].providers.get(provider)
    if not prov:
        raise HTTPException(status_code=404, detail="Provider not found")
    return mask_sensitive_fields(prov)

@router.put("/clients/{client}/providers/{provider}", response_model=ProviderConfig)
async def update_provider(client: ClientName, provider: str, update: ProviderConfig):
    cfg = await config_store.get_all()
    if client not in cfg.clients:
        raise HTTPException(status_code=404, detail="Client not found")
    if provider not in cfg.clients[client].providers:
        raise HTTPException(status_code=404, detail="Provider not found")
    cfg.clients[client].providers[provider] = update
    await config_store.update(cfg)
    return mask_sensitive_fields(update)

@router.delete("/clients/{client}/providers/{provider}")
async def delete_provider(client: ClientName, provider: str):
    cfg = await config_store.get_all()
    if client not in cfg.clients:
        raise HTTPException(status_code=404, detail="Client not found")
    if provider not in cfg.clients[client].providers:
        raise HTTPException(status_code=404, detail="Provider not found")
    del cfg.clients[client].providers[provider]
    await config_store.update(cfg)
    return JSONResponse(content={"detail": "Provider deleted"})

@router.get("/services", response_model=dict)
async def list_services():
    """List all services."""
    cfg = await config_store.get_all()
    return cfg.services

@router.post("/services", response_model=ServiceConfig)
async def create_service(service: ServiceConfig, name: str = Body(...)):
    """Create a new service."""
    cfg = await config_store.get_all()
    if name in cfg.services:
        raise HTTPException(status_code=400, detail="Service already exists")
    cfg.services[name] = service
    await config_store.update(cfg)
    return service

@router.get("/services/{service}", response_model=ServiceConfig)
async def get_service(service: str):
    cfg = await config_store.get_all()
    svc = cfg.services.get(service)
    if not svc:
        raise HTTPException(status_code=404, detail="Service not found")
    return svc

@router.put("/services/{service}", response_model=ServiceConfig)
async def update_service(service: str, update: ServiceConfig):
    cfg = await config_store.get_all()
    if service not in cfg.services:
        raise HTTPException(status_code=404, detail="Service not found")
    cfg.services[service] = update
    await config_store.update(cfg)
    return update

@router.delete("/services/{service}")
async def delete_service(service: str):
    cfg = await config_store.get_all()
    if service not in cfg.services:
        raise HTTPException(status_code=404, detail="Service not found")
    del cfg.services[service]
    await config_store.update(cfg)
    return JSONResponse(content={"detail": "Service deleted"})

@router.patch("/services/{service}/prompt_templates")
async def update_service_prompt_templates(service: str, prompt_templates: dict):
    cfg = await config_store.get_all()
    svc = cfg.services.get(service)
    if not svc:
        raise HTTPException(status_code=404, detail="Service not found")
    if not svc.options or "prompt_templates" not in svc.options:
        raise HTTPException(status_code=400, detail="Service does not support prompt_templates")
    svc.options["prompt_templates"].update(prompt_templates)
    cfg.services[service] = svc
    await config_store.update(cfg)
    return svc.options["prompt_templates"]

@router.patch("/services/{service}/llm_params")
async def update_service_llm_params(service: str, llm_params: dict):
    cfg = await config_store.get_all()
    svc = cfg.services.get(service)
    if not svc:
        raise HTTPException(status_code=404, detail="Service not found")
    if not svc.options or "llm_params" not in svc.options:
        raise HTTPException(status_code=400, detail="Service does not support llm_params")
    svc.options["llm_params"].update(llm_params)
    cfg.services[service] = svc
    await config_store.update(cfg)
    return svc.options["llm_params"]

@router.get("/services/list", response_model=list)
async def get_services_list():
    """Return a list of all service names."""
    cfg = await config_store.get_all()
    return list(cfg.services.keys())
