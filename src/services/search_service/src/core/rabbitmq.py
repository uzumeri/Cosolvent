import logging
import aio_pika
import asyncio
import openai
from .config import settings
from src.schemas.search_service_schema import AssetReadyForIndexing
from src.database.crud.search_service_crud import upsert_vector
from aio_pika import ExchangeType
from src.utils.profile_consumer import fetch_profile
from shared.events import QueueEventNames

logger = logging.getLogger(__name__)

# Set OpenAI key
openai.api_key = settings.OPENAI_API_KEY

connection: aio_pika.RobustConnection = None
channel: aio_pika.RobustChannel = None
exchange: aio_pika.Exchange = None

async def connect() -> None:
    global connection, channel, exchange
    connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
    channel = await connection.channel()
    exchange = await channel.declare_exchange("events", ExchangeType.TOPIC)

async def consume_asset_ready() -> None:
    queue = await channel.declare_queue(QueueEventNames.asset_ready_for_indexing, durable=True)
    # Bind to events exchange for asset indexing events
    await queue.bind(exchange, routing_key=QueueEventNames.asset_ready_for_indexing)
    await queue.consume(on_message)

async def on_message(message: aio_pika.IncomingMessage) -> None:
    async with message.process():
        event = AssetReadyForIndexing.parse_raw(message.body)
        logger.info(f"Received AssetReadyForIndexing: {event}")
        try:
            # Fetch and serialize profile
            profile = await fetch_profile(event.user_id)
            profile_text = profile.model_dump_json()
            combined = f"{event.description}\n\nPROFILE:\n{profile_text}"
            # Generate embedding
            resp = await openai.Embedding.acreate(
                input=combined,
                model="text-embedding-3-small"
            )
            vector = resp.data[0].embedding
            metadata = {"user_id": event.user_id, "context": combined}
            await upsert_vector(event.asset_id, vector, metadata)
            logger.info(f"Indexed asset {event.asset_id} with profile context")
        except Exception as e:
            logger.error(f"Indexing failed for {event.asset_id}: {e}")
