#!/usr/bin/env python
"""Seed the products table from data/canasta_basica_seed.yaml.

Usage:
    uv run python scripts/seed_canasta.py [--yaml PATH]

Environment:
    DATABASE_URL  — async DSN (postgresql+psycopg://...)
    DATABASE_URL_SYNC  — sync DSN (for settings validation)
"""

import argparse
import asyncio
import sys
from decimal import Decimal
from pathlib import Path

import yaml
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# Ensure packages are importable when running from repo root with uv.
sys.path.insert(0, str(Path(__file__).parent.parent / "packages/infrastructure/src"))
sys.path.insert(0, str(Path(__file__).parent.parent / "packages/domain/src"))

from cuantocuestave_infra.db.models import Product
from cuantocuestave_infra.settings import Settings

_DEFAULT_YAML = Path(__file__).parent.parent / "data" / "canasta_basica_seed.yaml"


def _slugify(text: str) -> str:
    """Very simple ASCII slug (slug is already set in YAML, kept for safety)."""
    return text.lower().replace(" ", "-")


async def seed(yaml_path: Path, session: AsyncSession) -> None:
    with yaml_path.open(encoding="utf-8") as fh:
        data: dict = yaml.safe_load(fh)

    categories: dict = data.get("categories", {})
    inserted = 0
    updated = 0

    for category_key, items in categories.items():
        for item in items:
            slug: str = item["slug"]
            # Decimal(str(float_value)) is mandatory to avoid floating-point drift
            pack_size = Decimal(str(item["canonical_pack_size"]))

            result = await session.execute(select(Product).where(Product.slug == slug))
            row = result.scalar_one_or_none()

            if row is None:
                row = Product(
                    slug=slug,
                    display_name=item["display_name"],
                    brand=item.get("brand"),
                    canonical_unit=item["canonical_unit"],
                    canonical_pack_size=pack_size,
                    category=category_key,
                    is_basic_basket=bool(item.get("is_basic_basket", False)),
                    published=False,
                )
                session.add(row)
                inserted += 1
            else:
                row.display_name = item["display_name"]
                row.brand = item.get("brand")
                row.canonical_unit = item["canonical_unit"]
                row.canonical_pack_size = pack_size
                row.category = category_key
                row.is_basic_basket = bool(item.get("is_basic_basket", False))
                updated += 1

    await session.commit()
    print(f"seed_canasta done — inserted={inserted} updated={updated}")


async def main(yaml_path: Path) -> None:
    settings = Settings()
    engine = create_async_engine(settings.database_url, echo=False)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with session_factory() as session:
        await seed(yaml_path, session)

    await engine.dispose()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed canasta básica products")
    parser.add_argument(
        "--yaml",
        type=Path,
        default=_DEFAULT_YAML,
        help="Path to the YAML seed file (default: data/canasta_basica_seed.yaml)",
    )
    args = parser.parse_args()

    if not args.yaml.exists():
        print(f"ERROR: YAML file not found: {args.yaml}", file=sys.stderr)
        sys.exit(1)

    asyncio.run(main(args.yaml))
