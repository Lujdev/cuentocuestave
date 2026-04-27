"""SQLAlchemy 2.0 declarative models — mirrors the domain data model."""
from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID, uuid4

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, NUMRANGE, UUID as PG_UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    pass


class Supermarket(Base):
    __tablename__ = "supermarkets"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    slug: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String(256), nullable=False)
    base_url: Mapped[str] = mapped_column(String(512), nullable=False)
    currency: Mapped[str] = mapped_column(String(8), default="USD")
    scraping_strategy: Mapped[str] = mapped_column(String(32), default="playwright")
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    listings: Mapped[list["ProductListing"]] = relationship(back_populates="supermarket")


class Product(Base):
    __tablename__ = "products"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    slug: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String(256), nullable=False)
    brand: Mapped[Optional[str]] = mapped_column(String(128))
    canonical_unit: Mapped[str] = mapped_column(String(16), nullable=False)
    canonical_pack_size: Mapped[Decimal] = mapped_column(Numeric(10, 3), nullable=False)
    category: Mapped[str] = mapped_column(String(64), nullable=False)
    is_basic_basket: Mapped[bool] = mapped_column(Boolean, default=False)
    image_url: Mapped[Optional[str]] = mapped_column(String(1024))
    description: Mapped[Optional[str]] = mapped_column(Text)
    published: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    listings: Mapped[list["ProductListing"]] = relationship(back_populates="canonical_product")


class ProductListing(Base):
    __tablename__ = "product_listings"
    __table_args__ = (
        UniqueConstraint("supermarket_id", "external_id"),
        Index("ix_product_listings_embedding", "embedding", postgresql_using="ivfflat"),
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    supermarket_id: Mapped[UUID] = mapped_column(ForeignKey("supermarkets.id"), nullable=False)
    external_id: Mapped[str] = mapped_column(String(256), nullable=False)
    raw_name: Mapped[str] = mapped_column(String(512), nullable=False)
    raw_brand: Mapped[Optional[str]] = mapped_column(String(128))
    raw_unit: Mapped[Optional[str]] = mapped_column(String(64))
    raw_category: Mapped[Optional[str]] = mapped_column(String(128))
    image_url: Mapped[Optional[str]] = mapped_column(String(1024))
    product_url: Mapped[Optional[str]] = mapped_column(String(1024))
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    first_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    embedding: Mapped[Optional[list[float]]] = mapped_column(Vector(384))
    match_status: Mapped[str] = mapped_column(String(16), default="pending")
    canonical_product_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("products.id"))
    match_confidence: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 4))
    match_method: Mapped[Optional[str]] = mapped_column(String(16))

    supermarket: Mapped["Supermarket"] = relationship(back_populates="listings")
    canonical_product: Mapped[Optional["Product"]] = relationship(back_populates="listings")
    prices: Mapped[list["Price"]] = relationship(back_populates="listing")


