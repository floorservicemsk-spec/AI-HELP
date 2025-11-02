from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    database_url: str = "postgresql://rag_user:rag_password@postgres:5432/rag_db"
    qdrant_host: str = "qdrant"
    qdrant_port: int = 6333
    qdrant_grpc_port: int = 6334
    secret_key: str = "your-secret-key-change-in-production"
    model_name: str = "openai-community/gpt2"  # Fallback model, can be changed to gpt-oss-20b
    embedding_model: str = "intfloat/multilingual-e5-large"
    xml_catalog_url: str = "https://av.my-step.eu/avaliable_products.xml"
    upload_dir: str = "/app/uploads"
    chunk_size: int = 500
    chunk_overlap: int = 50
    
    class Config:
        env_file = ".env"


settings = Settings()
