#!/usr/bin/env python3
"""
Test Stage 2 directly without the interactive menu
"""
import logging
import json
from pathlib import Path
from datetime import datetime

from src.scrapers.teams_scraper import TeamsScraper

def setup_logging():
    """Set up logging to both console and file."""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"test_stage2_{timestamp}.log"
    
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
    """Run Stage 2 test"""
    log_file = setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        # Load configuration
        config_path = Path("config/scraper.json")
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        logger.info("Starting Stage 2 test")
        
        # Check if leagues data exists
        leagues_file = Path("data/intermediate/leagues.json")
        if not leagues_file.exists():
            logger.error("No leagues data found. Please run Stage 1 first.")
            return
        
        # Run Stage 2
        scraper = TeamsScraper(config)
        output_file = scraper.scrape()
        
        logger.info(f"Output saved to: {output_file}")
        
        # Read and display results
        if output_file.exists():
            with open(output_file, 'r') as f:
                data = json.load(f)
            logger.info(f"Total teams collected: {data.get('total_teams', 0)}")
            logger.info(f"Leagues processed: {data.get('leagues_processed', 0)}")
            
            # Show first few leagues and their teams
            for i, league in enumerate(data.get('leagues', [])[:3], 1):
                logger.info(f"\nLeague {i}: {league['league_name']}")
                logger.info(f"  Teams found: {len(league['teams'])}")
                for j, team in enumerate(league['teams'][:3], 1):
                    logger.info(f"    Team {j}: {team['name']}")
        
    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    main()