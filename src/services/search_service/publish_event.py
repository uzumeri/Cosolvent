"""
Simple script to publish an AssetReadyForIndexing event to RabbitMQ for integration testing.
Usage:
  $ RABBITMQ_URL=amqp://guest:guest@localhost:5672/ python publish_event.py
"""
import os
import asyncio
import json
import aio_pika
from aio_pika import ExchangeType

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")

async def publish():
    conn = await aio_pika.connect_robust(RABBITMQ_URL)
    channel = await conn.channel()
    # Declare or get the 'events' exchange
    exchange = await channel.declare_exchange("events", ExchangeType.TOPIC)

    event = {
        "asset_id": "test-asset-123",
        "user_id": "test-user",
        "description": "A test asset for indexing and search."
    }
    message = aio_pika.Message(body=json.dumps(event).encode())
    await exchange.publish(message, routing_key="asset.ready_for_indexing")
    print("Published AssetReadyForIndexing event.")
    await conn.close()

if __name__ == "__main__":
    asyncio.run(publish())
