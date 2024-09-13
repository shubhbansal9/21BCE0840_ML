import pinecone
from app.core.config import settings

pinecone.init(api_key=settings.PINECONE_API_KEY)
index = pinecone.Index("document-retrieval")

async def search_similar_documents(query_vector, top_k=5, threshold=0.5):
    results = index.query(vector=query_vector, top_k=top_k, include_metadata=True)
    return [r for r in results.matches if r.score >= threshold]

async def store_vector(id: str, vector: list, metadata: dict):
    index.upsert([(id, vector, metadata)])