# sqlite_builder.py
import sqlite3
import json
import logging
from datetime import datetime
from decimal import Decimal
from .schema_mapper import SCHEMA_SQL, FTS_SQL

logger = logging.getLogger()

class SQLiteBuilder:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = sqlite3.connect(
            self.db_path,
            detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
        )
        self.conn.row_factory = sqlite3.Row

    def close(self):
        self.conn.close()

    # UNIVERSAL CLEANER — MUST BE USED EVERYWHERE
    def sanitize(self, val):
        if isinstance(val, (dict, list)):
            return json.dumps(val)
        if isinstance(val, datetime):
            return val.isoformat()
        if isinstance(val, Decimal):
            return float(val)
        return val

    def get_allowed_columns(self, table):
        sql = SCHEMA_SQL[table]
        lines = sql.split("\n")

        cols = []
        for line in lines:
            line = line.strip().rstrip(",")
            if not line or line.startswith(("CREATE", "FOREIGN", "PRIMARY", ")", "--")):
                continue
            col = line.split()[0].replace('"', "")
            cols.append(col)
        return cols

    def create_tables(self):
        cursor = self.conn.cursor()
        for _, sql in SCHEMA_SQL.items():
            cursor.execute(sql)
        self.conn.commit()

    def insert_data(self, data):
        cursor = self.conn.cursor()

        tables_order = [
            "vendor", "category", "product",
            "portfolio", "portfolio_collection",
            "portfolio_collection_product"
        ]

        vendor_name = data["vendor"][0]["business_name"]
        category_map = data["category_map"]

        for table in tables_order:
            rows = data.get(table, [])
            if not rows:
                continue

            # -------------------------------
            # SPECIAL CASE: PORTFOLIO TABLE
            # -------------------------------
            if table == "portfolio":
                clean_rows = []
                for row in rows:
                    clean_rows.append({
                        "id": row["id"],
                        "response_json": self.sanitize(row["response_json"])
                    })

                sql = 'INSERT INTO portfolio (id, response_json) VALUES (?, ?)'
                values = [(r["id"], r["response_json"]) for r in clean_rows]

                cursor.executemany(sql, values)
                logger.info(f"Inserted {len(values)} rows into portfolio")
                continue  # skip normal flow for portfolio

            # -------------------------------
            # NORMAL TABLE HANDLING
            # -------------------------------
            allowed = self.get_allowed_columns(table)
            final_rows = []

            for row in rows:
                clean = {}

                # sanitize all allowed fields
                for col in allowed:
                    clean[col] = self.sanitize(row.get(col))

                # -----------------------
                # PRODUCT ENRICHMENT
                # -----------------------
                if table == "product":
                    cid = row.get("category_id")

                    clean["category_name"] = category_map.get(cid)
                    clean["vendor_name"] = vendor_name
                    clean["is_in_stock"] = 1 if row.get("stock_quantity", 0) > 0 else 0

                    # process images
                    img_list = row.get("image_urls") or []
                    if isinstance(img_list, str):
                        try:
                            img_list = json.loads(img_list)
                        except:
                            img_list = [img_list]

                    primary = row.get("primary_image")
                    if primary:
                        img_list = [primary] + [i for i in img_list if i != primary]

                    clean["images_processed"] = json.dumps(img_list)

                    # JSON fields sanitize
                    clean["sizes"] = self.sanitize(row.get("sizes"))
                    clean["dimensions"] = self.sanitize(row.get("dimensions"))
                    clean["image_urls"] = self.sanitize(row.get("image_urls"))

                final_rows.append(clean)

            # Insert normally
            cols = list(final_rows[0].keys())
            placeholders = ",".join(["?"] * len(cols))
            column_names = ",".join([f'"{c}"' for c in cols])

            sql = f'INSERT INTO "{table}" ({column_names}) VALUES ({placeholders})'
            values = [tuple(r[c] for c in cols) for r in final_rows]

            cursor.executemany(sql, values)
            logger.info(f"Inserted {len(values)} rows into {table}")

        self.conn.commit()


    def create_fts_index(self):
        cursor = self.conn.cursor()
        for sql in FTS_SQL:
            cursor.execute(sql)
        self.conn.commit()

    def optimize_db(self):
        cursor = self.conn.cursor()
        cursor.execute("PRAGMA journal_mode=WAL;")
        cursor.execute("PRAGMA synchronous=NORMAL;")
        cursor.execute("VACUUM;")
        self.conn.commit()


