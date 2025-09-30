#!/usr/bin/env python3
"""
NHL HUT Card Scraper - Working version
Scrapes player cards from nhlhutbuilder.com with nationality filtering
"""

import time
import json
import os
import tempfile
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

class NHLHUTScraperWorking:
    def __init__(self):
        self.driver = None
        self.wait = None
        self.base_url = "https://nhlhutbuilder.com/cards.php"
        
    def setup_driver(self):
        """Setup Chrome WebDriver with appropriate options"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        # Create unique temp directory for each session
        temp_dir = tempfile.mkdtemp(prefix="chrome_")
        chrome_options.add_argument(f"--user-data-dir={temp_dir}")
        
        # Try to find Chrome binary
        possible_paths = [
            "/usr/bin/google-chrome",
            "/usr/bin/google-chrome-stable",
            "/usr/bin/chromium-browser",
            "/usr/bin/chromium"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                chrome_options.binary_location = path
                print(f"Using browser: {path}")
                break
        
        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.wait = WebDriverWait(self.driver, 15)
            print("✓ WebDriver initialized successfully")
            return True
        except Exception as e:
            print(f"✗ Failed to initialize WebDriver: {e}")
            return False
        
    def navigate_to_cards_page(self):
        """Navigate to the cards page"""
        print("Navigating to cards page...")
        try:
            self.driver.get(self.base_url)
            
            # Wait for page to load
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            time.sleep(3)  # Give extra time for JS to load
            
            print("✓ Page loaded successfully!")
            return True
        except Exception as e:
            print(f"✗ Failed to load page: {e}")
            return False
            
    def get_available_nationalities(self):
        """Get list of available nationalities from the dropdown"""
        print("Getting available nationalities...")
        
        try:
            # Find the nationality dropdown
            nationality_dropdown = self.wait.until(
                EC.presence_of_element_located((By.NAME, "nationality"))
            )
            
            # Get all options
            select = Select(nationality_dropdown)
            nationalities = []
            
            for option in select.options:
                if option.text.strip() and option.text.strip() != "All":
                    nationalities.append({
                        'value': option.get_attribute('value'),
                        'text': option.text.strip()
                    })
                    
            print(f"✓ Found {len(nationalities)} nationalities")
            return nationalities
            
        except Exception as e:
            print(f"✗ Error getting nationalities: {e}")
            return []
            
    def test_nationality_filter(self, nationality_value):
        """Test filtering by nationality"""
        print(f"\nTesting nationality filter: {nationality_value}")
        
        try:
            # Find and select nationality
            nationality_dropdown = self.driver.find_element(By.NAME, "nationality")
            select = Select(nationality_dropdown)
            select.select_by_value(nationality_value)
            
            # Wait for results to load
            time.sleep(3)
            
            # Check if results are displayed
            cards = self.driver.find_elements(By.CSS_SELECTOR, ".player-card, .card, [class*='card']")
            print(f"Found {len(cards)} potential card elements")
            
            # Check pagination info if available
            try:
                pagination_info = self.driver.find_element(By.CSS_SELECTOR, ".dataTables_info, .pagination-info, [class*='info']")
                print(f"Pagination info: {pagination_info.text}")
            except:
                print("No pagination info found")
                
            # Try to extract some card data
            if cards:
                print("Attempting to extract card data...")
                for i, card in enumerate(cards[:3]):  # First 3 cards
                    try:
                        card_text = card.text
                        if card_text.strip():
                            print(f"Card {i+1} text: {card_text[:100]}...")
                    except:
                        pass
                        
            return len(cards) > 0
            
        except Exception as e:
            print(f"✗ Error testing nationality {nationality_value}: {e}")
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
                print("✓ Modal/popup opened successfully!")
                
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
            print(f"✗ Error testing card click: {e}")
            return False
            
    def run_test(self):
        """Run basic functionality tests"""
        print("Starting NHL HUT Scraper Test (working version)...")
        
        try:
            # Setup
            if not self.setup_driver():
                return
                
            if not self.navigate_to_cards_page():
                return
            
            # Test 1: Get available nationalities
            nationalities = self.get_available_nationalities()
            
            # Test 2: Test a few nationalities
            if nationalities:
                test_nationalities = nationalities[:3]  # Test first 3
                for nationality in test_nationalities:
                    success = self.test_nationality_filter(nationality['value'])
                    if success:
                        # Test 3: Extract card data
                        cards_data = self.get_card_data()
                        
                        # Test 4: Test card click
                        self.test_card_click()
                        break
                        
            print("\n✓ Test completed successfully!")
            
        except Exception as e:
            print(f"✗ Test failed: {e}")
            
        finally:
            if self.driver:
                self.driver.quit()
                
    def close(self):
        """Close the driver"""
        if self.driver:
            self.driver.quit()

if __name__ == "__main__":
    scraper = NHLHUTScraperWorking()
    scraper.run_test()