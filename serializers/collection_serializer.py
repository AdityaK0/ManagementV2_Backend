"""
Pydantic models for Collection serialization
Matches Django's PortfolioCollectionSerializer
"""

from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from serializers.product_serializer import ProductListSchema


class PortfolioCollectionSchema(BaseModel):
    """Portfolio collection schema"""
    id: int
    name: str
    description: Optional[str] = None
    cover_image: Optional[str] = None
    slug: str
    is_featured: bool = False
    is_active: bool = True
    order: int = 0
    products: List[ProductListSchema] = []
    cover_image_url: Optional[str] = None
    product_count: int = 0
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
