from app.api.models import SearchQuery, SearchResult
from app.db.mongodb import get_document
from app.db.pinecone import search_similar_documents
from app.services.encoder import encode_text

async def search_documents(query: SearchQuery) -> List[SearchResult]:
    query_vector = await encode_text(query.text)
    similar_docs = await search_similar_documents(
        query_vector,
        top_k=query.top_k,
        threshold=query.threshold
    )
    results = []
    for doc in similar_docs:
        full_doc = await get_document(doc.id)
        results.append(SearchResult(
            id=doc.id,
            content=full_doc['content'],
            score=doc.score
        ))
    return results