"""
Elasticsearch client configuration and management
Uses AsyncElasticsearch for async operations
"""

from contextlib import asynccontextmanager
from elasticsearch import AsyncElasticsearch
from config import settings


def get_es_client() -> AsyncElasticsearch:
    """
    Create and return an AsyncElasticsearch client
    """
    host = settings.ES_HOST.strip()

    # ✅ Ensure host has http:// or https:// scheme
    if not host.startswith(("http://", "https://")):
        host = f"http://{host}"

    return AsyncElasticsearch(
        hosts=[host],  # ✅ use the corrected host string
        basic_auth=(settings.ES_USER, settings.ES_PASS) if settings.ES_USER else None,
        verify_certs=False,  # ✅ for local ES, disable SSL verify
        request_timeout=30,
    )


@asynccontextmanager
async def get_es_context():
    """
    Usage:
        async with get_es_context() as es:
            result = await es.search(...)
    """
    client = get_es_client()
    try:
        yield client
    finally:
        await client.close()
