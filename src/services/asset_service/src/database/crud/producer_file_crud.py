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

    # Return the newly created file as a Pydantic model
    # add the file in the producers table as well

    return await get_profile_file(db, str(result.inserted_id)), str(result.inserted_id)


async def get_profile_file(db, file_id):
    doc = await db.producer_files.find_one({'_id': ObjectId(file_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="File not found")
    # Map MongoDB fields to Pydantic model
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


async def delete_producer_file_crud(db, file_id: str, user_email: str):
    """
    Deletes a file from the database and S3.
    """

    file_to_delete = await get_producer_file(db, file_id)
    if not file_to_delete:
        raise HTTPException(status_code=404, detail="File not found")

    # Delete from S3
    await delete_file_from_s3(file_to_delete.url)
    
    # Delete from DB
    result = await db.producer_files.delete_one({'_id': ObjectId(file_id)})
    # delete the file from the producers table as well
    await db.producers.update_many(
        {'email': user_email, 'files.id': str(file_id)},
        {'$pull': {'files': {'id': str(file_id)}}}
    )

    return result.deleted_count > 0


async def update_producer_file_crud(db, file_id: str, update_data: dict, current_user_email: str = None):
    """
    Updates a file's metadata in the database.
    """
    update_data['updated_at'] = datetime.utcnow()
    result = await db.producer_files.update_one(
        {'_id': ObjectId(file_id)},
        {'$set': update_data}
    )
    producer_file = (await get_producer_file(db, file_id)).dict()
    if result.modified_count > 0:
        # Also update the file metadata in the producers table
        file_doc = await db.producers.find_one({'email': current_user_email})
        if not file_doc:
            logger.warning(f"Producer not found for email: {current_user_email}")

        if file_doc and 'email' in file_doc:
            # Find all producers with this email
            await db.producers.update_many(
                {'email': file_doc['email'], 'files.id': str(file_id)},
                {'$set': {f'files.$': {**producer_file, **update_data, 'id': str(file_id)}}}
            )
        # update the metadata description in the producer_files table
        await db.producer_files.update_one(
            {'_id': ObjectId(file_id)},
            {'$set': {'description': update_data.get('description', '')}}
        )
        return await get_producer_file(db, file_id)
        
    raise HTTPException(status_code=404, detail="File not found")
async def change_file_url(db, file_id, url, user_email):
    """
    Updates the file URL in both producer_files and producers tables.
    """
    # Update in producer_files table
    await db.producer_files.update_one(
        {'_id': ObjectId(file_id)},
        {'$set': {'url': url, 'updated_at': datetime.utcnow()}}
    )

    # Update in producers table (inside files array)
    await db.producers.update_many(
        {'email': user_email, 'files.id': str(file_id)},
        {'$set': {'files.$.url': url, 'files.$.updated_at': datetime.utcnow()}}
    )

    # Return the updated file
    return await get_producer_file(db, file_id)



async def get_all_profile_files_by_email(db, email):
    # Retrieve all files for a given email asynchronously
    cursor = db.producer_files.find({'email': email})
    docs = await cursor.to_list(length=None)
    files = []
    for doc in docs:
        doc['id'] = str(doc['_id'])
        doc.pop('_id', None)
        files.append(ProducerFileModel(**doc))
    return files




