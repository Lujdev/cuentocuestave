"""fase1_initial_schema

Revision ID: b04142d2a334
Revises:
Create Date: 2026-04-27 09:07:05.853512

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

# revision identifiers, used by Alembic.
revision: str = "b04142d2a334"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Enable pgvector extension
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "supermarkets",
        sa.Column("id", PG_UUID(as_uuid=True), primary_key=True),
        sa.Column("slug", sa.String(64), nullable=False, unique=True),
        sa.Column("display_name", sa.String(256), nullable=False),
        sa.Column("base_url", sa.String(512), nullable=False),
        sa.Column("currency", sa.String(8), server_default="USD"),
        sa.Column("scraping_strategy", sa.String(32), server_default="playwright"),
        sa.Column("enabled", sa.Boolean(), server_default="true"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
    )

    op.create_table(
        "products",
        sa.Column("id", PG_UUID(as_uuid=True), primary_key=True),
        sa.Column("slug", sa.String(128), nullable=False, unique=True),
        sa.Column("display_name", sa.String(256), nullable=False),
        sa.Column("brand", sa.String(128)),
        sa.Column("canonical_unit", sa.String(16), nullable=False),
        sa.Column("canonical_pack_size", sa.Numeric(10, 3), nullable=False),
        sa.Column("category", sa.String(64), nullable=False),
        sa.Column("is_basic_basket", sa.Boolean(), server_default="false"),
        sa.Column("image_url", sa.String(1024)),
        sa.Column("description", sa.Text()),
        sa.Column("published", sa.Boolean(), server_default="false"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
    )

    op.create_table(
        "scrape_runs",
        sa.Column("id", PG_UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "supermarket_id",
            PG_UUID(as_uuid=True),
            sa.ForeignKey("supermarkets.id"),
            nullable=False,
        ),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True)),
        sa.Column("status", sa.String(16), server_default="running"),
        sa.Column("items_seen", sa.Integer(), server_default="0"),
        sa.Column("items_new", sa.Integer(), server_default="0"),
        sa.Column("items_updated", sa.Integer(), server_default="0"),
        sa.Column("errors_count", sa.Integer(), server_default="0"),
        sa.Column("error_summary", JSONB()),
        sa.Column("worker_version", sa.String(64)),
        sa.Column("scrapling_version", sa.String(32)),
    )

    op.create_table(
        "product_listings",
        sa.Column("id", PG_UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "supermarket_id",
            PG_UUID(as_uuid=True),
            sa.ForeignKey("supermarkets.id"),
            nullable=False,
        ),
        sa.Column("external_id", sa.String(256), nullable=False),
        sa.Column("raw_name", sa.String(512), nullable=False),
        sa.Column("raw_brand", sa.String(128)),
        sa.Column("raw_unit", sa.String(64)),
        sa.Column("raw_category", sa.String(128)),
        sa.Column("image_url", sa.String(1024)),
        sa.Column("product_url", sa.String(1024)),
        sa.Column(
            "last_seen_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
        sa.Column(
            "first_seen_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
        sa.Column("embedding", Vector(384)),
        sa.Column("match_status", sa.String(16), server_default="pending"),
        sa.Column(
            "canonical_product_id",
            PG_UUID(as_uuid=True),
            sa.ForeignKey("products.id"),
        ),
        sa.Column("match_confidence", sa.Numeric(5, 4)),
        sa.Column("match_method", sa.String(16)),
        sa.UniqueConstraint("supermarket_id", "external_id"),
    )
    op.create_index(
        "ix_product_listings_embedding",
        "product_listings",
        ["embedding"],
        postgresql_using="ivfflat",
    )

    op.create_table(
        "prices",
        sa.Column(
            "id", sa.BigInteger(), primary_key=True, autoincrement=True
        ),
        sa.Column(
            "product_listing_id",
            PG_UUID(as_uuid=True),
            sa.ForeignKey("product_listings.id"),
            nullable=False,
        ),
        sa.Column("price_local", sa.Numeric(14, 4), nullable=False),
        sa.Column("currency", sa.String(8), nullable=False),
        sa.Column("price_usd", sa.Numeric(14, 4), nullable=False),
        sa.Column("price_ves_bcv", sa.Numeric(20, 4)),
        sa.Column("price_ves_paralelo", sa.Numeric(20, 4)),
        sa.Column("unit_price_usd", sa.Numeric(14, 6), nullable=False),
        sa.Column("available", sa.Boolean(), server_default="true"),
        sa.Column("observed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "scrape_run_id",
            PG_UUID(as_uuid=True),
            sa.ForeignKey("scrape_runs.id"),
            nullable=False,
        ),
    )
    op.create_index(
        "ix_prices_listing_observed",
        "prices",
        ["product_listing_id", "observed_at"],
    )

    op.create_table(
        "exchange_rates",
        sa.Column(
            "id", sa.BigInteger(), primary_key=True, autoincrement=True
        ),
        sa.Column("source", sa.String(32), nullable=False),
        sa.Column("rate_ves_per_usd", sa.Numeric(20, 4), nullable=False),
        sa.Column("observed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("raw_payload", JSONB()),
    )
    op.create_index(
        "ix_exchange_rates_source_observed",
        "exchange_rates",
        ["source", "observed_at"],
    )

    op.create_table(
        "minimum_wage_history",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("effective_from", sa.DateTime(timezone=True), nullable=False),
        sa.Column("effective_to", sa.DateTime(timezone=True)),
        sa.Column("amount_ves", sa.Numeric(20, 4), nullable=False),
        sa.Column("amount_usd_at_decree", sa.Numeric(14, 4)),
        sa.Column("decree_reference", sa.Text()),
        sa.Column("source_url", sa.String(1024)),
    )

    op.create_table(
        "matching_decisions",
        sa.Column(
            "id", sa.BigInteger(), primary_key=True, autoincrement=True
        ),
        sa.Column(
            "product_listing_id",
            PG_UUID(as_uuid=True),
            sa.ForeignKey("product_listings.id"),
            nullable=False,
        ),
        sa.Column(
            "decided_canonical_product_id",
            PG_UUID(as_uuid=True),
            sa.ForeignKey("products.id"),
        ),
        sa.Column("method", sa.String(16), nullable=False),
        sa.Column("confidence", sa.Numeric(5, 4)),
        sa.Column("llm_model", sa.String(128)),
        sa.Column("llm_prompt_hash", sa.String(64)),
        sa.Column("llm_response", JSONB()),
        sa.Column("decided_by", sa.String(16), server_default="auto"),
        sa.Column(
            "decided_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
    )

    op.create_table(
        "forecasts",
        sa.Column(
            "id", sa.BigInteger(), primary_key=True, autoincrement=True
        ),
        sa.Column(
            "product_id",
            PG_UUID(as_uuid=True),
            sa.ForeignKey("products.id"),
            nullable=False,
        ),
        sa.Column("model", sa.String(32), nullable=False),
        sa.Column("horizon_days", sa.Integer(), nullable=False),
        sa.Column(
            "predicted_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
        sa.Column("target_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("yhat", sa.Numeric(14, 4), nullable=False),
        sa.Column("yhat_lower", sa.Numeric(14, 4), nullable=False),
        sa.Column("yhat_upper", sa.Numeric(14, 4), nullable=False),
        sa.Column("currency", sa.String(8), server_default="USD"),
    )

    op.create_table(
        "anomalies",
        sa.Column(
            "id", sa.BigInteger(), primary_key=True, autoincrement=True
        ),
        sa.Column(
            "product_listing_id",
            PG_UUID(as_uuid=True),
            sa.ForeignKey("product_listings.id"),
            nullable=False,
        ),
        sa.Column(
            "detected_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
        sa.Column("score", sa.Numeric(8, 6), nullable=False),
        sa.Column("model", sa.String(32), nullable=False),
        sa.Column("price_observed", sa.Numeric(14, 4), nullable=False),
        sa.Column("reviewed", sa.Boolean(), server_default="false"),
        sa.Column("reviewed_by", sa.String(128)),
    )

    op.create_table(
        "product_clusters",
        sa.Column(
            "id", sa.BigInteger(), primary_key=True, autoincrement=True
        ),
        sa.Column(
            "product_id",
            PG_UUID(as_uuid=True),
            sa.ForeignKey("products.id"),
            nullable=False,
        ),
        sa.Column("cluster_id", sa.Integer(), nullable=False),
        sa.Column("algorithm", sa.String(32), nullable=False),
        sa.Column("version", sa.String(32), nullable=False),
        sa.Column(
            "assigned_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
    )


def downgrade() -> None:
    op.drop_table("product_clusters")
    op.drop_table("anomalies")
    op.drop_table("forecasts")
    op.drop_table("matching_decisions")
    op.drop_table("minimum_wage_history")
    op.drop_index("ix_prices_listing_observed", table_name="prices")
    op.drop_table("prices")
    op.drop_index("ix_product_listings_embedding", table_name="product_listings")
    op.drop_table("product_listings")
    op.drop_table("scrape_runs")
    op.drop_table("products")
    op.drop_table("supermarkets")
