from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

client = AsyncIOMotorClient(settings.MONGO_URI)
db = client.document_retrieval

async def get_document(doc_id: str):
    return await db.documents.find_one({"_id": doc_id})

async def store_document(document: dict):
    return await db.documents.insert_one(document)