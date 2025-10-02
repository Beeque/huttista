#!/usr/bin/env python3
"""
Country X-Factor Enricher
Enriches any country's players with X-Factor abilities
"""

import requests
import json
import time
from bs4 import BeautifulSoup

def fetch_xfactors_with_tiers(player_id, timeout=10, is_goalie=False):
    """Fetch X-Factor abilities for a player with timeout protection"""
    try:
        if is_goalie:
            url = f"https://nhlhutbuilder.com/goalie-stats.php?id={player_id}"
        else:
            url = f"https://nhlhutbuilder.com/player-stats.php?id={player_id}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        
        resp = requests.get(url, headers=headers, timeout=timeout)
        
        if resp.status_code != 200:
            return []
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        xfactors = []
        
        # Find all X-Factor ability containers
        ability_containers = soup.find_all('div', class_='ability_info')
        
        for container in ability_containers:
            # Get ability name
            name_elem = container.find('div', class_='ability_name')
            if not name_elem:
                continue
                
            ability_name = name_elem.get_text(strip=True)
            
            # Get AP cost (tier)
            ap_elem = container.find('div', class_='ability_points')
            if ap_elem:
                ap_amount = ap_elem.find('div', class_='ap_amount')
                if ap_amount:
                    ap_cost = ap_amount.get_text(strip=True)
                    try:
                        ap_cost = int(ap_cost)
                    except:
                        ap_cost = 1
                else:
                    ap_cost = 1
            else:
                ap_cost = 1
            
            # Determine tier based on AP cost
            if ap_cost == 1:
                tier = "Specialist"
            elif ap_cost == 2:
                tier = "All-Star"
            elif ap_cost == 3:
                tier = "Elite"
            else:
                tier = "Specialist"
            
            xfactors.append({
                'name': ability_name,
                'ap_cost': ap_cost,
                'tier': tier
            })
        
        return xfactors
        
    except Exception as e:
        print(f"   ❌ Error fetching X-Factors for {player_id}: {e}")
        return []

def enrich_country_xfactors(country):
    """Enrich country players with X-Factor data"""
    print(f"🏒 {country.upper()} X-FACTOR ENRICHER")
    print("=" * 50)
    
    # Load existing data
    try:
        with open(f'{country.lower()}.json', 'r', encoding='utf-8') as f:
            players = json.load(f)
    except FileNotFoundError:
        print(f"❌ {country.lower()}.json not found! Run universal_country_fetcher.py first.")
        return
    
    print(f"📊 Loaded {len(players)} players")
    
    # Check which players need X-Factor data
    players_without_xfactors = []
    for player in players:
        if 'xfactors' not in player or not player['xfactors']:
            players_without_xfactors.append(player)
    
    print(f"🎯 {len(players_without_xfactors)} players need X-Factor data")
    
    if not players_without_xfactors:
        print("✅ All players already have X-Factor data!")
        return
    
    # Enrich players with X-Factor data
    enriched_count = 0
    for i, player in enumerate(players_without_xfactors):
        player_id = player.get('player_id')
        if not player_id:
            print(f"   ⚠️  Player {i+1} has no player_id, skipping")
            continue
        
        print(f"   🔄 Processing player {i+1}/{len(players_without_xfactors)}: {player.get('full_name', 'Unknown')} (ID: {player_id})")
        
        # Check if this is a goalie
        goalie_fields = ['glove_high', 'glove_low', 'stick_high', 'stick_low', 'shot_recovery', 'aggression', 'agility', 'speed', 'positioning', 'breakaway', 'vision', 'poke_check', 'rebound_control', 'passing']
        is_goalie = any(field in player for field in goalie_fields)
        
        xfactors = fetch_xfactors_with_tiers(player_id, is_goalie=is_goalie)
        player['xfactors'] = xfactors
        
        if xfactors:
            print(f"      ✅ Found {len(xfactors)} X-Factors")
            enriched_count += 1
        else:
            print(f"      ⚠️  No X-Factors found")
        
        # Small delay to be nice to the server
        time.sleep(0.3)
    
    # Save enriched data
    print(f"\n💾 SAVING ENRICHED DATA...")
    with open(f'{country.lower()}.json', 'w', encoding='utf-8') as f:
        json.dump(players, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Enriched {enriched_count} players with X-Factor data")
    
    # Final summary
    players_with_xfactors = len([p for p in players if p.get('xfactors')])
    print(f"\n📊 FINAL SUMMARY:")
    print(f"   • Total players: {len(players)}")
    print(f"   • Players with X-Factors: {players_with_xfactors}")
    print(f"   • Players without X-Factors: {len(players) - players_with_xfactors}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python3 enrich_country_xfactors.py <country_name>")
        print("Example: python3 enrich_country_xfactors.py Denmark")
        sys.exit(1)
    
    country = sys.argv[1]
    enrich_country_xfactors(country)