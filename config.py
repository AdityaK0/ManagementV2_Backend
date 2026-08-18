from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Postgres Configuration
    POSTGRES_HOST: str | None = None
    POSTGRES_DB: str | None = None
    POSTGRES_USER: str | None = None
    POSTGRES_PASSWORD: str | None = None
    POSTGRES_PORT: int = 5432

    PORTFOLIO_PG_HOST: str | None = None
    PORTFOLIO_PG_PORT: int = 5435
    PORTFOLIO_PG_DB: str | None = None
    PORTFOLIO_PG_USER: str | None = None
    PORTFOLIO_PG_PASSWORD: str | None = None

    # API Configuration
    API_V1_PREFIX: str = "/api"
    MAX_PAGE_SIZE: int = 100
    DEFAULT_PAGE_SIZE: int = 10
    ENVIRONMENT: str | None = None
    REDIS_URL: str | None = None

    # SQLite cache directory
    SQLITE_CACHE_DIR: str = "../sqlite_cache"
    META_DIR: str | None = None

    # S3 / AWS
    S3_BUCKET_NAME: str | None = None
    AWS_REGION: str | None = None
    AWS_ACCESS_KEY_ID: str | None = None
    AWS_SECRET_ACCESS_KEY: str | None = None

    @property
    def PG_SSLMODE(self) -> str:
        if self.ENVIRONMENT in {"production", "staging"}:
            return "require"
        return "disable"


def load_settings() -> Settings:
    """
    Local development:
        Load values from .env if it exists.

    Production:
        Load values directly from environment variables.
    """

    local_env = Path(__file__).resolve().parent / ".env"

    if local_env.exists():
        print(f"Loaded local env: {local_env}")
        return Settings(_env_file=str(local_env))

    print("Loading settings from environment variables")
    return Settings()


settings = load_settings()