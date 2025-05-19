#!/usr/bin/env python3
"""
Inspect league page structure to understand how teams are displayed
"""
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from pathlib import Path

def main():
    # Create browser
    options = Options()
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    try:
        url = "https://tulospalvelu.palloliitto.fi/category/P202!etejp25/tables"
        print(f"Navigating to: {url}")
        driver.get(url)
        
        # Wait for page to load
        time.sleep(5)
        
        # Handle cookie consent if needed
        try:
            consent_button = driver.find_element("id", "CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll")
            consent_button.click()
            time.sleep(2)
        except:
            pass
        
        # Save page source and screenshot
        output_dir = Path("data/intermediate")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        page_source_file = output_dir / "league_page_source.html"
        with open(page_source_file, 'w') as f:
            f.write(driver.page_source)
        print(f"Page source saved to: {page_source_file}")
        
        screenshot_file = output_dir / "league_screenshot.png"
        driver.save_screenshot(str(screenshot_file))
        print(f"Screenshot saved to: {screenshot_file}")
        
        input("Press Enter to close browser...")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    main()