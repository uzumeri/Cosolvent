from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from uuid import UUID
import asyncpg

from src.database.crud import template_crud
from src.schema.template_schema import (
    TemplateCreate,
    TemplateUpdate,
    TemplateResponse,
)
from src.schema.profile_schema import SuccessResponse
from src.database.db import get_db

router = APIRouter(prefix="/admin/templates", tags=["Templates"])

@router.post("", response_model=TemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_new_template(template: TemplateCreate, db: asyncpg.Pool = Depends(get_db)):
    """
    Create a new template.
    """
    created = await template_crud.create_template(db, template)
    return TemplateResponse(**created.model_dump())

@router.get("", response_model=List[TemplateResponse])
async def get_all_templates_admin(db: asyncpg.Pool = Depends(get_db)):
    """
    Retrieve all templates.
    """
    items = await template_crud.get_all_templates(db)
    return [TemplateResponse(**i.model_dump()) for i in items]

@router.get("/active", response_model=TemplateResponse)
async def get_active_template_user(db: asyncpg.Pool = Depends(get_db)):
    """
    Get the active template.
    """
    active_template = await template_crud.get_active_template(db)
    if not active_template:
        raise HTTPException(status_code=404, detail="No active template found")
    return TemplateResponse(**active_template.model_dump())

@router.get("/{template_id}", response_model=TemplateResponse)
async def get_template_by_id_admin(template_id: UUID, db: asyncpg.Pool = Depends(get_db)):
    """
    Retrieve a single template by its ID.
    """
    template = await template_crud.get_template_by_id(db, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return TemplateResponse(**template.model_dump())

@router.put("/{template_id}", response_model=TemplateResponse)
async def update_template_admin(template_id: UUID, template_update: TemplateUpdate, db: asyncpg.Pool = Depends(get_db)):
    """
    Update a template.
    """
    updated_template = await template_crud.update_template(db, template_id, template_update)
    if not updated_template:
        raise HTTPException(status_code=404, detail="Template not found")
    return TemplateResponse(**updated_template.model_dump())

@router.delete("/{template_id}", response_model=SuccessResponse)
async def delete_template_admin(template_id: UUID, db: asyncpg.Pool = Depends(get_db)):
    """
    Delete a template.
    """
    if await template_crud.delete_template(db, template_id):
        return {"success": True, "message": "Template deleted successfully."}
    raise HTTPException(status_code=404, detail="Template not found")

@router.post("/{template_id}/set-active", response_model=TemplateResponse)
async def set_active_template_admin(template_id: UUID, db: asyncpg.Pool = Depends(get_db)):
    """
    Set a template as the active one.
    """
    active_template = await template_crud.set_active_template(db, template_id)
    if not active_template:
        raise HTTPException(status_code=404, detail="Template not found")
    return TemplateResponse(**active_template.model_dump())