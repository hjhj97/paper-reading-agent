from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    openai_api_key: str
    pinecone_api_key: str
    pinecone_environment: str
    pinecone_index_name: str = "paper-reading-agent"
    default_model: str = "gpt-4o-mini"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