# import sqlite3
# import json
# import logging
# from datetime import datetime
# from decimal import Decimal
# from .schema_mapper import SCHEMA_SQL, FTS_SQL

# logger = logging.getLogger()


# from .schema_mapper import SCHEMA_SQL

# def get_allowed_columns(self, table):
#     sql = SCHEMA_SQL[table]
#     lines = sql.split("\n")
#     columns = []
#     for line in lines:
#         line = line.strip().rstrip(",")
#         # a column definition has "something something TYPE"
#         if " " in line and not line.startswith(("CREATE", "FOREIGN", "PRIMARY", ")", "--")):
#             col_name = line.split()[0].replace('"', "")
#             columns.append(col_name)
#     return columns


# class SQLiteBuilder:
#     def __init__(self, db_path: str):
#         self.db_path = db_path
#         self.conn = sqlite3.connect(
#             self.db_path, 
#             detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
#         )
#         self.conn.row_factory = sqlite3.Row

#     def close(self):
#         if self.conn:
#             self.conn.close()

#     def create_tables(self):
#         """Creates all tables defined in schema map."""
#         cursor = self.conn.cursor()
#         for table_name, sql in SCHEMA_SQL.items():
#             logger.info(f"Creating table: {table_name}")
#             cursor.execute(sql)
#         self.conn.commit()

#     def insert_data(self, data: dict):
#         cursor = self.conn.cursor()

#         tables_order = [
#             "vendor", "category", "product",
#             "portfolio", "portfolio_collection",
#             "portfolio_collection_product"
#         ]

#         for table in tables_order:
#             rows = data.get(table, [])
#             if not rows:
#                 continue

#             allowed_cols = self.get_allowed_columns(table)

#             cleaned_rows = []
#             for row in rows:
#                 new_row = {}

#                 # 1. Keep only allowed columns
#                 for col in allowed_cols:
#                     new_row[col] = row.get(col)

#                 # 2. Enrich product
#                 if table == "product":
#                     # category_name
#                     new_row["category_name"] = data["category_map"].get(row["category_id"])

#                     # vendor_name
#                     new_row["vendor_name"] = data["vendor"][0]["business_name"]

#                     # is_in_stock
#                     new_row["is_in_stock"] = 1 if row.get("stock_quantity", 0) > 0 else 0

#                     # images_processed
#                     images = row.get("image_urls") or []
#                     primary = row.get("primary_image")

#                     if isinstance(images, str):
#                         try: images = json.loads(images)
#                         except: images = [images]

#                     if primary:
#                         images = [primary] + [i for i in images if i != primary]

#                     new_row["images_processed"] = json.dumps(images)

#                 cleaned_rows.append(new_row)

#             # Build SQL
#             cols = list(cleaned_rows[0].keys())
#             placeholders = ",".join(["?"] * len(cols))
#             col_names = ",".join([f'"{c}"' for c in cols])

#             sql = f'INSERT INTO "{table}" ({col_names}) VALUES ({placeholders})'

#             values = []
#             for r in cleaned_rows:
#                 values.append(tuple(r[c] for c in cols))

#             cursor.executemany(sql, values)
#             logger.info(f"Inserted {len(values)} rows into {table}")

#         self.conn.commit()


#     def create_fts_index(self):
#         """Creates FTS5 tables and populates them."""
#         cursor = self.conn.cursor()
#         for sql in FTS_SQL:
#             cursor.execute(sql)
#         self.conn.commit()

#     def optimize_db(self):
#         """Applies performance PRAGMAs."""
#         cursor = self.conn.cursor()
#         cursor.execute("PRAGMA journal_mode = WAL;")
#         cursor.execute("PRAGMA synchronous = NORMAL;")
#         cursor.execute("PRAGMA foreign_keys = ON;")
#         cursor.execute("VACUUM;") 
#         self.conn.commit()
