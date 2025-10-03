#!/usr/bin/env python3
"""
X-Factor Script Tester - Tests different xfactor enrichment scripts
"""

import sys
import os
import json
import time
import requests
from bs4 import BeautifulSoup

# Add OLDIES to path to import scripts
sys.path.append('/workspace/OLDIES')

# Test player IDs (mix of skaters and goalies)
TEST_PLAYERS = [
    {"id": 1034, "name": "VIKTOR ARVIDSSON", "is_goalie": False},  # Skater
    {"id": 1034, "name": "JACOB MARKSTROM", "is_goalie": True},   # Goalie (same ID!)
    {"id": 1, "name": "Test Player 1", "is_goalie": False},
    {"id": 100, "name": "Test Player 100", "is_goalie": False},
]

def test_enrich_country_xfactors():
    """Test the universal country xfactor enricher"""
    print("\n=== Testing enrich_country_xfactors.py ===")
    
    try:
        from enrich_country_xfactors import fetch_xfactors_with_tiers
        
        results = {}
        for player in TEST_PLAYERS:
            print(f"Testing {player['name']} (ID: {player['id']}, Goalie: {player['is_goalie']})")
            try:
                xfactors = fetch_xfactors_with_tiers(
                    player['id'], 
                    timeout=10, 
                    is_goalie=player['is_goalie']
                )
                results[player['id']] = {
                    'success': True,
                    'count': len(xfactors),
                    'xfactors': xfactors[:3] if xfactors else []  # First 3 for brevity
                }
                print(f"  ✅ Found {len(xfactors)} xfactors")
            except Exception as e:
                results[player['id']] = {
                    'success': False,
                    'error': str(e)
                }
                print(f"  ❌ Error: {e}")
            time.sleep(1)  # Rate limiting
        
        return results
        
    except ImportError as e:
        print(f"❌ Could not import enrich_country_xfactors: {e}")
        return None

def test_enrich_abilities():
    """Test the general abilities enricher"""
    print("\n=== Testing enrich_abilities.py ===")
    
    try:
        from enrich_abilities import fetch_abilities
        
        results = {}
        for player in TEST_PLAYERS:
            if player['is_goalie']:
                continue  # This script doesn't handle goalies
            
            print(f"Testing {player['name']} (ID: {player['id']})")
            try:
                abilities = fetch_abilities(player['id'])
                results[player['id']] = {
                    'success': True,
                    'count': len(abilities),
                    'abilities': abilities[:3] if abilities else []  # First 3 for brevity
                }
                print(f"  ✅ Found {len(abilities)} abilities")
            except Exception as e:
                results[player['id']] = {
                    'success': False,
                    'error': str(e)
                }
                print(f"  ❌ Error: {e}")
            time.sleep(1)  # Rate limiting
        
        return results
        
    except ImportError as e:
        print(f"❌ Could not import enrich_abilities: {e}")
        return None

def test_check_xfactors():
    """Test the xfactor checker"""
    print("\n=== Testing check_xfactors.py ===")
    
    try:
        from check_xfactors import fetch_player_abilities
        
        results = {}
        for player in TEST_PLAYERS:
            if player['is_goalie']:
                continue  # This script doesn't handle goalies
            
            print(f"Testing {player['name']} (ID: {player['id']})")
            try:
                abilities = fetch_player_abilities(player['id'])
                results[player['id']] = {
                    'success': True,
                    'count': len(abilities) if abilities else 0,
                    'abilities': abilities[:3] if abilities else []  # First 3 for brevity
                }
                print(f"  ✅ Found {len(abilities) if abilities else 0} abilities")
            except Exception as e:
                results[player['id']] = {
                    'success': False,
                    'error': str(e)
                }
                print(f"  ❌ Error: {e}")
            time.sleep(1)  # Rate limiting
        
        return results
        
    except ImportError as e:
        print(f"❌ Could not import check_xfactors: {e}")
        return None

