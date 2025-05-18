#!/usr/bin/env python3
"""
Main entry point for the Finnish Soccer League scraper.
Extracts team administrator (Joukkueenjohtaja) contact information.
"""

import logging
from datetime import datetime
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main scraping workflow."""
    start_time = datetime.now()
    logger.info("Starting Finnish Soccer League scraper")
    
    # Create output directory
    output_dir = Path("data")
    output_dir.mkdir(exist_ok=True)
    
    try:
        # TODO: Implement scraping workflow
        # 1. Initialize browser
        # 2. Navigate to categories page
        # 3. Apply filters
        # 4. Collect league links
        # 5. For each league, collect team links
        # 6. For each team, extract administrator info
        # 7. Process and save data
        
        logger.info("Scraping completed successfully")
        
    except Exception as e:
        logger.error(f"Scraping failed: {e}")
        raise
    
    finally:
        elapsed_time = datetime.now() - start_time
        logger.info(f"Total execution time: {elapsed_time}")


if __name__ == "__main__":
    main()
