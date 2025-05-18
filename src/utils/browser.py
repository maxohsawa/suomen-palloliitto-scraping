"""
Browser management utility for Selenium WebDriver.
"""

import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

logger = logging.getLogger(__name__)


class BrowserManager:
    def __init__(self, headless=False, window_size="1920,1080"):
        self.headless = headless
        self.window_size = window_size
        self.driver = None
    
    def __enter__(self):
        """Context manager entry."""
        self.driver = self._create_driver()
        return self.driver
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if self.driver:
            self.driver.quit()
    
    def _create_driver(self):
        """Create and configure Chrome WebDriver."""
        options = Options()
        
        if self.headless:
            options.add_argument('--headless=new')
        
        options.add_argument(f'--window-size={self.window_size}')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        # Install/update ChromeDriver automatically
        service = Service(ChromeDriverManager().install())
        
        driver = webdriver.Chrome(service=service, options=options)
        logger.info(f"Browser created (headless={self.headless})")
        
        return driver
