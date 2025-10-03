#!/usr/bin/env python3
"""
Test the best X-Factor script with master.json data
"""

import sys
import json
import time
sys.path.append('/workspace/OLDIES')

def test_with_master_json():
    """Test enrich_country_xfactors with master.json data"""
    print("🔍 Testing Best X-Factor Script with Master Data")
    print("=" * 60)
    
    # Load master.json
    try:
        with open('/workspace/master.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        players = data.get('players', [])
        print(f"📊 Loaded {len(players)} players from master.json")
    except Exception as e:
        print(f"❌ Error loading master.json: {e}")
        return
    
    # Import the best xfactor script
    try:
        from enrich_country_xfactors import fetch_xfactors_with_tiers
        print("✅ Successfully imported enrich_country_xfactors")
    except Exception as e:
        print(f"❌ Error importing enrich_country_xfactors: {e}")
        return
    
    # Test with a few sample players
    test_players = [
        {"id": 1034, "name": "VIKTOR ARVIDSSON", "position": "RW"},
        {"id": 1, "name": "Test Player 1", "position": "C"},
        {"id": 100, "name": "Test Player 100", "position": "LW"},
    ]
    
    print(f"\n🧪 Testing with {len(test_players)} sample players:")
    
    for player in test_players:
        print(f"\n📋 Testing: {player['name']} (ID: {player['id']}, Position: {player['position']})")
        
        # Determine if goalie
        is_goalie = player['position'] == 'G'
        
        try:
            xfactors = fetch_xfactors_with_tiers(
                player['id'], 
                timeout=10, 
                is_goalie=is_goalie
            )
            
            if xfactors:
                print(f"   ✅ Found {len(xfactors)} X-Factors:")
                for xf in xfactors:
                    print(f"      • {xf['name']} (AP: {xf['ap_cost']}, Tier: {xf['tier']})")
            else:
                print(f"   ⚠️  No X-Factors found")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        time.sleep(1)  # Rate limiting
    
    # Check how many players in master.json already have xfactors
    players_with_xfactors = [p for p in players if p.get('xfactors')]
    players_without_xfactors = [p for p in players if not p.get('xfactors')]
    
    print(f"\n📊 MASTER.JSON X-FACTOR STATUS:")
    print(f"   • Total players: {len(players)}")
    print(f"   • Players with X-Factors: {len(players_with_xfactors)}")
    print(f"   • Players without X-Factors: {len(players_without_xfactors)}")
    print(f"   • X-Factor coverage: {len(players_with_xfactors)/len(players)*100:.1f}%")
    
    if players_with_xfactors:
        print(f"\n🎯 Sample X-Factors from master.json:")
        for i, player in enumerate(players_with_xfactors[:3]):
            print(f"   {i+1}. {player.get('full_name', 'Unknown')} ({len(player.get('xfactors', []))} X-Factors)")
            for xf in player.get('xfactors', [])[:2]:  # Show first 2
                print(f"      • {xf.get('name', 'Unknown')} (AP: {xf.get('ap_cost', 'N/A')}, Tier: {xf.get('tier', 'N/A')})")

def analyze_xfactor_quality():
    """Analyze the quality of X-Factor data in master.json"""
    print(f"\n🔬 X-FACTOR DATA QUALITY ANALYSIS")
    print("=" * 60)
    
    try:
        with open('/workspace/master.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        players = data.get('players', [])
    except Exception as e:
        print(f"❌ Error loading master.json: {e}")
        return
    
    players_with_xfactors = [p for p in players if p.get('xfactors')]
    
    if not players_with_xfactors:
        print("❌ No players with X-Factors found in master.json")
        return
    
    # Analyze X-Factor distribution
    tier_counts = {"Specialist": 0, "All-Star": 0, "Elite": 0}
    ap_counts = {1: 0, 2: 0, 3: 0}
    total_xfactors = 0
    
    for player in players_with_xfactors:
        for xf in player.get('xfactors', []):
            total_xfactors += 1
            tier = xf.get('tier', 'Unknown')
            ap_cost = xf.get('ap_cost', 0)
            
            if tier in tier_counts:
                tier_counts[tier] += 1
            if ap_cost in ap_counts:
                ap_counts[ap_cost] += 1
    
    print(f"📊 X-Factor Distribution:")
    print(f"   • Total X-Factors: {total_xfactors}")
    print(f"   • Players with X-Factors: {len(players_with_xfactors)}")
    print(f"   • Average X-Factors per player: {total_xfactors/len(players_with_xfactors):.1f}")
    
    print(f"\n🏆 Tier Distribution:")
    for tier, count in tier_counts.items():
        percentage = count/total_xfactors*100 if total_xfactors > 0 else 0
        print(f"   • {tier}: {count} ({percentage:.1f}%)")
    
    print(f"\n⚡ AP Cost Distribution:")
    for ap, count in ap_counts.items():
        percentage = count/total_xfactors*100 if total_xfactors > 0 else 0
        print(f"   • {ap} AP: {count} ({percentage:.1f}%)")

if __name__ == "__main__":
    test_with_master_json()
    analyze_xfactor_quality()