#!/usr/bin/env python3
"""
USA LD Pressure All-Star Hunter - Finds USA defensemen with Pressure X-Factor at All-Star tier (2 AP)
"""

import json
import time
import requests
from bs4 import BeautifulSoup
from utils_clean import clean_common_fields

DT_URL = "https://nhlhutbuilder.com/php/player_stats.php"
PLAYER_URL = "https://nhlhutbuilder.com/player-stats.php?id={pid}"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'X-Requested-With': 'XMLHttpRequest',
    'Referer': 'https://nhlhutbuilder.com/player-stats.php',
}

PLAYER_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Referer': 'https://nhlhutbuilder.com/player-stats.php',
}

def fetch_page_with_filters(start: int, length: int, filters: dict):
    """Fetch page with filtering capabilities"""
    
    payload = {
        'draw': 1,
        'start': start,
        'length': length,
        'search[value]': '',
        'search[regex]': 'false',
    }
    
    columns = [
        'card_art','card','nationality','league','team','division','salary','position','hand','weight','height','full_name','overall','aOVR',
        'acceleration','agility','balance','endurance','speed','slap_shot_accuracy','slap_shot_power','wrist_shot_accuracy','wrist_shot_power',
        'deking','off_awareness','hand_eye','passing','puck_control','body_checking','strength','aggression','durability','fighting_skill',
        'def_awareness','shot_blocking','stick_checking','faceoffs','discipline','date_added','date_updated'
    ]
    
    for idx, name in enumerate(columns):
        payload[f'columns[{idx}][data]'] = name
        payload[f'columns[{idx}][name]'] = name
        payload[f'columns[{idx}][searchable]'] = 'true'
        payload[f'columns[{idx}][orderable]'] = 'true'
        payload[f'columns[{idx}][search][value]'] = ''
        payload[f'columns[{idx}][search][regex]'] = 'false'
    
    if 'nationality' in filters:
        payload['columns[2][search][value]'] = filters['nationality']
        payload['columns[2][search][regex]'] = 'false'
    
    if 'position' in filters:
        payload['columns[7][search][value]'] = filters['position']
        payload['columns[7][search][regex]'] = 'false'
    
    if 'hand' in filters:
        payload['columns[8][search][value]'] = filters['hand']
        payload['columns[8][search][regex]'] = 'false'
    
    resp = requests.post(DT_URL, data=payload, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    return resp.json()

def fetch_player_xfactors_detailed(pid: int):
    """Fetch detailed X-Factor abilities with tier information"""
    url = PLAYER_URL.format(pid=pid)
    
    try:
        resp = requests.get(url, headers=PLAYER_HEADERS, timeout=30)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        abilities = []
        ability_infos = soup.select('.ability_info')
        
        for info in ability_infos:
            name_elem = info.select_one('.ability_name')
            ability_name = name_elem.get_text(strip=True) if name_elem else None
            
            ap_elem = info.select_one('.ap_amount')
            ap_cost = None
            if ap_elem:
                try:
                    ap_cost = int(ap_elem.get_text(strip=True))
                except:
                    pass
            
            cat_elem = info.select_one('.xfactor_category')
            category = cat_elem.get_text(strip=True) if cat_elem else None
            
            tier = "Unknown"
            if ap_cost == 1:
                tier = "Specialist"
            elif ap_cost == 2:
                tier = "All-Star"
            elif ap_cost == 3:
                tier = "Elite"
            
            if ability_name:
                abilities.append({
                    'name': ability_name,
                    'ap_cost': ap_cost,
                    'tier': tier,
                    'category': category
                })
        
        return abilities
        
    except Exception as e:
        print(f"Error fetching X-Factors for player {pid}: {e}")
        return []

def hunt_usa_ld_pressure_allstar():
    """
    Hunt for USA LD players with Pressure X-Factor at All-Star tier (2 AP)
    """
    
    print("=== USA LD Pressure All-Star Hunter ===")
    print("Target: USA defensemen (LD) with Pressure X-Factor at All-Star tier (2 AP)")
    print()
    
    # Step 1: Get USA LD players
    print("Step 1: Fetching USA LD players...")
    
    filters = {
        'nationality': 'USA',
        'position': 'LD'
    }
    
    start = 0
    length = 200
    all_players = []
    
    data = fetch_page_with_filters(start, length, filters)
    total = data.get('recordsFiltered') or data.get('recordsTotal') or 0
    rows = data.get('data') or []
    all_players.extend(rows)
    print(f"Found {len(rows)} USA LD players (total available: {total})")
    
    # Get all pages (limited)
    page_count = 0
    max_pages = 3
    
    while len(all_players) < total and page_count < max_pages:
        start += length
        page_count += 1
        time.sleep(0.3)
        data = fetch_page_with_filters(start, length, filters)
        rows = data.get('data') or []
        all_players.extend(rows)
        print(f"Fetched {len(all_players)} / {total} (page {page_count})")
        
        if len(rows) == 0:
            break
    
    print(f"\nStep 2: Cleaning {len(all_players)} USA LD players...")
    cleaned_players = [clean_common_fields(p) for p in all_players]
    
    print("Step 3: Testing USA LD players for Pressure All-Star...")
    print(f"Testing {len(cleaned_players)} players...")
    
    pressure_allstar_players = []
    tested_count = 0
    
    for player in cleaned_players:
        pid = player.get('player_id')
        name = player.get('full_name', 'Unknown')
        team = player.get('team', 'Unknown')
        overall = player.get('overall', 'Unknown')
        
        if pid:
            print(f"  Testing {name} ({team}) - OVR: {overall} (ID: {pid})...")
            abilities = fetch_player_xfactors_detailed(int(pid))
            
            # Check for Pressure All-Star
            has_pressure_allstar = False
            pressure_abilities = []
            
            for ability in abilities:
                if ability['name'].upper() == 'PRESSURE':
                    pressure_abilities.append(ability)
                    if (ability['tier'] == 'All-Star' and 
                        ability['ap_cost'] == 2):
                        has_pressure_allstar = True
            
            if has_pressure_allstar:
                print(f"    ✅ FOUND PRESSURE ALL-STAR!")
                player['abilities'] = abilities
                pressure_allstar_players.append(player)
            else:
                # Show what X-Factors they have
                ability_names = [a['name'] for a in abilities]
                if ability_names:
                    print(f"    X-Factors: {', '.join(ability_names)}")
                    # Show Pressure tier if they have it
                    for ability in pressure_abilities:
                        print(f"      Pressure: {ability['tier']} ({ability['ap_cost']} AP)")
                else:
                    print(f"    No X-Factors")
            
            tested_count += 1
            time.sleep(0.5)  # Be nice to server
            
            # Limit testing to prevent too many requests
            if tested_count >= 30:  # Test first 30 players
                print(f"  Limited to first {tested_count} players to prevent server overload")
                break
    
    # Save results
    output_file = "usa_ld_pressure_allstar_players.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(pressure_allstar_players, f, ensure_ascii=False, indent=2)
    
    print(f"\n=== RESULTS ===")
    print(f"USA LD players with Pressure All-Star: {len(pressure_allstar_players)}")
    print(f"Results saved to: {output_file}")
    
    if len(pressure_allstar_players) > 0:
        print(f"\n🎯 USA LD Pressure All-Star players:")
        for i, player in enumerate(pressure_allstar_players, 1):
            name = player.get('full_name', 'Unknown')
            team = player.get('team', 'Unknown')
            position = player.get('position', 'Unknown')
            hand = player.get('hand', 'Unknown')
            overall = player.get('overall', 'Unknown')
            salary = player.get('salary', 'Unknown')
            nationality = player.get('nationality', 'Unknown')
            
            print(f"  {i}. {name} ({team}) - {position} {hand} - OVR: {overall} - Salary: ${salary:,}")
            print(f"     Nationality: {nationality}")
            
            # Show their X-Factors
            abilities = player.get('abilities', [])
            for ability in abilities:
                if ability['name'].upper() == 'PRESSURE':
                    print(f"     🎯 Pressure: {ability['tier']} ({ability['ap_cost']} AP) - {ability['category']}")
            
            # Show all X-Factors
            all_xfactors = [f"{a['name']} ({a['tier']}, {a['ap_cost']} AP)" for a in abilities]
            print(f"     All X-Factors: {', '.join(all_xfactors)}")
    else:
        print("❌ No USA LD players found with Pressure All-Star")
        print("💡 This could mean:")
        print("   - Pressure All-Star is very rare among USA LD players")
        print("   - We need to test more players")
        print("   - The ability name might be different (e.g., PRESSURE+ vs PRESSURE)")
    
    return pressure_allstar_players

def main():
    print("Starting USA LD Pressure All-Star Hunter...")
    print("=" * 60)
    
    results = hunt_usa_ld_pressure_allstar()
    
    print(f"\nUSA LD Pressure All-Star hunt completed!")
    print(f"Found {len(results)} USA LD players with Pressure All-Star")

if __name__ == '__main__':
    main()