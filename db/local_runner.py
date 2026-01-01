from psycopg2 import connect
from .postgres_reader import PostgresReader
from .postgres_writer import PostgresWriter
from .publish_service import publish_vendor
import os
from config import settings

def run_local(vendor_slug: str):
    reader = PostgresReader()

    conn = connect(
        host=settings.PORTFOLIO_PG_HOST,
        database=settings.PORTFOLIO_PG_DB,
        user=settings.PORTFOLIO_PG_USER,
        password=settings.PORTFOLIO_PG_PASSWORD,
        port=settings.PORTFOLIO_PG_PORT,
    )
    writer = PostgresWriter(conn)

    try:
        result = publish_vendor(vendor_slug, reader, writer)
        conn.commit()
        print("✅ LOCAL PUBLISH SUCCESS:", result)
    except Exception as e:
        conn.rollback()
        print("❌ LOCAL PUBLISH FAILED:", e)
    finally:
        reader.close()
        conn.close()
