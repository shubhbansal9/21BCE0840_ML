from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Document Retrieval System"
    MONGO_URI: str
    PINECONE_API_KEY: str
    REDIS_HOST: str
    REDIS_PORT: int

    class Config:
        env_file = ".env"

settings = Settings()