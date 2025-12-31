SCHEMA_SQL = {
    "vendor": """
        CREATE TABLE IF NOT EXISTS vendor (
            id INTEGER PRIMARY KEY,
            business_name TEXT,
            business_description TEXT,
            business_email TEXT,
            business_type TEXT,
            business_phone TEXT,
            whatsapp_number TEXT,
            gstin TEXT,
            website TEXT,
            telegram_chat_id TEXT,
            logo TEXT,
            is_onboarded BOOLEAN,
            is_active BOOLEAN,
            is_verified BOOLEAN,
            secret TEXT,
            secret_expires_at DATETIME,
            geolocation TEXT,
            handle TEXT,
            created_at DATETIME,
            updated_at DATETIME
        );
    """,

    "category": """
        CREATE TABLE IF NOT EXISTS category (
            id INTEGER PRIMARY KEY,
            name TEXT,
            description TEXT,
            parent_id INTEGER,
            is_active BOOLEAN,
            is_default BOOLEAN,
            created_at DATETIME
        );
    """,

    "product": """
        CREATE TABLE IF NOT EXISTS product (
            id INTEGER PRIMARY KEY,
            category_id INTEGER,

            name TEXT,
            description TEXT,
            price REAL,
       

            stock_quantity INTEGER,
            min_stock_level INTEGER,
            sku TEXT,
            gender TEXT,

            sizes TEXT,
            dimensions TEXT,
            image_urls TEXT,
            primary_image TEXT,

            -- ENRICHED FIELDS
            vendor_name TEXT,
            category_name TEXT,
            images_processed TEXT,
            is_in_stock BOOLEAN,

            is_active BOOLEAN,
            is_featured BOOLEAN,
            is_archived BOOLEAN,
            meta_title TEXT,
            meta_description TEXT,
            created_at DATETIME,
            updated_at DATETIME
        );
    """,

    "portfolio": """
        CREATE TABLE IF NOT EXISTS portfolio (
            id INTEGER PRIMARY KEY,
            response_json TEXT  
        );
    """,

    "portfolio_collection": """
        CREATE TABLE IF NOT EXISTS portfolio_collection (
            id INTEGER PRIMARY KEY,
            portfolio_id INTEGER,
            name TEXT,
            description TEXT,
            cover_image TEXT,
            is_featured BOOLEAN,
            is_active BOOLEAN,
            "order" INTEGER,
            slug TEXT,
            created_at DATETIME,
            updated_at DATETIME
        );
    """,

    "portfolio_collection_product": """
        CREATE TABLE IF NOT EXISTS portfolio_collection_product (
            collection_id INTEGER,
            product_id INTEGER,
            PRIMARY KEY (collection_id, product_id)
        );
    """,

    "db_version":"""
        CREATE TABLE IF NOT EXISTS db_version (
        version TEXT PRIMARY KEY,
        published_at DATETIME
        );
    """
}

FTS_SQL = [
    """
    CREATE VIRTUAL TABLE IF NOT EXISTS products_search USING fts5(
        id UNINDEXED,
        name,
        description,
        sku,
        category_name,
        vendor_name,
        tokenize='porter'
    );
    """,
    """
    INSERT INTO products_search(id, name, description, sku, category_name, vendor_name)
    SELECT id, name, description, sku, category_name, vendor_name
    FROM product
    WHERE is_active = 1 AND is_archived = 0;
    """
]