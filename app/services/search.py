import os
from pinecone import Pinecone, ServerlessSpec
from app.services.encoder import encode_text
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)
pc = Pinecone(api_key=settings.PINECONE_API_KEY)

if settings.PINECONE_INDEX_NAME not in pc.list_indexes().names():
    pc.create_index(
        name=settings.PINECONE_INDEX_NAME,
        dimension=786, 
        metric='cosine', 
        spec=ServerlessSpec(
            cloud='aws',
            region='us-east-1'
        )
    )

from app.db.pinecone import connect_to_pinecone


async def search_documents(text: str, top_k: int = 5, threshold: float = 0.05):
    pinecone_index = connect_to_pinecone()
    query_vector = encode_text(text)
    results = pinecone_index.query(
        vector=query_vector,
        top_k=top_k,
        include_metadata=True
    )

    filtered_results = [
        {
            "id": match['id'],
            "score": match['score'],
            "title": match['metadata']['title'],
            "url": match['metadata']['url']
        }
        for match in results['matches']
        if match['score'] >= threshold
    ]
    
    logger.info(f"Search query '{text}' returned {len(filtered_results)} results")
    
    return filtered_results