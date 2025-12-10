from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional, Dict, Any


class SocialLinks(BaseModel):
    facebook: Optional[str] = None
    instagram: Optional[str] = None
    twitter: Optional[str] = None
    linkedin: Optional[str] = None
    youtube: Optional[str] = None


class ProductBasic(BaseModel):
    id: int
    name: str
    price: str
    stock_quantity: int
    description: str
    images: List[str]
    is_in_stock: bool
    is_featured: bool
    created_at: str
    is_active: bool


class PortfolioSchema(BaseModel):
    id: int
    business_name: str
    display_name: str
    tagline: Optional[str]
    slug: str
    business_name_slug: str
    about_us: Optional[str]

    theme_color: Optional[str]
    accent_color: Optional[str]
    background_color: Optional[str]
    font_family: Optional[str]
    text_color: Optional[str] = None
    layout_style: Optional[str] = None

    show_pricing: bool = True
    show_contact_form: bool = True
    is_public: bool = True
    is_carousel:bool = False
    show_stock_status:bool = False

    view_count: int = 0
    total_collections: int = 0
    total_testimonials: int = 0

    featured_products: List[ProductBasic] = []

    banner_image: Optional[str]
    logo: Optional[str]
    gallery_images: List[Any] = []
    carousel_images: List[Any] = []
    

    contact_email: Optional[str]
    contact_phone: Optional[str]
    whatsapp_number: Optional[str]

    social_links: SocialLinks

    address: Optional[Any]

    created_at: Optional[str]
    updated_at: Optional[str]
