import time
start = time.time()
import asyncio
import json
import logging
from concurrent.futures import ThreadPoolExecutor  # retained if needed
import aio_pika
from src.core.config import Settings
from src.database.crud.profile_management_crud import PROFILECRUD
from src.database.crud.asset_crud import AssetCRUD
from shared.events import QueueEventNames
from src.utils.mock_profile_generation_llm import LLMPROFILEGENERATION
from src.utils.publisher import publish_profile_generated_event
import sys
from datetime import date, datetime
from fastapi import HTTPException

# Configure logging
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
logging.basicConfig(level=logging.INFO, handlers=[handler])
logger = logging.getLogger(__name__)

async def process_metadata(message: aio_pika.IncomingMessage):
    async with message.process():
        try:
            logger.info("Processing metadata...")
            data = json.loads(message.body.decode())
            # Extract job details and resume_path
            asset_id = data.get("asset_id")
            user_id = data.get("user_id")
            
            # Fetch existing metadata and profile
            metadata = await AssetCRUD.get_by_id(asset_id)
            cur_profile = await PROFILECRUD.get_profile_by_user_id(user_id)
            if not cur_profile:
                raise HTTPException(status_code=404, detail=f"Profile not found for user_id: {user_id}")

            # Generate new profile via mock LLM
            active_profile = cur_profile["active_profile"] if cur_profile else None
            draft_profile = cur_profile["draft_profile"] if cur_profile else None
            if active_profile and not draft_profile:
                llm = LLMPROFILEGENERATION(active_profile, metadata, user_id)
            else:
                llm = LLMPROFILEGENERATION(draft_profile, metadata, user_id)
            generated_profile = llm.generate_profile()
            
            # Serialize date objects to datetime for MongoDB compatibility
            def convert_dates(obj):
                from datetime import date, datetime as dt
                if isinstance(obj, dict):
                    return {k: convert_dates(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [convert_dates(v) for v in obj]
                elif isinstance(obj, date) and not isinstance(obj, dt):
                    return dt.combine(obj, dt.min.time())
                else:
                    return obj

            profile_data = generated_profile.dict() if hasattr(generated_profile, 'dict') else generated_profile
            profile_data = convert_dates(profile_data)
            await PROFILECRUD.update_draft_profile(user_id, profile_data)
            await publish_profile_generated_event({
                "user_id": user_id,
            })
            logger.info(f"profile for asset {asset_id} processed successfully with generated profile: {generated_profile}")

        except json.JSONDecodeError:
            logger.error("Failed to decode JSON from message body.")
        except Exception as e:
            logger.error(f"Error processing message: {e}")

async def consume_messages():
    """Consumes messages from RabbitMQ and processes them."""
    try:
        logger.info("Starting consumer...")
        connection = await aio_pika.connect_robust(Settings.Config.RABBITMQ_URL)
        async with connection:
            channel = await connection.channel()
            queue = await channel.declare_queue(QueueEventNames.metadata_completed, durable=True)

            logger.info(" [*] Waiting for messages. To exit press CTRL+C")
            await queue.consume(process_metadata)

            # Keep running indefinitely
            await asyncio.Future()
    except Exception as e:
        logger.exception(f"Error in message consumption: {e}")

if __name__ == "__main__":
    try:
        print(f"Consumer script started, time taken: {time.time() - start}")
        logger.info("CONSUMER RUNNING")
        asyncio.run(consume_messages())
    except KeyboardInterrupt:
        logger.info("Shutting down consumer...")
