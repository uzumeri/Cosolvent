# profile_crud.py
from fastapi import HTTPException
from datetime import datetime
from bson import ObjectId
from src.database.models.producer_file_model import ProducerFileModel
from utils.s3_uploader import delete_file_from_s3
import logging

logger = logging.getLogger(__name__)
async def create_producer_file(db, data,):
    data['created_at'] = datetime.utcnow()
    result = await db.producer_files.insert_one(data)

    return await get_profile_file(db, str(result.inserted_id)), str(result.inserted_id)


async def get_profile_file(db, file_id):
    doc = await db.producer_files.find_one({'_id': ObjectId(file_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="File not found")
    doc['id'] = str(doc['_id'])
    doc.pop('_id', None)
    return ProducerFileModel(**doc)


async def get_producer_file(db, file_id: str):
    """
    Retrieves a single file by its ID.
    """
    doc = await db.producer_files.find_one({'_id': ObjectId(file_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="File not found")

    doc['id'] = str(doc['_id'])
    doc.pop('_id', None)
    return ProducerFileModel(**doc)


async def delete_producer_file_crud(db, file_id: str, ):
    """
    Deletes a file from the database and S3.
    """

    file_to_delete = await get_producer_file(db, file_id)
    if not file_to_delete:
        raise HTTPException(status_code=404, detail="File not found")

    await delete_file_from_s3(file_to_delete.url)
    
    result = await db.producer_files.delete_one({'_id': ObjectId(file_id)})


    return result.deleted_count > 0


async def update_producer_file_crud(db, file_id: str, update_data: dict):
    """
    Updates a file's metadata in the database.
    """
    update_data['updated_at'] = datetime.utcnow()
    result = await db.producer_files.update_one(
        {'_id': ObjectId(file_id)},
        {'$set': update_data}
    )
    if not result.matched_count:
        raise HTTPException(status_code=404, detail="File not found")
    return await get_producer_file(db, file_id)
        
async def change_file_url(db, file_id, url):
    """
    Updates the file URL in both producer_files and producers tables.
    """
    await db.producer_files.update_one(
        {'_id': ObjectId(file_id)},
        {'$set': {'url': url, 'updated_at': datetime.utcnow()}}
    )

    return await get_producer_file(db, file_id)


