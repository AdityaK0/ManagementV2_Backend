# DVMSPortfolioBackend
# FastAPI Portfolio API

A FastAPI application serving public portfolio APIs backed by Elasticsearch.

## Overview

This FastAPI application provides public-facing portfolio APIs that are backed by Elasticsearch instead of PostgreSQL. It serves:

- Portfolio overview
- Products listing with search and filtering
- Collections

## Installation

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your Elasticsearch configuration
```

## Running the Application

Start the development server:
```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

API documentation:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Project Structure

```
fastapi_portfolio/
├── main.py                 # Application entry point
├── config.py              # Configuration settings
├── .env                   # Environment variables
├── requirements.txt       # Python dependencies
├── api/                   # API routers
│   ├── portfolio.py      # Portfolio endpoints
│   ├── products.py       # Product endpoints
│   └── collections.py    # Collection endpoints
├── services/              # Business logic
│   ├── es_client.py      # Elasticsearch client
│   ├── portfolio_service.py
│   ├── product_service.py
│   └── collection_service.py
├── serializers/           # Pydantic models
│   ├── portfolio_serializer.py
│   ├── product_serializer.py
│   └── collection_serializer.py
└── utils/                 # Utilities
    ├── pagination.py      # Pagination helpers
    └── mapper.py          # ES response mapping
```

## API Endpoints

### Portfolio
- `GET /api/portfolio/public/{business_name}/` - Get vendor portfolio summary

### Products
- `GET /api/portfolio/public/{business_name}/products/` - Get paginated products
  - Query params: `page`, `page_size`, `search`
- `GET /api/portfolio/public/{business_name}/products/filter/` - Get filtered products
  - Query params: `category`, `min_price`, `max_price`, `is_active`, `page`, `page_size`

### Collections
- `GET /api/portfolio/public/{business_name}/collections/` - Get all active collections

## Environment Variables

- `ES_HOST`: Elasticsearch host (e.g., `localhost:9200`)
- `ES_USER`: Elasticsearch username (optional)
- `ES_PASS`: Elasticsearch password (optional)
- `PRODUCTS_INDEX`: Elasticsearch index for products
- `COLLECTIONS_INDEX`: Elasticsearch index for collections
- `PORTFOLIOS_INDEX`: Elasticsearch index for portfolios

## Next Steps

1. Index your data in Elasticsearch
2. Configure Elasticsearch mappings to match expected fields
3. Implement the TODO sections in service files
4. Add comprehensive error handling and logging
5. Add request validation and rate limiting
6. Configure proper CORS settings for production

## Elasticsearch Index Structure

### Expected Document Fields

#### Portfolio Document
- `id`, `vendor_slug`, `business_name`, `display_name`, `tagline`, `slug`
- `about_us`, `theme_color`, `accent_color`, `layout_style`
- `show_pricing`, `show_contact_form`, `is_public`
- `view_count`, `total_collections`, `total_testimonials`
- `featured_products` (array or nested)
- `banner_image`, `logo`, `gallery_images`
- `contact_email`, `contact_phone`, `address`, `whatsapp_number`
- `facebook_url`, `instagram_url`, `twitter_url`, `linkedin_url`, `youtube_url`
- `created_at`, `updated_at`

#### Product Document
- `id`, `vendor_slug`, `name`, `description`, `price`
- `stock_quantity`, `is_active`, `is_archived`, `is_featured`
- `sku`, `category`, `images` (array or nested)
- `vendor_name`, `is_in_stock`
- `meta_title`, `meta_description`
- `created_at`

#### Collection Document
- `id`, `vendor_slug`, `name`, `description`
- `cover_image`, `slug`, `is_featured`, `is_active`, `order`
- `products` (array or nested), `product_count`
- `created_at`

## Development Notes

- All service functions use async/await for Elasticsearch operations
- Response formats match Django's serializers for compatibility
- Pagination follows Django REST Framework conventions
- Error handling is basic and should be enhanced for production
- CORS is currently open; configure appropriately for production
