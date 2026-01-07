# db/connection.py
from psycopg2.pool import SimpleConnectionPool
from config import settings

pg_pool: SimpleConnectionPool | None = None


def init_pg_pool():
    global pg_pool
    if pg_pool is None:
        pg_pool = SimpleConnectionPool(
            minconn=1,
            maxconn=4,
            host=settings.PORTFOLIO_PG_HOST,
            database=settings.PORTFOLIO_PG_DB,
            user=settings.PORTFOLIO_PG_USER,
            password=settings.PORTFOLIO_PG_PASSWORD,
            port=settings.PORTFOLIO_PG_PORT,
            connect_timeout=3,
            sslmode=settings.PG_SSLMODE,
        )


def get_db():
    """
    FastAPI dependency.
    Gets ONE connection from pool, releases automatically.
    """
    conn = pg_pool.getconn()
    try:
        yield conn
    finally:
        pg_pool.putconn(conn)
