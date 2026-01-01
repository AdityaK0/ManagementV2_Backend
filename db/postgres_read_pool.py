import os
import psycopg2
from psycopg2.pool import SimpleConnectionPool
from config import settings

_pool = None

def get_pg_pool():
    global _pool
    if _pool is None:
        _pool = SimpleConnectionPool(
            minconn=1,
            maxconn=10,
            host=settings.PORTFOLIO_PG_HOST,
            database=settings.PORTFOLIO_PG_DB,
            user=settings.PORTFOLIO_PG_USER,
            password=settings.PORTFOLIO_PG_PASSWORD,
            port=settings.PORTFOLIO_PG_PORT,
        )
    return _pool
