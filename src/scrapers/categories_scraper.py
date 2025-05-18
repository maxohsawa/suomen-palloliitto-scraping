"""
Scraper for Stage 1: Categories page.
"""

import json
import logging
import time
from pathlib import Path
from datetime import datetime

from src.utils.browser import BrowserManager
from src.pages.categories_page import CategoriesPage

logger = logging.getLogger(__name__)


class CategoriesScraper:
    def __init__(self, config_path="config/scraper.json"):
        with open(config_path) as f:
            self.config = json.load(f)
    
    def explore(self):
        """Explore the categories page to understand its structure."""
        browser_config = self.config.get("browser", {})
        
        # For exploration, let's use non-headless mode
        with BrowserManager(headless=False, window_size=browser_config.get("window_size", "1920,1080")) as driver:
            page = CategoriesPage(driver)
            page.navigate()
            
            # Explore the filter structure
            page.explore_filters()
            
            # Try applying filters
            logger.info("\nTrying to apply filters...")
            success = page.apply_filters_for_scraping()
            
            if success:
                # Get results
                results = page.get_results()
                logger.info(f"\nFound {len(results)} leagues/cups:")
                for i, result in enumerate(results[:5]):  # Show first 5
                    logger.info(f"{i+1}. {result['name']} - {result['url']}")
            
            # Save page source for analysis
            page_source = page.get_page_source()
            output_path = Path("data/intermediate/categories_page_source.html")
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(page_source)
            logger.info(f"\nPage source saved to {output_path}")
            
            # Keep browser open for manual inspection
            input("\nPress Enter to close the browser and continue...\n")
    
    def scrape(self, delay=2.0, resume=False, dry_run=False):
        """Scrape league/cup URLs from categories page."""
        logger.info("Starting Categories scraper")
        
        if dry_run:
            logger.info("DRY RUN - would scrape categories")
            return
        
        output_path = Path(self.config["output"]["leagues_file"])
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Check if resuming
        if resume and output_path.exists():
            logger.info(f"Resuming: {output_path} already exists, skipping categories stage")
            return
        
        browser_config = self.config.get("browser", {})
        results = []
        
        try:
            with BrowserManager(
                headless=browser_config.get("headless", True),
                window_size=browser_config.get("window_size", "1920,1080")
            ) as driver:
                page = CategoriesPage(driver)
                page.navigate()
                
                # Apply filters
                logger.info("Applying filters...")
                success = page.apply_filters_for_scraping()
                
                if not success:
                    raise Exception("Failed to apply filters")
                
                # Get results
                results = page.get_results()
                logger.info(f"Found {len(results)} leagues/cups")
                
                # Add metadata
                data = {
                    "timestamp": datetime.now().isoformat(),
                    "filters_applied": {
                        "sport": "Jalkapallo (Football)",
                        "area": "Etelä (South)",
                        "type": "Sarja/cup (Leagues and Cups)",
                        "gender": "Pojat (Boys)",
                        "age": "All ages"
                    },
                    "leagues": results
                }
                
                # Save results
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                
                logger.info(f"Saved {len(results)} leagues to {output_path}")
                
        except Exception as e:
            logger.error(f"Error during categories scraping: {e}")
            raise
        
        finally:
            time.sleep(delay)  # Respect rate limiting
