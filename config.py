from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
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
    ENVIRONMENT: str | None = None
    REDIS_URL: str | None = None

    # SQLite cache directory (relative to project)
    SQLITE_CACHE_DIR: str = "../sqlite_cache"

    # Do not auto-load env file here
    model_config = SettingsConfigDict(env_file=None, case_sensitive=False)


def load_settings() -> Settings:
    """
    Load env from parent folder if `.env.prod` exists.
    Otherwise load `.env.local` from current project.
    """

    # Path to parent folder .env.prod → ../.env.prod
    parent_env = Path(__file__).resolve().parent.parent / ".env.prod"

    # Project local .env.local → ./ .env.local
    local_env = Path(__file__).resolve().parent / ".env.local"

    if parent_env.exists():
        # Use the production env from parent folder
        return Settings(_env_file=str(parent_env))
    
    # Default fallback: load local env
    return Settings(_env_file=str(local_env))


settings = load_settings()
