"""
Data mapping utilities for transforming Elasticsearch results
to match Django serializer response formats
"""
from typing import Dict, Any, List


def map_es_hit(hit: Dict[str, Any]) -> Dict[str, Any]:
    """
    Map a single Elasticsearch hit to a flattened document
    
    Args:
        hit: Elasticsearch hit object with '_source' field
    
    Returns:
        Flattened document with fields from '_source'
    """
    source = hit.get("_source", {})
    return source


def map_es_hits(hits: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Map multiple Elasticsearch hits to a list of documents
    
    Args:
        hits: List of Elasticsearch hit objects
    
    Returns:
        List of flattened documents
    """
    return [map_es_hit(hit) for hit in hits]


def map_es_search_response(response: Dict[str, Any]) -> tuple[List[Dict], int]:
    """
    Extract results and total count from Elasticsearch search response
    
    Args:
        response: Elasticsearch search response
    
    Returns:
        Tuple of (results list, total count)
    """
    hits = response.get("hits", {}).get("hits", [])
    total = response.get("hits", {}).get("total", {})
    
    # Handle Elasticsearch 7.x vs 8.x total format
    if isinstance(total, dict):
        total_count = total.get("value", 0)
    else:
        total_count = total
    
    results = map_es_hits(hits)
    
    return results, total_count
