#!/usr/bin/env python3
"""
Cards Comparator - Compares default view cards with master.json and suggests additions
"""

import json
import time
from collections import defaultdict

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
        players_by_name = {p.get('full_name', '').upper(): p for p in players if p.get('full_name')}
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
            'by_name': players_by_name,
            'by_card_id': players_by_card_id
        }
        
    except Exception as e:
        print(f"❌ Error loading master.json: {e}")
        return None

def load_default_cards():
    """Load the default cards analysis data"""
    print("📂 Loading default cards data...")
    
    try:
        with open('cards_default_view_analysis.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        cards = data.get('first_10_cards', [])
        print(f"✅ Loaded {len(cards)} cards from default view")
        
        return cards
        
    except Exception as e:
        print(f"❌ Error loading default cards: {e}")
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
    
    # Strategy 3: Name-based match (case insensitive)
    if name in master_data['by_name']:
        return master_data['by_name'][name], 'name_match'
    
    # Strategy 4: Fuzzy matching for similar names
    # Look for partial matches
    for master_name, master_player in master_data['by_name'].items():
        if name in master_name or master_name in name:
            # Additional checks for team/card type similarity
            master_team = master_player.get('team', '')
            master_card = master_player.get('card', '')
            
            if team == master_team or card_type == master_card:
                return master_player, 'fuzzy_match'
    
    return None, None

def compare_cards():
    """Compare default view cards with master.json"""
    
    print("🏒 NHL HUT Builder - Cards Comparator")
    print("=" * 60)
    print("Comparing default view cards with master.json database")
    print("=" * 60)
    
    # Load data
    master_data = load_master_data()
    default_cards = load_default_cards()
    
    if not master_data or not default_cards:
        print("❌ Failed to load required data")
        return
    
    print(f"\n🔍 COMPARISON ANALYSIS:")
    print(f"=" * 60)
    
    results = {
        'found': [],
        'missing': [],
        'matches_by_type': defaultdict(int)
    }
    
    print(f"\n🎯 Checking {len(default_cards)} default view cards:")
    print(f"-" * 60)
    
    for i, card in enumerate(default_cards, 1):
        name = card.get('full_name', 'Unknown')
        card_type = card.get('card', 'Unknown')
        team = card.get('team', 'Unknown')
        overall = card.get('overall', '?')
        player_id = card.get('player_id', '?')
        
        print(f"{i:2d}. {name:25s} | {card_type:4s} | {team:6s} | OVR:{overall:3d} | ID:{player_id}")
        
        # Find matching player
        match, match_type = find_matching_player(card, master_data)
        
        if match:
            results['found'].append({
                'card': card,
                'match': match,
                'match_type': match_type
            })
            results['matches_by_type'][match_type] += 1
            
            # Show match details
            match_name = match.get('full_name', 'Unknown')
            match_card = match.get('card', 'Unknown')
            match_team = match.get('team', 'Unknown')
            match_overall = match.get('overall', '?')
            
            print(f"    ✅ FOUND: {match_name} | {match_card} | {match_team} | OVR:{match_overall} ({match_type})")
            
            # Check if there are differences
            differences = []
            if card.get('overall') != match.get('overall'):
                differences.append(f"OVR: {card.get('overall')} vs {match.get('overall')}")
            if card.get('card') != match.get('card'):
                differences.append(f"Card: {card.get('card')} vs {match.get('card')}")
            if card.get('salary') != match.get('salary'):
                differences.append(f"Salary: {card.get('salary')} vs {match.get('salary')}")
            
            if differences:
                print(f"    📝 Differences: {', '.join(differences)}")
        else:
            results['missing'].append(card)
            print(f"    ❌ NOT FOUND in master.json")
    
    # Summary
    print(f"\n📊 COMPARISON SUMMARY:")
    print(f"=" * 60)
    print(f"Total cards checked: {len(default_cards)}")
    print(f"Found in master.json: {len(results['found'])}")
    print(f"Missing from master.json: {len(results['missing'])}")
    
    print(f"\n🔍 Match types:")
    for match_type, count in results['matches_by_type'].items():
        print(f"  {match_type}: {count} matches")
    
    # Show missing cards
    if results['missing']:
        print(f"\n❌ MISSING CARDS ({len(results['missing'])} cards not in master.json):")
        print(f"-" * 60)
        
        for i, card in enumerate(results['missing'], 1):
            name = card.get('full_name', 'Unknown')
            card_type = card.get('card', 'Unknown')
            team = card.get('team', 'Unknown')
            overall = card.get('overall', '?')
            nationality = card.get('nationality', 'Unknown')
            position = card.get('position', '?')
            player_id = card.get('player_id', '?')
            
            print(f"{i:2d}. {name:25s} | {card_type:4s} | {team:6s} | OVR:{overall:3d} | {nationality:10s} | {position:3s} | ID:{player_id}")
        
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
        print(f"\n✅ All default view cards are already in master.json!")
    
    # Save comparison results
    output_file = "cards_comparison_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'comparison_date': time.strftime('%Y-%m-%d %H:%M:%S'),
            'total_cards_checked': len(default_cards),
            'found_in_master': len(results['found']),
            'missing_from_master': len(results['missing']),
            'matches_by_type': dict(results['matches_by_type']),
            'missing_cards': results['missing'],
            'found_cards': [
                {
                    'card': card['card'],
                    'match': card['match'],
                    'match_type': card['match_type']
                } for card in results['found']
            ]
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Comparison results saved to: {output_file}")
    
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
    
    # Add URL field to missing cards (they don't have it from the API)
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
        
        # Show added cards
        print(f"\n➕ ADDED CARDS:")
        for i, card in enumerate(missing_cards, 1):
            name = card.get('full_name', 'Unknown')
            card_type = card.get('card', 'Unknown')
            team = card.get('team', 'Unknown')
            overall = card.get('overall', '?')
            print(f"  {i:2d}. {name:25s} | {card_type:4s} | {team:6s} | OVR:{overall:3d}")
        
    except Exception as e:
        print(f"❌ Error saving master.json: {e}")

def main():
    print("\n🏒 Starting Cards Comparison...")
    
    results = compare_cards()
    
    print(f"\n✅ Cards comparison completed!")
    
    if results and results['missing']:
        print(f"💡 Tip: You can manually check the missing cards and add them individually if needed.")
        print(f"   All comparison data is saved in 'cards_comparison_results.json'")

if __name__ == '__main__':
    main()