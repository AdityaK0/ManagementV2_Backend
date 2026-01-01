from psycopg2.extras import execute_values


class PostgresWriter:
    def __init__(self, conn):
        self.conn = conn


    def upsert_vendor(self, vendor):
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO vendor (id, handle, name)
                VALUES (%s, %s, %s)
                ON CONFLICT (id) DO UPDATE
                SET
                    handle = EXCLUDED.handle,
                    name = EXCLUDED.name,
                    updated_at = now()
            """, (
                vendor["id"],
                vendor["handle"],
                vendor["business_name"],  # coming from Django
            ))


    def create_new_version(self, vendor_id, version):
        with self.conn.cursor() as cur:
            cur.execute(
                "UPDATE vendor_version SET is_active=false WHERE vendor_id=%s",
                (vendor_id,)
            )
            cur.execute("""
                INSERT INTO vendor_version (vendor_id, version, is_active)
                VALUES (%s, %s, true)
                RETURNING id
            """, (vendor_id, version))
            return cur.fetchone()[0]

    def insert_portfolio_snapshot(self, vendor_id, vendor_version_id, snapshot_json):
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO portfolio (vendor_id, vendor_version_id, snapshot)
                VALUES (%s, %s, %s)
            """, (vendor_id, vendor_version_id, snapshot_json))

    def bulk_insert(self, table, columns, rows):
        if not rows:
            return
        with self.conn.cursor() as cur:
            sql = f"INSERT INTO {table} ({','.join(columns)}) VALUES %s"
            execute_values(cur, sql, rows)

    def fetch_product_id_map(self, vendor_version_id):
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT id, product_uid
                FROM product
                WHERE vendor_version_id = %s AND is_active=true
            """, (vendor_version_id,))
            return {uid: pid for pid, uid in cur.fetchall()}

    def fetch_collection_id_map(self, vendor_version_id):
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT id, slug
                FROM portfolio_collection
                WHERE vendor_version_id = %s
            """, (vendor_version_id,))
            return {slug: cid for cid, slug in cur.fetchall()}
