"""
Teams page object - Handles scraping team URLs from league pages.
"""
import logging
import time
from pathlib import Path
from typing import Dict, List, Any

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

logger = logging.getLogger(__name__)


class TeamsPage:
    """Page object for extracting team information from league pages."""
    
    def __init__(self, driver, config):
        self.driver = driver
        self.config = config
        self.wait = WebDriverWait(driver, 20)
        self.output_dir = Path("data/intermediate")
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def extract_teams(self, league_url: str) -> List[Dict[str, str]]:
        """Extract team URLs from a league page.
        
        Args:
            league_url: URL of the league page
            
        Returns:
            List of dictionaries containing team information
        """
        logger.info(f"Navigating to league page: {league_url}")
        self.driver.get(league_url)
        
        # Handle cookie consent if needed
        self._handle_cookie_consent()
        
        # Wait for page to load
        time.sleep(self.config.get('delays', {}).get('page_load', 3))
        
        teams = []
        
        try:
            # Wait for tables to load
            logger.info("Waiting for tables to load")
            
            # Wait for at least one table to be present
            self.wait.until(
                EC.presence_of_element_located((By.TAG_NAME, "table"))
            )
            
            # Find all tables on the page
            tables = self.driver.find_elements(By.TAG_NAME, "table")
            logger.info(f"Found {len(tables)} tables on the page")
            
            # Process each table
            for table_idx, table in enumerate(tables):
                try:
                    rows = table.find_elements(By.TAG_NAME, "tr")
                    logger.debug(f"Table {table_idx + 1} has {len(rows)} rows")
                    
                    for row_idx, row in enumerate(rows):
                        try:
                            cells = row.find_elements(By.TAG_NAME, "td")
                            
                            # Check if third cell exists and contains a link
                            if len(cells) >= 3:
                                third_cell = cells[2]  # 0-indexed, so 3rd cell is index 2
                                links = third_cell.find_elements(By.TAG_NAME, "a")
                                
                                for link in links:
                                    href = link.get_attribute('href')
                                    if href and '/team/' in href:
                                        team_info = {
                                            'name': link.text.strip(),
                                            'url': href
                                        }
                                        if team_info['name']:  # Only add if name is not empty
                                            teams.append(team_info)
                                            logger.debug(f"Found team: {team_info['name']}")
                                            
                        except Exception as e:
                            logger.debug(f"Error processing row {row_idx} in table {table_idx}: {e}")
                            
                except Exception as e:
                    logger.debug(f"Error processing table {table_idx}: {e}")
            
            logger.info(f"Total teams found: {len(teams)}")
                
            # Debug: save page source if no teams found
            if len(teams) == 0:
                logger.warning("No teams found on the page, saving page source for debugging")
                debug_file = self.output_dir / f"debug_teams_page_{int(time.time())}.html"
                with open(debug_file, 'w') as f:
                    f.write(self.driver.page_source)
                logger.info(f"Page source saved to: {debug_file}")
                
                # Also save a screenshot
                screenshot_file = self.output_dir / f"debug_teams_screenshot_{int(time.time())}.png"
                self.driver.save_screenshot(str(screenshot_file))
                logger.info(f"Screenshot saved to: {screenshot_file}")
                
        except TimeoutException:
            logger.error("Timeout waiting for tables to load")
            # Save debug info even on timeout
            debug_file = self.output_dir / f"debug_timeout_{int(time.time())}.html"
            with open(debug_file, 'w') as f:
                f.write(self.driver.page_source)
            logger.info(f"Page source saved to: {debug_file}")
        except Exception as e:
            logger.error(f"Error extracting teams: {e}")
            
        return teams
    
    def _handle_cookie_consent(self):
        """Handle cookie consent popup if it appears."""
        try:
            # Check if cookie consent is present
            consent_dialog = self.driver.find_elements(By.ID, "CybotCookiebotDialog")
            if consent_dialog and consent_dialog[0].is_displayed():
                logger.info("Cookie consent dialog found")
                
                # Try to click "Allow all" button
                try:
                    allow_all_button = self.driver.find_element(
                        By.ID, "CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll"
                    )
                    if allow_all_button.is_displayed():
                        allow_all_button.click()
                        logger.info("Clicked 'Allow all' button")
                        time.sleep(1)
                        return
                except NoSuchElementException:
                    pass
                    
                # Try alternative button IDs or classes
                alternative_selectors = [
                    "CybotCookiebotDialogBodyButtonAccept",
                    ".cookie-accept",
                    "[data-accept-cookies]"
                ]
                
                for selector in alternative_selectors:
                    try:
                        if selector.startswith("#"):
                            button = self.driver.find_element(By.ID, selector[1:])
                        elif selector.startswith("."):
                            button = self.driver.find_element(By.CLASS_NAME, selector[1:])
                        else:
                            button = self.driver.find_element(By.CSS_SELECTOR, selector)
                            
                        if button.is_displayed():
                            button.click()
                            logger.info(f"Clicked consent button: {selector}")
                            time.sleep(1)
                            return
                    except NoSuchElementException:
                        continue
                        
        except Exception as e:
            logger.debug(f"No cookie consent or error handling it: {e}")