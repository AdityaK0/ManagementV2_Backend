from elasticsearch import Elasticsearch
from config import settings


def get_es_sync_client() -> Elasticsearch:
    """
    Sync ES client for CLI scripts — avoid async warnings
    """
    host = settings.ES_HOST.strip()

    if not host.startswith(("http://", "https://")):
        host = f"http://{host}"

    return Elasticsearch(
        hosts=[host],
        basic_auth=(settings.ES_USER, settings.ES_PASS) if settings.ES_USER else None,
        verify_certs=False,
        request_timeout=30,
    )
