Below are your models, cleaned up and consistently formatted, split by file paths. All original fields are preserved.

---

## `apps/users/models.py`

```python
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = [
        ("customer", "Customer"),
        ("vendor", "Vendor"),
        ("admin", "Admin"),
    ]

    name = models.CharField(max_length=300, blank=True, null=True)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="vendor")
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # If needed, you can customize group/permission related_name to avoid clashes.
    # groups = models.ManyToManyField(
    #     "auth.Group",
    #     related_name="customuser_groups",
    #     blank=True,
    # )
    # user_permissions = models.ManyToManyField(
    #     "auth.Permission",
    #     related_name="customuser_permissions",
    #     blank=True,
    # )

    def __str__(self) -> str:
        return f"{self.username} ({self.role})"


class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="addresses")
    street_address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    is_default = models.BooleanField(default=False)
    zip_code = models.CharField(max_length=100, null=True)
    address_type = models.CharField(
        max_length=20,
        choices=[
            ("shipping", "Shipping"),
            ("billing", "Billing"),
            ("both", "Both"),
        ],
        default="both",
    )
    longitude = models.CharField(max_length=20, null=True)
    latitude = models.CharField(max_length=20, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.street_address}, {self.city}"
```

---

## `apps/vendors/models.py`

```python
from django.conf import settings
from django.db import models
from cloudinary.models import CloudinaryField


class Vendor(models.Model):
    BUSSINES_TYPE = [
        ("clothing", "Clothing"),
        ("electronics", "Electronics"),
        ("furniture", "Furniture"),
        ("other", "Other"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="vendor",
    )
    business_name = models.CharField(max_length=200)
    business_name_slug = models.SlugField(max_length=200, blank=True, null=True)
    business_description = models.TextField(blank=True)
    business_email = models.EmailField(unique=True, null=True)
    business_type = models.CharField(max_length=25, choices=BUSSINES_TYPE, default="other")
    business_phone = models.CharField(max_length=20)
    whatsapp_number = models.CharField(max_length=20, blank=True, null=True)
    gstin = models.CharField(max_length=20, blank=True)
    website = models.URLField(blank=True, null=True)
    logo = CloudinaryField("image", folder="vendors", blank=True, null=True)
    is_onboarded = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.business_name

    @property
    def total_products(self) -> int:
        return self.products.filter(is_active=True).count()

    @property
    def average_rating(self) -> float:
        # This would be calculated from product reviews
        return 0.0
```

---

## `apps/products/models.py`

```python
from django.db import models
from cloudinary.models import CloudinaryField
from apps.vendors.models import Vendor


class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    parent = models.ForeignKey("self", on_delete=models.CASCADE, blank=True, null=True)
    vendor = models.ForeignKey(
        Vendor,
        on_delete=models.CASCADE,
        related_name="categories",
        null=True,
        blank=True,
    )
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("name", "vendor")  # vendor-specific names

    def __str__(self) -> str:
        return self.name


class Product(models.Model):
    CATEGORIES = [
        ("clothing", "clothing"),
        ("electronics", "electonics"),  # kept original spelling from your snippet
        ("sports", "sports"),
    ]

    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name="products")
    name = models.CharField(max_length=200)
    description = models.TextField()
    # category = models.CharField(choices=CATEGORIES, max_length=100)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
    )
    price = models.DecimalField(max_digits=10, decimal_places=2)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    stock_quantity = models.IntegerField(default=0)
    min_stock_level = models.IntegerField(default=5)
    sku = models.CharField(max_length=100, unique=True)
    weight = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    dimensions = models.JSONField(default=dict, blank=True)  # {length, width, height}
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.name

    @property
    def is_in_stock(self) -> bool:
        return self.stock_quantity > 0

    @property
    def is_low_stock(self) -> bool:
        return self.stock_quantity <= self.min_stock_level


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    # image = CloudinaryField('image', folder='products')  # handled by Cloudinary
    image = CloudinaryField("image")
    image_url = models.URLField(max_length=500, blank=True)
    image_b64 = models.TextField(null=True)
    alt_text = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    github_image_url = models.URLField(max_length=500, blank=True, null=True)

    def __str__(self) -> str:
        return f"Image for {self.product.name}"

    @property
    def display_url(self) -> str:
        """Return the best available image URL."""
        if self.image and hasattr(self.image, "url") and self.image.url:
            return self.image.url  # Cloudinary image (works only if config is valid)
        if self.image_url:
            return self.image_url  # fallback for manually uploaded images
        if self.github_image_url:
            return self.github_image_url  # permanent backup URL
        return "https://via.placeholder.com/300x300?text=No+Image"  # final fallback
```

