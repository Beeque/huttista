#!/usr/bin/env python3
"""
USA LD X-Factor Enricher - Adds X-Factor abilities to LD players in usa.json
"""

import json
import time
import requests
from bs4 import BeautifulSoup

PLAYER_URL = "https://nhlhutbuilder.com/player-stats.php?id={pid}"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Referer': 'https://nhlhutbuilder.com/player-stats.php',
}

def fetch_player_xfactors_detailed(pid: int):
    """Fetch detailed X-Factor abilities with tier information"""
    url = PLAYER_URL.format(pid=pid)
    
    try:
        resp = requests.get(url, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        abilities = []
        ability_infos = soup.select('.ability_info')
        
        for info in ability_infos:
            name_elem = info.select_one('.ability_name')
            ability_name = name_elem.get_text(strip=True) if name_elem else None
            
            ap_elem = info.select_one('.ap_amount')
            ap_cost = None
            if ap_elem:
                try:
                    ap_cost = int(ap_elem.get_text(strip=True))
                except:
                    pass
            
            cat_elem = info.select_one('.xfactor_category')
            category = cat_elem.get_text(strip=True) if cat_elem else None
            
            tier = "Unknown"
            if ap_cost == 1:
                tier = "Specialist"
            elif ap_cost == 2:
                tier = "All-Star"
            elif ap_cost == 3:
                tier = "Elite"
            
            if ability_name:
                abilities.append({
                    'name': ability_name,
                    'ap_cost': ap_cost,
                    'tier': tier,
                    'category': category
                })
        
        return abilities
        
    except Exception as e:
        print(f"Error fetching X-Factors for player {pid}: {e}")
        return []

def enrich_usa_ld_players_with_xfactors():
    """
    Enrich LD players in usa.json with X-Factor abilities
    """
    
    print("=== USA LD X-Factor Enricher ===")
    print("Adding X-Factor abilities to LD players...")
    print()
    
    # Load USA players
    try:
        with open('usa.json', 'r') as f:
            players = json.load(f)
        print(f"Loaded {len(players)} USA players")
    except FileNotFoundError:
        print("❌ usa.json not found!")
        return
    
    # Find LD players without X-Factors
    ld_players = [p for p in players if p.get('position') == 'LD']
    ld_players_without_xfactors = [p for p in ld_players if not p.get('abilities')]
    
    print(f"Found {len(ld_players)} LD players")
    print(f"LD players without X-Factors: {len(ld_players_without_xfactors)}")
    
    if not ld_players_without_xfactors:
        print("✅ All LD players already have X-Factor abilities!")
        return players
    
    enriched_players = []
    processed_count = 0
    
    for i, player in enumerate(players, 1):
        name = player.get('full_name', 'Unknown')
        pid = player.get('player_id')
        team = player.get('team', 'Unknown')
        position = player.get('position', 'Unknown')
        overall = player.get('overall', 'Unknown')
        
        # Only process LD players without X-Factors
        if (position == 'LD' and 
            not player.get('abilities') and 
            pid):
            
            print(f"  {i:3d}. {name} ({team}) - {position} - OVR: {overall} (ID: {pid})...")
            
            # Fetch X-Factor abilities
            abilities = fetch_player_xfactors_detailed(int(pid))
            player['abilities'] = abilities
            
            if abilities:
                ability_names = [a['name'] for a in abilities]
                print(f"      X-Factors: {', '.join(ability_names)}")
            else:
                print(f"      No X-Factors")
            
            processed_count += 1
            
            # Be nice to server
            time.sleep(0.5)
            
            # Progress update every 10 players
            if processed_count % 10 == 0:
                print(f"    Progress: {processed_count}/{len(ld_players_without_xfactors)} LD players processed")
        
        enriched_players.append(player)
    
    # Save enriched data
    output_file = "usa.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(enriched_players, f, ensure_ascii=False, indent=2)
    
    print(f"\n=== ENRICHMENT COMPLETE ===")
    print(f"✅ Enriched {processed_count} LD players with X-Factor abilities")
    print(f"Results saved to: {output_file}")
    
    # Analysis
    all_players_with_xfactors = [p for p in enriched_players if p.get('abilities')]
    print(f"Total players with X-Factors: {len(all_players_with_xfactors)}")
    
    if all_players_with_xfactors:
        # Count by tier
        specialist_count = 0
        allstar_count = 0
        elite_count = 0
        
        for player in all_players_with_xfactors:
            for ability in player.get('abilities', []):
                if ability['tier'] == 'Specialist':
                    specialist_count += 1
                elif ability['tier'] == 'All-Star':
                    allstar_count += 1
                elif ability['tier'] == 'Elite':
                    elite_count += 1
        
        print(f"\nX-Factor Tier Distribution:")
        print(f"  Specialist (1 AP): {specialist_count}")
        print(f"  All-Star (2 AP): {allstar_count}")
        print(f"  Elite (3 AP): {elite_count}")
        
        # Show some LD examples
        ld_with_xfactors = [p for p in enriched_players if p.get('position') == 'LD' and p.get('abilities')]
        print(f"\nSample LD X-Factor abilities:")
        for player in ld_with_xfactors[:5]:
            if player.get('abilities'):
                name = player.get('full_name', 'Unknown')
                abilities = player.get('abilities', [])
                ability_strs = [f"{a['name']} ({a['tier']})" for a in abilities]
                print(f"  {name}: {', '.join(ability_strs)}")
    
    return enriched_players

def main():
    print("Starting USA LD X-Factor Enricher...")
    print("=" * 60)
    print("⚠️  WARNING: This will take a while (121 LD players × 0.5s = ~1 minute)")
    print("=" * 60)
    
    enriched_players = enrich_usa_ld_players_with_xfactors()
    
    print(f"\n🎯 ENRICHMENT COMPLETE!")
    print(f"All USA players (LW + RW + LD) now have X-Factor abilities!")
    print(f"Ready to commit to GitHub")

if __name__ == '__main__':
    main()