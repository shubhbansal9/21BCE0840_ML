import pinecone
from app.core.config import settings

def connect_to_pinecone():
    pinecone.init(api_key=settings.PINECONE_API_KEY, environment=settings.PINECONE_ENVIRONMENT)
    pinecone.Index(settings.PINECONE_INDEX_NAME)

def close_pinecone_connection():
    pinecone.deinit()