def test_usa_xfactors():
    """Test the USA-specific xfactor enricher"""
    print("\n=== Testing enrich_usa_xfactors.py ===")
    
    try:
        from enrich_usa_xfactors import fetch_player_xfactors_detailed
        
        results = {}
        for player in TEST_PLAYERS:
            if player['is_goalie']:
                continue  # This script doesn't handle goalies
            
            print(f"Testing {player['name']} (ID: {player['id']})")
            try:
                xfactors = fetch_player_xfactors_detailed(player['id'])
                results[player['id']] = {
                    'success': True,
                    'count': len(xfactors) if xfactors else 0,
                    'xfactors': xfactors[:3] if xfactors else []  # First 3 for brevity
                }
                print(f"  ✅ Found {len(xfactors) if xfactors else 0} xfactors")
            except Exception as e:
                results[player['id']] = {
                    'success': False,
                    'error': str(e)
                }
                print(f"  ❌ Error: {e}")
            time.sleep(1)  # Rate limiting
        
        return results
        
    except ImportError as e:
        print(f"❌ Could not import enrich_usa_xfactors: {e}")
        return None

def analyze_script_features():
    """Analyze features of each script"""
    print("\n=== Script Feature Analysis ===")
    
    scripts = [
        {
            'name': 'enrich_country_xfactors.py',
            'features': [
                '✅ Universal (works for any country)',
                '✅ Handles both skaters and goalies',
                '✅ Timeout protection',
                '✅ Proper URL handling (player-stats.php vs goalie-stats.php)',
                '✅ Tier information (AP cost)',
                '✅ Error handling',
                '✅ Progress tracking'
            ]
        },
        {
            'name': 'enrich_abilities.py',
            'features': [
                '✅ General purpose',
                '❌ Only handles skaters (no goalie support)',
                '✅ Tier information (AP cost)',
                '✅ Fallback parsing methods',
                '❌ No timeout protection',
                '❌ No progress tracking'
            ]
        },
        {
            'name': 'check_xfactors.py',
            'features': [
                '✅ Multiple selector strategies',
                '❌ Only handles skaters (no goalie support)',
                '✅ Debugging output',
                '❌ No timeout protection',
                '❌ No tier information',
                '❌ No progress tracking'
            ]
        },
        {
            'name': 'enrich_usa_xfactors.py',
            'features': [
                '❌ USA-specific only',
                '❌ Only handles skaters (no goalie support)',
                '✅ Detailed tier information',
                '❌ No timeout protection',
                '❌ No progress tracking'
            ]
        }
    ]
    
    for script in scripts:
        print(f"\n📄 {script['name']}:")
        for feature in script['features']:
            print(f"  {feature}")

def main():
    """Run all tests and provide analysis"""
    print("🔍 X-Factor Script Tester")
    print("=" * 50)
    
    # Analyze features first
    analyze_script_features()
    
    # Run tests
    test_results = {}
    
    test_results['enrich_country_xfactors'] = test_enrich_country_xfactors()
    test_results['enrich_abilities'] = test_enrich_abilities()
    test_results['check_xfactors'] = test_check_xfactors()
    test_results['enrich_usa_xfactors'] = test_usa_xfactors()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    for script_name, results in test_results.items():
        if results is None:
            print(f"\n❌ {script_name}: Could not test")
            continue
            
        print(f"\n📄 {script_name}:")
        successful_tests = sum(1 for r in results.values() if r.get('success', False))
        total_tests = len(results)
        print(f"  Success Rate: {successful_tests}/{total_tests} ({successful_tests/total_tests*100:.1f}%)")
        
        if successful_tests > 0:
            total_xfactors = sum(r.get('count', 0) for r in results.values() if r.get('success', False))
            print(f"  Total X-Factors Found: {total_xfactors}")
    
    # Recommendation
    print("\n" + "=" * 50)
    print("🏆 RECOMMENDATION")
    print("=" * 50)
    
    print("Based on analysis and testing:")
    print("🥇 BEST: enrich_country_xfactors.py")
    print("   - Universal (works for any country)")
    print("   - Handles both skaters and goalies")
    print("   - Proper URL handling")
    print("   - Timeout protection")
    print("   - Progress tracking")
    print("   - Error handling")
    print("   - Tier information")
    
    print("\n🥈 SECOND: enrich_abilities.py")
    print("   - Good general purpose script")
    print("   - Multiple parsing strategies")
    print("   - Tier information")
    print("   - But: No goalie support, no timeout protection")

if __name__ == "__main__":
    main()