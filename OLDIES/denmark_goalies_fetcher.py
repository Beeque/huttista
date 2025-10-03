#!/usr/bin/env python3
"""
Denmark Goalies Fetcher
Fetches Denmark goalies separately and merges with existing data
"""

import requests
import json
import time
from utils_clean import clean_common_fields

# API endpoint
GOALIE_URL = "https://nhlhutbuilder.com/php/goalie_stats.php"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'X-Requested-With': 'XMLHttpRequest',
    'Referer': 'https://nhlhutbuilder.com/goalie-stats.php',
}

def fetch_goalies_with_timeout(nationality, max_retries=3, timeout=30):
    """Fetch all goalies for a nationality with timeout protection"""
    print(f"🥅 Fetching Denmark goalies...")
    
    all_players = []
    start = 0
    length = 100
    page = 1
    max_pages = 20  # Safety limit
    
    while page <= max_pages:
        print(f"   📄 Page {page} (start={start})")
        
        payload = {
            'draw': page,
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
        
        # Set nationality filter
        payload['columns[2][search][value]'] = nationality
        payload['columns[2][search][regex]'] = 'false'
        
        try:
            print(f"   🔄 Requesting page {page}...")
            resp = requests.post(GOALIE_URL, data=payload, headers=HEADERS, timeout=timeout)
            
            if resp.status_code != 200:
                print(f"   ❌ HTTP {resp.status_code}")
                break
                
            data = resp.json()
            
            if 'data' not in data:
                print(f"   ❌ No 'data' field in response")
                break
                
            players = data['data']
            if not players:
                print(f"   ✅ No more players found")
                break
                
            print(f"   ✅ Found {len(players)} goalies on page {page}")
            all_players.extend(players)
            
            # Check if we got fewer players than requested (last page)
            if len(players) < length:
                print(f"   ✅ Last page reached (got {len(players)} < {length})")
                break
                
            start += length
            page += 1
            
            # Small delay to be nice to the server
            time.sleep(0.5)
            
        except requests.exceptions.Timeout:
            print(f"   ⏰ Timeout on page {page}, retrying...")
            time.sleep(2)
            continue
        except Exception as e:
            print(f"   ❌ Error on page {page}: {e}")
            break
    
    print(f"🥅 Total goalies found: {len(all_players)}")
    return all_players

def add_player_urls(players):
    """Add URL field to each player"""
    for player in players:
        player_id = player.get('player_id')
        if player_id:
            player['url'] = f"https://nhlhutbuilder.com/player-stats.php?id={player_id}"
        else:
            player['url'] = None
    return players

def run_denmark_goalies_fetcher():
    """Main function to fetch Denmark goalies and merge with existing data"""
    print("🇩🇰 DENMARK GOALIES FETCHER")
    print("=" * 50)
    
    # Load existing skaters
    try:
        with open('denmark.json', 'r', encoding='utf-8') as f:
            existing_players = json.load(f)
    except FileNotFoundError:
        print("❌ denmark.json not found! Run denmark_complete_fetcher.py first.")
        return
    
    print(f"📊 Loaded {len(existing_players)} existing players")
    
    # Fetch goalies
    print("\n🥅 FETCHING GOALIES")
    goalies = fetch_goalies_with_timeout('Denmark')
    
    if not goalies:
        print("❌ No goalies found!")
        return
    
    # Clean the goalie data
    print(f"\n🧹 CLEANING GOALIE DATA...")
    cleaned_goalies = []
    for i, player in enumerate(goalies):
        if i % 50 == 0:
            print(f"   Cleaning goalie {i+1}/{len(goalies)}")
        cleaned_player = clean_common_fields(player)
        # Ensure position is set to G for goalies
        cleaned_player['position'] = 'G'
        cleaned_goalies.append(cleaned_player)
    
    # Add URLs to goalies
    print(f"\n🔗 ADDING GOALIE URLs...")
    cleaned_goalies = add_player_urls(cleaned_goalies)
    
    # Merge with existing players
    print(f"\n🔄 MERGING DATA...")
    all_players = existing_players + cleaned_goalies
    
    # Save merged data
    output_file = 'denmark.json'
    print(f"\n💾 SAVING MERGED DATA TO {output_file}...")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_players, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Saved {len(all_players)} players to {output_file}")
    
    # Final summary
    skaters = len([p for p in all_players if p.get('position') != 'G'])
    goalies_count = len([p for p in all_players if p.get('position') == 'G'])
    
    print(f"\n📊 FINAL SUMMARY:")
    print(f"   • Skaters: {skaters}")
    print(f"   • Goalies: {goalies_count}")
    print(f"   • Total: {len(all_players)}")

if __name__ == "__main__":
    run_denmark_goalies_fetcher()