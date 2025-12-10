import sqlite3
import logging
import os
from contextlib import asynccontextmanager
from fastapi import HTTPException

logger = logging.getLogger("sqlite_manager")

class SQLiteManager:
    """
    High-performance SQLite Client.
    - Manages connections to vendor databases.
    - Applies runtime optimizations (MMAP, cache_size).
    - Handles file swapping logic (stat check).
    """
    _instances = {}

    def __init__(self, cache_dir:str = os.environ.get("SQLITE_CACHE_DIR", "../sqlite_cache")):
        self.cache_dir = cache_dir
        # Store connection per vendor: { "vendor_slug": { "conn": Connection, "mtime": float } }
        self.connections = {}

    def _get_db_path(self, vendor_slug: str):
        return os.path.join(self.cache_dir, f"{vendor_slug}.db")

    def _get_connection(self, vendor_slug: str):
        """
        Returns a raw sqlite3 connection. 
        Reopens if file has changed (atomic swap detection).
        """
        db_path = self._get_db_path(vendor_slug)
        
        if not os.path.exists(db_path):
            return None

        current_mtime = os.stat(db_path).st_mtime
        cached = self.connections.get(vendor_slug)

        # Reuse connection if file hasn't changed
        if cached and cached["mtime"] == current_mtime:
            # Check if connection is actually alive
            try:
                # Lightweight check
                cached["conn"].execute("SELECT 1").fetchone()
                return cached["conn"]
            except sqlite3.Error:
                pass # Connection stale/error, recreate

        # Close old connection if exists
        if cached:
            try:
                cached["conn"].close()
            except:
                pass

        # Create New Connection
        logger.info(f"Opening new connection for {vendor_slug}")
        conn = sqlite3.connect(
            db_path, 
            timeout=5.0, 
            check_same_thread=False, # Needed for async access if managing carefully
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        
        # 🚀 PERFORMANCE OPTIMIZATIONS (Runtime)
        conn.execute("PRAGMA mmap_size = 30000000000;") # ~30GB, basically maps entire DB to RAM
        conn.execute("PRAGMA cache_size = -20000;")     # 20MB page cache
        conn.execute("PRAGMA synchronous = NORMAL;")    # Safer than OFF, faster than FULL
        conn.execute("PRAGMA temp_store = MEMORY;")     # Temp tables in RAM
        conn.execute("PRAGMA query_only = 1;")          # Prevent accidental writes
        
        conn.row_factory = sqlite3.Row
        
        self.connections[vendor_slug] = {
            "conn": conn,
            "mtime": current_mtime
        }
        return conn

    @asynccontextmanager
    async def get_db(self, vendor_slug: str):
        """
        Context manager for usage in FastAPI Routes.
        usage: async with manager.get_db("vendor") as db: ...
        """
        conn = self._get_connection(vendor_slug)
        if not conn:
            # If DB missing, maybe trigger download or raise 503
            logger.error(f"Database not found for {vendor_slug}")
            raise HTTPException(status_code=503, detail="Vendor data unavailable (initializing)")
        
        try:
            yield conn
        except Exception as e:
            logger.error(f"DB Error for {vendor_slug}: {e}")
            raise e
        # We generally DON'T close here to allow pooling/reuse. 
        # Check _get_connection logic for invalidation.

# Global Instance
sqlite_manager = SQLiteManager(cache_dir=os.environ.get("SQLITE_CACHE_DIR", "../sqlite_cache"))
