#!/usr/bin/env python3
"""
NHL HUT Card Scraper
Scrapes player cards from nhlhutbuilder.com with nationality filtering
"""

import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

class NHLHUTScraper:
    def __init__(self):
        self.driver = None
        self.wait = None
        self.base_url = "https://nhlhutbuilder.com/cards.php"
        
    def setup_driver(self):
        """Setup Chrome WebDriver with appropriate options"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in background
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-plugins")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        chrome_options.add_argument("--remote-debugging-port=9222")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--allow-running-insecure-content")
        import tempfile
        import os
        temp_dir = tempfile.mkdtemp()
        chrome_options.add_argument(f"--user-data-dir={temp_dir}")
        chrome_options.add_argument("--disable-background-timer-throttling")
        chrome_options.add_argument("--disable-backgrounding-occluded-windows")
        chrome_options.add_argument("--disable-renderer-backgrounding")
        
        # Try to find Chrome/Chromium binary
        import os
        possible_paths = [
            "/usr/bin/google-chrome",
            "/usr/bin/google-chrome-stable",
            "/usr/bin/chromium-browser",
            "/usr/bin/chromium",
            "/usr/bin/chrome"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                chrome_options.binary_location = path
                print(f"Using browser: {path}")
                break
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)
        
    def navigate_to_cards_page(self):
        """Navigate to the cards page"""
        print("Navigating to cards page...")
        self.driver.get(self.base_url)
        
        # Wait for page to load
        self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "card-search")))
        print("Page loaded successfully!")
        
    def get_available_nationalities(self):
        """Get list of available nationalities from the dropdown"""
        print("Getting available nationalities...")
        
        # Find the nationality dropdown
        nationality_dropdown = self.wait.until(
            EC.presence_of_element_located((By.NAME, "nationality"))
        )
        
        # Get all options
        select = Select(nationality_dropdown)
        nationalities = []
        
        for option in select.options:
            if option.text.strip() and option.text.strip() != "All":
                nationalities.append(option.text.strip())
                
        print(f"Found {len(nationalities)} nationalities: {nationalities[:10]}...")
        return nationalities
        
    def test_nationality_filter(self, nationality):
        """Test filtering by a specific nationality"""
        print(f"\nTesting nationality filter: {nationality}")
        
        try:
            # Find and select nationality
            nationality_dropdown = self.driver.find_element(By.NAME, "nationality")
            select = Select(nationality_dropdown)
            select.select_by_visible_text(nationality)
            
            # Wait for results to load
            time.sleep(2)
            
            # Check if results are displayed
            cards = self.driver.find_elements(By.CSS_SELECTOR, ".player-card, .card, [class*='card']")
            print(f"Found {len(cards)} cards for {nationality}")
            
            # Check pagination info if available
            try:
                pagination_info = self.driver.find_element(By.CSS_SELECTOR, ".dataTables_info, .pagination-info, [class*='info']")
                print(f"Pagination info: {pagination_info.text}")
            except:
                print("No pagination info found")
                
            return len(cards) > 0
            
        except Exception as e:
            print(f"Error testing nationality {nationality}: {e}")
            return False
            
    def get_card_data(self):
        """Extract basic card data from current page"""
        print("Extracting card data...")
        
        cards_data = []
        
        try:
            # Wait for cards to load
            cards = self.wait.until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".player-card, .card, [class*='card']"))
            )
            
            for i, card in enumerate(cards[:5]):  # Limit to first 5 for testing
                try:
                    card_data = {}
                    
                    # Try to extract player name
                    name_elements = card.find_elements(By.CSS_SELECTOR, ".player-name, .name, [class*='name']")
                    if name_elements:
                        card_data['name'] = name_elements[0].text.strip()
                    
                    # Try to extract overall rating
                    rating_elements = card.find_elements(By.CSS_SELECTOR, ".overall, .rating, [class*='overall']")
                    if rating_elements:
                        card_data['overall'] = rating_elements[0].text.strip()
                    
                    # Try to extract position
                    position_elements = card.find_elements(By.CSS_SELECTOR, ".position, [class*='position']")
                    if position_elements:
                        card_data['position'] = position_elements[0].text.strip()
                    
                    # Try to extract price
                    price_elements = card.find_elements(By.CSS_SELECTOR, ".price, [class*='price']")
                    if price_elements:
                        card_data['price'] = price_elements[0].text.strip()
                    
                    if card_data:
                        cards_data.append(card_data)
                        print(f"Card {i+1}: {card_data}")
                        
                except Exception as e:
                    print(f"Error extracting card {i+1}: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error extracting cards: {e}")
            
        return cards_data
        
    def test_card_click(self):
        """Test clicking on a card to see details"""
        print("\nTesting card click...")
        
        try:
            # Find first clickable card
            cards = self.driver.find_elements(By.CSS_SELECTOR, ".player-card, .card, [class*='card']")
            if not cards:
                print("No cards found to click")
                return False
                
            first_card = cards[0]
            print(f"Clicking on first card...")
            
            # Scroll to card
            self.driver.execute_script("arguments[0].scrollIntoView(true);", first_card)
            time.sleep(1)
            
            # Click the card
            first_card.click()
            time.sleep(2)
            
            # Check if modal or details opened
            modals = self.driver.find_elements(By.CSS_SELECTOR, ".modal, .popup, [class*='modal'], [class*='popup']")
            if modals:
                print("Modal/popup opened successfully!")
                
                # Try to extract some details
                try:
                    modal_text = modals[0].text
                    print(f"Modal content preview: {modal_text[:200]}...")
                except:
                    pass
                    
                # Close modal
                try:
                    close_buttons = self.driver.find_elements(By.CSS_SELECTOR, ".close, .modal-close, [class*='close']")
                    if close_buttons:
                        close_buttons[0].click()
                        time.sleep(1)
                except:
                    pass
                    
                return True
            else:
                print("No modal/popup opened")
                return False
                
        except Exception as e:
            print(f"Error testing card click: {e}")
            return False
            
    def run_test(self):
        """Run basic functionality tests"""
        print("Starting NHL HUT Scraper Test...")
        
        try:
            # Setup
            self.setup_driver()
            self.navigate_to_cards_page()
            
            # Test 1: Get available nationalities
            nationalities = self.get_available_nationalities()
            
            # Test 2: Test a few nationalities
            test_nationalities = nationalities[:3] if len(nationalities) >= 3 else nationalities
            for nationality in test_nationalities:
                success = self.test_nationality_filter(nationality)
                if success:
                    # Test 3: Extract card data
                    cards_data = self.get_card_data()
                    
                    # Test 4: Test card click
                    self.test_card_click()
                    break
                    
            print("\nTest completed successfully!")
            
        except Exception as e:
            print(f"Test failed: {e}")
            
        finally:
            if self.driver:
                self.driver.quit()
                
    def close(self):
        """Close the driver"""
        if self.driver:
            self.driver.quit()

if __name__ == "__main__":
    scraper = NHLHUTScraper()
    scraper.run_test()