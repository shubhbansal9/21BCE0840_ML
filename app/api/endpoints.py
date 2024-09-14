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


@router.post("/search")
async def search(request: SearchQuery, db: AsyncIOMotorDatabase = Depends(get_mongodb)):
  

    start_time = time.time()

    # Rate Limit Check (Improved)
    try:
        user_id = request.user_id
        if not isinstance(user_id, ObjectId):
            user_id = ObjectId(user_id)

        await check_rate_limit(db, user_id)  # Call separate function for clarity

    except (HTTPException, Exception) as e:
        logger.error(f"Error performing rate limit check: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

    # Cache Handling
    cache_key = f"search:{request.text}:{request.top_k}:{request.threshold}"
    cached_results = cache.get(cache_key)

    if cached_results:
        logger.debug(f"Cache hit for: {cache_key}")
        results = eval(cached_results)  # Assuming results are JSON-encoded
    else:
        logger.debug("Cache miss")
        try:
            results = await search_documents(request.text, request.top_k, request.threshold)
            cache.set(cache_key, results)  # Cache the retrieved results
            logger.debug(f"Results cached with key: {cache_key}")
        except Exception as e:
            logger.error(f"Error performing search: {str(e)}")
            raise HTTPException(status_code=500, detail="Search operation failed")

    # Return Detailed Response
    end_time = time.time()
    inference_time = end_time - start_time

    logger.info(f"Search completed. User: {user_id}, Query: {request.text}, "
                f"Time: {inference_time:.2f}s")

    return {
        "query": request.text,
        "results": results,
        "total_results": len(results),
        "inference_time": inference_time,
    }


async def check_rate_limit(db: AsyncIOMotorDatabase, user_id: ObjectId):
 

    try:
        user = await db.users.find_one({"_id": user_id})
        if user is None:
            user = {"_id": user_id, "request_count": 0}
            await db.users.insert_one(user)  # Create new user entry

        if user.get("request_count", 0) >= 5:
            raise HTTPException(status_code=429, detail="Rate limit exceeded")

        # Increment user request count
        await db.users.update_one({"_id": user_id}, {"$inc": {"request_count": 1}})

    except Exception as e:
        logger.error(f"Error querying or updating user: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


def cache_results(text: str, results):

    # Assuming results are JSON-encodable (validation or conversion might be needed)
    cache.set(f"search:{text}", results)