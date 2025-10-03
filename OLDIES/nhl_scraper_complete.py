#!/usr/bin/env python3
"""
NHL HUT Card Scraper - Complete version
Scrapes ALL player cards from nhlhutbuilder.com with nationality filtering
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

class NHLHUTScraperComplete:
    def __init__(self):
        self.driver = None
        self.wait = None
        self.base_url = "https://nhlhutbuilder.com/cards.php"
        self.all_cards = []
        
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
        """Extract card data from current page using correct selectors"""
        print("Extracting cards from current page...")
        
        cards_data = []
        
        try:
            # Wait for cards to load - use the correct selector
            cards = self.wait.until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.advanced-stats.view_player"))
            )
            
            print(f"Found {len(cards)} player cards")
            
            for i, card in enumerate(cards):
                try:
                    card_data = {}
                    
                    # Get player ID from the id attribute
                    player_id = card.get_attribute('id')
                    if player_id:
                        card_data['player_id'] = player_id
                    
                    # Get player stats URL
                    href = card.get_attribute('href')
                    if href:
                        card_data['stats_url'] = href
                    
                    # Get card image
                    img = card.find_element(By.TAG_NAME, 'img')
                    if img:
                        card_data['image_url'] = img.get_attribute('src')
                        card_data['image_alt'] = img.get_attribute('alt')
                    
                    # Try to extract additional info from the card
                    card_text = card.text.strip()
                    if card_text:
                        card_data['text_content'] = card_text
                    
                    # Get any data attributes
                    data_attrs = {}
                    for attr in card.get_property('attributes'):
                        if attr['name'].startswith('data-'):
                            data_attrs[attr['name']] = attr['value']
                    if data_attrs:
                        card_data['data_attributes'] = data_attrs
                    
                    if card_data:
                        cards_data.append(card_data)
                        
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
                next_button = self.driver.find_element(By.CSS_SELECTOR, "#players_table_next, .paginate_button.next, [class*='next']")
                if next_button.is_enabled() and next_button.is_displayed():
                    print("Clicking next page...")
                    next_button.click()
                    time.sleep(2)
                    page += 1
                else:
                    print("No more pages available")
                    break
            except:
                # No next button found, we're done
                print("No next button found, pagination complete")
                break
                
        print(f"Total cards extracted: {len(all_cards)}")
        return all_cards
        
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
        
    def scrape_all_nationalities(self):
        """Scrape cards for all nationalities"""
        print("Starting comprehensive scrape of all nationalities...")
        
        # Get all nationalities
        nationalities = self.get_available_nationalities()
        if not nationalities:
            print("No nationalities found")
            return []
            
        all_cards = []
        total_nationalities = len(nationalities)
        
        for i, nationality in enumerate(nationalities, 1):
            print(f"\nProgress: {i}/{total_nationalities} - {nationality['text']}")
            
            try:
                cards = self.scrape_nationality(nationality['value'], nationality['text'])
                all_cards.extend(cards)
                print(f"✓ Scraped {len(cards)} cards for {nationality['text']}")
                
                # Add a small delay between nationalities
                time.sleep(1)
                
            except Exception as e:
                print(f"✗ Error scraping {nationality['text']}: {e}")
                continue
                
        print(f"\n=== SCRAPING COMPLETE ===")
        print(f"Total cards scraped: {len(all_cards)}")
        print(f"Nationalities processed: {total_nationalities}")
        
        return all_cards
        
    def save_results(self, cards, filename="nhl_cards.json"):
        """Save scraped cards to JSON file"""
        print(f"Saving results to {filename}...")
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(cards, f, indent=2, ensure_ascii=False)
            print(f"✓ Results saved to {filename}")
            return True
        except Exception as e:
            print(f"✗ Error saving results: {e}")
            return False
            
    def run_complete_scrape(self):
        """Run complete scraping of all cards"""
        print("Starting NHL HUT Complete Scraper...")
        
        try:
            # Setup
            if not self.setup_driver():
                return
                
            if not self.navigate_to_cards_page():
                return
            
            # Scrape all nationalities
            all_cards = self.scrape_all_nationalities()
            
            if all_cards:
                # Save results
                self.save_results(all_cards)
                
                # Print summary
                print(f"\n=== SUMMARY ===")
                print(f"Total cards: {len(all_cards)}")
                
                # Count by nationality
                nationality_counts = {}
                for card in all_cards:
                    nat = card.get('nationality', 'Unknown')
                    nationality_counts[nat] = nationality_counts.get(nat, 0) + 1
                    
                print("Cards by nationality:")
                for nat, count in sorted(nationality_counts.items()):
                    print(f"  {nat}: {count} cards")
                    
            else:
                print("No cards were scraped")
                        
            print("\n✓ Complete scrape finished!")
            
        except Exception as e:
            print(f"✗ Scrape failed: {e}")
            
        finally:
            if self.driver:
                self.driver.quit()
                
    def close(self):
        """Close the driver"""
        if self.driver:
            self.driver.quit()

if __name__ == "__main__":
    scraper = NHLHUTScraperComplete()
    scraper.run_complete_scrape()