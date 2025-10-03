#!/usr/bin/env python3
"""
Austria Complete Fetcher
Fetches all Austria players (skaters + goalies) with complete data
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

def fetch_skaters_with_timeout(nationality, max_retries=3, timeout=30):
    """Fetch all skaters for a nationality with timeout protection"""
    print(f"🏒 Fetching Austria skaters...")
    
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
    print(f"🥅 Fetching Austria goalies...")
    
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

def run_austria_fetcher():
    """Main function to fetch all Austria players"""
    print("🇦🇹 AUSTRIA COMPLETE FETCHER")
    print("=" * 50)
    
    # Fetch skaters
    print("\n1️⃣ FETCHING SKATERS")
    skaters = fetch_skaters_with_timeout('Austria')
    
    # Fetch goalies  
    print("\n2️⃣ FETCHING GOALIES")
    goalies = fetch_goalies_with_timeout('Austria')
    
    # Combine all players
    all_players = skaters + goalies
    
    print(f"\n📊 SUMMARY:")
    print(f"   • Skaters: {len(skaters)}")
    print(f"   • Goalies: {len(goalies)}")
    print(f"   • Total: {len(all_players)}")
    
    if not all_players:
        print("❌ No players found!")
        return
    
    # Clean the data
    print(f"\n🧹 CLEANING DATA...")
    cleaned_players = []
    for i, player in enumerate(all_players):
        if i % 50 == 0:
            print(f"   Cleaning player {i+1}/{len(all_players)}")
        cleaned_player = clean_common_fields(player)
        cleaned_players.append(cleaned_player)
    
    # Save to file
    output_file = 'austria.json'
    print(f"\n💾 SAVING TO {output_file}...")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(cleaned_players, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Saved {len(cleaned_players)} players to {output_file}")
    
    # Position breakdown
    positions = {}
    for player in cleaned_players:
        pos = player.get('position', 'Unknown')
        positions[pos] = positions.get(pos, 0) + 1
    
    print(f"\n📈 POSITION BREAKDOWN:")
    for pos, count in sorted(positions.items()):
        print(f"   • {pos}: {count} players")

if __name__ == "__main__":
    run_austria_fetcher()