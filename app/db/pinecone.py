import os
from pinecone import Pinecone, ServerlessSpec
from app.core.config import settings

def connect_to_pinecone():
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

    if settings.PINECONE_INDEX_NAME not in pc.list_indexes().names():
        pc.create_index(
            name=settings.PINECONE_INDEX_NAME, 
            dimension=768,  
            metric='cosine', 
            spec=ServerlessSpec(
                cloud='aws',
                region='us-east-1'
            )
        )
    return pc.Index(settings.PINECONE_INDEX_NAME) 

def close_pinecone_connection(pc):
    pc.deinit()
