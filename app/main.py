from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import router
from app.core.config import settings
from app.core.logging import setup_logging
from app.scraper.scheduler import start_scheduler
from app.db.pinecone import init_pinecone

app = FastAPI(title=settings.PROJECT_NAME)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(router)

# Setup logging
logger = setup_logging()

@app.on_event("startup")
async def startup_event():
    logger.info("Starting up the application")
    init_pinecone()
    start_scheduler()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)