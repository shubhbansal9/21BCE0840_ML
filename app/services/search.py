import pinecone
from app.services.encoder import encode_text
from app.core.config import settings

async def search_documents(query: str, top_k: int, threshold: float):
    index = pinecone.Index(settings.PINECONE_INDEX_NAME)
    query_vector = encode_text(query)
    results = index.query(query_vector, top_k=top_k, include_metadata=True)
    
    filtered_results = [
        {
            "id": match["id"],
            "score": match["score"],
            "metadata": match["metadata"]
        }
        for match in results["matches"]
        if match["score"] >= threshold
    ]
    
    return filtered_results
