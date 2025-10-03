#!/usr/bin/env python3
"""
Truculence All-Star Hunter - Finds players with Truculence X-Factor at All-Star tier (2 AP)
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

def hunt_truculence_allstar():
    """
    Hunt for players with Truculence X-Factor at All-Star tier (2 AP)
    """
    
    print("=== Truculence All-Star Hunter ===")
    print("Target: Players with Truculence X-Factor at All-Star tier (2 AP)")
    print()
    
    # Step 1: Get a sample of players to test
    print("Step 1: Fetching sample players...")
    
    # Try different filters to get diverse players
    test_filters = [
        {"name": "High overall players", "filters": {}},
        {"name": "Defensemen", "filters": {"position": "D"}},
        {"name": "Physical players", "filters": {}},  # We'll filter by physical stats later
    ]
    
    all_players = []
    
    for test_case in test_filters:
        print(f"  Testing: {test_case['name']}")
        data = fetch_page_with_filters(0, 50, test_case['filters'])
        rows = data.get('data') or []
        all_players.extend(rows)
        print(f"    Found {len(rows)} players")
    
    # Remove duplicates and clean data
    unique_players = []
    seen_ids = set()
    for player in all_players:
        cleaned_player = clean_common_fields(player)
        pid = cleaned_player.get('player_id')
        if pid and pid not in seen_ids:
            unique_players.append(cleaned_player)
            seen_ids.add(pid)
    
    print(f"\nStep 2: Testing {len(unique_players)} unique players for Truculence All-Star...")
    print(f"Sample players to test:")
    for i, player in enumerate(unique_players[:5]):
        name = player.get('full_name', 'Unknown')
        team = player.get('team', 'Unknown')
        position = player.get('position', 'Unknown')
        overall = player.get('overall', 'Unknown')
        print(f"  {i+1}. {name} ({team}) - {position} - OVR: {overall}")
    
    truculence_allstar_players = []
    tested_count = 0
    
    for player in unique_players:
        pid = player.get('player_id')
        name = player.get('full_name', 'Unknown')
        
        if pid:
            print(f"  Testing {name} (ID: {pid})...")
            abilities = fetch_player_xfactors_detailed(int(pid))
            
            # Check for Truculence All-Star
            has_truculence_allstar = False
            for ability in abilities:
                if (ability['name'].upper() == 'TRUCULENCE' and 
                    ability['tier'] == 'All-Star' and 
                    ability['ap_cost'] == 2):
                    has_truculence_allstar = True
                    break
            
            if has_truculence_allstar:
                print(f"    ✅ FOUND TRUCULENCE ALL-STAR!")
                player['abilities'] = abilities
                truculence_allstar_players.append(player)
            else:
                # Show what abilities they have
                ability_names = [a['name'] for a in abilities]
                if ability_names:
                    print(f"    X-Factors: {', '.join(ability_names)}")
                else:
                    print(f"    No X-Factors")
            
            tested_count += 1
            time.sleep(0.5)  # Be nice to server
            
            # Limit testing to prevent too many requests
            if tested_count >= 20:  # Test first 20 players
                print(f"  Limited to first {tested_count} players to prevent server overload")
                break
    
    # Save results
    output_file = "truculence_allstar_players.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(truculence_allstar_players, f, ensure_ascii=False, indent=2)
    
    print(f"\n=== RESULTS ===")
    print(f"Players with Truculence All-Star: {len(truculence_allstar_players)}")
    print(f"Results saved to: {output_file}")
    
    if len(truculence_allstar_players) > 0:
        print(f"\n🎯 Truculence All-Star players:")
        for i, player in enumerate(truculence_allstar_players, 1):
            name = player.get('full_name', 'Unknown')
            team = player.get('team', 'Unknown')
            position = player.get('position', 'Unknown')
            overall = player.get('overall', 'Unknown')
            salary = player.get('salary', 'Unknown')
            
            print(f"  {i}. {name} ({team}) - {position} - OVR: {overall} - Salary: ${salary:,}")
            
            # Show their X-Factors
            abilities = player.get('abilities', [])
            for ability in abilities:
                if ability['name'].upper() == 'TRUCULENCE':
                    print(f"     🥊 Truculence: {ability['tier']} ({ability['ap_cost']} AP)")
    else:
        print("❌ No players found with Truculence All-Star")
        print("💡 This could mean:")
        print("   - Truculence All-Star is very rare")
        print("   - We need to test more players")
        print("   - The ability name might be different")
    
    return truculence_allstar_players

def main():
    print("Starting Truculence All-Star Hunter...")
    print("=" * 60)
    
    results = hunt_truculence_allstar()
    
    print(f"\nTruculence All-Star hunt completed!")
    print(f"Found {len(results)} players with Truculence All-Star")

if __name__ == '__main__':
    main()