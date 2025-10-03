#!/usr/bin/env python3
"""
NHL HUT Card Scraper using requests
Scrapes player cards from nhlhutbuilder.com with nationality filtering
"""

import requests
import json
import time
from bs4 import BeautifulSoup
from urllib.parse import urlencode

class NHLHUTScraperRequests:
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
            
    def parse_page(self, html):
        """Parse the HTML page to extract information"""
        if not html:
            return None
            
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
            print(f"Found {len(nationalities)} nationalities")
            return {'nationalities': nationalities}
        
        # Look for cards
        cards = soup.find_all(['div', 'tr'], class_=lambda x: x and 'card' in x.lower() if x else False)
        if cards:
            print(f"Found {len(cards)} potential cards")
            return {'cards': len(cards)}
            
        # Look for pagination info
        pagination_info = soup.find(text=lambda text: text and 'Showing' in text and 'entries' in text)
        if pagination_info:
            print(f"Pagination info: {pagination_info.strip()}")
            return {'pagination': pagination_info.strip()}
            
        return {'content': 'Page loaded but no specific elements found'}
        
    def test_basic_access(self):
        """Test basic access to the site"""
        print("Testing basic access to NHL HUT Builder...")
        
        html = self.get_page()
        if html:
            print("✓ Successfully accessed the site")
            result = self.parse_page(html)
            if result:
                print(f"✓ Page parsed successfully: {result}")
                return True
        else:
            print("✗ Failed to access the site")
            return False
            
    def test_nationality_filter(self, nationality_value):
        """Test filtering by nationality"""
        print(f"\nTesting nationality filter: {nationality_value}")
        
        params = {'nationality': nationality_value}
        html = self.get_page(params)
        
        if html:
            result = self.parse_page(html)
            if result and 'cards' in result:
                print(f"✓ Found {result['cards']} cards for nationality {nationality_value}")
                return True
            elif result and 'pagination' in result:
                print(f"✓ Pagination info: {result['pagination']}")
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
            result = self.parse_page(html)
            if result and 'nationalities' in result:
                return result['nationalities']
        
        return []
        
    def run_test(self):
        """Run basic functionality tests"""
        print("Starting NHL HUT Scraper Test (requests version)...")
        
        # Test 1: Basic access
        if not self.test_basic_access():
            print("Basic access test failed, stopping.")
            return
            
        # Test 2: Get nationalities
        nationalities = self.get_available_nationalities()
        if nationalities:
            print(f"Found {len(nationalities)} nationalities")
            
            # Test 3: Test a few nationalities
            test_nationalities = nationalities[:3]  # Test first 3
            for nationality in test_nationalities:
                success = self.test_nationality_filter(nationality['value'])
                if success:
                    print(f"✓ Successfully tested nationality: {nationality['text']}")
                else:
                    print(f"✗ Failed to test nationality: {nationality['text']}")
        else:
            print("No nationalities found, trying direct filter test...")
            # Try some common nationalities
            test_values = ['finland', 'canada', 'usa', 'sweden']
            for value in test_values:
                self.test_nationality_filter(value)
                
        print("\nTest completed!")

if __name__ == "__main__":
    scraper = NHLHUTScraperRequests()
    scraper.run_test()