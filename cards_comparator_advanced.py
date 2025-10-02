#!/usr/bin/env python3
"""
Advanced Cards Comparator - Compares more cards from default view with master.json
"""

import json
import time
import requests
from collections import defaultdict
from utils_clean import clean_common_fields

# API endpoint
DT_URL = "https://nhlhutbuilder.com/php/player_stats.php"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'X-Requested-With': 'XMLHttpRequest',
    'Referer': 'https://nhlhutbuilder.com/cards.php',
}

def fetch_more_cards(count=100):
    """Fetch more cards from the default view"""
    
    print(f"🔍 Fetching {count} cards from default view...")
    
    payload = {
        'draw': 1,
        'start': 0,
        'length': count,
        'search[value]': '',
        'search[regex]': 'false',
    }
    
    # Define all columns
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
    
    # Default sorting: by date_added (most recent first)
    payload['order[0][column]'] = '35'  # date_added column index
    payload['order[0][dir]'] = 'desc'
    
    try:
        resp = requests.post(DT_URL, data=payload, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        
        data = resp.json()
        cards = data.get('data', [])
        
        print(f"✅ Fetched {len(cards)} cards")
        
        # Clean cards
        cleaned_cards = [clean_common_fields(card) for card in cards]
        
        return cleaned_cards
        
    except Exception as e:
        print(f"❌ Error fetching cards: {e}")
        return []

def load_master_data():
    """Load the master.json data"""
    print("📂 Loading master.json data...")
    
    try:
        with open('master.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        players = data.get('players', [])
        print(f"✅ Loaded {len(players)} players from master.json")
        
        # Create lookup dictionaries for efficient searching
        players_by_id = {p.get('player_id'): p for p in players if p.get('player_id')}
        players_by_card_id = {}
        
        # Create card-based lookup (card type + player name + team)
        for player in players:
            card_type = player.get('card', '')
            name = player.get('full_name', '').upper()
            team = player.get('team', '')
            card_key = f"{card_type}|{name}|{team}"
            players_by_card_id[card_key] = player
        
        return {
            'players': players,
            'by_id': players_by_id,
            'by_card_id': players_by_card_id
        }
        
    except Exception as e:
        print(f"❌ Error loading master.json: {e}")
        return None

def find_matching_player(card, master_data):
    """Find matching player in master data using multiple strategies"""
    
    # Strategy 1: Exact player_id match
    player_id = card.get('player_id')
    if player_id and player_id in master_data['by_id']:
        return master_data['by_id'][player_id], 'player_id'
    
    # Strategy 2: Card-based match (card type + name + team)
    card_type = card.get('card', '')
    name = card.get('full_name', '').upper()
    team = card.get('team', '')
    card_key = f"{card_type}|{name}|{team}"
    
    if card_key in master_data['by_card_id']:
        return master_data['by_card_id'][card_key], 'card_match'
    
    return None, None

def compare_more_cards(card_count=100):
    """Compare more cards from default view with master.json"""
    
    print("🏒 NHL HUT Builder - Advanced Cards Comparator")
    print("=" * 60)
    print(f"Comparing {card_count} cards from default view with master.json database")
    print("=" * 60)
    
    # Load data
    master_data = load_master_data()
    if not master_data:
        return
    
    # Fetch more cards
    cards = fetch_more_cards(card_count)
    if not cards:
        return
    
    print(f"\n🔍 COMPARISON ANALYSIS:")
    print(f"=" * 60)
    
    results = {
        'found': [],
        'missing': [],
        'matches_by_type': defaultdict(int),
        'missing_by_card_type': defaultdict(int),
        'missing_by_team': defaultdict(int),
        'missing_by_nationality': defaultdict(int)
    }
    
    print(f"\n🎯 Checking {len(cards)} cards from default view:")
    print(f"-" * 60)
    
    for i, card in enumerate(cards, 1):
        name = card.get('full_name', 'Unknown')
        card_type = card.get('card', 'Unknown')
        team = card.get('team', 'Unknown')
        overall = card.get('overall', '?')
        nationality = card.get('nationality', 'Unknown')
        
        # Show progress every 20 cards
        if i % 20 == 0 or i <= 10:
            print(f"{i:3d}. {name:25s} | {card_type:4s} | {team:6s} | OVR:{overall:3d} | {nationality}")
        
        # Find matching player
        match, match_type = find_matching_player(card, master_data)
        
        if match:
            results['found'].append({
                'card': card,
                'match': match,
                'match_type': match_type
            })
            results['matches_by_type'][match_type] += 1
        else:
            results['missing'].append(card)
            results['missing_by_card_type'][card_type] += 1
            results['missing_by_team'][team] += 1
            results['missing_by_nationality'][nationality] += 1
    
    # Summary
    print(f"\n📊 COMPARISON SUMMARY:")
    print(f"=" * 60)
    print(f"Total cards checked: {len(cards)}")
    print(f"Found in master.json: {len(results['found'])}")
    print(f"Missing from master.json: {len(results['missing'])}")
    
    print(f"\n🔍 Match types:")
    for match_type, count in results['matches_by_type'].items():
        print(f"  {match_type}: {count} matches")
    
    # Show missing cards analysis
    if results['missing']:
        print(f"\n❌ MISSING CARDS ANALYSIS ({len(results['missing'])} cards not in master.json):")
        print(f"-" * 60)
        
        print(f"\n📊 Missing by Card Type:")
        for card_type, count in sorted(results['missing_by_card_type'].items(), key=lambda x: x[1], reverse=True):
            print(f"  {card_type:10s}: {count:3d} cards")
        
        print(f"\n🏒 Missing by Team:")
        for team, count in sorted(results['missing_by_team'].items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {team:10s}: {count:3d} cards")
        
        print(f"\n🌍 Missing by Nationality:")
        for nationality, count in sorted(results['missing_by_nationality'].items(), key=lambda x: x[1], reverse=True):
            print(f"  {nationality:15s}: {count:3d} cards")
        
        # Show first 20 missing cards
        print(f"\n❌ First 20 missing cards:")
        for i, card in enumerate(results['missing'][:20], 1):
            name = card.get('full_name', 'Unknown')
            card_type = card.get('card', 'Unknown')
            team = card.get('team', 'Unknown')
            overall = card.get('overall', '?')
            nationality = card.get('nationality', 'Unknown')
            position = card.get('position', '?')
            player_id = card.get('player_id', '?')
            
            print(f"  {i:2d}. {name:25s} | {card_type:4s} | {team:6s} | OVR:{overall:3d} | {nationality:10s} | {position:3s} | ID:{player_id}")
        
        # Ask if user wants to add missing cards
        print(f"\n🤔 SUGGESTION:")
        print(f"Found {len(results['missing'])} cards that are not in master.json.")
        print(f"These appear to be newer cards that were added recently.")
        
        response = input(f"\n❓ Would you like to add these missing cards to master.json? (y/n): ").lower().strip()
        
        if response in ['y', 'yes', 'joo', 'kyllä']:
            add_missing_cards(results['missing'], master_data)
        else:
            print("❌ Skipping addition of missing cards.")
    
    else:
        print(f"\n✅ All {len(cards)} cards from default view are already in master.json!")
    
    # Save comparison results
    output_file = f"cards_comparison_advanced_{card_count}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'comparison_date': time.strftime('%Y-%m-%d %H:%M:%S'),
            'total_cards_checked': len(cards),
            'found_in_master': len(results['found']),
            'missing_from_master': len(results['missing']),
            'matches_by_type': dict(results['matches_by_type']),
            'missing_by_card_type': dict(results['missing_by_card_type']),
            'missing_by_team': dict(results['missing_by_team']),
            'missing_by_nationality': dict(results['missing_by_nationality']),
            'missing_cards': results['missing'][:50],  # Save first 50 missing cards
            'found_cards': [
                {
                    'card': card['card'],
                    'match_type': card['match_type']
                } for card in results['found'][:20]  # Save first 20 found cards
            ]
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Advanced comparison results saved to: {output_file}")
    
    return results

def add_missing_cards(missing_cards, master_data):
    """Add missing cards to master.json"""
    
    print(f"\n➕ ADDING MISSING CARDS TO MASTER.JSON:")
    print(f"=" * 60)
    
    # Load current master.json
    try:
        with open('master.json', 'r', encoding='utf-8') as f:
            master_json = json.load(f)
    except Exception as e:
        print(f"❌ Error loading master.json: {e}")
        return
    
    # Add URL field to missing cards
    for card in missing_cards:
        player_id = card.get('player_id')
        if player_id:
            card['url'] = f"https://nhlhutbuilder.com/player-stats.php?id={player_id}"
        
        # Add empty xfactors array if not present
        if 'xfactors' not in card:
            card['xfactors'] = []
    
    # Add missing cards to master data
    current_count = len(master_json.get('players', []))
    master_json['players'].extend(missing_cards)
    new_count = len(master_json['players'])
    
    # Update metadata
    if 'metadata' in master_json:
        master_json['metadata']['total_players'] = new_count
        master_json['metadata']['last_updated'] = time.strftime('%Y-%m-%d %H:%M:%S')
        master_json['metadata']['last_added'] = len(missing_cards)
    
    # Save updated master.json
    try:
        # Create backup first
        backup_file = f"master_backup_{int(time.time())}.json"
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(master_json, f, ensure_ascii=False, indent=2)
        print(f"💾 Backup created: {backup_file}")
        
        # Save updated file
        with open('master.json', 'w', encoding='utf-8') as f:
            json.dump(master_json, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Successfully added {len(missing_cards)} cards to master.json")
        print(f"📊 Total players: {current_count} → {new_count}")
        
    except Exception as e:
        print(f"❌ Error saving master.json: {e}")

def main():
    print("\n🏒 Starting Advanced Cards Comparison...")
    
    # Ask user how many cards to check
    try:
        card_count = input("\n❓ How many cards would you like to check? (default: 100): ").strip()
        if not card_count:
            card_count = 100
        else:
            card_count = int(card_count)
    except ValueError:
        card_count = 100
    
    results = compare_more_cards(card_count)
    
    print(f"\n✅ Advanced cards comparison completed!")
    
    if results and results['missing']:
        print(f"💡 Tip: You can manually check the missing cards and add them individually if needed.")
        print(f"   All comparison data is saved in the results file.")

if __name__ == '__main__':
    main()