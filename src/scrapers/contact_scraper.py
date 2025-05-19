"""
Contact scraper - Stage 3 of the scraping pipeline.
Extracts team administrator (Joukkueenjohtaja) contact information from team pages.
"""
import csv
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

from src.pages.contact_page import ContactPage
from src.utils.browser import BrowserManager

logger = logging.getLogger(__name__)


class ContactScraper:
    """Scraper for collecting team administrator contact information."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the contact scraper.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.output_dir = Path("data")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.intermediate_dir = Path("data/intermediate")
        
    def scrape(self) -> Path:
        """Scrape contact information from all teams collected in Stage 2.
        
        Returns:
            Path to the output CSV file with contact information
        """
        logger.info("Starting Stage 3: Contact scraping")
        
        # Load teams data from Stage 2
        teams_file = self.intermediate_dir / "teams.json"
        if not teams_file.exists():
            raise FileNotFoundError(f"Stage 2 output not found: {teams_file}")
            
        with open(teams_file, 'r') as f:
            teams_data = json.load(f)
            
        all_teams = []
        for league in teams_data.get('leagues', []):
            for team in league.get('teams', []):
                all_teams.append({
                    'league_name': league['league_name'],
                    'team_name': team['name'],
                    'team_url': team['url']
                })
                
        logger.info(f"Found {len(all_teams)} teams to process")
        
        contacts = []
        browser_config = self.config.get("browser", {})
        
        try:
            with BrowserManager(
                headless=browser_config.get("headless", True),
                window_size=browser_config.get("window_size", "1920,1080")
            ) as driver:
                contact_page = ContactPage(driver, self.config)
                
                for i, team in enumerate(all_teams, 1):
                    logger.info(f"Processing team {i}/{len(all_teams)}: {team['team_name']}")
                    
                    # Skip null team placeholders
                    if '/team/0/' in team['team_url']:
                        logger.warning(f"  Skipping null team placeholder: {team['team_url']}")
                        continue
                    
                    try:
                        # Convert /info URL to /players URL
                        players_url = team['team_url'].replace('/info', '/players')
                        
                        contact_info = contact_page.extract_contact(players_url)
                        
                        if contact_info:
                            contact_data = {
                                'league': team['league_name'],
                                'team': team['team_name'],
                                'administrator_name': contact_info['name'],
                                'position': contact_info.get('position', 'Unknown'),
                                'email': contact_info['email']
                            }
                            
                            # Add phone if available
                            if 'phone' in contact_info:
                                contact_data['phone'] = contact_info['phone']
                            
                            contacts.append(contact_data)
                            logger.info(f"  Found administrator: {contact_info['name']} ({contact_info.get('position', 'Unknown')})")
                        else:
                            logger.warning(f"  No administrator found for {team['team_name']}")
                            
                    except Exception as e:
                        logger.error(f"  Error processing team: {e}")
                        
                # Remove duplicates (same administrator might manage multiple teams)
                unique_contacts = []
                seen_emails = set()
                
                for contact in contacts:
                    email = contact['email']
                    if email not in seen_emails:
                        seen_emails.add(email)
                        unique_contacts.append(contact)
                    else:
                        # Find existing contact and append team info
                        for existing in unique_contacts:
                            if existing['email'] == email:
                                existing['team'] += f", {contact['team']}"
                                existing['league'] += f", {contact['league']}"
                                # If positions differ, append both
                                if contact['position'] != existing['position']:
                                    existing['position'] += f", {contact['position']}"
                                break
                
                # Save results to CSV
                output_file = self.output_dir / "contacts.csv"
                with open(output_file, 'w', newline='', encoding='utf-8') as f:
                    # Include phone field if any contacts have phone numbers
                    has_phone = any('phone' in contact for contact in unique_contacts)
                    fieldnames = ['administrator_name', 'position', 'email', 'team', 'league']
                    if has_phone:
                        fieldnames.insert(3, 'phone')  # Insert phone after email
                    
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    
                    writer.writeheader()
                    writer.writerows(unique_contacts)
                
                logger.info(f"Contact data saved to {output_file}")
                logger.info(f"Total unique administrators found: {len(unique_contacts)}")
                
                return output_file
                
        except Exception as e:
            logger.error(f"Failed to complete contact scraping: {e}")
            raise