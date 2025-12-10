"""
Pydantic models for Product serialization
Matches Django's ProductListSerializer
"""

from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime


class ProductImage(BaseModel):
    """Product image schema"""
    id: int
    image_url: Optional[str] = None
    alt_text: Optional[str] = None
    is_primary: bool = False



class ProductListSerializer(BaseModel):
    id: int
    name: str
    price: str
    images: List[str] = []
    is_in_stock: bool
    is_featured: bool
    created_at: Optional[str]
    is_active: bool

class ProductListSchema(BaseModel):
    """Product list item schema"""
    id: int
    name: str
    price: float
    stock_quantity: int
    vendor_name: Optional[str] = None
    gender: Optional[str] = None
    description: Optional[str] = None
    images: List[str] = []  # List of image URLs
    is_in_stock: bool
    sizes: List[str] = []
    is_featured: bool = False
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    created_at: Optional[datetime] = None
    is_active: bool = True
    
    class Config:
        from_attributes = True


class ProductFilterParams(BaseModel):
    """Product filter parameters"""
    category: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    is_active: Optional[bool] = None
    is_featured: Optional[bool] = None


class PaginatedProductsResponse(BaseModel):
    """Paginated products response"""
    results: List[ProductListSchema]
    count: int
    total_pages: int
    current_page: int
    has_next: bool
    has_previous: bool
