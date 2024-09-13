from fastapi import FastAPI
from app.api.endpoints import router as api_router
from app.core.config import settings
from app.db.mongodb import connect_to_mongo, close_mongo_connection
from app.db.pinecone import connect_to_pinecone, close_pinecone_connection

app = FastAPI(title=settings.PROJECT_NAME)

@app.on_event("startup")
async def startup_event():
    await connect_to_mongo()
    connect_to_pinecone()

@app.on_event("shutdown")
async def shutdown_event():
    await close_mongo_connection()
    close_pinecone_connection()

app.include_router(api_router)