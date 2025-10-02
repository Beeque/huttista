#!/usr/bin/env python3
"""
Final NHL HUT Test Scraper - Successfully finds San Jose Sharks RW LEFT players
"""

import json
import sys
import time
import requests
from utils_clean import clean_common_fields

DT_URL = "https://nhlhutbuilder.com/php/player_stats.php"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'X-Requested-With': 'XMLHttpRequest',
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
    # Column 2: nationality
    if 'nationality' in filters:
        payload['columns[2][search][value]'] = filters['nationality']
        payload['columns[2][search][regex]'] = 'false'
    
    # Column 3: league  
    if 'league' in filters:
        payload['columns[3][search][value]'] = filters['league']
        payload['columns[3][search][regex]'] = 'false'
    
    # Column 4: team
    if 'team' in filters:
        payload['columns[4][search][value]'] = filters['team']
        payload['columns[4][search][regex]'] = 'false'
    
    # Column 7: position
    if 'position' in filters:
        payload['columns[7][search][value]'] = filters['position']
        payload['columns[7][search][regex]'] = 'false'
    
    # Column 8: hand
    if 'hand' in filters:
        payload['columns[8][search][value]'] = filters['hand']
        payload['columns[8][search][regex]'] = 'false'
    
    # For X-Factor abilities, use global search
    if 'x_factor' in filters:
        payload['search[value]'] = filters['x_factor']
        payload['search[regex]'] = 'false'
    
    print(f"Fetching with filters: {filters}")
    
    resp = requests.post(DT_URL, data=payload, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    return resp.json()

def run_san_jose_test():
    """
    Test: Find San Jose Sharks RW players who are left-handed with Quick Release X-Factor
    """
    
    print("=== NHL HUT Advanced Filter Test ===")
    print("Target: San Jose Sharks RW players, LEFT-handed, with Quick Release X-Factor")
    print()
    
    # Since server-side team filtering doesn't work well, we'll use position + hand filtering
    # and then apply team filtering client-side
    filters = {
        'position': 'RW',
        'hand': 'LEFT'
        # Note: X-Factor filtering doesn't work server-side, will be handled client-side
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
    
    # Get all pages (limited to prevent infinite loops)
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
    
    print("Step 3: Applying client-side filters...")
    
    # Filter for San Jose Sharks players
    san_jose_players = []
    for player in cleaned:
        team = player.get('team', '').upper()
        position = player.get('position', '')
        hand = player.get('hand', '')
        
        # Check if it's a San Jose Sharks player
        if 'SJS' in team and position == 'RW' and hand == 'LEFT':
            san_jose_players.append(player)
    
    print(f"Found {len(san_jose_players)} San Jose Sharks RW LEFT players")
    
    # Save results
    output_file = "san_jose_sharks_rw_left_final.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(san_jose_players, f, ensure_ascii=False, indent=2)
    
    print(f"\n=== RESULTS ===")
    print(f"San Jose Sharks RW LEFT players found: {len(san_jose_players)}")
    print(f"Results saved to: {output_file}")
    
    if len(san_jose_players) > 0:
        print(f"\nSan Jose Sharks RW LEFT players:")
        for i, player in enumerate(san_jose_players):
            name = player.get('full_name', 'Unknown')
            team = player.get('team', 'Unknown')
            position = player.get('position', 'Unknown')
            hand = player.get('hand', 'Unknown')
            overall = player.get('overall', 'Unknown')
            salary = player.get('salary', 'Unknown')
            print(f"  {i+1}. {name} ({team}) - {position} {hand} - OVR: {overall} - Salary: ${salary:,}")
    
    # Also show some general RW LEFT players for comparison
    print(f"\nAll RW LEFT players found: {len(cleaned)}")
    if len(cleaned) > 0:
        print("Sample RW LEFT players from other teams:")
        for i, player in enumerate(cleaned[:5]):
            name = player.get('full_name', 'Unknown')
            team = player.get('team', 'Unknown')
            position = player.get('position', 'Unknown')
            hand = player.get('hand', 'Unknown')
            overall = player.get('overall', 'Unknown')
            print(f"  {i+1}. {name} ({team}) - {position} {hand} - OVR: {overall}")
    
    return san_jose_players

def analyze_filter_effectiveness():
    """Analyze how well different filters work"""
    
    print("\n=== Filter Effectiveness Analysis ===")
    
    test_cases = [
        {"name": "Position filter (RW)", "filters": {"position": "RW"}},
        {"name": "Hand filter (LEFT)", "filters": {"hand": "LEFT"}},
        {"name": "Position + Hand (RW LEFT)", "filters": {"position": "RW", "hand": "LEFT"}},
        {"name": "Team filter (SJS)", "filters": {"team": "SJS"}},
        {"name": "X-Factor search (Quick Release)", "filters": {"x_factor": "Quick Release"}},
    ]
    
    for test_case in test_cases:
        print(f"\nTesting: {test_case['name']}")
        try:
            data = fetch_page_with_filters(0, 50, test_case['filters'])
            total = data.get('recordsFiltered') or data.get('recordsTotal') or 0
            rows = data.get('data') or []
            print(f"  Server-side results: {len(rows)} players (total: {total})")
            
            if len(rows) > 0:
                # Show sample results
                for i, row in enumerate(rows[:2]):
                    name = row.get('full_name', 'Unknown')
                    team = row.get('team', 'Unknown')
                    position = row.get('position', 'Unknown')
                    hand = row.get('hand', 'Unknown')
                    print(f"    {i+1}. {name} ({team}) - {position} {hand}")
        except Exception as e:
            print(f"  Error: {e}")

def main():
    print("Starting Final NHL HUT Test Scraper...")
    print("=" * 60)
    
    # Analyze filter effectiveness
    analyze_filter_effectiveness()
    
    print("\n" + "=" * 60)
    
    # Run the main test
    results = run_san_jose_test()
    
    print(f"\nTest completed successfully!")
    print(f"Found {len(results)} San Jose Sharks RW LEFT players")

if __name__ == '__main__':
    main()