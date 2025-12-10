"""
Pagination utilities for converting page/page_size to Elasticsearch from/size
"""

from typing import Dict
from config import settings


def get_pagination(page: int = 1, page_size: int = 10) -> Dict[str, int]:
    """
    Convert page and page_size to Elasticsearch 'from_' and 'size' parameters
    
    Args:
        page: Current page number (1-indexed)
        page_size: Number of items per page
    
    Returns:
        Dict with 'from_' and 'size' keys
    
    Example:
        get_pagination(page=2, page_size=20) -> {"from_": 20, "size": 20}
    """
    # Ensure page_size is within limits
    page_size = min(page_size, settings.MAX_PAGE_SIZE)
    page_size = max(page_size, 1)
    
    # Calculate from_
    from_ = (page - 1) * page_size
    
    return {"from_": from_, "size": page_size}


def format_paginated_response(
    results: list,
    count: int,
    current_page: int,
    page_size: int
) -> Dict:
    """
    Format response data with pagination metadata
    
    Args:
        results: List of items for current page
        count: Total number of items
        current_page: Current page number
        page_size: Number of items per page
    
    Returns:
        Dict with results and pagination metadata matching Django's format
    """
    total_pages = (count + page_size - 1) // page_size if count > 0 else 0
    
    return {
        "results": results,
        "count": count,
        "total_pages": total_pages,
        "current_page": current_page,
        "has_next": current_page < total_pages,
        "has_previous": current_page > 1,
    }
