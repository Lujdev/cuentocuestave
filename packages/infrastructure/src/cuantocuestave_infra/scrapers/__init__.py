"""Scraper registry — maps supermarket slug to scraper class."""

from cuantocuestave_infra.scrapers.base import BaseScrapler
from cuantocuestave_infra.scrapers.excelsior_gama import ExcelsiorGamaScraper
from cuantocuestave_infra.scrapers.plazas import PlazasScraper

SCRAPERS: dict[str, type[BaseScrapler]] = {
    PlazasScraper.supermarket_slug: PlazasScraper,
    ExcelsiorGamaScraper.supermarket_slug: ExcelsiorGamaScraper,
}

__all__ = ["SCRAPERS", "BaseScrapler", "PlazasScraper", "ExcelsiorGamaScraper"]
