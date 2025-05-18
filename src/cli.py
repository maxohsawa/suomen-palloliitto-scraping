#!/usr/bin/env python3
"""
CLI interface for the Finnish Soccer League scraper.
Allows running specific stages of the scraping process.
"""

import click
import logging
from datetime import datetime
from pathlib import Path

from src.scrapers.categories_scraper import CategoriesScraper

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@click.command()
@click.option('--stage', type=click.Choice(['categories', 'teams', 'contact', 'all']), 
              default='all', help='Which stage to run')
@click.option('--delay', type=float, default=2.0, 
              help='Delay between requests in seconds')
@click.option('--resume', is_flag=True, 
              help='Resume from last checkpoint')
@click.option('--dry-run', is_flag=True, 
              help='Show what would be done without actually doing it')
@click.option('--config', type=click.Path(exists=True), 
              default='config/scraper.json', help='Path to configuration file')
def main(stage, delay, resume, dry_run, config):
    """Finnish Soccer League scraper with staged processing."""
    start_time = datetime.now()
    
    logger.info(f"Starting scraper - Stage: {stage}, Delay: {delay}s")
    if dry_run:
        logger.info("DRY RUN MODE - No actual requests will be made")
    
    # Create necessary directories
    for dir_path in ['data', 'data/intermediate', 'logs']:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    try:
        if stage == 'all':
            run_categories(delay, resume, dry_run, config)
            run_teams(delay, resume, dry_run)
            run_contact(delay, resume, dry_run)
        elif stage == 'categories':
            run_categories(delay, resume, dry_run, config)
        elif stage == 'teams':
            run_teams(delay, resume, dry_run)
        elif stage == 'contact':
            run_contact(delay, resume, dry_run)
        
        logger.info("Scraping completed successfully")
        
    except Exception as e:
        logger.error(f"Scraping failed: {e}")
        raise
    
    finally:
        elapsed_time = datetime.now() - start_time
        logger.info(f"Total execution time: {elapsed_time}")


def run_categories(delay, resume, dry_run, config_path):
    """Stage 1: Scrape league/cup URLs from categories page."""
    logger.info("Running Categories stage")
    scraper = CategoriesScraper(config_path)
    scraper.scrape(delay=delay, resume=resume, dry_run=dry_run)


def run_teams(delay, resume, dry_run):
    """Stage 2: Scrape team URLs from league pages."""
    logger.info("Running Teams stage")
    # TODO: Implement teams scraping
    logger.info("Teams stage not yet implemented")


def run_contact(delay, resume, dry_run):
    """Stage 3: Scrape administrator contact info from team pages."""
    logger.info("Running Contact stage")
    # TODO: Implement contact scraping
    logger.info("Contact stage not yet implemented")


if __name__ == "__main__":
    main()
