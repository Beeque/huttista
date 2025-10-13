#!/usr/bin/env python3
"""
Analyze faceoffs stats from master.json players
Fetches detailed faceoffs data from NHL HUT Builder
"""

import json
import requests
from bs4 import BeautifulSoup
import time
from typing import List, Dict, Optional
import re

def load_master_data():
    """Load master.json data"""
    try:
        with open('master.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading master.json: {e}")
        return None

def fetch_player_faceoffs(player_id: int, is_goalie: bool = False) -> Optional[int]:
    """Fetch faceoffs stat for a specific player"""
    try:
        if is_goalie:
            url = f"https://nhlhutbuilder.com/goalie-stats.php?id={player_id}"
        else:
            url = f"https://nhlhutbuilder.com/player-stats.php?id={player_id}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for faceoffs in specific element
        faceoffs_elem = soup.find('td', id='faceoffs')
        if faceoffs_elem:
            try:
                return int(faceoffs_elem.get_text(strip=True))
            except:
                pass
        
        # Also look in tables as backup
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 2:
                    key = cells[0].get_text(strip=True).lower()
                    value = cells[1].get_text(strip=True)
                    
                    if 'face off' in key or 'faceoffs' in key:
                        try:
                            return int(value)
                        except:
                            pass
        
        return None
        
    except Exception as e:
        print(f"Error fetching faceoffs for player {player_id}: {e}")
        return None

def analyze_faceoffs():
    """Analyze faceoffs for all skaters in master.json"""
    print("🏒 NHL Faceoffs Analyzer")
    print("=" * 50)
    
    # Load master data
    master_data = load_master_data()
    if not master_data:
        return
    
    players = master_data.get('players', [])
    print(f"📊 Loaded {len(players)} players from master.json")
    
    # Filter skaters only
    skaters = [p for p in players if not p.get('is_goalie', False)]
    print(f"🏒 Found {len(skaters)} skaters")
    
    # Fetch faceoffs data for each skater
    faceoffs_data = []
    
    print("\n🔄 Fetching faceoffs data...")
    for i, player in enumerate(skaters):
        player_id = player.get('player_id')
        if not player_id:
            continue
            
        print(f"   {i+1:3d}/{len(skaters)} - {player.get('name', 'Unknown')} (ID: {player_id})")
        
        faceoffs = fetch_player_faceoffs(player_id, is_goalie=False)
        if faceoffs is not None:
            player_data = {
                'name': player.get('name', 'Unknown'),
                'player_id': player_id,
                'position': player.get('position', 'N/A'),
                'overall': player.get('overall', 0),
                'nationality': player.get('nationality', 'N/A'),
                'faceoffs': faceoffs
            }
            faceoffs_data.append(player_data)
            print(f"      ✅ Faceoffs: {faceoffs}")
        else:
            print(f"      ❌ No faceoffs data")
        
        # Small delay to be nice to the server
        time.sleep(0.3)
    
    # Sort by faceoffs (highest first)
    faceoffs_data.sort(key=lambda x: x['faceoffs'], reverse=True)
    
    # Display top 20
    print(f"\n🏆 TOP 20 KENTTÄPELAAJAA - PARAS FACEOFFS:")
    print("=" * 80)
    
    for i, player in enumerate(faceoffs_data[:20], 1):
        print(f"{i:2d}. {player['name']:<25} | "
              f"Faceoffs: {player['faceoffs']:3d} | "
              f"Overall: {player['overall']:2d} | "
              f"Position: {player['position']:2s} | "
              f"Nationality: {player['nationality']}")
    
    print("=" * 80)
    print(f"📊 Analyzed {len(faceoffs_data)} players with faceoffs data")
    
    # Save results
    with open('faceoffs_analysis.json', 'w', encoding='utf-8') as f:
        json.dump(faceoffs_data, f, indent=2, ensure_ascii=False)
    print(f"💾 Results saved to faceoffs_analysis.json")

if __name__ == "__main__":
    analyze_faceoffs()