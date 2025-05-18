"""
Page object for the categories page (Finnish version with Vuetify buttons).
"""

import logging
import time
from pathlib import Path
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException

logger = logging.getLogger(__name__)


class CategoriesPage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 20)  # Increased timeout
        self.url = "https://tulospalvelu.palloliitto.fi/categories"
    
    def navigate(self):
        """Navigate to the categories page."""
        logger.info(f"Navigating to {self.url}")
        self.driver.get(self.url)
        time.sleep(3)  # Let page load
        
        # Handle cookie consent popup
        self._handle_cookie_consent()
    
    def _handle_cookie_consent(self):
        """Handle cookie consent popup if it appears."""
        try:
            logger.info("Checking for cookie consent popup")
            
            # Look for the cookie consent dialog
            consent_dialog = self.driver.find_elements(By.ID, "CybotCookiebotDialog")
            if consent_dialog:
                logger.info("Cookie consent dialog found")
                
                # Try to find and click "Allow all" button
                try:
                    allow_all_button = self.wait.until(
                        EC.element_to_be_clickable((By.ID, "CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll"))
                    )
                    logger.info("Clicking 'Allow all' button")
                    allow_all_button.click()
                    time.sleep(2)  # Wait for popup to close
                    logger.info("Cookie consent handled")
                except TimeoutException:
                    logger.warning("Allow all button not found, trying alternative method")
                    
                    # Try to find and click "Deny" button as fallback
                    try:
                        deny_button = self.driver.find_element(By.ID, "CybotCookiebotDialogBodyButtonDecline")
                        logger.info("Clicking 'Deny' button")
                        deny_button.click()
                        time.sleep(2)
                        logger.info("Cookie consent handled with deny")
                    except NoSuchElementException:
                        logger.warning("Deny button not found")
                        
                    # Try to close dialog using close button
                    try:
                        close_button = self.driver.find_element(By.CLASS_NAME, "CybotCookiebotBannerCloseButton")
                        logger.info("Clicking close button")
                        close_button.click()
                        time.sleep(2)
                    except NoSuchElementException:
                        logger.warning("Close button not found")
            else:
                logger.info("No cookie consent dialog found")
                
        except Exception as e:
            logger.warning(f"Error handling cookie consent: {e}")
            # Continue anyway - maybe the popup isn't there
    
    def explore_filters(self):
        """Explore the filter structure to understand the page."""
        try:
            # Look for Vuetify buttons
            buttons = self.driver.find_elements(By.CSS_SELECTOR, "button.v-btn")
            logger.info(f"Found {len(buttons)} Vuetify buttons")
            
            for i, button in enumerate(buttons[:20]):  # Look at first 20 buttons
                try:
                    button_text = button.text.strip()
                    button_value = button.get_attribute("value")
                    button_class = button.get_attribute("class")
                    is_active = "v-btn--active" in button_class
                    
                    logger.info(f"Button {i}: text='{button_text}', value='{button_value}', active={is_active}")
                    
                except Exception as e:
                    logger.debug(f"Error with button {i}: {e}")
            
            # Look for filter groups/containers
            groups = self.driver.find_elements(By.CSS_SELECTOR, "div.v-btn-toggle")
            logger.info(f"Found {len(groups)} button groups")
            
            return True
            
        except Exception as e:
            logger.error(f"Error exploring filters: {e}")
            return False
    
    def apply_filter(self, filter_text=None, filter_value=None):
        """Apply a filter by clicking the appropriate button."""
        try:
            if filter_value:
                # Find button by value attribute
                selector = f"button[value='{filter_value}']" 
                button = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                logger.info(f"Clicking button with value='{filter_value}'")
            elif filter_text:
                # Find button by text content
                buttons = self.driver.find_elements(By.CSS_SELECTOR, "button.v-btn")
                button = None
                for btn in buttons:
                    if filter_text.lower() in btn.text.lower():
                        button = btn
                        break
                
                if not button:
                    logger.error(f"No button found with text containing '{filter_text}'")
                    return False
                
                logger.info(f"Clicking button with text='{button.text}'")
            else:
                logger.error("Must provide either filter_text or filter_value")
                return False
            
            # Scroll to button and click using JavaScript
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
            time.sleep(0.5)
            
            # Try JavaScript click first (works even if element is obscured)
            try:
                self.driver.execute_script("arguments[0].click();", button)
                logger.info("Clicked using JavaScript")
            except Exception as e:
                logger.warning(f"JavaScript click failed: {e}, trying regular click")
                # Fallback to regular click
                button.click()
                logger.info("Clicked using regular click")
            
            time.sleep(2)  # Increased wait for filter to apply
            
            return True
            
        except Exception as e:
            logger.error(f"Error applying filter: {e}", exc_info=True)
            return False
    
    def apply_filters_for_scraping(self):
        """Apply the specific filters needed for scraping."""
        filters = [
            {"value": "football", "text": "Jalkapallo"},
            {"value": "spletela", "text": "Etelä"},
            {"value": "league", "text": "Sarja/cup"},
            {"value": "B", "text": "Pojat"},
            # No filter for age (all ages)
        ]
        
        for i, filter_config in enumerate(filters):
            logger.info(f"Applying filter {i+1}: {filter_config}")
            success = self.apply_filter(
                filter_value=filter_config.get("value"),
                filter_text=filter_config.get("text")
            )
            if not success:
                logger.error(f"Failed to apply filter {i+1}")
                return False
            time.sleep(1)  # Wait between filters
        
        logger.info("All filters applied successfully")
        
        # After applying filters, check if there's a date picker or modal to close
        self._handle_date_picker()
        
        # Wait for results to load
        time.sleep(5)
        
        # Try scrolling to trigger any lazy loading
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
        
        return True
    
    def _handle_date_picker(self):
        """Handle date picker or modal that might appear."""
        try:
            # Check for modal or date picker
            # Look for close button (X) or "Valitse kaikki" (Select all) button
            close_buttons = self.driver.find_elements(By.CSS_SELECTOR, "button.v-dialog__close, button[aria-label='Close'], i.v-icon.notranslate.mdi.mdi-close")
            if close_buttons:
                logger.info(f"Found {len(close_buttons)} close buttons")
                close_buttons[0].click()
                time.sleep(1)
                return
            
            # Look for overlay to click outside
            overlays = self.driver.find_elements(By.CSS_SELECTOR, ".v-overlay__scrim")
            if overlays:
                logger.info("Found overlay, clicking to close")
                overlays[0].click()
                time.sleep(1)
                return
            
            # Look for a "confirm" or "ok" button
            confirm_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'OK') or contains(text(), 'Valitse') or contains(text(), 'Vahvista')]")
            if confirm_buttons:
                logger.info("Found confirm button, clicking")
                confirm_buttons[0].click()
                time.sleep(1)
                return
                
            logger.info("No date picker or modal found to close")
            
        except Exception as e:
            logger.warning(f"Error handling date picker: {e}")
    
    def get_results(self):
        """Get the league/cup results after filtering."""
        try:
            # Let's wait for the page to fully load after filters
            logger.info("Waiting for results to load...")
            
            # Save debug info before searching
            self._save_debug_info()
            
            # Look for the results div with id="results"
            try:
                results_div = self.wait.until(
                    EC.presence_of_element_located((By.ID, "results"))
                )
                logger.info("Results div found")
                
                # Find all anchor tags within the results div
                category_links = results_div.find_elements(By.TAG_NAME, "a")
                logger.info(f"Found {len(category_links)} anchor tags in results div")
                
                results = []
                for link in category_links:
                    try:
                        href = link.get_attribute("href")
                        if not href or "/category/" not in href:
                            continue
                            
                        # Get text from the link or its child elements
                        text = link.text.strip()
                        if not text:
                            # Try to get text from child divs
                            divs = link.find_elements(By.TAG_NAME, "div")
                            for div in divs:
                                div_text = div.text.strip()
                                if div_text and not div_text == "Etelä Jalkapallo 2025":
                                    text = div_text
                                    break
                        
                        if text and href:
                            # Clean up the text - take first meaningful line
                            lines = text.split("\n")
                            name = ""
                            for line in lines:
                                if line.strip() and line.strip() not in ["Etelä Jalkapallo 2025"]:
                                    name = line.strip()
                                    break
                            
                            if name:
                                results.append({
                                    "name": name,
                                    "url": href
                                })
                                logger.debug(f"Added result: {name} - {href}")
                    
                    except Exception as e:
                        logger.warning(f"Error parsing link: {e}")
                        continue
                
                logger.info(f"Found {len(results)} valid league/cup results")
                
                # Log first few results for verification
                for i, result in enumerate(results[:5]):
                    logger.info(f"Result {i+1}: {result['name']} - {result['url']}")
                
                return results
                
            except TimeoutException:
                logger.error("Results div not found")
                self._save_debug_info()
                return []
                
        except Exception as e:
            logger.error(f"Error getting results: {e}", exc_info=True)
            self._save_debug_info()
            return []
    
    def _save_debug_info(self):
        """Save debug information when results are not found."""
        try:
            # Save page source with proper encoding
            page_source = self.driver.page_source
            debug_file = Path("data/intermediate/debug_results_page.html")
            debug_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Write with explicit encoding
            with open(debug_file, "w", encoding="utf-8") as f:
                f.write(page_source)
            logger.info(f"Saved page source to {debug_file}")
            
            # Verify file was written
            if debug_file.exists():
                logger.info(f"File size: {debug_file.stat().st_size} bytes")
            
            # Save screenshot
            screenshot_file = Path("data/intermediate/debug_screenshot.png")
            self.driver.save_screenshot(str(screenshot_file))
            logger.info(f"Saved screenshot to {screenshot_file}")
            
            # Log current URL
            current_url = self.driver.current_url
            logger.info(f"Current URL: {current_url}")
            
            # Log page title
            page_title = self.driver.title
            logger.info(f"Page title: {page_title}")
            
        except Exception as e:
            logger.error(f"Error saving debug info: {e}")
    
    def get_page_source(self):
        """Get the current page source for debugging."""
        return self.driver.page_source