# Lambda SQLite Builder

This folder contains the Serverless builder for per-vendor SQLite databases.

## 📂 Structure
- `handler.py`: Main Lambda entry point.
- `builder/`: logic for fetching Postgres data, building SQLite, and uploading.
- `layers/`: Instructions to build dependencies layer.
- `django_integration/`: Code snippet for Django DRF View.

## 🚀 Deployment Steps

### 1. Build and Deploy Layer
Follow instructions in `layers/README.md` to create `psycopg2` + `redis` layer.
Attach this layer to your Lambda function.

### 2. Deploy Lambda Function
You can zip this folder (excluding `layers/` and `venv`) and upload.

**Using Zip:**
```bash
# From lambda_sqlite_builder directory
zip -r lambda_function.zip . -x "layers/*" -x "django_integration/*"
```
Upload `lambda_function.zip` to AWS Lambda.
Set Handler: `handler.handler`
Runtime: `Python 3.10` (includes SQLite with FTS5 support).

### 3. Environment Variables
Set the following in Lambda Configuration:

- `DB_HOST`: Postgres Host
- `DB_NAME`: Database Name
- `DB_USER`: Postgres User
- `DB_PASSWORD`: Postgres Password
- `DB_PORT`: 5432
- `S3_BUCKET_NAME`: Your S3 bucket name
- `REDIS_URL`: `redis://host:port` (if using ElastiCache, ensure VPC access)

### 4. IAM Permissions
The Lambda Execution Role needs:
- **S3 Write Access**: `s3:PutObject` on `arn:aws:s3:::YOUR_BUCKET/sqlite_cache/*`
- **VPCAccess** (if RDS/Redis are in VPC): `AWSLambdaVPCAccessExecutionRole`

### 5. FastAPI Integration
In your FastAPI `main.py` or startup logic, add:
```python
import asyncio
from background.redis_listener import start_background_listener

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(start_background_listener())
```

### 6. DRF Integration
Copy `django_integration/views.py` to your Django app and map the URL:
```python
path('internal/publish/<slug:vendor_slug>/', PublishVendorPortfolioView.as_view())
```

## 🔄 How it works
1. **DRF** calls `POST /internal/publish/{vendor_slug}`.
2. **Lambda** fetches all data for vendor from **Postgres**.
3. **Lambda** creates clean SQLite DB with FTS5.
4. **Lambda** uploads to S3 (`sqlite_cache/vendor.db`).
5. **Lambda** publishes "Ready" event to **Redis**.
6. **FastAPI** (listener) sees event, downloads DB, and hot-swaps the file.
