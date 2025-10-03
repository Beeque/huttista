#!/usr/bin/env python3
"""
Explore cards.php page structure using requests (no Selenium)
"""

import requests
from bs4 import BeautifulSoup
import time

def explore_cards_page_requests():
    """Explore the cards.php page structure using requests"""
    print("🔍 Exploring cards.php page structure with requests...")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    try:
        # Get the main cards page
        print("🌐 Loading cards.php...")
        response = requests.get("https://nhlhutbuilder.com/cards.php", headers=headers, timeout=30)
        response.raise_for_status()
        
        print(f"✅ Page loaded successfully (Status: {response.status_code})")
        print(f"📄 Content length: {len(response.text)} characters")
        
        # Parse with BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for sort options
        print("\n🔍 Looking for sort options...")
        sort_selects = soup.find_all('select')
        for i, select in enumerate(sort_selects):
            name = select.get('name', 'no-name')
            select_id = select.get('id', 'no-id')
            print(f"✅ Select {i+1}: name='{name}', id='{select_id}'")
            
            options = select.find_all('option')
            print(f"   Options ({len(options)}):")
            for opt in options[:10]:  # First 10 options
                value = opt.get('value', 'no-value')
                text = opt.get_text(strip=True)
                print(f"     - {text} (value: {value})")
            if len(options) > 10:
                print(f"     ... and {len(options) - 10} more")
        
        # Look for card links
        print("\n🔍 Looking for card links...")
        card_links = soup.find_all('a', href=True)
        player_links = [link for link in card_links if 'player-stats.php?id=' in link['href'] or 'goalie-stats.php?id=' in link['href']]
        
        print(f"✅ Found {len(player_links)} player/goalie links")
        
        # Show first few examples
        for i, link in enumerate(player_links[:5]):
            href = link['href']
            text = link.get_text(strip=True)
            print(f"   Link {i+1}: {text} -> {href}")
        
        # Look for card containers
        print("\n🔍 Looking for card containers...")
        card_containers = soup.find_all(['div', 'article', 'section'], class_=True)
        card_classes = [elem for elem in card_containers if 'card' in elem.get('class', [])]
        
        print(f"✅ Found {len(card_classes)} elements with 'card' in class")
        for i, elem in enumerate(card_classes[:3]):
            classes = ' '.join(elem.get('class', []))
            print(f"   Container {i+1}: <{elem.name}> class='{classes}'")
        
        # Look for pagination
        print("\n🔍 Looking for pagination...")
        pagination_links = soup.find_all('a', href=True)
        page_links = [link for link in pagination_links if 'page=' in link['href'] or 'p=' in link['href']]
        
        print(f"✅ Found {len(page_links)} pagination links")
        for i, link in enumerate(page_links[:5]):
            href = link['href']
            text = link.get_text(strip=True)
            print(f"   Page link {i+1}: {text} -> {href}")
        
        # Look for forms (might contain sort options)
        print("\n🔍 Looking for forms...")
        forms = soup.find_all('form')
        print(f"✅ Found {len(forms)} forms")
        for i, form in enumerate(forms):
            action = form.get('action', 'no-action')
            method = form.get('method', 'no-method')
            print(f"   Form {i+1}: action='{action}', method='{method}'")
            
            # Look for inputs in form
            inputs = form.find_all(['input', 'select'])
            for inp in inputs[:5]:
                inp_type = inp.get('type', inp.name)
                inp_name = inp.get('name', 'no-name')
                inp_value = inp.get('value', 'no-value')
                print(f"     Input: type='{inp_type}', name='{inp_name}', value='{inp_value}'")
        
        # Save page source for manual inspection
        print("\n📄 Saving page source for manual inspection...")
        with open("/workspace/cards_page_source_requests.html", "w", encoding="utf-8") as f:
            f.write(response.text)
        print("✅ Page source saved to cards_page_source_requests.html")
        
        # Try to find specific patterns
        print("\n🔍 Looking for specific patterns...")
        
        # Look for DataTables (common for card listings)
        datatables = soup.find_all(['table', 'div'], class_=True)
        dt_elements = [elem for elem in datatables if 'data' in elem.get('class', []) or 'table' in elem.get('class', [])]
        print(f"✅ Found {len(dt_elements)} potential DataTable elements")
        
        # Look for JavaScript that might load cards
        scripts = soup.find_all('script')
        card_scripts = [script for script in scripts if script.string and ('card' in script.string.lower() or 'player' in script.string.lower())]
        print(f"✅ Found {len(card_scripts)} scripts mentioning cards/players")
        
        print("\n✅ Exploration complete!")
        
    except Exception as e:
        print(f"❌ Error during exploration: {e}")

if __name__ == "__main__":
    explore_cards_page_requests()