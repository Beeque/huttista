#!/usr/bin/env python3
"""
X-Factor Tier Analyzer - Analyzes X-Factor abilities by tier (Specialist, All-Star, Elite)
"""

import json
import time
import requests
from bs4 import BeautifulSoup

PLAYER_URL = "https://nhlhutbuilder.com/player-stats.php?id={pid}"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Referer': 'https://nhlhutbuilder.com/player-stats.php',
}

def fetch_player_xfactors_detailed(pid: int):
    """Fetch detailed X-Factor abilities with tier information"""
    url = PLAYER_URL.format(pid=pid)
    
    try:
        resp = requests.get(url, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        abilities = []
        
        # Look for X-Factor abilities with detailed information
        ability_infos = soup.select('.ability_info')
        
        for info in ability_infos:
            # Get the ability name
            name_elem = info.select_one('.ability_name')
            ability_name = name_elem.get_text(strip=True) if name_elem else None
            
            # Get AP cost
            ap_elem = info.select_one('.ap_amount')
            ap_cost = None
            if ap_elem:
                try:
                    ap_cost = int(ap_elem.get_text(strip=True))
                except:
                    pass
            
            # Get category
            cat_elem = info.select_one('.xfactor_category')
            category = cat_elem.get_text(strip=True) if cat_elem else None
            
            # Determine tier based on AP cost
            tier = "Unknown"
            if ap_cost == 1:
                tier = "Specialist"
            elif ap_cost == 2:
                tier = "All-Star"
            elif ap_cost == 3:
                tier = "Elite"
            
            if ability_name and ability_name not in [a['name'] for a in abilities]:
                abilities.append({
                    'name': ability_name,
                    'ap_cost': ap_cost,
                    'tier': tier,
                    'category': category,
                    'description': info.get_text(strip=True)
                })
        
        return abilities
        
    except Exception as e:
        print(f"Error fetching X-Factors for player {pid}: {e}")
        return []

def analyze_xfactor_tiers():
    """Analyze X-Factor tiers across different players"""
    
    print("=== X-Factor Tier Analysis ===")
    print("Analyzing X-Factor abilities by tier...")
    print()
    
    # Test with some known players to understand the tier system
    test_players = [
        {"name": "Carl Grundström (SJS)", "pid": 2546},  # We know this has Quick Release
        {"name": "Carl Grundstrom (SJS)", "pid": 1504},  # This has Quick Pick
    ]
    
    all_abilities = {}
    tier_counts = {"Specialist": 0, "All-Star": 0, "Elite": 0, "Unknown": 0}
    
    for player_info in test_players:
        name = player_info["name"]
        pid = player_info["pid"]
        
        print(f"Analyzing {name} (ID: {pid})...")
        abilities = fetch_player_xfactors_detailed(pid)
        
        if abilities:
            print(f"  Found {len(abilities)} X-Factor abilities:")
            for ability in abilities:
                print(f"    - {ability['name']} ({ability['tier']}, {ability['ap_cost']} AP)")
                
                # Count by tier
                tier_counts[ability['tier']] += 1
                
                # Store ability info
                if ability['name'] not in all_abilities:
                    all_abilities[ability['name']] = {
                        'tiers_found': [],
                        'ap_costs': [],
                        'descriptions': []
                    }
                
                all_abilities[ability['name']]['tiers_found'].append(ability['tier'])
                all_abilities[ability['name']]['ap_costs'].append(ability['ap_cost'])
                all_abilities[ability['name']]['descriptions'].append(ability['description'])
        else:
            print(f"  No X-Factor abilities found")
        
        print()
        time.sleep(1)  # Be nice to server
    
    # Summary
    print("=== X-Factor Tier Summary ===")
    print(f"Tier distribution:")
    for tier, count in tier_counts.items():
        print(f"  {tier}: {count}")
    
    print(f"\nUnique abilities found: {len(all_abilities)}")
    for ability_name, info in all_abilities.items():
        unique_tiers = list(set(info['tiers_found']))
        unique_ap_costs = list(set(info['ap_costs']))
        print(f"  {ability_name}: Tiers {unique_tiers}, AP costs {unique_ap_costs}")
    
    return all_abilities, tier_counts

def test_truculence_allstar_search():
    """Test searching for Truculence All-Star tier players"""
    
    print("\n=== Testing Truculence All-Star Search ===")
    print("This would require a more sophisticated approach...")
    print("Current limitation: X-Factor filtering doesn't work server-side")
    print("Would need to:")
    print("1. Get all players")
    print("2. Check each player's X-Factors individually")
    print("3. Filter for Truculence + All-Star tier")
    print()
    
    # For now, just show what we found in our analysis
    print("Based on our analysis, we would need to:")
    print("- Fetch player pages individually")
    print("- Parse X-Factor abilities with tier information")
    print("- Filter for specific ability + tier combinations")
    print("- This would be computationally expensive but technically possible")

def main():
    print("Starting X-Factor Tier Analyzer...")
    print("=" * 60)
    
    # Analyze X-Factor tiers
    abilities, tier_counts = analyze_xfactor_tiers()
    
    # Test Truculence All-Star search concept
    test_truculence_allstar_search()
    
    print(f"\nX-Factor tier analysis completed!")
    print(f"Found {len(abilities)} unique abilities across {sum(tier_counts.values())} total instances")

if __name__ == '__main__':
    main()