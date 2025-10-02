#!/usr/bin/env python3
"""
Universal Country Fetcher
Fetches all players (skaters + goalies) for any country with complete data including URLs
"""

import requests
import json
import time
from utils_clean import clean_common_fields

# API endpoints
SKATER_URL = "https://nhlhutbuilder.com/php/player_stats.php"
GOALIE_URL = "https://nhlhutbuilder.com/php/goalie_stats.php"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'X-Requested-With': 'XMLHttpRequest',
    'Referer': 'https://nhlhutbuilder.com/player-stats.php',
}

GOALIE_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'X-Requested-With': 'XMLHttpRequest',
    'Referer': 'https://nhlhutbuilder.com/goalie-stats.php',
}

def fetch_skaters_with_timeout(nationality, max_retries=3, timeout=30):
    """Fetch all skaters for a nationality with timeout protection"""
    print(f"🏒 Fetching {nationality} skaters...")
    
    all_players = []
    start = 0
    length = 100
    page = 1
    max_pages = 50  # Safety limit
    
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
        
        # Set nationality filter
        payload['columns[2][search][value]'] = nationality
        payload['columns[2][search][regex]'] = 'false'
        
        try:
            print(f"   🔄 Requesting page {page}...")
            resp = requests.post(SKATER_URL, data=payload, headers=HEADERS, timeout=timeout)
            
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
                
            print(f"   ✅ Found {len(players)} players on page {page}")
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
    
    print(f"🏒 Total skaters found: {len(all_players)}")
    return all_players

def fetch_goalies_with_timeout(nationality, max_retries=3, timeout=30):
    """Fetch all goalies for a nationality with timeout protection"""
    print(f"🥅 Fetching {nationality} goalies...")
    
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
            resp = requests.post(GOALIE_URL, data=payload, headers=GOALIE_HEADERS, timeout=timeout)
            
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
            # Check if this is a goalie (has goalie-specific stats)
            goalie_fields = ['glove_high', 'glove_low', 'stick_high', 'stick_low', 'shot_recovery', 'aggression', 'agility', 'speed', 'positioning', 'breakaway', 'vision', 'poke_check', 'rebound_control', 'passing']
            has_goalie_stats = any(field in player for field in goalie_fields)
            
            if has_goalie_stats:
                # This is a goalie, use goalie-stats.php
                player['url'] = f"https://nhlhutbuilder.com/goalie-stats.php?id={player_id}"
            else:
                # This is a skater, use player-stats.php
                player['url'] = f"https://nhlhutbuilder.com/player-stats.php?id={player_id}"
        else:
            player['url'] = None
    return players

def run_universal_fetcher(nationality):
    """Main function to fetch all players for a nationality"""
    print(f"🌍 UNIVERSAL COUNTRY FETCHER - {nationality.upper()}")
    print("=" * 60)
    
    # Fetch skaters
    print("\n1️⃣ FETCHING SKATERS")
    skaters = fetch_skaters_with_timeout(nationality)
    
    # Fetch goalies  
    print("\n2️⃣ FETCHING GOALIES")
    goalies = fetch_goalies_with_timeout(nationality)
    
    # Process skaters and goalies separately
    print(f"\n🧹 CLEANING SKATERS...")
    cleaned_skaters = []
    for i, player in enumerate(skaters):
        if i % 50 == 0:
            print(f"   Cleaning skater {i+1}/{len(skaters)}")
        cleaned_player = clean_common_fields(player)
        cleaned_skaters.append(cleaned_player)
    
    print(f"\n🧹 CLEANING GOALIES...")
    cleaned_goalies = []
    for i, player in enumerate(goalies):
        if i % 50 == 0:
            print(f"   Cleaning goalie {i+1}/{len(goalies)}")
        cleaned_player = clean_common_fields(player)
        # Ensure position is set to G for goalies
        cleaned_player['position'] = 'G'
        cleaned_goalies.append(cleaned_player)
    
    # Combine all players
    all_players = cleaned_skaters + cleaned_goalies
    
    print(f"\n📊 SUMMARY:")
    print(f"   • Skaters: {len(cleaned_skaters)}")
    print(f"   • Goalies: {len(cleaned_goalies)}")
    print(f"   • Total: {len(all_players)}")
    
    if not all_players:
        print("❌ No players found!")
        return
    
    # Add URLs to players
    print(f"\n🔗 ADDING PLAYER URLs...")
    all_players = add_player_urls(all_players)
    
    # Save to file
    output_file = f'{nationality.lower()}.json'
    print(f"\n💾 SAVING TO {output_file}...")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_players, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Saved {len(all_players)} players to {output_file}")
    
    # Position breakdown
    positions = {}
    for player in all_players:
        pos = player.get('position', 'Unknown')
        positions[pos] = positions.get(pos, 0) + 1
    
    print(f"\n📈 POSITION BREAKDOWN:")
    for pos, count in sorted(positions.items()):
        print(f"   • {pos}: {count} players")
    
    # Final summary
    skaters_final = len([p for p in all_players if p.get('position') != 'G'])
    goalies_final = len([p for p in all_players if p.get('position') == 'G'])
    
    print(f"\n🏒 FINAL BREAKDOWN:")
    print(f"   • Skaters: {skaters_final}")
    print(f"   • Goalies: {goalies_final}")
    print(f"   • Total: {len(all_players)}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python3 universal_country_fetcher.py <country_name>")
        print("Example: python3 universal_country_fetcher.py Finland")
        sys.exit(1)
    
    nationality = sys.argv[1]
    run_universal_fetcher(nationality)