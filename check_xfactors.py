#!/usr/bin/env python3
"""
Check X-Factor abilities for specific players
"""

import json
import time
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://nhlhutbuilder.com/player-stats.php?id={pid}"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Referer': 'https://nhlhutbuilder.com/player-stats.php',
}

def fetch_player_abilities(pid: int):
    """Fetch X-Factor abilities for a specific player"""
    url = BASE_URL.format(pid=pid)
    print(f"Fetching abilities for player ID {pid}...")
    
    try:
        resp = requests.get(url, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        abilities = []
        
        # Look for X-Factor abilities in the page
        # Try different selectors that might contain abilities
        ability_selectors = [
            '.player_abi',
            '.ability_info',
            '.xfactor',
            '.x-factor',
            '[class*="abi"]',
            '[class*="ability"]'
        ]
        
        for selector in ability_selectors:
            elements = soup.select(selector)
            if elements:
                print(f"Found {len(elements)} elements with selector: {selector}")
                for elem in elements:
                    # Try to extract ability name and AP cost
                    name = None
                    ap = None
                    
                    # Look for ability name in title, alt, or text
                    title = elem.get('title', '')
                    alt = elem.get('alt', '')
                    text = elem.get_text(strip=True)
                    
                    if title:
                        name = title.split(':')[0].strip() if ':' in title else title.strip()
                    elif alt:
                        name = alt.strip()
                    elif text:
                        name = text.strip()
                    
                    # Look for AP cost
                    ap_elem = elem.select_one('.ap_amount, [class*="ap"]')
                    if ap_elem:
                        try:
                            ap = int(ap_elem.get_text(strip=True))
                        except:
                            pass
                    
                    if name and name not in [a['name'] for a in abilities]:
                        abilities.append({'name': name, 'ap': ap})
                        print(f"  - {name} (AP: {ap})")
        
        # If no abilities found with selectors, try to find in page text
        if not abilities:
            print("No abilities found with selectors, searching page text...")
            page_text = soup.get_text()
            if 'Quick Release' in page_text:
                print("Found 'Quick Release' in page text")
                abilities.append({'name': 'Quick Release', 'ap': None})
        
        return abilities
        
    except Exception as e:
        print(f"Error fetching abilities for player {pid}: {e}")
        return []

def main():
    # Load the San Jose players
    with open('san_jose_sharks_rw_left_final.json', 'r') as f:
        players = json.load(f)
    
    print("=== X-Factor Ability Check ===")
    print(f"Checking {len(players)} San Jose Sharks RW LEFT players...")
    print()
    
    for i, player in enumerate(players, 1):
        name = player.get('full_name', 'Unknown')
        pid = player.get('player_id')
        overall = player.get('overall', 'Unknown')
        card_type = player.get('card', 'Unknown')
        
        print(f"{i}. {name} (ID: {pid}, OVR: {overall}, Card: {card_type})")
        
        if pid:
            abilities = fetch_player_abilities(int(pid))
            player['abilities'] = abilities
            
            if abilities:
                print(f"   X-Factor abilities: {[a['name'] for a in abilities]}")
                if any('Quick Release' in a['name'] for a in abilities):
                    print("   ✅ HAS QUICK RELEASE!")
                else:
                    print("   ❌ No Quick Release")
            else:
                print("   ❌ No abilities found")
            
            print()
            time.sleep(1)  # Be nice to the server
        else:
            print("   ❌ No player ID")
            print()
    
    # Save updated data
    with open('san_jose_sharks_rw_left_final.json', 'w', encoding='utf-8') as f:
        json.dump(players, f, ensure_ascii=False, indent=2)
    
    print("Updated data saved to san_jose_sharks_rw_left_final.json")

if __name__ == '__main__':
    main()