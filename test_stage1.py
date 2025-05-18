#!/usr/bin/env python3
"""
Test Stage 1 directly without the interactive menu
"""
import logging
import json
from pathlib import Path
from datetime import datetime

from src.scrapers.categories_scraper import CategoriesScraper

def setup_logging():
    """Set up logging to both console and file."""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"test_stage1_{timestamp}.log"
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    # Also log to the console that we're logging to a file
    print(f"Logging to file: {log_file}")
    logging.info(f"Logging to file: {log_file}")
    
    return log_file

def main():
    """Run Stage 1 test"""
    log_file = setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        # Load configuration
        config_path = Path("config/scraper.json")
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        logger.info("Starting Stage 1 test")
        logger.info(f"Filters: {config.get('filters', {})}")
        
        # Run Stage 1
        scraper = CategoriesScraper(config)
        output_file = scraper.scrape()
        
        logger.info(f"Output saved to: {output_file}")
        
        # Read and display results
        if output_file.exists():
            with open(output_file, 'r') as f:
                data = json.load(f)
            logger.info(f"Found {len(data.get('categories', []))} categories")
            for category in data.get('categories', []):
                logger.info(f"  - {category['text']}: {category['url']}")
        
    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    main()