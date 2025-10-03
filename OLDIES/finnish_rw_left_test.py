#!/usr/bin/env python3
"""
Finnish RW LEFT Test Scraper - Finds Finnish players who are RW and left-handed
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
    
    print(f"Fetching with filters: {filters}")
    
    resp = requests.post(DT_URL, data=payload, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    return resp.json()

def run_finnish_rw_left_test():
    """
    Test: Find Finnish players who are RW and left-handed
    """
    
    print("=== Finnish RW LEFT Test Scraper ===")
    print("Target: Finnish players, RW position, LEFT-handed")
    print()
    
    # Step 1: Get all Finnish players first
    print("Step 1: Fetching all Finnish players...")
    filters = {
        'nationality': 'Finland'
    }
    
    start = 0
    length = 200
    all_rows = []
    
    data = fetch_page_with_filters(start, length, filters)
    total = data.get('recordsFiltered') or data.get('recordsTotal') or 0
    rows = data.get('data') or []
    all_rows.extend(rows)
    print(f"Found {len(rows)} Finnish players (total available: {total})")
    
    # Get all pages (limited)
    page_count = 0
    max_pages = 5
    
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
    
    print(f"\nStep 2: Cleaning {len(all_rows)} Finnish players...")
    cleaned = [clean_common_fields(r) for r in all_rows]
    
    print("Step 3: Filtering for RW LEFT players...")
    finnish_rw_left = []
    
    for player in cleaned:
        nationality = player.get('nationality', '').strip()
        position = player.get('position', '').strip()
        hand = player.get('hand', '').strip()
        
        # Check if Finnish, RW, and LEFT
        if (nationality.lower() == 'finland' and 
            position == 'RW' and 
            hand == 'LEFT'):
            finnish_rw_left.append(player)
    
    print(f"Found {len(finnish_rw_left)} Finnish RW LEFT players")
    
    # Save results
    output_file = "finnish_rw_left_players.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(finnish_rw_left, f, ensure_ascii=False, indent=2)
    
    print(f"\n=== RESULTS ===")
    print(f"Finnish RW LEFT players found: {len(finnish_rw_left)}")
    print(f"Results saved to: {output_file}")
    
    if len(finnish_rw_left) > 0:
        print(f"\n🇫🇮 Finnish RW LEFT players:")
        for i, player in enumerate(finnish_rw_left, 1):
            name = player.get('full_name', 'Unknown')
            team = player.get('team', 'Unknown')
            position = player.get('position', 'Unknown')
            hand = player.get('hand', 'Unknown')
            overall = player.get('overall', 'Unknown')
            salary = player.get('salary', 'Unknown')
            nationality = player.get('nationality', 'Unknown')
            
            print(f"  {i}. {name} ({team}) - {position} {hand} - OVR: {overall} - Salary: ${salary:,}")
            print(f"     Nationality: {nationality}")
    else:
        print("❌ No Finnish RW LEFT players found")
    
    # Also show some general Finnish players for context
    print(f"\nAll Finnish players found: {len(cleaned)}")
    if len(cleaned) > 0:
        print("Sample Finnish players:")
        for i, player in enumerate(cleaned[:5]):
            name = player.get('full_name', 'Unknown')
            team = player.get('team', 'Unknown')
            position = player.get('position', 'Unknown')
            hand = player.get('hand', 'Unknown')
            overall = player.get('overall', 'Unknown')
            print(f"  {i+1}. {name} ({team}) - {position} {hand} - OVR: {overall}")
    
    return finnish_rw_left

def analyze_finnish_players():
    """Analyze Finnish players by position and hand"""
    
    print("\n=== Finnish Players Analysis ===")
    
    # Get all Finnish players
    filters = {'nationality': 'Finland'}
    data = fetch_page_with_filters(0, 200, filters)
    rows = data.get('data') or []
    
    if not rows:
        print("No Finnish players found")
        return
    
    # Analyze by position
    positions = {}
    hands = {}
    position_hand = {}
    
    for row in rows:
        position = row.get('position', 'Unknown')
        hand = row.get('hand', 'Unknown')
        pos_hand = f"{position} {hand}"
        
        positions[position] = positions.get(position, 0) + 1
        hands[hand] = hands.get(hand, 0) + 1
        position_hand[pos_hand] = position_hand.get(pos_hand, 0) + 1
    
    print(f"Finnish players by position:")
    for pos, count in sorted(positions.items()):
        print(f"  {pos}: {count}")
    
    print(f"\nFinnish players by hand:")
    for hand, count in sorted(hands.items()):
        print(f"  {hand}: {count}")
    
    print(f"\nFinnish players by position + hand:")
    for pos_hand, count in sorted(position_hand.items()):
        print(f"  {pos_hand}: {count}")

def main():
    print("Starting Finnish RW LEFT Test Scraper...")
    print("=" * 60)
    
    # Analyze Finnish players first
    analyze_finnish_players()
    
    print("\n" + "=" * 60)
    
    # Run the main test
    results = run_finnish_rw_left_test()
    
    print(f"\nFinnish RW LEFT test completed!")
    print(f"Found {len(results)} Finnish RW LEFT players")

if __name__ == '__main__':
    main()