---

## `apps/portfolio/models.py`

```python
from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from cloudinary.models import CloudinaryField
from apps.vendors.models import Vendor
from apps.products.models import Product


class Portfolio(models.Model):
    """Main portfolio model — one per vendor."""

    vendor = models.OneToOneField(
        Vendor,
        on_delete=models.CASCADE,
        related_name="portfolio",
    )

    # Basic Info
    display_name = models.CharField(max_length=200, help_text="Display name for portfolio")
    tagline = models.CharField(max_length=300, blank=True, help_text="Short tagline/slogan")
    slug = models.SlugField(unique=True, max_length=100)

    # Content
    about_us = models.TextField(blank=True)
    our_story = models.TextField(blank=True)
    mission = models.TextField(blank=True)
    vision = models.TextField(blank=True)

    # Media
    logo = CloudinaryField("image", folder="portfolio/logos", blank=True, null=True)
    banner_image = CloudinaryField("image", folder="portfolio/banners", blank=True, null=True)
    gallery_images = models.JSONField(default=list, blank=True)  # Array of cloudinary URLs
    title = models.CharField(max_length=255, default="My Portfolio")
    featured_products = models.ManyToManyField(
        Product,
        blank=True,
        related_name="featured_in_portfolios",
    )

    # Design Customization
    theme_color = models.CharField(max_length=7, default="#3B82F6")  # Hex color
    accent_color = models.CharField(max_length=7, default="#10B981")
    background_color = models.CharField(max_length=7, default="#FFFFFF")
    text_color = models.CharField(max_length=7, default="#1F2937")
    font_family = models.CharField(
        max_length=50,
        default="Inter",
        choices=[
            ("Inter", "Inter"),
            ("Roboto", "Roboto"),
            ("Open Sans", "Open Sans"),
            ("Poppins", "Poppins"),
            ("Montserrat", "Montserrat"),
        ],
    )

    # Layout Options
    LAYOUT_CHOICES = [
        ("modern", "Modern Grid"),
        ("classic", "Classic List"),
        ("masonry", "Masonry Layout"),
        ("minimal", "Minimal Cards"),
    ]
    layout_style = models.CharField(max_length=20, choices=LAYOUT_CHOICES, default="modern")

    # Social Media
    facebook_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    youtube_url = models.URLField(blank=True)
    website_url = models.URLField(blank=True)

    # Display Settings
    show_pricing = models.BooleanField(default=True)
    show_stock_status = models.BooleanField(default=True)
    show_contact_form = models.BooleanField(default=True)
    show_social_links = models.BooleanField(default=True)
    show_testimonials = models.BooleanField(default=True)
    show_gallery = models.BooleanField(default=True)

    # Portfolio Settings
    is_public = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    want_to_show_on_platform = models.BooleanField(default=False)  # For platform featuring
    custom_domain = models.CharField(max_length=100, blank=True, unique=True, null=True)
    custom_css = models.TextField(blank=True, help_text="Custom CSS for advanced styling")

    # SEO
    meta_title = models.CharField(max_length=60, blank=True)
    meta_description = models.CharField(max_length=160, blank=True)
    meta_keywords = models.CharField(max_length=200, blank=True)

    # Analytics
    view_count = models.PositiveIntegerField(default=0)
    last_viewed = models.DateTimeField(null=True, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]
        verbose_name = "Portfolio"
        verbose_name_plural = "Portfolios"

    def save(self, *args, **kwargs) -> None:
        if not self.slug:
            base_slug = slugify(self.display_name or self.vendor.business_name)
            self.slug = base_slug
            # Ensure unique slug
            counter = 1
            while Portfolio.objects.filter(slug=self.slug).exists():
                self.slug = f"{base_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)

    def get_absolute_url(self) -> str:
        return reverse("portfolio:public_view", kwargs={"slug": self.slug})

    def get_featured_products(self):
        return self.vendor.products.filter(
            is_active=True,
            is_featured=True,
            is_archived=False,
        )[:8]

    def get_all_products(self):
        return self.vendor.products.filter(
            is_active=True,
            is_archived=False,
        )

    def __str__(self) -> str:
        return f"{self.display_name or self.vendor.business_name} Portfolio"


class PortfolioSection(models.Model):
    """Custom sections for portfolio (About, Services, etc.)."""

    portfolio = models.ForeignKey(
        Portfolio, on_delete=models.CASCADE, related_name="sections"
    )
    title = models.CharField(max_length=100)
    content = models.TextField()
    section_type = models.CharField(
        max_length=20,
        choices=[
            ("text", "Text Content"),
            ("gallery", "Image Gallery"),
            ("video", "Video Embed"),
            ("testimonials", "Testimonials"),
            ("contact", "Contact Form"),
        ],
        default="text",
    )
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order"]
        unique_together = ["portfolio", "title"]


class PortfolioCollection(models.Model):
    """Product collections within portfolio."""

    portfolio = models.ForeignKey(
        Portfolio, on_delete=models.CASCADE, related_name="collections"
    )
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    cover_image = CloudinaryField("image", blank=True, null=True)
    products = models.ManyToManyField(Product, related_name="portfolio_collections")

    # Display settings
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    # SEO
    slug = models.SlugField(max_length=100)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order", "name"]
        unique_together = ["portfolio", "slug"]

    def save(self, *args, **kwargs) -> None:
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.portfolio.display_name} - {self.name}"


class PortfolioTestimonial(models.Model):
    """Customer testimonials for portfolio."""

    portfolio = models.ForeignKey(
        Portfolio, on_delete=models.CASCADE, related_name="testimonials"
    )
    customer_name = models.CharField(max_length=100)
    customer_email = models.EmailField(blank=True)
    customer_image = CloudinaryField(
        "image", folder="portfolio/testimonials", blank=True, null=True
    )
    customer_designation = models.CharField(max_length=100, blank=True)
    company = models.CharField(max_length=100, blank=True)

    testimonial_text = models.TextField()
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)], default=5)

    # Display settings
    is_featured = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "-created_at"]

    def __str__(self) -> str:
        return f"Testimonial by {self.customer_name} for {self.portfolio.display_name}"


class PortfolioAnalytics(models.Model):
    """Analytics tracking for portfolio."""

    portfolio = models.ForeignKey(
        Portfolio, on_delete=models.CASCADE, related_name="analytics"
    )

    # Metrics
    date = models.DateField()
    page_views = models.PositiveIntegerField(default=0)
    unique_visitors = models.PositiveIntegerField(default=0)
    product_views = models.PositiveIntegerField(default=0)
    contact_form_submissions = models.PositiveIntegerField(default=0)
    social_link_clicks = models.PositiveIntegerField(default=0)

    # Traffic sources
    direct_traffic = models.PositiveIntegerField(default=0)
    social_traffic = models.PositiveIntegerField(default=0)
    search_traffic = models.PositiveIntegerField(default=0)
    referral_traffic = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["portfolio", "date"]
        ordering = ["-date"]


class PortfolioContactInquiry(models.Model):
    """Contact form submissions."""

    portfolio = models.ForeignKey(
        Portfolio, on_delete=models.CASCADE, related_name="inquiries"
    )

    # Contact details
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    subject = models.CharField(max_length=200)
    message = models.TextField()

    # Product inquiry (optional)
    product = models.ForeignKey(
        Product, on_delete=models.SET_NULL, null=True, blank=True, related_name="portfolio_inquiries"
    )

    # Status
    STATUS_CHOICES = [
        ("new", "New"),
        ("read", "Read"),
        ("replied", "Replied"),
        ("closed", "Closed"),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="new")

    # Metadata
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Inquiry from {self.name} for {self.portfolio.display_name}"


class PortfolioTheme(models.Model):
    """Pre-built themes for portfolios."""

    name = models.CharField(max_length=100)
    description = models.TextField()
    preview_image = CloudinaryField("image", folder="portfolio/themes")

    # Theme configuration (JSON)
    theme_config = models.JSONField(default=dict)
    # Example: {
    #     "colors": {"primary": "#3B82F6", "secondary": "#10B981"},
    #     "layout": "modern",
    #     "fonts": {"heading": "Poppins", "body": "Inter"}
    # }

    is_active = models.BooleanField(default=True)
    is_premium = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "name"]

    def __str__(self) -> str:
        return self.name
```

---


