from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Document Retrieval System"
    MONGODB_URL: str
    REDIS_URL: str
    PINECONE_API_KEY: str
    PINECONE_INDEX_NAME: str
    class Config:
        env_file = ".env"

settings = Settings()