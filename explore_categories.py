#!/usr/bin/env python3
"""
Script to explore the categories page structure.
Run this to understand how the filters work.
"""

import logging
from src.scrapers.categories_scraper import CategoriesScraper

# Set up detailed logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

if __name__ == "__main__":
    scraper = CategoriesScraper()
    scraper.explore()