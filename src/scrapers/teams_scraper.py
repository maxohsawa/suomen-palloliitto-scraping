"""
Teams scraper - Stage 2 of the scraping pipeline.
Extracts team URLs from league pages.
"""
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

from src.pages.teams_page import TeamsPage
from src.utils.browser import BrowserManager

logger = logging.getLogger(__name__)


class TeamsScraper:
    """Scraper for collecting team URLs from league pages."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the teams scraper.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.output_dir = Path("data/intermediate")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def scrape(self) -> Path:
        """Scrape teams from all leagues collected in Stage 1.
        
        Returns:
            Path to the output file with team URLs
        """
        logger.info("Starting Stage 2: Teams scraping")
        
        # Load leagues data from Stage 1
        leagues_file = self.output_dir / "leagues.json"
        if not leagues_file.exists():
            raise FileNotFoundError(f"Stage 1 output not found: {leagues_file}")
            
        with open(leagues_file, 'r') as f:
            leagues_data = json.load(f)
            
        leagues = leagues_data.get('leagues', [])
        logger.info(f"Found {len(leagues)} leagues to process")
        
        all_teams = []
        browser_config = self.config.get("browser", {})
        
        try:
            with BrowserManager(
                headless=browser_config.get("headless", True),
                window_size=browser_config.get("window_size", "1920,1080")
            ) as driver:
                teams_page = TeamsPage(driver, self.config)
                
                for i, league in enumerate(leagues, 1):
                    logger.info(f"Processing league {i}/{len(leagues)}: {league['name']}")
                    
                    try:
                        teams = teams_page.extract_teams(league['url'])
                        
                        league_teams = {
                            'league_name': league['name'],
                            'league_url': league['url'],
                            'teams': teams
                        }
                        all_teams.append(league_teams)
                        
                        logger.info(f"  Found {len(teams)} teams")
                        
                    except Exception as e:
                        logger.error(f"  Error processing league: {e}")
                        
                # Save results
                output_file = self.output_dir / "teams.json"
                output_data = {
                    'timestamp': datetime.now().isoformat(),
                    'leagues_processed': len(leagues),
                    'total_teams': sum(len(lt['teams']) for lt in all_teams),
                    'leagues': all_teams
                }
                
                with open(output_file, 'w') as f:
                    json.dump(output_data, f, indent=2, ensure_ascii=False)
                    
                logger.info(f"Teams data saved to {output_file}")
                logger.info(f"Total teams collected: {output_data['total_teams']}")
                
                return output_file
                
        except Exception as e:
            logger.error(f"Failed to complete teams scraping: {e}")
            raise