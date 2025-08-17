from fastapi import HTTPException
from datetime import datetime
from bson import ObjectId
from typing import Optional
from src.database.models.profile_model import ProducerModel
from utils.profile_agent import generate_producer_description_with_ai
from src.database.crud.template_crud import get_active_template
import logging

logger = logging.getLogger(__name__)

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
        # Check if it's an application
        result_app = await db.producer_applications.update_one({'_id': ObjectId(producer_id)}, {'$set': update_data})
        if result_app.matched_count == 0:
            raise HTTPException(status_code=404, detail="Profile or application not found")
        return await get_application(db, producer_id)
    
    return await get_profile(db, producer_id)

async def get_profile_from_approved(db, producer_id):
    doc = await db.producers.find_one({'_id': ObjectId(producer_id)})
    if not doc:
        return None # Return None instead of raising exception to allow checking
    # Default country if missing
    doc.setdefault('country', 'Canada')
    doc['files'] = await get_all_profile_files_by_email(db, doc['email'])
    return ProducerModel(**doc)
    
async def get_profile_by_email(db, email: str):
    """Retrieves a producer's profile by their email."""
    doc = await db.producers.find_one({'email': email})
    if not doc:
        return None
    # Default country if missing
    doc.setdefault('country', 'Canada')
    logger.info(f"Retrieved profile for email {email}: {doc}")
    # doc['files'] = await get_all_profile_files_by_email(db, doc['email'])
    return ProducerModel(**doc)

async def get_profile(db, producer_id):
    doc = await db.producers.find_one({'_id': ObjectId(producer_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Profile not found in approved producers")
    # Default country if missing
    doc.setdefault('country', 'Canada')
    return ProducerModel(**doc)

async def get_application(db, application_id):
    doc = await db.producer_applications.find_one({'_id': ObjectId(application_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Application not found")
    # Default country if missing
    doc.setdefault('country', 'Canada')
    doc['files'] = await get_all_profile_files_by_email(db, doc['email'])

    doc['id'] = str(doc['_id'])
    doc.pop('_id')

    return ApplicationModel(**doc)

async def get_all_applications(db, status: Optional[str] = None, skip: int = 0, limit: int = 100):
    query = {}
    if status:
        query['status'] = status
    cursor = db.producer_applications.find(query).skip(skip).limit(limit)
    docs = await cursor.to_list(length=limit)
    applications = []
    for doc in docs:
        # Default country if missing
        doc.setdefault('country', 'Canada')
        doc['files'] = await get_all_profile_files_by_email(db, doc['email'])
        applications.append(ApplicationModel(**doc))
    return applications

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
        producers.append(ProducerModel(**doc))
    return producers

async def delete_profile(db, producer_id):
    result = await db.producers.update_one({'_id': ObjectId(producer_id)}, {'$set': {'status': 'suspended'}})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    return True

async def approve_profile(db, application_id):
    application_doc = await db.producer_applications.find_one({'_id': ObjectId(application_id)})
    if not application_doc:
        raise HTTPException(status_code=404, detail="Application not found")
    application = ApplicationModel(**application_doc)
    # Retrieve associated files for this producer application
    profile_files = await get_all_profile_files_by_email(db, application.email)
    # Prepare new producer data, including embedded file list
    producer_data = application.dict(exclude={'id', 'status'})
    # Convert file models to dicts for embedding
    producer_data['files'] = [file.dict(by_alias=True) for file in profile_files]
    producer_data['status'] = 'active'
    producer_data['updated_at'] = datetime.utcnow()

    # Insert into producers collection asynchronously
    result = await db.producers.insert_one(producer_data)
    new_producer_id = str(result.inserted_id)

    # Delete from applications collection asynchronously
    await db.producer_applications.delete_one({'_id': ObjectId(application_id)})
    
    # Generate AI profile description draft
    await generate_ai_profile(db, new_producer_id, producer_data)
    
    # Return the newly created producer profile model
    return await get_profile(db, new_producer_id)

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


