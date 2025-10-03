#!/usr/bin/env python3
"""
Test AJAX cards API directly with requests
"""

import requests
from bs4 import BeautifulSoup
import json

def test_ajax_cards():
    """Test the AJAX cards API"""
    print("🔍 Testing AJAX cards API...")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'X-Requested-With': 'XMLHttpRequest',
        'Referer': 'https://nhlhutbuilder.com/cards.php',
    }
    
    # Test data for AJAX call
    data = {
        'limit': '40',
        'card_type_id': '',
        'team_id': '',
        'league_id': '',
        'position': '',
        'nationality': '',
        'sort': 'added',  # SORT BY: ADDED
        'hand': '',
        'player_id': '',
        'player_type': '',
        'superstar_abilities': '',
        'abilities_match': '',
        'pageNumber': '1'
    }
    
    try:
        print("🌐 Making AJAX call to find_cards.php...")
        response = requests.post(
            "https://nhlhutbuilder.com/php/find_cards.php",
            headers=headers,
            data=data,
            timeout=30
        )
        
        print(f"✅ Response status: {response.status_code}")
        print(f"📄 Response length: {len(response.text)} characters")
        
        if response.status_code == 200:
            # Parse the HTML response
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find all card links
            card_links = soup.find_all('a', href=True)
            player_links = [link for link in card_links if 'player-stats.php?id=' in link['href'] or 'goalie-stats.php?id=' in link['href']]
            
            print(f"✅ Found {len(player_links)} player/goalie links")
            
            # Show first few examples
            for i, link in enumerate(player_links[:5]):
                href = link['href']
                text = link.get_text(strip=True)
                print(f"   Link {i+1}: {text} -> {href}")
            
            # Save response for inspection
            with open("/workspace/ajax_response.html", "w", encoding="utf-8") as f:
                f.write(response.text)
            print("✅ AJAX response saved to ajax_response.html")
            
            return player_links
        else:
            print(f"❌ AJAX call failed with status {response.status_code}")
            print(f"Response: {response.text[:500]}...")
            return []
            
    except Exception as e:
        print(f"❌ Error making AJAX call: {e}")
        return []

if __name__ == "__main__":
    test_ajax_cards()