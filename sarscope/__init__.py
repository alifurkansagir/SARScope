"""
__init__.py for SarScope package
"""

__version__ = "1.0.0"
__author__ = "SarScope Development Team"
__description__ = "E-Commerce Intelligence Tool for Price Monitoring, Trend Hunting, and Dynamic Pricing"

from sarscope.database import DatabaseManager
from sarscope.core.models import Product, Competitor, PricingOpportunity, TrendOpportunity
from sarscope.core.scraper import SarScopeScraper
from sarscope.core.pricer import PricingEngine
from sarscope.core.trend_hunter import TrendHunter

__all__ = [
    "DatabaseManager",
    "Product",
    "Competitor",
    "PricingOpportunity",
    "TrendOpportunity",
    "SarScopeScraper",
    "PricingEngine",
    "TrendHunter",
]
