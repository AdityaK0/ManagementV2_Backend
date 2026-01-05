"""
FastAPI Portfolio API - Main Application Entry Point
Serves public portfolio APIs backed by Elasticsearch
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import portfolio, products, collections
from db.connection import init_pg_pool

app = FastAPI(
    title="Portfolio API",
    description="Public portfolio APIs backed by Elasticsearch",
    version="1.0.0"
)

@app.on_event("startup")
def startup():
    init_pg_pool()



app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately in production
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Latency tracking middleware (for performance monitoring)
# from middleware.latency_tracker import track_latency_middleware
# app.middleware("http")(track_latency_middleware)

# Include routers
app.include_router(portfolio.router, tags=["portfolio"])
app.include_router(products.router, tags=["products"])
app.include_router(collections.router, tags=["collections"])

# Internal API (for DRF/Dev integration)
from api import internal
app.include_router(internal.router, prefix="/internal", tags=["internal"])



@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Portfolio API is running"}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
