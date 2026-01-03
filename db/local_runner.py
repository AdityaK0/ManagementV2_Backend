from psycopg2 import connect
from .postgres_reader import PostgresReader
from .postgres_writer import PostgresWriter
from .publish_service import publish_vendor
from .cleanup_older_data import cleanup_old_versions
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


        # 2️⃣ Cleanup (same connection is OK locally)
        cleanup_old_versions(
            conn,
            active_version_id=result["vendor_version_id"]
        )
        conn.commit()
        print("🧹 OLD VERSIONS CLEANED")
    except Exception as e:
        conn.rollback()
        print("❌ LOCAL PUBLISH FAILED:", e)
    finally:
        reader.close()
        conn.close()
