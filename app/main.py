from fastapi import FastAPI
from app.api.endpoints import router as api_router
from app.core.config import settings
from app.db.mongodb import connect_to_mongo, close_mongo_connection
from app.db.pinecone import connect_to_pinecone, close_pinecone_connection
from app.scraper.spider import start_scraping
import uvicorn
import asyncio

app = FastAPI(title=settings.PROJECT_NAME)

async def startup():
    await connect_to_mongo()
    connect_to_pinecone()
    asyncio.create_task(asyncio.to_thread(start_scraping())) 

async def shutdown():
    await close_mongo_connection()
    close_pinecone_connection()

if __name__ == "__main__":
    uvicorn.run(app, lifespan=uvicorn.Lifespan(startup=startup, shutdown=shutdown))

app.include_router(api_router)