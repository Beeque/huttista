#!/usr/bin/env python3
"""
Sweden Complete Fetcher - Fetches all Sweden players with complete data
"""

import json
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

def fetch_page_with_filters(start: int, length: int, nationality: str):
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
    
    if nationality:
        payload['columns[2][search][value]'] = nationality
        payload['columns[2][search][regex]'] = 'false'
    
    resp = requests.post(DT_URL, data=payload, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    return resp.json()

def fetch_sweden_players():
    """
    Fetch all Sweden players
    """
    
    print("=== Sweden Player Fetcher ===")
    print("Target: Fetch all Sweden players")
    print()
    
    # Step 1: Get all Sweden players
    print("Step 1: Fetching Sweden players...")
    
    start = 0
    length = 200
    all_players = []
    
    data = fetch_page_with_filters(start, length, 'Sweden')
    total = data.get('recordsFiltered') or data.get('recordsTotal') or 0
    rows = data.get('data') or []
    all_players.extend(rows)
    print(f"Found {len(rows)} Sweden players (total available: {total})")
    
    # Get all pages
    page_count = 0
    max_pages = 10
    
    while len(all_players) < total and page_count < max_pages:
        start += length
        page_count += 1
        time.sleep(0.3)
        data = fetch_page_with_filters(start, length, 'Sweden')
        rows = data.get('data') or []
        all_players.extend(rows)
        print(f"Fetched {len(all_players)} / {total} (page {page_count})")
        
        if len(rows) == 0:
            break
    
    print(f"\nStep 2: Cleaning {len(all_players)} Sweden players...")
    cleaned_players = [clean_common_fields(p) for p in all_players]
    
    # Additional client-side filtering
    sweden_players = []
    for player in cleaned_players:
        nationality = player.get('nationality', '').strip()
        
        if nationality.upper() == 'SWEDEN':
            sweden_players.append(player)
    
    print(f"Final Sweden players: {len(sweden_players)}")
    return sweden_players

def main():
    print("Starting Sweden Complete Fetcher...")
    print("=" * 60)
    
    sweden_players = fetch_sweden_players()
    
    # Save to file
    output_file = "sweden_complete.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(sweden_players, f, ensure_ascii=False, indent=2)
    
    print(f"\n=== RESULTS ===")
    print(f"🇸🇪 Sweden players: {len(sweden_players)}")
    print(f"Results saved to: {output_file}")
    
    # Analysis
    if sweden_players:
        print(f"\n📊 Sweden Players Analysis:")
        
        # By position
        positions = {}
        for player in sweden_players:
            pos = player.get('position', 'Unknown')
            positions[pos] = positions.get(pos, 0) + 1
        
        for pos, count in sorted(positions.items()):
            print(f"  {pos}: {count}")
        
        # By hand
        left_handed = [p for p in sweden_players if p.get('hand') == 'LEFT']
        right_handed = [p for p in sweden_players if p.get('hand') == 'RIGHT']
        print(f"  Left-handed: {len(left_handed)}")
        print(f"  Right-handed: {len(right_handed)}")
        
        # By overall rating
        overalls = [p.get('overall', 0) for p in sweden_players if isinstance(p.get('overall'), int)]
        if overalls:
            avg_overall = sum(overalls) / len(overalls)
            max_overall = max(overalls)
            min_overall = min(overalls)
            print(f"  Average Overall: {avg_overall:.1f}")
            print(f"  Highest Overall: {max_overall}")
            print(f"  Lowest Overall: {min_overall}")
        
        # Show top 10 players
        print(f"\n🏆 Top 10 Sweden players:")
        sorted_players = sorted(sweden_players, 
                              key=lambda x: x.get('overall', 0), 
                              reverse=True)
        
        for i, player in enumerate(sorted_players[:10], 1):
            name = player.get('full_name', 'Unknown')
            team = player.get('team', 'Unknown')
            position = player.get('position', 'Unknown')
            hand = player.get('hand', 'Unknown')
            overall = player.get('overall', 'Unknown')
            salary = player.get('salary', 'Unknown')
            
            print(f"  {i:2d}. {name:<20} ({team}) - {position} {hand} - OVR: {overall} - ${salary:,}")
    
    return sweden_players

if __name__ == '__main__':
    main()