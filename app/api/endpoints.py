from fastapi import APIRouter, HTTPException, Depends
from app.api.models import SearchQuery, SearchResponse
from app.services.search import search_documents
from app.core.logging import logger
from app.utils.caching import cache
from app.db.mongodb import get_mongodb
import time

router = APIRouter()

@router.get("/health")
async def health_check():
    return {"status": "healthy"}

@router.post("/search", response_model=SearchResponse)
async def search(query: SearchQuery, db=Depends(get_mongodb)):
    start_time = time.time()
    
    # Check user rate limit
    user_id = query.user_id
    user = await db.users.find_one({"_id": user_id})
    if user and user.get("request_count", 0) >= 5:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    # Increment or create user request count
    await db.users.update_one(
        {"_id": user_id},
        {"$inc": {"request_count": 1}},
        upsert=True
    )

    # Check cache
    cache_key = f"search:{query.text}:{query.top_k}:{query.threshold}"
    cached_result = cache.get(cache_key)
    if cached_result:
        return cached_result

    # Perform search
    results = await search_documents(query.text, query.top_k, query.threshold)

    # Cache results
    cache.set(cache_key, results)

    end_time = time.time()
    inference_time = end_time - start_time

    logger.info(f"Search completed. User: {user_id}, Query: {query.text}, Time: {inference_time:.2f}s")

    return SearchResponse(results=results, inference_time=inference_time)
