#!/usr/bin/env python3
"""
Advanced NHL HUT Test Scraper
Tests advanced filtering capabilities including team, position, hand, and X-Factor abilities
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
    """
    Fetch page with advanced filtering capabilities
    
    filters dict can contain:
    - team: Team name (e.g., "San Jose Sharks", "SJS")
    - position: Position (e.g., "RW", "LW", "C", "D", "G")
    - hand: Handedness (e.g., "LEFT", "RIGHT")
    - nationality: Nationality (e.g., "Canada", "USA")
    - league: League (e.g., "NHL", "AHL")
    - x_factor: X-Factor ability name (e.g., "Quick Release")
    """
    
    payload = {
        'draw': 1,
        'start': start,
        'length': length,
        'search[value]': '',
        'search[regex]': 'false',
    }
    
    # Define all available columns based on the existing scraper
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
    
    # For X-Factor abilities, we might need to use global search or a different approach
    # since abilities might not be in the main columns
    if 'x_factor' in filters:
        payload['search[value]'] = filters['x_factor']
        payload['search[regex]'] = 'false'
    
    print(f"Fetching with filters: {filters}")
    print(f"Payload search values: nationality={payload.get('columns[2][search][value]', 'None')}, "
          f"team={payload.get('columns[4][search][value]', 'None')}, "
          f"position={payload.get('columns[7][search][value]', 'None')}, "
          f"hand={payload.get('columns[8][search][value]', 'None')}")
    
    resp = requests.post(DT_URL, data=payload, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    return resp.json()

def run_advanced_test():
    """
    Test the advanced scraper with San Jose Sharks RW players who are left-handed with Quick Release
    """
    
    # Define our test filters
    filters = {
        'team': 'SJS',  # Use correct team abbreviation
        'position': 'RW',
        'hand': 'LEFT',
        'x_factor': 'Quick Release'
    }
    
    start = 0
    length = 200
    all_rows = []
    
    print("=== Advanced NHL HUT Test Scraper ===")
    print("Testing filters:")
    for key, value in filters.items():
        print(f"  {key}: {value}")
    print()
    
    try:
        # First attempt with full team name
        print("Attempt 1: Using full team name 'San Jose Sharks'")
        data = fetch_page_with_filters(start, length, filters)
        total = data.get('recordsFiltered') or data.get('recordsTotal') or 0
        rows = data.get('data') or []
        print(f"Found {len(rows)} players (total available: {total})")
        
        if len(rows) == 0:
            # Try with abbreviated team name
            print("\nAttempt 2: Trying abbreviated team name 'SJS'")
            filters['team'] = 'SJS'
            data = fetch_page_with_filters(start, length, filters)
            total = data.get('recordsFiltered') or data.get('recordsTotal') or 0
            rows = data.get('data') or []
            print(f"Found {len(rows)} players (total available: {total})")
        
        if len(rows) == 0:
            # Try to find San Jose players by searching for "San Jose" in team names
            print("\nAttempt 2.5: Searching for San Jose players...")
            # First get some data to see what team names look like
            test_data = fetch_page_with_filters(0, 50, {"position": "RW"})
            test_rows = test_data.get('data') or []
            san_jose_players = []
            for row in test_rows:
                team = row.get('team', '')
                if 'san jose' in team.lower() or 'sjs' in team.lower():
                    san_jose_players.append(row)
            print(f"Found {len(san_jose_players)} San Jose players in sample data")
            if len(san_jose_players) > 0:
                print("Sample San Jose team names:")
                for player in san_jose_players[:3]:
                    print(f"  - {player.get('team', 'Unknown')}")
                # Use the first team name we found
                if san_jose_players:
                    correct_team_name = san_jose_players[0].get('team', '')
                    print(f"Using team name: '{correct_team_name}'")
                    filters['team'] = correct_team_name
                    data = fetch_page_with_filters(start, length, filters)
                    total = data.get('recordsFiltered') or data.get('recordsTotal') or 0
                    rows = data.get('data') or []
                    print(f"Found {len(rows)} players with correct team name")
        
        if len(rows) == 0:
            # Try without team filter to see if position/hand filters work
            print("\nAttempt 3: Trying without team filter (position + hand only)")
            filters_no_team = {k: v for k, v in filters.items() if k != 'team'}
            data = fetch_page_with_filters(start, length, filters_no_team)
            total = data.get('recordsFiltered') or data.get('recordsTotal') or 0
            rows = data.get('data') or []
            print(f"Found {len(rows)} players (total available: {total})")
        
        if len(rows) == 0:
            # Try with just position filter
            print("\nAttempt 4: Trying with just position filter")
            filters_position_only = {'position': filters['position']}
            data = fetch_page_with_filters(start, length, filters_position_only)
            total = data.get('recordsFiltered') or data.get('recordsTotal') or 0
            rows = data.get('data') or []
            print(f"Found {len(rows)} players (total available: {total})")
        
        # If we found some results, get all pages (but limit to prevent infinite loops)
        if len(rows) > 0:
            all_rows.extend(rows)
            print(f"\nFetching all pages (max 5 pages to prevent infinite loops)...")
            
            page_count = 0
            max_pages = 5  # Limit to prevent infinite loops
            
            while len(all_rows) < total and page_count < max_pages:
                start += length
                page_count += 1
                time.sleep(0.3)
                current_filters = filters if len(rows) > 0 else filters_position_only
                data = fetch_page_with_filters(start, length, current_filters)
                rows = data.get('data') or []
                all_rows.extend(rows)
                print(f"Fetched {len(all_rows)} / {total} (page {page_count})")
                
                if len(rows) == 0:  # No more data
                    break
        
        # Clean the data
        print(f"\nCleaning {len(all_rows)} records...")
        cleaned = [clean_common_fields(r) for r in all_rows]
        
        # Apply additional client-side filtering for San Jose Sharks
        if 'team' in filters:
            team_filter = filters['team']
            if team_filter == 'San Jose Sharks':
                # Try different variations of San Jose Sharks
                team_variations = ['San Jose Sharks', 'SJS', 'San Jose', 'Sharks']
                filtered_cleaned = []
                for row in cleaned:
                    team = row.get('team', '').strip()
                    if any(variation.lower() in team.lower() for variation in team_variations):
                        filtered_cleaned.append(row)
                cleaned = filtered_cleaned
                print(f"After team filtering: {len(cleaned)} players")
        
        # Apply position filter
        if 'position' in filters:
            position_filter = filters['position']
            cleaned = [r for r in cleaned if (r.get('position') or '').strip() == position_filter]
            print(f"After position filtering: {len(cleaned)} players")
        
        # Apply hand filter
        if 'hand' in filters:
            hand_filter = filters['hand']
            cleaned = [r for r in cleaned if (r.get('hand') or '').strip() == hand_filter]
            print(f"After hand filtering: {len(cleaned)} players")
        
        # Save results
        output_file = "test_san_jose_rw_left_quick_release.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(cleaned, f, ensure_ascii=False, indent=2)
        
        print(f"\n=== RESULTS ===")
        print(f"Total players found: {len(cleaned)}")
        print(f"Results saved to: {output_file}")
        
        if len(cleaned) > 0:
            print(f"\nSample players:")
            for i, player in enumerate(cleaned[:3]):
                name = player.get('full_name', 'Unknown')
                team = player.get('team', 'Unknown')
                position = player.get('position', 'Unknown')
                hand = player.get('hand', 'Unknown')
                overall = player.get('overall', 'Unknown')
                print(f"  {i+1}. {name} ({team}) - {position} {hand} - OVR: {overall}")
        
        return cleaned
        
    except Exception as e:
        print(f"Error during scraping: {e}")
        return []

def analyze_filter_capabilities():
    """
    Analyze what filters are available and how they work
    """
    print("=== Filter Capability Analysis ===")
    
    # Test different filter combinations
    test_cases = [
        {"description": "All RW players", "filters": {"position": "RW"}},
        {"description": "All left-handed players", "filters": {"hand": "LEFT"}},
        {"description": "All San Jose players", "filters": {"team": "San Jose Sharks"}},
        {"description": "All San Jose RW players", "filters": {"team": "San Jose Sharks", "position": "RW"}},
        {"description": "All left-handed RW players", "filters": {"position": "RW", "hand": "LEFT"}},
    ]
    
    for test_case in test_cases:
        print(f"\nTesting: {test_case['description']}")
        try:
            data = fetch_page_with_filters(0, 50, test_case['filters'])
            total = data.get('recordsFiltered') or data.get('recordsTotal') or 0
            rows = data.get('data') or []
            print(f"  Found {len(rows)} players (total: {total})")
            
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
    print("Starting Advanced NHL HUT Test Scraper...")
    print("=" * 50)
    
    # First analyze filter capabilities
    analyze_filter_capabilities()
    
    print("\n" + "=" * 50)
    
    # Run the main test
    results = run_advanced_test()
    
    print(f"\nTest completed. Found {len(results)} matching players.")

if __name__ == '__main__':
    main()