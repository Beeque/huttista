#!/usr/bin/env python3
"""
NHL HUT Card Scraper - Final version
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

class NHLHUTScraperFinal:
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
            
    def filter_by_nationality(self, nationality_value):
        """Filter cards by nationality"""
        print(f"Filtering by nationality: {nationality_value}")
        
        try:
            # Find and select nationality
            nationality_dropdown = self.driver.find_element(By.NAME, "nationality")
            select = Select(nationality_dropdown)
            select.select_by_value(nationality_value)
            
            # Wait for results to load
            time.sleep(3)
            
            # Check pagination info
            try:
                pagination_info = self.driver.find_element(By.CSS_SELECTOR, ".dataTables_info, .pagination-info, [class*='info']")
                print(f"Pagination info: {pagination_info.text}")
            except:
                print("No pagination info found")
                
            return True
            
        except Exception as e:
            print(f"✗ Error filtering by nationality {nationality_value}: {e}")
            return False
            
    def extract_cards_from_page(self):
        """Extract card data from current page"""
        print("Extracting cards from current page...")
        
        cards_data = []
        
        try:
            # Wait for cards to load
            cards = self.wait.until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".player-card, .card, [class*='card']"))
            )
            
            print(f"Found {len(cards)} card elements")
            
            for i, card in enumerate(cards):
                try:
                    card_data = {}
                    
                    # Get card text content
                    card_text = card.text.strip()
                    if not card_text:
                        continue
                    
                    # Try to extract player name (usually the largest text)
                    name_elements = card.find_elements(By.CSS_SELECTOR, ".player-name, .name, [class*='name'], h3, h4, h5, strong, b")
                    if name_elements:
                        for name_elem in name_elements:
                            name_text = name_elem.text.strip()
                            if name_text and len(name_text) > 2:
                                card_data['name'] = name_text
                                break
                    
                    # Try to extract overall rating (usually a number)
                    rating_elements = card.find_elements(By.CSS_SELECTOR, ".overall, .rating, [class*='overall'], [class*='rating']")
                    if rating_elements:
                        for rating_elem in rating_elements:
                            rating_text = rating_elem.text.strip()
                            if rating_text.isdigit():
                                card_data['overall'] = rating_text
                                break
                    
                    # Try to extract position
                    position_elements = card.find_elements(By.CSS_SELECTOR, ".position, [class*='position'], .pos")
                    if position_elements:
                        for pos_elem in position_elements:
                            pos_text = pos_elem.text.strip()
                            if pos_text:
                                card_data['position'] = pos_text
                                break
                    
                    # Try to extract price
                    price_elements = card.find_elements(By.CSS_SELECTOR, ".price, [class*='price'], .cost, .value")
                    if price_elements:
                        for price_elem in price_elements:
                            price_text = price_elem.text.strip()
                            if price_text and ('$' in price_text or 'M' in price_text):
                                card_data['price'] = price_text
                                break
                    
                    # If we have at least a name, add the card
                    if 'name' in card_data:
                        cards_data.append(card_data)
                        print(f"Card {i+1}: {card_data}")
                        
                except Exception as e:
                    print(f"Error extracting card {i+1}: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error extracting cards: {e}")
            
        return cards_data
        
    def handle_pagination(self):
        """Handle pagination to get all cards"""
        print("Handling pagination...")
        
        all_cards = []
        page = 1
        
        while True:
            print(f"Processing page {page}...")
            
            # Extract cards from current page
            page_cards = self.extract_cards_from_page()
            all_cards.extend(page_cards)
            
            # Check if there's a next page
            try:
                next_button = self.driver.find_element(By.CSS_SELECTOR, ".next, .pagination-next, [class*='next']")
                if next_button.is_enabled() and next_button.is_displayed():
                    next_button.click()
                    time.sleep(2)
                    page += 1
                else:
                    break
            except:
                # No next button found, we're done
                break
                
        print(f"Total cards extracted: {len(all_cards)}")
        return all_cards
        
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
            
            # Try to click the card
            try:
                first_card.click()
            except:
                # If direct click fails, try JavaScript click
                self.driver.execute_script("arguments[0].click();", first_card)
            
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
            
    def scrape_nationality(self, nationality_value, nationality_text):
        """Scrape all cards for a specific nationality"""
        print(f"\n=== Scraping {nationality_text} ===")
        
        # Filter by nationality
        if not self.filter_by_nationality(nationality_value):
            return []
            
        # Extract all cards with pagination
        all_cards = self.handle_pagination()
        
        # Add nationality info to each card
        for card in all_cards:
            card['nationality'] = nationality_text
            
        return all_cards
        
    def run_test(self):
        """Run basic functionality tests"""
        print("Starting NHL HUT Scraper Test (final version)...")
        
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
                    cards = self.scrape_nationality(nationality['value'], nationality['text'])
                    if cards:
                        print(f"✓ Successfully scraped {len(cards)} cards for {nationality['text']}")
                        
                        # Test 3: Test card click
                        self.test_card_click()
                        break
                    else:
                        print(f"✗ No cards found for {nationality['text']}")
                        
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
    scraper = NHLHUTScraperFinal()
    scraper.run_test()