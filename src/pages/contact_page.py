"""
Contact page object - Handles scraping administrator contact information from team pages.
"""
import logging
import time
from pathlib import Path
from typing import Dict, Optional

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

logger = logging.getLogger(__name__)


class ContactPage:
    """Page object for extracting contact information from team players pages."""
    
    def __init__(self, driver, config):
        self.driver = driver
        self.config = config
        self.wait = WebDriverWait(driver, 20)
        self.output_dir = Path("data/intermediate")
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def extract_contact(self, players_url: str) -> Optional[Dict[str, str]]:
        """Extract team administrator contact information from a players page.
        
        Args:
            players_url: URL of the team players page
            
        Returns:
            Dictionary with name and email, or None if not found
        """
        logger.info(f"Navigating to players page: {players_url}")
        self.driver.get(players_url)
        
        # Handle cookie consent if needed
        self._handle_cookie_consent()
        
        # Wait for page to load
        time.sleep(self.config.get('delays', {}).get('page_load', 3))
        
        try:
            # Wait for the player list container
            logger.info("Waiting for player list to load")
            
            # Find the active officials section
            officials_section = self.wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "activeofficials"))
            )
            
            # Find the table inside the officials section
            table = officials_section.find_element(By.TAG_NAME, "table")
            rows = table.find_elements(By.TAG_NAME, "tr")
            
            logger.debug(f"Found {len(rows)} rows in officials table")
            
            # Collect all officials with contact information
            all_officials = []
            
            for row in rows:
                try:
                    cells = row.find_elements(By.TAG_NAME, "td")
                    
                    if len(cells) >= 2:
                        # Get position from first cell
                        position = cells[0].text.strip()
                        
                        # Extract contact from the row
                        contact_info = self._extract_contact_from_row(row)
                        
                        if contact_info:
                            contact_info['position'] = position
                            all_officials.append(contact_info)
                            logger.info(f"Found official: {position} - {contact_info['name']}")
                            
                except Exception as e:
                    logger.debug(f"Error processing row: {e}")
            
            # Return the first official with "Joukkueenjohtaja" if found
            for official in all_officials:
                if "Joukkueenjohtaja" in official.get('position', ''):
                    logger.info("Returning Joukkueenjohtaja")
                    return official
            
            # Otherwise return the first official with contact info
            if all_officials:
                logger.info(f"No Joukkueenjohtaja found, returning first official: {all_officials[0]['position']}")
                return all_officials[0]
            
            logger.warning("No officials with contact information found")
            
            # Debug: save page source if no administrator found
            debug_file = self.output_dir / f"debug_contact_{int(time.time())}.html"
            with open(debug_file, 'w') as f:
                f.write(self.driver.page_source)
            logger.info(f"Page source saved to: {debug_file}")
            
        except TimeoutException:
            logger.error("Timeout waiting for officials section to load")
        except Exception as e:
            logger.error(f"Error extracting contact: {e}")
            
        return None
    
    def _extract_contact_from_row(self, row) -> Optional[Dict[str, str]]:
        """Extract contact information from a table row."""
        try:
            # Find the namefield cell
            namefield_cell = row.find_element(By.CLASS_NAME, "namefield")
            return self._extract_contact_from_cell(namefield_cell)
        except Exception as e:
            logger.debug(f"Error extracting contact from row: {e}")
            return None
    
    def _extract_contact_from_cell(self, cell) -> Optional[Dict[str, str]]:
        """Extract contact information from a table cell."""
        try:
            # Get the name from the first <a> tag
            name_link = cell.find_element(By.TAG_NAME, "a")
            name = name_link.text.strip()
            
            # Look for contact info in the nested structure
            email = None
            phone = None
            
            try:
                # Find all links within the nested div
                div_in_link = name_link.find_element(By.TAG_NAME, "div")
                contact_links = div_in_link.find_elements(By.TAG_NAME, "a")
                
                for link in contact_links:
                    href = link.get_attribute("href")
                    if href:
                        if href.startswith("mailto:"):
                            email = href.replace("mailto:", "")
                        elif href.startswith("tel:"):
                            phone = href.replace("tel:", "")
                
                if email:  # We need at least an email
                    logger.info(f"Found administrator: {name} - {email}")
                    
                    result = {
                        'name': name,
                        'email': email
                    }
                    if phone:
                        result['phone'] = phone
                    
                    return result
                else:
                    logger.warning(f"No email found for administrator: {name}")
                    
            except NoSuchElementException:
                logger.debug(f"No nested div/links found for: {name}")
                
        except Exception as e:
            logger.debug(f"Error extracting contact from cell: {e}")
            
        return None
    
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