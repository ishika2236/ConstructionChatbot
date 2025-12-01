from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Azure OpenAI Configuration (for chat/LLM only)
    azure_openai_api_key: str
    azure_openai_endpoint: str
    azure_openai_deployment: str  # Chat/LLM deployment name (e.g., gpt-4o)
    azure_openai_api_version: str = "2024-02-15-preview"
    
    # Note: Using local HuggingFace embeddings (no API key needed)
    
    # Document Processing Configuration
    chroma_persist_dir: str = "./chroma_db"
    chunk_size: int = 1000
    chunk_overlap: int = 200
    max_retrieval_docs: int = 5
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
