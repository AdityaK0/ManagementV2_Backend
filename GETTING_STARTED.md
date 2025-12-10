# Getting Started with FastAPI Portfolio API

## Quick Start

### 1. Set Up Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
cp .env.example .env
# Edit .env with your Elasticsearch configuration
```

### 4. Run the Application

```bash
uvicorn main:app --reload
```

Visit:
- API: http://localhost:8000
- Swagger Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Testing the API

### Example Requests

1. **Get Portfolio**
```bash
curl http://localhost:8000/api/portfolio/public/riddhi-amporium-3/
```

2. **Get Products**
```bash
curl http://localhost:8000/api/portfolio/public/riddhi-amporium-3/products/?page=1&page_size=10
```

3. **Search Products**
```bash
curl "http://localhost:8000/api/portfolio/public/riddhi-amporium-3/products/?search=shirt"
```

4. **Filter Products**
```bash
curl "http://localhost:8000/api/portfolio/public/riddhi-amporium-3/products/filter/?min_price=100&max_price=500"
```

5. **Get Collections**
```bash
curl http://localhost:8000/api/portfolio/public/riddhi-amporium-3/collections/
```

## Next Steps

1. **Set up Elasticsearch** - Ensure ES is running and accessible
2. **Index your data** - Populate ES indices with portfolio, product, and collection data
3. **Map your fields** - Ensure ES document structure matches expected fields (see README.md)
4. **Test endpoints** - Use the examples above to verify data retrieval
5. **Production setup** - Configure CORS, add authentication, set up logging

## Troubleshooting

### Elasticsearch Connection Issues

- Verify ES is running: `curl http://localhost:9200`
- Check `.env` has correct `ES_HOST`
- Ensure network connectivity

### Import Errors

- Verify you're in the correct directory
- Check virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`

### No Data Returned

- Verify data exists in Elasticsearch indices
- Check index names match `.env` configuration
- Ensure `vendor_slug` field in documents matches the `business_name` in URL
