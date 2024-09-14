from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson.objectid import ObjectId
class MongoDB:
    client: AsyncIOMotorClient = None

db = MongoDB()

async def connect_to_mongo():
    db.client = AsyncIOMotorClient(settings.MONGODB_URL)

async def close_mongo_connection():
    db.client.close()


async def get_mongodb() -> AsyncIOMotorDatabase:
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    return client.db