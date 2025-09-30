#!/usr/bin/env python3
"""
NHL HUT Card Scraper - Simple version
Scrapes player cards from nhlhutbuilder.com with nationality filtering
"""

import requests
import json
import time
from bs4 import BeautifulSoup
from urllib.parse import urlencode

class NHLHUTScraperSimple:
    def __init__(self):
        self.session = requests.Session()
        self.base_url = "https://nhlhutbuilder.com/cards.php"
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
    def get_page(self, params=None):
        """Get the cards page with optional parameters"""
        try:
            if params:
                url = f"{self.base_url}?{urlencode(params)}"
            else:
                url = self.base_url
                
            print(f"Fetching: {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"Error fetching page: {e}")
            return None
            
    def parse_nationalities(self, html):
        """Parse the HTML page to extract nationalities"""
        if not html:
            return []
            
        soup = BeautifulSoup(html, 'html.parser')
        
        # Look for filter dropdowns
        nationality_select = soup.find('select', {'name': 'nationality'})
        if nationality_select:
            nationalities = []
            for option in nationality_select.find_all('option'):
                if option.get('value') and option.get('value') != '':
                    nationalities.append({
                        'value': option.get('value'),
                        'text': option.text.strip()
                    })
            return nationalities
        
        return []
        
    def parse_cards(self, html):
        """Parse the HTML page to extract card information"""
        if not html:
            return []
            
        soup = BeautifulSoup(html, 'html.parser')
        cards = []
        
        # Look for different possible card selectors
        card_selectors = [
            'div[class*="card"]',
            'div[class*="player"]',
            'tr[class*="card"]',
            'tr[class*="player"]',
            '.player-card',
            '.card',
            '[data-player]'
        ]
        
        for selector in card_selectors:
            elements = soup.select(selector)
            if elements:
                print(f"Found {len(elements)} elements with selector: {selector}")
                for element in elements:
                    card_data = self.extract_card_data(element)
                    if card_data:
                        cards.append(card_data)
                break
                
        return cards
        
    def extract_card_data(self, element):
        """Extract data from a card element"""
        card_data = {}
        
        # Try to extract player name
        name_selectors = [
            '.player-name', '.name', '[class*="name"]',
            'h3', 'h4', 'h5', 'strong', 'b'
        ]
        
        for selector in name_selectors:
            name_elem = element.select_one(selector)
            if name_elem and name_elem.get_text(strip=True):
                card_data['name'] = name_elem.get_text(strip=True)
                break
                
        # Try to extract overall rating
        rating_selectors = [
            '.overall', '.rating', '[class*="overall"]',
            '[class*="rating"]', '.score'
        ]
        
        for selector in rating_selectors:
            rating_elem = element.select_one(selector)
            if rating_elem and rating_elem.get_text(strip=True):
                card_data['overall'] = rating_elem.get_text(strip=True)
                break
                
        # Try to extract position
        position_selectors = [
            '.position', '[class*="position"]', '.pos'
        ]
        
        for selector in position_selectors:
            pos_elem = element.select_one(selector)
            if pos_elem and pos_elem.get_text(strip=True):
                card_data['position'] = pos_elem.get_text(strip=True)
                break
                
        # Try to extract price
        price_selectors = [
            '.price', '[class*="price"]', '.cost', '.value'
        ]
        
        for selector in price_selectors:
            price_elem = element.select_one(selector)
            if price_elem and price_elem.get_text(strip=True):
                card_data['price'] = price_elem.get_text(strip=True)
                break
                
        return card_data if card_data else None
        
    def test_nationality_filter(self, nationality_value):
        """Test filtering by nationality"""
        print(f"\nTesting nationality filter: {nationality_value}")
        
        params = {'nationality': nationality_value}
        html = self.get_page(params)
        
        if html:
            cards = self.parse_cards(html)
            if cards:
                print(f"✓ Found {len(cards)} cards for nationality {nationality_value}")
                for i, card in enumerate(cards[:3]):  # Show first 3 cards
                    print(f"  Card {i+1}: {card}")
                return True
            else:
                print(f"✗ No cards found for nationality {nationality_value}")
                return False
        else:
            print(f"✗ Failed to fetch page for nationality {nationality_value}")
            return False
            
    def get_available_nationalities(self):
        """Get list of available nationalities"""
        print("Getting available nationalities...")
        
        html = self.get_page()
        if html:
            nationalities = self.parse_nationalities(html)
            print(f"Found {len(nationalities)} nationalities")
            return nationalities
        
        return []
        
    def run_test(self):
        """Run basic functionality tests"""
        print("Starting NHL HUT Scraper Test (simple version)...")
        
        # Test 1: Basic access
        html = self.get_page()
        if not html:
            print("✗ Failed to access the site")
            return
            
        print("✓ Successfully accessed the site")
        
        # Test 2: Get nationalities
        nationalities = self.get_available_nationalities()
        if nationalities:
            print(f"✓ Found {len(nationalities)} nationalities")
            
            # Test 3: Test a few nationalities
            test_nationalities = nationalities[:5]  # Test first 5
            for nationality in test_nationalities:
                success = self.test_nationality_filter(nationality['value'])
                if success:
                    print(f"✓ Successfully tested nationality: {nationality['text']}")
                    break
                else:
                    print(f"✗ Failed to test nationality: {nationality['text']}")
        else:
            print("✗ No nationalities found")
            
        print("\nTest completed!")

if __name__ == "__main__":
    scraper = NHLHUTScraperSimple()
    scraper.run_test()