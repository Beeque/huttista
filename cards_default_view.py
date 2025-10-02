#!/usr/bin/env python3
"""
Cards Default View - Analyzes what cards are shown on NHL HUT Builder cards.php with default filters
"""

import requests
import json
import time
from utils_clean import clean_common_fields

# API endpoint
DT_URL = "https://nhlhutbuilder.com/php/player_stats.php"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'X-Requested-With': 'XMLHttpRequest',
    'Referer': 'https://nhlhutbuilder.com/cards.php',
}

def fetch_default_cards():
    """Fetch cards with default sorting (most recent additions by default)"""
    
    print("🏒 Fetching cards from NHL HUT Builder with DEFAULT filters...")
    print("=" * 60)
    
    payload = {
        'draw': 1,
        'start': 0,
        'length': 50,  # Default page size
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
    
    # Set up column definitions (no filters)
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
        print(f"📡 Sending request to API...")
        resp = requests.post(DT_URL, data=payload, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        
        data = resp.json()
        cards = data.get('data', [])
        total = data.get('recordsTotal', 0)
        filtered = data.get('recordsFiltered', 0)
        
        print(f"✅ Successfully fetched data!")
        print(f"📊 Total records: {total}")
        print(f"🔍 Filtered records: {filtered}")
        print(f"📄 Cards in response: {len(cards)}")
        
        return data
        
    except Exception as e:
        print(f"❌ Error fetching data: {e}")
        return None

def analyze_cards(data):
    """Analyze the cards data"""
    
    if not data:
        return None
    
    cards = data.get('data', [])
    total = data.get('recordsTotal', 0)
    filtered = data.get('recordsFiltered', 0)
    
    print(f"\n📊 ANALYSIS OF DEFAULT VIEW:")
    print(f"=" * 60)
    print(f"Total cards available: {total}")
    print(f"Cards shown by default: {filtered}")
    print(f"Cards in first page: {len(cards)}")
    
    if not cards:
        print("❌ No cards found")
        return None
    
    # Clean cards
    cleaned_cards = [clean_common_fields(card) for card in cards]
    
    # Analyze card types
    card_types = {}
    nationalities = {}
    teams = {}
    positions = {}
    leagues = {}
    overalls = []
    
    for card in cleaned_cards:
        card_type = card.get('card', 'Unknown')
        nationality = card.get('nationality', 'Unknown')
        team = card.get('team', 'Unknown')
        position = card.get('position', 'Unknown')
        league = card.get('league', 'Unknown')
        overall = card.get('overall')
        
        card_types[card_type] = card_types.get(card_type, 0) + 1
        nationalities[nationality] = nationalities.get(nationality, 0) + 1
        teams[team] = teams.get(team, 0) + 1
        positions[position] = positions.get(position, 0) + 1
        leagues[league] = leagues.get(league, 0) + 1
        
        if isinstance(overall, int):
            overalls.append(overall)
    
    print(f"\n🎯 FIRST 10 CARDS (default sort = most recently added):")
    print(f"-" * 60)
    for i, card in enumerate(cleaned_cards[:10], 1):
        name = card.get('full_name', 'Unknown')
        overall = card.get('overall', '?')
        team = card.get('team', 'Unknown')
        position = card.get('position', '?')
        card_type = card.get('card', 'Unknown')
        nationality = card.get('nationality', 'Unknown')
        league = card.get('league', 'Unknown')
        date_added = card.get('date_added', 'Unknown')
        
        print(f"{i:2d}. {name:25s} | {card_type:4s} | OVR:{overall:3d} | {team:6s} | {position:3s} | {nationality:10s} | {league:6s}")
        print(f"    Added: {date_added}")
    
    print(f"\n📈 CARD TYPES DISTRIBUTION (first {len(cleaned_cards)} cards):")
    print(f"-" * 60)
    for card_type, count in sorted(card_types.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / len(cleaned_cards)) * 100
        print(f"  {card_type:20s}: {count:3d} cards ({percentage:5.1f}%)")
    
    print(f"\n🌍 TOP 10 NATIONALITIES (first {len(cleaned_cards)} cards):")
    print(f"-" * 60)
    for nationality, count in sorted(nationalities.items(), key=lambda x: x[1], reverse=True)[:10]:
        percentage = (count / len(cleaned_cards)) * 100
        print(f"  {nationality:20s}: {count:3d} cards ({percentage:5.1f}%)")
    
    print(f"\n🏒 TOP 10 TEAMS (first {len(cleaned_cards)} cards):")
    print(f"-" * 60)
    for team, count in sorted(teams.items(), key=lambda x: x[1], reverse=True)[:10]:
        percentage = (count / len(cleaned_cards)) * 100
        print(f"  {team:20s}: {count:3d} cards ({percentage:5.1f}%)")
    
    print(f"\n🏟️ LEAGUES DISTRIBUTION (first {len(cleaned_cards)} cards):")
    print(f"-" * 60)
    for league, count in sorted(leagues.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / len(cleaned_cards)) * 100
        print(f"  {league:20s}: {count:3d} cards ({percentage:5.1f}%)")
    
    print(f"\n🎯 POSITIONS DISTRIBUTION (first {len(cleaned_cards)} cards):")
    print(f"-" * 60)
    for position, count in sorted(positions.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / len(cleaned_cards)) * 100
        print(f"  {position:20s}: {count:3d} cards ({percentage:5.1f}%)")
    
    if overalls:
        avg_overall = sum(overalls) / len(overalls)
        min_overall = min(overalls)
        max_overall = max(overalls)
        
        print(f"\n⭐ OVERALL RATINGS (first {len(cleaned_cards)} cards):")
        print(f"-" * 60)
        print(f"  Average Overall: {avg_overall:.1f}")
        print(f"  Min Overall: {min_overall}")
        print(f"  Max Overall: {max_overall}")
    
    # Save results
    output_file = "cards_default_view_analysis.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'total_records': total,
            'filtered_records': filtered,
            'cards_in_response': len(cards),
            'first_10_cards': cleaned_cards[:10],
            'card_types': card_types,
            'nationalities': nationalities,
            'teams': teams,
            'positions': positions,
            'leagues': leagues,
            'overall_stats': {
                'average': avg_overall if overalls else None,
                'min': min_overall if overalls else None,
                'max': max_overall if overalls else None
            },
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Full analysis saved to: {output_file}")
    
    return {
        'total': total,
        'filtered': filtered,
        'cards': cleaned_cards[:10],
        'card_types': card_types,
        'nationalities': nationalities,
        'teams': teams,
        'positions': positions,
        'leagues': leagues
    }

def main():
    print("\n🏒 NHL HUT BUILDER - CARDS PAGE DEFAULT VIEW ANALYSIS")
    print("=" * 60)
    print("Analyzing what cards are shown on https://nhlhutbuilder.com/cards.php")
    print("with DEFAULT filters (no filters applied)")
    print("=" * 60)
    
    # Fetch default cards
    data = fetch_default_cards()
    
    if data:
        # Analyze the cards
        analysis = analyze_cards(data)
        
        if analysis:
            print(f"\n✅ SUMMARY:")
            print(f"=" * 60)
            print(f"📊 Total cards in database: {analysis['total']}")
            print(f"🔍 Default view shows: ALL {analysis['filtered']} cards")
            print(f"📄 Cards per page: {len(analysis['cards'])}")
            print(f"🎯 Default sort: Date Added (newest first)")
            print(f"🏆 Most common card type: {max(analysis['card_types'], key=analysis['card_types'].get)}")
            print(f"🌍 Most common nationality: {max(analysis['nationalities'], key=analysis['nationalities'].get)}")
            print(f"🏒 Most common team: {max(analysis['teams'], key=analysis['teams'].get)}")
            print(f"🏟️ Most common league: {max(analysis['leagues'], key=analysis['leagues'].get)}")
            print(f"🎯 Most common position: {max(analysis['positions'], key=analysis['positions'].get)}")
    else:
        print("❌ Failed to fetch cards data")
    
    print(f"\n✅ Analysis completed!")

if __name__ == '__main__':
    main()