class Price(Base):
    __tablename__ = "prices"
    __table_args__ = (
        Index("ix_prices_listing_observed", "product_listing_id", "observed_at"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    product_listing_id: Mapped[UUID] = mapped_column(ForeignKey("product_listings.id"), nullable=False)
    price_local: Mapped[Decimal] = mapped_column(Numeric(14, 4), nullable=False)
    currency: Mapped[str] = mapped_column(String(8), nullable=False)
    price_usd: Mapped[Decimal] = mapped_column(Numeric(14, 4), nullable=False)
    price_ves_bcv: Mapped[Optional[Decimal]] = mapped_column(Numeric(20, 4))
    price_ves_paralelo: Mapped[Optional[Decimal]] = mapped_column(Numeric(20, 4))
    unit_price_usd: Mapped[Decimal] = mapped_column(Numeric(14, 6), nullable=False)
    available: Mapped[bool] = mapped_column(Boolean, default=True)
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    scrape_run_id: Mapped[UUID] = mapped_column(ForeignKey("scrape_runs.id"), nullable=False)

    listing: Mapped["ProductListing"] = relationship(back_populates="prices")


class ExchangeRate(Base):
    __tablename__ = "exchange_rates"
    __table_args__ = (
        Index("ix_exchange_rates_source_observed", "source", "observed_at"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    source: Mapped[str] = mapped_column(String(32), nullable=False)
    rate_ves_per_usd: Mapped[Decimal] = mapped_column(Numeric(20, 4), nullable=False)
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    raw_payload: Mapped[Optional[dict]] = mapped_column(JSONB)


class MinimumWageHistory(Base):
    __tablename__ = "minimum_wage_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    effective_from: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    effective_to: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    amount_ves: Mapped[Decimal] = mapped_column(Numeric(20, 4), nullable=False)
    amount_usd_at_decree: Mapped[Optional[Decimal]] = mapped_column(Numeric(14, 4))
    decree_reference: Mapped[Optional[str]] = mapped_column(Text)
    source_url: Mapped[Optional[str]] = mapped_column(String(1024))


class ScrapeRun(Base):
    __tablename__ = "scrape_runs"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    supermarket_id: Mapped[UUID] = mapped_column(ForeignKey("supermarkets.id"), nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(16), default="running")
    items_seen: Mapped[int] = mapped_column(Integer, default=0)
    items_new: Mapped[int] = mapped_column(Integer, default=0)
    items_updated: Mapped[int] = mapped_column(Integer, default=0)
    errors_count: Mapped[int] = mapped_column(Integer, default=0)
    error_summary: Mapped[Optional[dict]] = mapped_column(JSONB)
    worker_version: Mapped[Optional[str]] = mapped_column(String(64))
    scrapling_version: Mapped[Optional[str]] = mapped_column(String(32))


class MatchingDecision(Base):
    __tablename__ = "matching_decisions"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    product_listing_id: Mapped[UUID] = mapped_column(ForeignKey("product_listings.id"), nullable=False)
    decided_canonical_product_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("products.id"))
    method: Mapped[str] = mapped_column(String(16), nullable=False)
    confidence: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 4))
    llm_model: Mapped[Optional[str]] = mapped_column(String(128))
    llm_prompt_hash: Mapped[Optional[str]] = mapped_column(String(64))
    llm_response: Mapped[Optional[dict]] = mapped_column(JSONB)
    decided_by: Mapped[str] = mapped_column(String(16), default="auto")
    decided_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Forecast(Base):
    __tablename__ = "forecasts"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    product_id: Mapped[UUID] = mapped_column(ForeignKey("products.id"), nullable=False)
    model: Mapped[str] = mapped_column(String(32), nullable=False)
    horizon_days: Mapped[int] = mapped_column(Integer, nullable=False)
    predicted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    target_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    yhat: Mapped[Decimal] = mapped_column(Numeric(14, 4), nullable=False)
    yhat_lower: Mapped[Decimal] = mapped_column(Numeric(14, 4), nullable=False)
    yhat_upper: Mapped[Decimal] = mapped_column(Numeric(14, 4), nullable=False)
    currency: Mapped[str] = mapped_column(String(8), default="USD")


class Anomaly(Base):
    __tablename__ = "anomalies"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    product_listing_id: Mapped[UUID] = mapped_column(ForeignKey("product_listings.id"), nullable=False)
    detected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    score: Mapped[Decimal] = mapped_column(Numeric(8, 6), nullable=False)
    model: Mapped[str] = mapped_column(String(32), nullable=False)
    price_observed: Mapped[Decimal] = mapped_column(Numeric(14, 4), nullable=False)
    reviewed: Mapped[bool] = mapped_column(Boolean, default=False)
    reviewed_by: Mapped[Optional[str]] = mapped_column(String(128))


class ProductCluster(Base):
    __tablename__ = "product_clusters"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    product_id: Mapped[UUID] = mapped_column(ForeignKey("products.id"), nullable=False)
    cluster_id: Mapped[int] = mapped_column(Integer, nullable=False)
    algorithm: Mapped[str] = mapped_column(String(32), nullable=False)
    version: Mapped[str] = mapped_column(String(32), nullable=False)
    assigned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
