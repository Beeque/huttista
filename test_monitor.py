#!/usr/bin/env python3
"""
Test script for NHL HUT Builder Cards Monitor
Tests the monitoring functionality without running the full service
"""

import json
import time
import requests
from datetime import datetime
from utils_clean import clean_common_fields

# API endpoint
DT_URL = "https://nhlhutbuilder.com/php/player_stats.php"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'X-Requested-With': 'XMLHttpRequest',
    'Referer': 'https://nhlhutbuilder.com/cards.php',
}

def test_api_connection():
    """Test connection to NHL HUT Builder API"""
    print("🔍 Testing API connection...")
    
    payload = {
        'draw': 1,
        'start': 0,
        'length': 10,
        'search[value]': '',
        'search[regex]': 'false',
    }
    
    # Define minimal columns for testing
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
    payload['order[0][column]'] = '35'
    payload['order[0][dir]'] = 'desc'
    
    try:
        resp = requests.post(DT_URL, data=payload, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        
        data = resp.json()
        cards = data.get('data', [])
        total = data.get('recordsTotal', 0)
        
        print(f"✅ API connection successful!")
        print(f"📊 Total cards available: {total}")
        print(f"📄 Cards in test response: {len(cards)}")
        
        if cards:
            print(f"\n🎯 Sample cards:")
            for i, card in enumerate(cards[:5], 1):
                cleaned_card = clean_common_fields(card)
                name = cleaned_card.get('full_name', 'Unknown')
                overall = cleaned_card.get('overall', '?')
                team = cleaned_card.get('team', 'Unknown')
                card_type = cleaned_card.get('card', 'Unknown')
                nationality = cleaned_card.get('nationality', 'Unknown')
                position = cleaned_card.get('position', '?')
                player_id = cleaned_card.get('player_id', '?')
                
                print(f"  {i}. {name:25s} | {card_type:4s} | {team:6s} | OVR:{overall:3d} | {nationality:10s} | {position:3s} | ID:{player_id}")
        
        return True
        
    except Exception as e:
        print(f"❌ API connection failed: {e}")
        return False

def test_master_json():
    """Test master.json loading and structure"""
    print("\n📂 Testing master.json...")
    
    try:
        with open('master.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        players = data.get('players', [])
        metadata = data.get('metadata', {})
        
        print(f"✅ Master.json loaded successfully!")
        print(f"📊 Total players: {len(players)}")
        print(f"📝 Metadata: {metadata}")
        
        if players:
            # Show sample player
            sample_player = players[0]
            name = sample_player.get('full_name', 'Unknown')
            player_id = sample_player.get('player_id', '?')
            has_xfactors = 'xfactors' in sample_player
            
            print(f"\n🎯 Sample player:")
            print(f"  Name: {name}")
            print(f"  ID: {player_id}")
            print(f"  Has X-Factors: {has_xfactors}")
            
            if has_xfactors:
                xfactors = sample_player.get('xfactors', [])
                print(f"  X-Factors: {len(xfactors)} abilities")
        
        return True
        
    except FileNotFoundError:
        print("⚠️ master.json not found - will be created when needed")
        return True
    except Exception as e:
        print(f"❌ Error loading master.json: {e}")
        return False

def test_utils_clean():
    """Test utils_clean.py functionality"""
    print("\n🧹 Testing utils_clean.py...")
    
    try:
        # Test data cleaning
        test_card = {
            'full_name': '<a href="?id=1234">JOHN DOE</a>',
            'weight': '200 lbs',
            'height': "6'2\"",
            'salary': '$5.0M',
            'overall': '85'
        }
        
        cleaned = clean_common_fields(test_card)
        
        print(f"✅ Data cleaning working!")
        print(f"📊 Test results:")
        print(f"  Name: {test_card['full_name']} → {cleaned.get('full_name')}")
        print(f"  Weight: {test_card['weight']} → {cleaned.get('weight')} kg")
        print(f"  Height: {test_card['height']} → {cleaned.get('height')} cm")
        print(f"  Salary: {test_card['salary']} → ${cleaned.get('salary'):,}")
        print(f"  Overall: {test_card['overall']} → {cleaned.get('overall')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing utils_clean.py: {e}")
        return False

def test_xfactor_fetching():
    """Test X-Factor fetching functionality"""
    print("\n🎯 Testing X-Factor fetching...")
    
    try:
        from bs4 import BeautifulSoup
        
        # Test with a known player ID
        test_player_id = 1939  # JACCOB SLAVIN
        url = f"https://nhlhutbuilder.com/player-stats.php?id={test_player_id}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        }
        
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        ability_infos = soup.select('.ability_info')
        
        print(f"✅ X-Factor fetching working!")
        print(f"📊 Found {len(ability_infos)} X-Factor abilities")
        
        if ability_infos:
            print(f"🎯 Sample abilities:")
            for i, info in enumerate(ability_infos[:3], 1):
                name_elem = info.select_one('.ability_name')
                ap_elem = info.select_one('.ap_amount')
                
                name = name_elem.get_text(strip=True) if name_elem else 'Unknown'
                ap = ap_elem.get_text(strip=True) if ap_elem else '?'
                
                print(f"  {i}. {name} ({ap} AP)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing X-Factor fetching: {e}")
        return False

def main():
    print("🧪 NHL HUT Builder Cards Monitor - Test Suite")
    print("=" * 60)
    print("Testing all components before building executables")
    print("=" * 60)
    
    tests = [
        ("API Connection", test_api_connection),
        ("Master JSON", test_master_json),
        ("Data Cleaning", test_utils_clean),
        ("X-Factor Fetching", test_xfactor_fetching),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running test: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n📊 TEST RESULTS:")
    print(f"=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name:20s}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Summary: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! Ready to build executables.")
        return True
    else:
        print("⚠️ Some tests failed. Please fix issues before building.")
        return False

if __name__ == '__main__':
    success = main()
    if success:
        print("\n💡 Next step: Run 'python build_executables.py' to create Windows executables")
    else:
        print("\n💡 Please fix the failing tests before building executables")