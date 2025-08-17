from fastapi import HTTPException
from datetime import datetime
from bson import ObjectId
from typing import Optional
from src.database.models.profile_model import ProducerModel
from utils.profile_agent import generate_producer_description_with_ai
from src.database.crud.template_crud import get_active_template
import logging

logger = logging.getLogger(__name__)

def _normalize_embedded_files(doc: dict):
    """Ensure each embedded file dict has an '_id' key for Pydantic alias."""
    files = doc.get('files')
    if isinstance(files, list):
        for f in files:
            # If stored under 'id', normalize to alias '_id'
            if 'id' in f:
                f['_id'] = f.pop('id')
            # Mirror alias back to 'id' for field name population
            if '_id' in f:
                f['id'] = f['_id']
    return doc

async def get_application_by_email(db, email: str):
    """Checks if an application with the given email exists."""
    return await db.producer_applications.find_one({'email': email}) 

async def create_profile(db, data):
    data['status'] = 'pending_review'
    data['created_at'] = datetime.utcnow()
    data['updated_at'] = datetime.utcnow()
    result = await db.producers.insert_one(data)
    profile_id = str(result.inserted_id)
    profile = await get_profile(db, profile_id)
    return profile, profile_id


async def update_profile(db, producer_id, update_data):
    update_data['updated_at'] = datetime.utcnow()
    result = await db.producers.update_one({'_id': ObjectId(producer_id)}, {'$set': update_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Profile not found")
    return await get_profile(db, producer_id)


async def get_profile_by_email(db, email: str):
    """Retrieves a producer's profile by their email."""
    doc = await db.producers.find_one({'email': email})
    if not doc:
        return None
    # Default country if missing
    doc.setdefault('country', 'Canada')
    # Normalize embedded files for Pydantic
    _normalize_embedded_files(doc)
    logger.info(f"Retrieved profile for email {email}: {doc}")
    return ProducerModel(**doc)

async def get_profile(db, producer_id):
    doc = await db.producers.find_one({'_id': ObjectId(producer_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Profile not found in approved producers")
    # Default country if missing
    doc.setdefault('country', 'Canada')
    # Normalize embedded files for Pydantic
    _normalize_embedded_files(doc)
    return ProducerModel(**doc)



async def get_all_producers(db, status: Optional[str] = None, skip: int = 0, limit: int = 100):
    query = {}
    if status:
        query['status'] = status
    cursor = db.producers.find(query).skip(skip).limit(limit)
    docs = await cursor.to_list(length=limit)
    producers = []
    for doc in docs:
        # Default country if missing
        doc.setdefault('country', 'Canada')
        # Normalize embedded files
        _normalize_embedded_files(doc)
        producers.append(ProducerModel(**doc))
    return producers

async def delete_profile(db, producer_id):
    result = await db.producers.update_one({'_id': ObjectId(producer_id)}, {'$set': {'status': 'suspended'}})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    return True

async def reject_profile(db, application_id: str, reason: str):
    result = await db.producer_applications.update_one(
        {'_id': ObjectId(application_id)}, 
        {'$set': {'status': 'rejected', 'rejection_reason': reason, 'updated_at': datetime.utcnow()}}
    )
    return result.matched_count > 0

async def generate_ai_profile(db, producer_id, profile_data):
    """Generates an AI profile draft for a producer."""
    # Get template
    template = await get_active_template(db)
    content = template.content if template else None
    if not content:
        raise HTTPException(status_code=404, detail="No active template found")

    # Get URLs for the producer's files
    profile_files = profile_data.get('files', [])
    # Each ProducerFileModel has a `url` attribute
    s3_urls = [file.url for file in profile_files if getattr(file, 'url', None)]
    if not s3_urls:
        s3_urls = []
    # Generate AI description
    ai_description = generate_producer_description_with_ai(s3_urls, profile_data, content)

    if not ai_description:
        raise HTTPException(status_code=500, detail="Failed to generate AI profile description")
    
    result = await db.producers.update_one({'_id': ObjectId(producer_id)}, {'$set': {'ai_profile_draft': ai_description}})

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Profile not found in db")
    return True

async def approve_ai_draft(db, producer_id):
    profile = await db.producers.find_one({'_id': ObjectId(producer_id)})
    if not profile or not profile.get('ai_profile_draft'):
        raise HTTPException(status_code=404, detail="No AI draft found")
    await db.producers.update_one({'_id': ObjectId(producer_id)}, {
        '$set': {
            'ai_profile': profile['ai_profile_draft'],
        },
        '$unset': {
            'ai_profile_draft': ""
        }
    })
    # await index_producer(producer_id, db)  # Index the new producer profile
    return True

async def reject_ai_draft(db, producer_id):
    """Rejects/deletes the AI profile draft for a producer."""
    profile = await db.producers.find_one({'_id': ObjectId(producer_id)})
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found.")
    result = await db.producers.update_one(
        {'_id': ObjectId(producer_id)},
        {'$unset': {'ai_profile_draft': ""}}
    )
    return result.matched_count > 0

async def add_file_in_producer_profile(db, producer_id:str, file:ProducerModel):
    """
    Adds a file to the producer's profile.
    """
    # Embed file using alias so Pydantic ProducerModel recognizes '_id'
    file_data = file.dict(by_alias=True)
    # Mirror id fields for Pydantic validation
    if '_id' in file_data:
        file_data['id'] = file_data['_id']
    result = await db.producers.update_one(
        {'_id': ObjectId(producer_id)},
        {'$push': {'files': file_data}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    return await get_profile(db, producer_id)
async def update_file_in_producer_profile(db, producer_id:str, file:ProducerModel):
    """
    Updates a file in the producer's profile.
    """
    # Update embedded file using alias
    file_data = file.dict(by_alias=True)
    # Mirror id fields for Pydantic validation
    if '_id' in file_data:
        file_data['id'] = file_data['_id']
    result = await db.producers.update_one(
        {'_id': ObjectId(producer_id), 'files.id': file.id},
        {'$set': {'files.$': file_data}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Profile or file not found")
    
    return await get_profile(db, producer_id)
async def remove_file_from_producer_profile(db, producer_id: str, file_id: str):
    """Removes a file from the producer's profile.
    """ 
    result = await db.producers.update_one(
        {'_id': ObjectId(producer_id)},
        {'$pull': {'files': {'_id': file_id}}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Profile or file not found")
    
    return await get_profile(db, producer_id)
