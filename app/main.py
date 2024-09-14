from fastapi import FastAPI
from app.api.endpoints import router as api_router
from app.core.config import settings
from app.db.mongodb import connect_to_mongo, close_mongo_connection
from app.db.pinecone import connect_to_pinecone, close_pinecone_connection
from app.scraper.spider import scrape_news  
import uvicorn
import asyncio
import logging

app = FastAPI(title=settings.PROJECT_NAME)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def startup():
    await connect_to_mongo()
    connect_to_pinecone()
    asyncio.create_task(run_scraper())

async def run_scraper():
    try:
        await scrape_news() 
        logger.info("Scraping completed successfully")
    except Exception as e:
        logger.error(f"Error during scraping: {str(e)}")

async def shutdown():
    await close_mongo_connection()
    close_pinecone_connection()

app.add_event_handler("startup", startup)
app.add_event_handler("shutdown", shutdown)

app.include_router(api_router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)