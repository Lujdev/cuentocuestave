from dataclasses import dataclass, field
from decimal import Decimal
from uuid import UUID


@dataclass(frozen=True)
class Product:
    id: UUID
    slug: str
    display_name: str
    brand: str | None
    canonical_unit: str  # "kg" | "l" | "unidad"
    canonical_pack_size: Decimal
    category: str
    is_basic_basket: bool
    image_url: str | None
    published: bool


@dataclass(frozen=True)
class ProductListing:
    id: UUID
    supermarket_id: UUID
    external_id: str
    raw_name: str
    raw_brand: str | None
    raw_unit: str | None
    raw_category: str | None
    image_url: str | None
    product_url: str | None
    match_status: str  # "pending" | "matched" | "ambiguous" | "rejected"
    canonical_product_id: UUID | None = None
    match_confidence: Decimal | None = None
    match_method: str | None = None  # "auto" | "llm" | "manual"
    embedding: list[float] = field(default_factory=list)
