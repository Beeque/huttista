#!/usr/bin/env python3
"""
Perfect NHL HUT Test Scraper - Finds San Jose Sharks RW LEFT with Quick Release X-Factor
"""

import json
import sys
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
    """Fetch page with advanced filtering capabilities"""
    
    payload = {
        'draw': 1,
        'start': start,
        'length': length,
        'search[value]': '',
        'search[regex]': 'false',
    }
    
    # Define all available columns
    columns = [
        'card_art','card','nationality','league','team','division','salary','position','hand','weight','height','full_name','overall','aOVR',
        'acceleration','agility','balance','endurance','speed','slap_shot_accuracy','slap_shot_power','wrist_shot_accuracy','wrist_shot_power',
        'deking','off_awareness','hand_eye','passing','puck_control','body_checking','strength','aggression','durability','fighting_skill',
        'def_awareness','shot_blocking','stick_checking','faceoffs','discipline','date_added','date_updated'
    ]
    
    # Set up column definitions
    for idx, name in enumerate(columns):
        payload[f'columns[{idx}][data]'] = name
        payload[f'columns[{idx}][name]'] = name
        payload[f'columns[{idx}][searchable]'] = 'true'
        payload[f'columns[{idx}][orderable]'] = 'true'
        payload[f'columns[{idx}][search][value]'] = ''
        payload[f'columns[{idx}][search][regex]'] = 'false'
    
    # Apply filters to specific columns
    if 'nationality' in filters:
        payload['columns[2][search][value]'] = filters['nationality']
        payload['columns[2][search][regex]'] = 'false'
    
    if 'league' in filters:
        payload['columns[3][search][value]'] = filters['league']
        payload['columns[3][search][regex]'] = 'false'
    
    if 'team' in filters:
        payload['columns[4][search][value]'] = filters['team']
        payload['columns[4][search][regex]'] = 'false'
    
    if 'position' in filters:
        payload['columns[7][search][value]'] = filters['position']
        payload['columns[7][search][regex]'] = 'false'
    
    if 'hand' in filters:
        payload['columns[8][search][value]'] = filters['hand']
        payload['columns[8][search][regex]'] = 'false'
    
    resp = requests.post(DT_URL, data=payload, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    return resp.json()

def fetch_player_xfactors(pid: int):
    """Fetch X-Factor abilities for a specific player"""
    url = PLAYER_URL.format(pid=pid)
    
    try:
        resp = requests.get(url, headers=PLAYER_HEADERS, timeout=30)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        abilities = []
        
        # Look for X-Factor abilities
        ability_elements = soup.select('.player_abi')
        
        for elem in ability_elements:
            title = elem.get('title', '')
            if title:
                # Extract ability name from title
                ability_name = title.split(':')[0].strip() if ':' in title else title.strip()
                if ability_name and ability_name not in [a['name'] for a in abilities]:
                    abilities.append({'name': ability_name, 'ap': None})
        
        return abilities
        
    except Exception as e:
        print(f"Error fetching X-Factors for player {pid}: {e}")
        return []

def run_perfect_test():
    """
    Perfect test: Find San Jose Sharks RW players who are left-handed with Quick Release X-Factor
    """
    
    print("=== PERFECT NHL HUT Test Scraper ===")
    print("Target: San Jose Sharks RW players, LEFT-handed, with Quick Release X-Factor")
    print()
    
    # Step 1: Get all RW LEFT players
    filters = {
        'position': 'RW',
        'hand': 'LEFT'
    }
    
    start = 0
    length = 200
    all_rows = []
    
    print("Step 1: Fetching all RW LEFT players...")
    data = fetch_page_with_filters(start, length, filters)
    total = data.get('recordsFiltered') or data.get('recordsTotal') or 0
    rows = data.get('data') or []
    all_rows.extend(rows)
    print(f"Found {len(rows)} players (total available: {total})")
    
    # Get all pages (limited)
    page_count = 0
    max_pages = 3
    
    while len(all_rows) < total and page_count < max_pages:
        start += length
        page_count += 1
        time.sleep(0.3)
        data = fetch_page_with_filters(start, length, filters)
        rows = data.get('data') or []
        all_rows.extend(rows)
        print(f"Fetched {len(all_rows)} / {total} (page {page_count})")
        
        if len(rows) == 0:
            break
    
    print(f"\nStep 2: Cleaning {len(all_rows)} records...")
    cleaned = [clean_common_fields(r) for r in all_rows]
    
    print("Step 3: Filtering for San Jose Sharks players...")
    san_jose_players = []
    for player in cleaned:
        team = player.get('team', '').upper()
        position = player.get('position', '')
        hand = player.get('hand', '')
        
        if 'SJS' in team and position == 'RW' and hand == 'LEFT':
            san_jose_players.append(player)
    
    print(f"Found {len(san_jose_players)} San Jose Sharks RW LEFT players")
    
    print("\nStep 4: Checking X-Factor abilities...")
    perfect_matches = []
    
    for i, player in enumerate(san_jose_players, 1):
        name = player.get('full_name', 'Unknown')
        pid = player.get('player_id')
        overall = player.get('overall', 'Unknown')
        card_type = player.get('card', 'Unknown')
        
        print(f"  {i}. {name} (ID: {pid}, OVR: {overall}, Card: {card_type})")
        
        if pid:
            xfactors = fetch_player_xfactors(int(pid))
            player['xfactors'] = xfactors
            
            # Check if has Quick Release
            has_quick_release = any('QUICK RELEASE' in xf['name'].upper() for xf in xfactors)
            
            if has_quick_release:
                print(f"     ✅ HAS QUICK RELEASE X-Factor!")
                perfect_matches.append(player)
            else:
                xfactor_names = [xf['name'] for xf in xfactors]
                print(f"     ❌ X-Factors: {xfactor_names}")
            
            time.sleep(0.5)  # Be nice to server
        else:
            print(f"     ❌ No player ID")
    
    # Save results
    output_file = "perfect_san_jose_quick_release.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(perfect_matches, f, ensure_ascii=False, indent=2)
    
    print(f"\n=== PERFECT RESULTS ===")
    print(f"Players matching ALL criteria: {len(perfect_matches)}")
    print(f"Results saved to: {output_file}")
    
    if len(perfect_matches) > 0:
        print(f"\n🎯 PERFECT MATCHES:")
        for i, player in enumerate(perfect_matches, 1):
            name = player.get('full_name', 'Unknown')
            team = player.get('team', 'Unknown')
            position = player.get('position', 'Unknown')
            hand = player.get('hand', 'Unknown')
            overall = player.get('overall', 'Unknown')
            salary = player.get('salary', 'Unknown')
            xfactors = [xf['name'] for xf in player.get('xfactors', [])]
            
            print(f"  {i}. {name} ({team}) - {position} {hand} - OVR: {overall} - Salary: ${salary:,}")
            print(f"     X-Factors: {', '.join(xfactors)}")
    else:
        print("❌ No players found matching ALL criteria")
    
    return perfect_matches

def main():
    print("Starting Perfect NHL HUT Test Scraper...")
    print("=" * 60)
    
    results = run_perfect_test()
    
    print(f"\nPerfect test completed!")
    print(f"Found {len(results)} players matching ALL criteria")

if __name__ == '__main__':
    main()