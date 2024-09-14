import os
from pinecone import Pinecone, ServerlessSpec
from app.services.encoder import encode_text
from app.core.config import settings
import logging

# Set up logging
logger = logging.getLogger(__name__)
# Initialize Pinecone using the new method
pc = Pinecone(api_key=settings.PINECONE_API_KEY)

# Ensure that the index exists, or create one if it doesn't
if settings.PINECONE_INDEX_NAME not in pc.list_indexes().names():
    pc.create_index(
        name=settings.PINECONE_INDEX_NAME,
        dimension=384,  # Update this to match your vector dimension
        metric='cosine',  # Correct the metric name to 'cosine'
        spec=ServerlessSpec(
            cloud='aws',
            region='us-east-1'
        )
    )

# Function to search documents
from app.db.pinecone import connect_to_pinecone


async def search_documents(text: str, top_k: int = 5, threshold: float = 0.1):
    pinecone_index = connect_to_pinecone()
    
    # Encode the search query
    query_vector = encode_text(text)
    
    # Search in Pinecone
    results = pinecone_index.query(
        vector=query_vector,
        top_k=top_k,
        include_metadata=True
    )
    
    # Filter results based on threshold and format the output
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