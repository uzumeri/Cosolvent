import asyncio
import json
import logging
import sys

import openai
from aio_pika import connect_robust
from pydantic import BaseModel

from src.core.config import settings
from src.core.vector_store import index
from src.database.crud.profile_crud import PROFILECRUD
from shared.events import QueueEventNames

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProfileEvent(BaseModel):
    user_id: str


def serialize_profile_to_text(profile: dict) -> str:
    parts = []
    basic = profile.get("basic_info", {})
    name = " ".join(filter(None, [
        basic.get("first_name"),
        basic.get("middle_name"),
        basic.get("last_name")
    ]))
    if name:
        parts.append(f"Name: {name}.")
    if basic.get("country"):
        parts.append(f"Country: {basic['country']}.")
    detail = profile.get("active_profile") or profile.get("draft_profile") or {}
    if detail.get("description"):
        parts.append(f"Description: {detail['description']}.")
    if detail.get("farm_name"):
        cp = detail.get("contact_person", "")
        parts.append(f"Farm name: {detail['farm_name']}. Contact person: {cp}.")
    for prod in detail.get("products") or []:
        pparts = []
        if prod.get("name"): pparts.append(prod["name"])
        if prod.get("category"): pparts.append(f"category {prod['category']}")
        if prod.get("variety"): pparts.append(f"variety {prod['variety']}")
        if prod.get("quantity_available") is not None and prod.get("unit"):
            pparts.append(f"{prod['quantity_available']} {prod['unit']}")
        if pparts:
            parts.append("Product: " + ", ".join(pparts) + ".")
    return " ".join(parts)

async def handle_profile_generated(user_id: str):
    logger.info(f"Handling profile_generated for user_id={user_id}")
    try:
        profile_json = await PROFILECRUD.get_profile_by_user_id(user_id)
    except Exception as e:
        logger.error(f"Error fetching profile for {user_id}: {e}")
        return

    text = serialize_profile_to_text(profile_json)
    if not text:
        logger.warning(f"No text to embed for user {user_id}; skipping")
        return

    try:
        emb_resp = openai.embeddings.create(model=settings.embedding_model, input=[text])
        embedding = emb_resp.data[0].embedding
    except Exception as e:
        logger.error(f"OpenAI embedding failed for {user_id}: {e}")
        return

    metadata = {}
    basic = profile_json.get("basic_info", {})
    if basic.get("country"): metadata["country"] = basic["country"]
    detail = profile_json.get("active_profile") or profile_json.get("draft_profile") or {}
    cats = [p["category"] for p in detail.get("products") or [] if p.get("category")]
    if cats: metadata["categories"] = list(set(cats))

    try:
        index.upsert(vectors=[(user_id, embedding, metadata)])
        logger.info(f"Upserted profile vector for user {user_id}")
    except Exception as e:
        logger.error(f"Pinecone upsert failed for {user_id}: {e}")

async def consume_profile_events():
    logger.info("Connecting to RabbitMQ...")
    try:
        connection = await connect_robust(settings.rabbitmq_url)
    except Exception as e:
        logger.error(f"Failed to connect to RabbitMQ: {e}")
        return

    channel = await connection.channel()
    queue = await channel.declare_queue(
        QueueEventNames.profile_approved, durable=True
    )
    logger.info(f"Declared queue '{QueueEventNames.profile_approved}', awaiting messages...")

    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            async with message.process():
                try:
                    body = message.body.decode()
                    evt = ProfileEvent(**json.loads(body))
                    await handle_profile_generated(evt.user_id)
                except Exception as e:
                    logger.error(f"Failed processing message: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(consume_profile_events())
    except KeyboardInterrupt:
        logger.info("Profile consumer stopped by user")
        sys.exit(0)