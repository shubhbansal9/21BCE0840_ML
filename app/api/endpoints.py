from fastapi import APIRouter, HTTPException, Depends
from app.api.models import SearchQuery, SearchResult
from app.services.search import search_documents
from app.utils.caching import cache_result
from typing import List

router = APIRouter()

@router.get("/health")
async def health_check():
    return {"status": "healthy"}

@router.post("/search", response_model=List[SearchResult])
@cache_result(expiration=1800)
async def search(query: SearchQuery):
    results = await search_documents(query)
    if not results:
        raise HTTPException(status_code=404, detail="No matching documents found")
    return results