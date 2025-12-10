"""
Configuration settings for FastAPI Portfolio API
Uses pydantic-settings for environment variable management
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # Elasticsearch Configuration
    ES_HOST: str = "localhost:9205"
    ES_USER: str = ""
    ES_PASS: str = ""
    
    # Elasticsearch Indices
# Elasticsearch Indices
    PRODUCTS_INDEX: str = "product_index"
    COLLECTIONS_INDEX: str = "portfoliocollection_index"
    PORTFOLIOS_INDEX: str = "portfolio_index"
    
    # Postgres Configuration
    POSTGRES_HOST: str | None = None
    POSTGRES_DB: str | None = None
    POSTGRES_USER: str | None = None
    POSTGRES_PASSWORD: str | None = None
    POSTGRES_PORT: int = 5432

    # API Configuration
    API_V1_PREFIX: str = "/api"
    MAX_PAGE_SIZE: int = 100
    DEFAULT_PAGE_SIZE: int = 10
    SQLITE_CACHE_DIR: str = "../sqlite_cache"
    ENVIRONMENT: str = "local"
    
    class Config:
        env_file = ".env.local"
        case_sensitive = False


# Global settings instance
settings = Settings()