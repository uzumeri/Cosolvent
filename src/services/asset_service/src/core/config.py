import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://mongodb:27017")
    DB_NAME: str = os.getenv("DB_NAME", "COSOLVENT_DB")
    S3_REGION: str = os.getenv("S3_REGION", "us-east-2")
    S3_BUCKET: str = os.getenv("ASSETS_BUCKET", "assets")
    S3_ACCESS_KEY: str = os.getenv("S3_ACCESS_KEY")
    S3_SECRET_KEY: str = os.getenv("S3_SECRET_KEY")
    # RabbitMQ connection URL for event publishing
    RABBITMQ_URL: str = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/")