# template_crud.py
import logging
from fastapi import HTTPException
from datetime import datetime
from uuid import UUID
from motor.motor_asyncio import AsyncIOMotorDatabase

from src.database.models.template_model import TemplateModel
from src.schema.template_schema import TemplateCreate, TemplateUpdate

logger = logging.getLogger(__name__)

async def create_template(db: AsyncIOMotorDatabase, template: TemplateCreate) -> TemplateModel:
    template_data = TemplateModel(name=template.name, content=template.content)
    await db.templates.insert_one(template_data.model_dump(by_alias=True))
    return template_data

async def get_all_templates(db: AsyncIOMotorDatabase) -> list[TemplateModel]:
    templates_cursor = db.templates.find()
    templates = await templates_cursor.to_list(length=None)
    return [TemplateModel(**t) for t in templates]

async def get_template_by_id(db: AsyncIOMotorDatabase, template_id: UUID) -> TemplateModel | None:
    template = await db.templates.find_one({"id": template_id})
    if template:
        return TemplateModel(**template)
    return None

async def get_active_template(db: AsyncIOMotorDatabase) -> TemplateModel | None:
    template = await db.templates.find_one({"is_active": True})
    if template:
        return TemplateModel(**template)
    return None

async def update_template(db: AsyncIOMotorDatabase, template_id: UUID, template_update: TemplateUpdate) -> TemplateModel | None:
    update_data = template_update.model_dump(exclude_unset=True)
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No update data provided")

    update_data["updated_at"] = datetime.utcnow()

    result = await db.templates.update_one(
        {"id": template_id},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        return None
    
    return await get_template_by_id(db, template_id)

async def delete_template(db: AsyncIOMotorDatabase, template_id: UUID) -> bool:
    result = await db.templates.delete_one({"id": template_id})
    return result.deleted_count > 0

async def set_active_template(db: AsyncIOMotorDatabase, template_id: UUID) -> TemplateModel | None:
    # Deactivate all other templates
    await db.templates.update_many(
        {"is_active": True},
        {"$set": {"is_active": False, "updated_at": datetime.utcnow()}}
    )
    
    # Activate the specified template
    result = await db.templates.update_one(
        {"id": template_id},
        {"$set": {"is_active": True, "updated_at": datetime.utcnow()}}
    )
    
    if result.matched_count == 0:
        return None
        
    return await get_template_by_id(db, template_id)