#!/usr/bin/env python3
"""
USA Goalies Fetcher - Fetches USA G players using goalie_stats.php API
"""

import json
import time
import requests
from utils_clean import clean_common_fields

DT_URL = "https://nhlhutbuilder.com/php/goalie_stats.php"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'X-Requested-With': 'XMLHttpRequest',
    'Referer': 'https://nhlhutbuilder.com/goalie-stats.php',
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
        'card_art','card','nationality','league','team','division','salary','hand','weight','height','full_name','overall','aOVR',
        'glove_high','glove_low','stick_high','stick_low','shot_recovery','aggression','agility','speed','positioning','breakaway',
        'vision','poke_check','rebound_control','passing','date_added','date_updated'
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

def fetch_usa_goalies():
    """
    Fetch all USA goalies
    """
    
    print("=== USA Goalies Fetcher ===")
    print("Target: Fetch all USA goalies using goalie_stats.php API")
    print()
    
    # Step 1: Get all USA goalies
    print("Step 1: Fetching USA goalies...")
    
    start = 0
    length = 200
    all_players = []
    
    data = fetch_page_with_filters(start, length, 'USA')
    total = data.get('recordsFiltered') or data.get('recordsTotal') or 0
    rows = data.get('data') or []
    all_players.extend(rows)
    print(f"Found {len(rows)} USA goalies (total available: {total})")
    
    # Get all pages
    page_count = 0
    max_pages = 10
    
    while len(all_players) < total and page_count < max_pages:
        start += length
        page_count += 1
        time.sleep(0.3)
        data = fetch_page_with_filters(start, length, 'USA')
        rows = data.get('data') or []
        all_players.extend(rows)
        print(f"Fetched {len(all_players)} / {total} (page {page_count})")
        
        if len(rows) == 0:
            break
    
    print(f"\nStep 2: Cleaning {len(all_players)} USA goalies...")
    cleaned_players = [clean_common_fields(p) for p in all_players]
    
    # Add position field for goalies
    for player in cleaned_players:
        player['position'] = 'G'
    
    # Additional client-side filtering
    usa_goalies = []
    for player in cleaned_players:
        nationality = player.get('nationality', '').strip()
        
        if nationality.upper() == 'USA':
            usa_goalies.append(player)
    
    print(f"Final USA goalies: {len(usa_goalies)}")
    return usa_goalies

def merge_usa_players_with_goalies():
    """
    Merge USA goalies with existing USA players
    """
    
    print("\n=== Merging USA Players with Goalies ===")
    
    # Load existing USA players (LW + RW + LD + RD + C)
    try:
        with open('usa.json', 'r') as f:
            existing_players = json.load(f)
        print(f"Loaded {len(existing_players)} existing USA players (LW + RW + LD + RD + C)")
    except FileNotFoundError:
        print("No existing usa.json found")
        existing_players = []
    
    # Fetch USA goalies
    usa_goalies = fetch_usa_goalies()
    
    # Merge all USA players
    all_usa_players = existing_players + usa_goalies
    
    # Save merged file
    output_file = "usa.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_usa_players, f, ensure_ascii=False, indent=2)
    
    print(f"\n=== MERGED RESULTS ===")
    print(f"🇺🇸 Total USA players: {len(all_usa_players)}")
    print(f"  - LW players: {len([p for p in all_usa_players if p.get('position') == 'LW'])}")
    print(f"  - RW players: {len([p for p in all_usa_players if p.get('position') == 'RW'])}")
    print(f"  - LD players: {len([p for p in all_usa_players if p.get('position') == 'LD'])}")
    print(f"  - RD players: {len([p for p in all_usa_players if p.get('position') == 'RD'])}")
    print(f"  - C players: {len([p for p in all_usa_players if p.get('position') == 'C'])}")
    print(f"  - G players: {len(usa_goalies)}")
    print(f"Results saved to: {output_file}")
    
    # Analysis
    if all_usa_players:
        print(f"\n📊 USA Players Analysis:")
        
        # By position
        lw_count = len([p for p in all_usa_players if p.get('position') == 'LW'])
        rw_count = len([p for p in all_usa_players if p.get('position') == 'RW'])
        ld_count = len([p for p in all_usa_players if p.get('position') == 'LD'])
        rd_count = len([p for p in all_usa_players if p.get('position') == 'RD'])
        c_count = len([p for p in all_usa_players if p.get('position') == 'C'])
        g_count = len([p for p in all_usa_players if p.get('position') == 'G'])
        print(f"  LW players: {lw_count}")
        print(f"  RW players: {rw_count}")
        print(f"  LD players: {ld_count}")
        print(f"  RD players: {rd_count}")
        print(f"  C players: {c_count}")
        print(f"  G players: {g_count}")
        
        # By hand
        left_handed = [p for p in all_usa_players if p.get('hand') == 'LEFT']
        right_handed = [p for p in all_usa_players if p.get('hand') == 'RIGHT']
        print(f"  Left-handed: {len(left_handed)}")
        print(f"  Right-handed: {len(right_handed)}")
        
        # By overall rating
        overalls = [p.get('overall', 0) for p in all_usa_players if isinstance(p.get('overall'), int)]
        if overalls:
            avg_overall = sum(overalls) / len(overalls)
            max_overall = max(overalls)
            min_overall = min(overalls)
            print(f"  Average Overall: {avg_overall:.1f}")
            print(f"  Highest Overall: {max_overall}")
            print(f"  Lowest Overall: {min_overall}")
        
        # Show top 10 players
        print(f"\n🏆 Top 10 USA players:")
        sorted_players = sorted(all_usa_players, 
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
    
    return all_usa_players

def main():
    print("Starting USA Goalies Fetcher and Merger...")
    print("=" * 60)
    
    all_players = merge_usa_players_with_goalies()
    
    print(f"\n🎯 FINAL RESULT:")
    print(f"Total USA players (LW + RW + LD + RD + C + G): {len(all_players)}")
    print(f"Data saved to usa.json")
    print(f"Ready for GitHub commit!")

if __name__ == '__main__':
    main()