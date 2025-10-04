#!/usr/bin/env python3
"""
Script to analyze master.json and find the top 20 players with highest faceoffs
"""

import json
import sys
from typing import List, Dict, Tuple

def load_master_json(file_path: str) -> Dict:
    """Load the master.json file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: File {file_path} not found")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format - {e}")
        sys.exit(1)

def extract_faceoff_data(data: Dict) -> List[Tuple[str, int, str, str]]:
    """Extract player names and faceoff ratings from the data"""
    players = []
    
    # The data structure has a "players" array
    if 'players' in data and isinstance(data['players'], list):
        for player in data['players']:
            if isinstance(player, dict) and 'faceoffs' in player and 'full_name' in player:
                name = player['full_name']
                faceoffs = player['faceoffs']
                position = player.get('position', 'Unknown')
                team = player.get('team', 'Unknown')
                players.append((name, faceoffs, position, team))
    
    return players

def get_top_20_faceoffs(players: List[Tuple[str, int, str, str]]) -> List[Tuple[str, int, str, str]]:
    """Get the top 20 players with highest faceoffs"""
    # Sort by faceoffs in descending order
    sorted_players = sorted(players, key=lambda x: x[1], reverse=True)
    return sorted_players[:20]

def main():
    file_path = '/workspace/master.json'
    
    print("Loading master.json...")
    data = load_master_json(file_path)
    
    print("Extracting faceoff data...")
    players = extract_faceoff_data(data)
    
    if not players:
        print("No player data found with faceoffs information")
        return
    
    print(f"Found {len(players)} players with faceoff data")
    
    print("\nFinding top 20 players with highest faceoffs...")
    top_20 = get_top_20_faceoffs(players)
    
    print("\n" + "="*80)
    print("TOP 20 PELAAJAA KORKEIMMILLA FACEOFFS-ARVOILLA")
    print("="*80)
    print(f"{'#':<3} {'Nimi':<25} {'Faceoffs':<10} {'Pelipaikka':<8} {'Joukkue':<6}")
    print("-"*80)
    
    for i, (name, faceoffs, position, team) in enumerate(top_20, 1):
        print(f"{i:<3} {name:<25} {faceoffs:<10} {position:<8} {team:<6}")
    
    print("="*80)
    print(f"Yhteensä analysoitu {len(players)} pelaajaa")
    print(f"Korkein faceoffs-arvo: {top_20[0][1]} ({top_20[0][0]})")

if __name__ == "__main__":
    main()