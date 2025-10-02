#!/usr/bin/env python3
"""
USA LW Counter - Counts all USA players with LW position
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
    
    resp = requests.post(DT_URL, data=payload, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    return resp.json()

def count_usa_lw_players():
    """
    Count all USA LW players
    """
    
    print("=== USA LW Player Counter ===")
    print("Target: Count all USA players with LW position")
    print()
    
    # Step 1: Get all USA LW players
    print("Step 1: Fetching USA LW players...")
    
    filters = {
        'nationality': 'USA',
        'position': 'LW'
    }
    
    start = 0
    length = 200
    all_players = []
    
    data = fetch_page_with_filters(start, length, filters)
    total = data.get('recordsFiltered') or data.get('recordsTotal') or 0
    rows = data.get('data') or []
    all_players.extend(rows)
    print(f"Found {len(rows)} USA LW players (total available: {total})")
    
    # Get all pages
    page_count = 0
    max_pages = 10  # Allow more pages for complete count
    
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
    
    print(f"\nStep 2: Cleaning {len(all_players)} USA LW players...")
    cleaned_players = [clean_common_fields(p) for p in all_players]
    
    # Additional client-side filtering to ensure accuracy
    usa_lw_players = []
    for player in cleaned_players:
        nationality = player.get('nationality', '').strip()
        position = player.get('position', '').strip()
        
        if (nationality.upper() == 'USA' and 
            position == 'LW'):
            usa_lw_players.append(player)
    
    # Save results
    output_file = "usa_lw_players.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(usa_lw_players, f, ensure_ascii=False, indent=2)
    
    print(f"\n=== FINAL RESULTS ===")
    print(f"🇺🇸 USA LW players found: {len(usa_lw_players)}")
    print(f"Results saved to: {output_file}")
    
    if len(usa_lw_players) > 0:
        print(f"\n📊 USA LW Player Analysis:")
        
        # Analyze by hand
        left_handed = [p for p in usa_lw_players if p.get('hand') == 'LEFT']
        right_handed = [p for p in usa_lw_players if p.get('hand') == 'RIGHT']
        
        print(f"  Left-handed: {len(left_handed)}")
        print(f"  Right-handed: {len(right_handed)}")
        
        # Analyze by overall rating
        overalls = [p.get('overall', 0) for p in usa_lw_players if isinstance(p.get('overall'), int)]
        if overalls:
            avg_overall = sum(overalls) / len(overalls)
            max_overall = max(overalls)
            min_overall = min(overalls)
            print(f"  Average Overall: {avg_overall:.1f}")
            print(f"  Highest Overall: {max_overall}")
            print(f"  Lowest Overall: {min_overall}")
        
        # Show top 10 players
        print(f"\n🏆 Top 10 USA LW players:")
        sorted_players = sorted(usa_lw_players, 
                              key=lambda x: x.get('overall', 0), 
                              reverse=True)
        
        for i, player in enumerate(sorted_players[:10], 1):
            name = player.get('full_name', 'Unknown')
            team = player.get('team', 'Unknown')
            hand = player.get('hand', 'Unknown')
            overall = player.get('overall', 'Unknown')
            salary = player.get('salary', 'Unknown')
            
            print(f"  {i:2d}. {name:<20} ({team}) - {hand} - OVR: {overall} - ${salary:,}")
        
        if len(usa_lw_players) > 10:
            print(f"  ... and {len(usa_lw_players) - 10} more players")
    
    return len(usa_lw_players)

def main():
    print("Starting USA LW Player Counter...")
    print("=" * 50)
    
    count = count_usa_lw_players()
    
    print(f"\n🎯 ULTIMATE RESULT:")
    print(f"Total USA LW players: {count}")
    print(f"Counter completed successfully!")

if __name__ == '__main__':
    main()