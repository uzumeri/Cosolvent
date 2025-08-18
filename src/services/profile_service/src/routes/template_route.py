# admin.py
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from uuid import UUID
from motor.motor_asyncio import AsyncIOMotorDatabase

from src.database.crud import template_crud
from src.schema.template_schema import (
    TemplateCreate,
    TemplateUpdate,
    TemplateResponse,
)
from src.schema.profile_schema import SuccessResponse
from src.database.db import get_mongo_service

router = APIRouter(prefix="/admin/templates", tags=["Templates"])

@router.post("", response_model=TemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_new_template(template: TemplateCreate, db: AsyncIOMotorDatabase = Depends(get_mongo_service)):
    """
    Create a new template.
    """
    return await template_crud.create_template(db, template)

@router.get("", response_model=List[TemplateResponse])
async def get_all_templates_admin(db: AsyncIOMotorDatabase = Depends(get_mongo_service)):
    """
    Retrieve all templates.
    """
    return await template_crud.get_all_templates(db)

@router.get("/active", response_model=TemplateResponse)
async def get_active_template_user(db: AsyncIOMotorDatabase = Depends(get_mongo_service)):
    """
    Get the active template.
    """
    active_template = await template_crud.get_active_template(db)
    if not active_template:
        raise HTTPException(status_code=404, detail="No active template found")
    return active_template

@router.get("/{template_id}", response_model=TemplateResponse)
async def get_template_by_id_admin(template_id: UUID, db: AsyncIOMotorDatabase = Depends(get_mongo_service)):
    """
    Retrieve a single template by its ID.
    """
    template = await template_crud.get_template_by_id(db, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template

@router.put("/{template_id}", response_model=TemplateResponse)
async def update_template_admin(template_id: UUID, template_update: TemplateUpdate, db: AsyncIOMotorDatabase = Depends(get_mongo_service)):
    """
    Update a template.
    """
    updated_template = await template_crud.update_template(db, template_id, template_update)
    if not updated_template:
        raise HTTPException(status_code=404, detail="Template not found")
    return updated_template

@router.delete("/{template_id}", response_model=SuccessResponse)
async def delete_template_admin(template_id: UUID, db: AsyncIOMotorDatabase = Depends(get_mongo_service)):
    """
    Delete a template.
    """
    if await template_crud.delete_template(db, template_id):
        return {"success": True, "message": "Template deleted successfully."}
    raise HTTPException(status_code=404, detail="Template not found")

@router.post("/{template_id}/set-active", response_model=TemplateResponse)
async def set_active_template_admin(template_id: UUID, db: AsyncIOMotorDatabase = Depends(get_mongo_service)):
    """
    Set a template as the active one.
    """
    active_template = await template_crud.set_active_template(db, template_id)
    if not active_template:
        raise HTTPException(status_code=404, detail="Template not found")
    return active_template