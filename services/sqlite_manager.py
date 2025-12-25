import sqlite3
import logging
import os
import asyncio
from contextlib import asynccontextmanager
from collections import defaultdict
from typing import Dict, List
from fastapi import HTTPException

logger = logging.getLogger("sqlite_manager")

class SQLiteManager:
    def __init__(self, cache_dir: str = os.environ.get("SQLITE_CACHE_DIR", "../sqlite_cache")):
        self.cache_dir = cache_dir
        # Connection pooling
        self._pools: Dict[str, List] = defaultdict(list)
        self._locks: Dict[str, asyncio.Lock] = defaultdict(asyncio.Lock)
        self._max_pool_size = 5  # Max connections per vendor

    def _get_db_path(self, vendor_slug: str):
        return os.path.join(self.cache_dir, f"{vendor_slug}.current.db")

    def _get_connection(self, vendor_slug: str):
        """
        Creates a new SQLite connection with aggressive read optimizations.
        This is a sync method called from async context via asyncio.to_thread().
        """
        db_path = self._get_db_path(vendor_slug)

        if not os.path.exists(db_path):
            return None

        logger.debug(f"Opening SQLite connection for {vendor_slug}")

        conn = sqlite3.connect(
            db_path,
            timeout=2.0,
            check_same_thread=False,
            detect_types=sqlite3.PARSE_DECLTYPES,
        )

        conn.row_factory = sqlite3.Row

        # OPT-1: Aggressive read-only optimizations
        conn.execute("PRAGMA query_only = 1;")
        conn.execute("PRAGMA synchronous = OFF;")  # Safe for read-only
        conn.execute("PRAGMA temp_store = MEMORY;")
        conn.execute("PRAGMA cache_size = -64000;")  # 64MB page cache
        conn.execute("PRAGMA mmap_size = 268435456;")  # 256MB memory-mapped I/O
        conn.execute("PRAGMA page_size = 4096;")  # Optimal for modern systems
        conn.execute("PRAGMA locking_mode = NORMAL;")
        conn.execute("PRAGMA journal_mode = WAL;")  # Ensure WAL mode

        return conn

    async def _create_connection(self, vendor_slug: str):
        """Create connection off event loop"""
        return await asyncio.to_thread(self._get_connection, vendor_slug)

    @asynccontextmanager
    async def get_db(self, vendor_slug: str):
        """
        OPT-2: Connection pooling context manager.
        Reuses connections when available, creates new ones when pool is empty.
        """
        conn = None
        
        # Try to get from pool
        async with self._locks[vendor_slug]:
            if self._pools[vendor_slug]:
                conn = self._pools[vendor_slug].pop()
                logger.debug(f"Reused connection for {vendor_slug} (pool size: {len(self._pools[vendor_slug])})")
        
        # Create new if pool empty
        if not conn:
            conn = await self._create_connection(vendor_slug)
            if conn:
                logger.debug(f"Created new connection for {vendor_slug}")
        
        if not conn:
            logger.error(f"Database not found for {vendor_slug}")
            raise HTTPException(status_code=503, detail="Vendor data unavailable")
        
        try:
            yield conn
        except Exception as e:
            logger.error(f"SQLite error for {vendor_slug}: {e}")
            raise
        finally:
            # OPT-5: Return to pool or close async
            async with self._locks[vendor_slug]:
                if len(self._pools[vendor_slug]) < self._max_pool_size:
                    self._pools[vendor_slug].append(conn)
                    logger.debug(f"Returned connection to pool for {vendor_slug} (pool size: {len(self._pools[vendor_slug])})")
                else:
                    # Pool full, close connection off event loop
                    await asyncio.to_thread(conn.close)
                    logger.debug(f"Closed connection for {vendor_slug} (pool full)")

sqlite_manager = SQLiteManager(
    cache_dir=os.environ.get("SQLITE_CACHE_DIR", "../sqlite_cache")
)


# import sqlite3
# import logging
# import os
# from contextlib import asynccontextmanager
# from fastapi import HTTPException

# logger = logging.getLogger("sqlite_manager")

# class SQLiteManager:
#     """
#     High-performance SQLite Client.
#     - Manages connections to vendor databases.
#     - Applies runtime optimizations (MMAP, cache_size).
#     - Handles file swapping logic (stat check).
#     """
#     _instances = {}

#     def __init__(self, cache_dir:str = os.environ.get("SQLITE_CACHE_DIR", "../sqlite_cache")):
#         self.cache_dir = cache_dir
#         self.connections = {}

#     def _get_db_path(self, vendor_slug: str):
#         # return os.path.join(self.cache_dir, f"{vendor_slug}.db")
#         return os.path.join(self.cache_dir, f"{vendor_slug}.current.db")

#     def _get_connection(self, vendor_slug: str):
#         """
#         Returns a raw sqlite3 connection. 
#         Reopens if file has changed (atomic swap detection).
#         """
#         db_path = self._get_db_path(vendor_slug)
        
#         if not os.path.exists(db_path):
#             return None

#         current_mtime = os.stat(db_path).st_mtime
#         cached = self.connections.get(vendor_slug)

#         # Reuse connection if file hasn't changed
#         if cached and cached["mtime"] == current_mtime:
#             # Check if connection is actually alive
#             try:
#                 # Lightweight check
#                 cached["conn"].execute("SELECT 1").fetchone()
#                 return cached["conn"]
#             except sqlite3.Error:
#                 pass # Connection stale/error, recreate

#         # Close old connection if exists
#         if cached:
#             try:
#                 cached["conn"].close()
#             except:
#                 pass

#         # Create New Connection
#         logger.info(f"Opening new connection for {vendor_slug}")
#         conn = sqlite3.connect(
#             db_path, 
#             timeout=5.0, 
#             check_same_thread=False, # Needed for async access if managing carefully
#             detect_types=sqlite3.PARSE_DECLTYPES
#         )
        
#         # 🚀 PERFORMANCE OPTIMIZATIONS (Runtime)
#         conn.execute("PRAGMA mmap_size = 30000000000;") # ~30GB, basically maps entire DB to RAM
#         conn.execute("PRAGMA cache_size = -20000;")     # 20MB page cache
#         conn.execute("PRAGMA synchronous = NORMAL;")    # Safer than OFF, faster than FULL
#         conn.execute("PRAGMA temp_store = MEMORY;")     # Temp tables in RAM
#         conn.execute("PRAGMA query_only = 1;")          # Prevent accidental writes
        
#         conn.row_factory = sqlite3.Row
        
#         self.connections[vendor_slug] = {
#             "conn": conn,
#             "mtime": current_mtime
#         }
#         return conn

#     @asynccontextmanager
#     async def get_db(self, vendor_slug: str):
#         """
#         Context manager for usage in FastAPI Routes.
#         usage: async with manager.get_db("vendor") as db: ...
#         """
#         conn = self._get_connection(vendor_slug)
#         if not conn:
#             # If DB missing, maybe trigger download or raise 503
#             logger.error(f"Database not found for {vendor_slug}")
#             raise HTTPException(status_code=503, detail="Vendor data unavailable (initializing)")
        
#         try:
#             yield conn
#         except Exception as e:
#             logger.error(f"DB Error for {vendor_slug}: {e}")
#             raise e
#         # We generally DON'T close here to allow pooling/reuse. 
#         # Check _get_connection logic for invalidation.

# # Global Instance
# sqlite_manager = SQLiteManager(cache_dir=os.environ.get("SQLITE_CACHE_DIR", "../sqlite_cache"))
