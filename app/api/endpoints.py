from fastapi import APIRouter, HTTPException, Depends
from app.api.models import SearchQuery, SearchResponse
from app.services.search import search_documents
from app.core.logging import logger
from app.utils.caching import cache
from app.db.mongodb import get_mongodb
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson.objectid import ObjectId
import time

router = APIRouter()


@router.post("/search", response_model=SearchResponse)
async def search(query: SearchQuery, db: AsyncIOMotorDatabase = Depends(get_mongodb)):
    start_time = time.time()
    logger.debug(f"DB object type: {type(db)}")
    logger.debug(f"Search query received: {query.dict()}")

    user_id = query.user_id
    try:
        if not isinstance(user_id, ObjectId):
            logger.debug(f"Converting user_id to ObjectId: {user_id}")
            user_id = ObjectId(user_id)

        user = await db.users.find_one({"_id": user_id})
        logger.debug(f"User found: {user}")

        if user is None:
            logger.warning(f"User not found: {user_id}")
            user = {"_id": user_id, "request_count": 0}
            logger.debug(f"Creating new user entry: {user}")

        if user.get("request_count", 0) >= 5:
            logger.warning(f"Rate limit exceeded for user: {user_id}")
            raise HTTPException(status_code=429, detail="Rate limit exceeded")
        result = await db.users.update_one(
            {"_id": user_id},
            {"$inc": {"request_count": 1}},
            upsert=True
        )
        logger.debug(f"User request count updated: {result.raw_result}")

    except Exception as e:
        logger.error(f"Error querying or updating user: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

    # Check cache
    cache_key = f"search:{query.text}:{query.top_k}:{query.threshold}"
    logger.debug(f"Cache key: {cache_key}")
    cached_result = cache.get(cache_key)

    if cached_result:
        logger.debug(f"Cache hit: {cached_result}")
        results = cached_result
    else:
        logger.debug("Cache miss")

        # Perform search
        try:
            results = await search_documents(query.text, query.top_k, query.threshold)
            logger.debug(f"Search results before deduplication: {results}")
        except Exception as e:
            logger.error(f"Error performing search: {str(e)}")
            raise HTTPException(status_code=500, detail="Search operation failed")

        # Deduplicate results based on URL
        results = list({result['url']: result for result in results}.values())
        logger.debug(f"Search results after deduplication: {results}")

        # Cache results
        cache.set(cache_key, results)
        logger.debug(f"Results cached with key: {cache_key}")

    end_time = time.time()
    inference_time = end_time - start_time

    logger.info(f"Search completed. User: {user_id}, Query: {query.text}, Time: {inference_time:.2f}s")

    return {
        "query": query.text,
        "results": results,
        "total_results": len(results),
        "inference_time": inference_time
    }
