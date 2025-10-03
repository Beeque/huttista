#!/usr/bin/env python3
"""
Process Missing Cards - Final Version
Uses reliable universal_country_fetcher.py approach to fetch missing cards
"""

import json
import requests
import time
from utils_clean import clean_common_fields
from enrich_country_xfactors import fetch_xfactors_with_tiers

def load_missing_cards():
    """Load missing card URLs from JSON file"""
    try:
        with open('missing_cards_urls.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ missing_cards_urls.json tiedostoa ei löydy!")
        return []
    except json.JSONDecodeError as e:
        print(f"❌ Virhe JSON:n lukemisessa: {e}")
        return []

def extract_player_id_from_url(url):
    """Extract player ID from URL"""
    if 'player-stats.php?id=' in url:
        return url.split('player-stats.php?id=')[1]
    elif 'goalie-stats.php?id=' in url:
        return url.split('goalie-stats.php?id=')[1]
    return None

def is_goalie_url(url):
    """Check if URL is for a goalie"""
    return 'goalie-stats.php' in url

def fetch_player_data_direct(player_id, is_goalie=False, timeout=15):
    """
    Fetch player data directly from player-stats.php or goalie-stats.php page
    (Same approach as working update_missing_cards.py)
    """
    from bs4 import BeautifulSoup
    
    player_page_url = f"https://nhlhutbuilder.com/{'goalie-stats.php' if is_goalie else 'player-stats.php'}?id={player_id}"
    page_headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    }
    
    try:
        page_response = requests.get(player_page_url, headers=page_headers, timeout=timeout)
        page_response.raise_for_status()
        
        page_soup = BeautifulSoup(page_response.text, 'html.parser')
        
        player_data = {}
        
        # Find player name
        name_found = False
        for div in page_soup.find_all('div'):
            text = div.get_text().strip()
            if 'Overall' in text and 'Card Type' in text:
                lines = text.split('\n')
                for line in lines:
                    line = line.strip()
                    if (line and 
                        not line.isdigit() and 
                        'Overall' not in line and 
                        'Card Type' not in line and
                        'Nationality' not in line and
                        'Age' not in line and
                        'Position' not in line and
                        'Shoots' not in line and
                        'Weight' not in line and
                        'Height' not in line and
                        'Salary' not in line and
                        'Division' not in line and
                        len(line) > 3 and
                        not line.startswith('HUT') and
                        not line.startswith('Champions')):
                        player_data['full_name'] = line
                        name_found = True
                        break
                if name_found:
                    break
        
        if not name_found:
            print(f"⚠️ Ei löytynyt nimeä player_id:lle {player_id}")
            return None
        
        # Find player data from tables
        tables = page_soup.find_all('table')
        
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 2:
                    key = cells[0].get_text().strip()
                    value = cells[1].get_text().strip()
                    
                    if key and value:
                        if key == 'Overall':
                            player_data['overall'] = int(value) if value.isdigit() else value
                        elif key == 'Card Type':
                            player_data['card'] = value
                        elif key == 'Nationality':
                            player_data['nationality'] = value
                        elif key == 'Age':
                            player_data['age'] = int(value) if value.isdigit() else value
                        elif key == 'Position':
                            player_data['position'] = value
                        elif key == 'Shoots':
                            player_data['hand'] = value
                        elif key == 'Weight':
                            player_data['weight'] = value
                        elif key == 'Height':
                            player_data['height'] = value
                        elif key == 'Salary':
                            player_data['salary'] = value
                        elif key == 'Division':
                            player_data['division'] = value
                        elif key == 'Average Overall':
                            player_data['aOVR'] = float(value) if value.replace('.', '').isdigit() else value
                        elif key == 'Adjusted Overall':
                            player_data['adjusted_overall'] = float(value) if value.replace('.', '').isdigit() else value
                        
                        # Skater stats
                        elif key in ['Acceleration', 'Agility', 'Balance', 'Endurance', 'Speed', 
                                   'Slap Shot Accuracy', 'Slap Shot Power', 'Wrist Shot Accuracy', 'Wrist Shot Power',
                                   'Deking', 'Offensive Awareness', 'Hand-Eye', 'Passing', 'Puck Control',
                                   'Body Checking', 'Strength', 'Aggression', 'Durability', 'Fighting Skill',
                                   'Defensive Awareness', 'Shot Blocking', 'Stick Checking', 'Face Offs', 'Discipline']:
                            stat_key = key.lower().replace(' ', '_').replace('-', '_')
                            player_data[stat_key] = int(value) if value.isdigit() else value
                        
                        # Goalie stats
                        elif key in ['Glove High', 'Glove Low', '5 Hole', 'Stick High', 'Stick Low', 
                                   'Shot Recovery', 'Positioning', 'Breakaway', 'Vision', 'Poke Check', 'Rebound Control']:
                            stat_key = key.lower().replace(' ', '_').replace('-', '_').replace('5_hole', 'five_hole')
                            player_data[stat_key] = int(value) if value.isdigit() else value
        
        player_data['player_id'] = int(player_id)
        player_data['url'] = player_page_url
        
        # Clean the data using utils_clean
        cleaned_data = clean_common_fields(player_data)
        
        return cleaned_data
        
    except Exception as e:
        print(f"❌ Virhe pelaajan {player_id} datan hakemisessa: {e}")
        return None

def load_master_json():
    """Load master.json"""
    try:
        with open('master.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ master.json tiedostoa ei löydy!")
        return {'players': []}
    except json.JSONDecodeError as e:
        print(f"❌ Virhe master.json:n lukemisessa: {e}")
        return {'players': []}

def save_master_json(master_data):
    """Save master.json"""
    try:
        with open('master.json', 'w', encoding='utf-8') as f:
            json.dump(master_data, f, indent=2, ensure_ascii=False)
        print(f"✅ Master.json tallennettu: {len(master_data['players'])} pelaajaa")
    except Exception as e:
        print(f"❌ Virhe master.json:n tallentamisessa: {e}")

def process_missing_cards():
    """Main function to process missing cards"""
    print("🔄 PROCESS MISSING CARDS - FINAL VERSION")
    print("=" * 50)
    
    # Load missing cards
    missing_urls = load_missing_cards()
    if not missing_urls:
        print("❌ Ei puuttuvia kortteja käsiteltäväksi!")
        return
    
    print(f"📂 Ladataan {len(missing_urls)} puuttuvaa URL:ia...")
    
    # Load master.json
    master_data = load_master_json()
    existing_urls = {player.get('url') for player in master_data['players'] if player.get('url')}
    print(f"📊 Master.json sisältää {len(existing_urls)} uniikkia URLia")
    
    # Process missing cards
    new_players = []
    processed_count = 0
    
    for i, url in enumerate(missing_urls, 1):
        if url in existing_urls:
            print(f"⏭️ URL {i}/{len(missing_urls)}: {url} (löytyy jo)")
            continue
            
        player_id = extract_player_id_from_url(url)
        if not player_id:
            print(f"❌ Ei voitu poimia player_id URL:ista: {url}")
            continue
            
        is_goalie = is_goalie_url(url)
        print(f"🔄 Käsitellään {i}/{len(missing_urls)}: {url}")
        
        # Fetch player data
        player_data = fetch_player_data_direct(player_id, is_goalie)
        if not player_data:
            print(f"❌ Ei voitu hakea dataa player_id:lle {player_id}")
            continue
        
        # Fetch X-Factors
        print(f"🎯 Haetaan X-Factors player_id:lle {player_id}...")
        xfactors = fetch_xfactors_with_tiers(player_id, timeout=10, is_goalie=is_goalie)
        if xfactors:
            player_data['xfactors'] = xfactors
            print(f"✅ X-Factors haettu: {len(xfactors)} kykyä")
        else:
            player_data['xfactors'] = []
            print(f"⚠️ Ei X-Factor kykyjä player_id:lle {player_id}")
        
        new_players.append(player_data)
        processed_count += 1
        
        print(f"✅ Käsitelty: {player_data.get('full_name', 'N/A')} (ID: {player_id})")
        
        # Small delay to be respectful
        time.sleep(0.5)
        
        # Save progress every 10 players
        if processed_count % 10 == 0:
            print(f"💾 Väliaikainen tallennus: {processed_count} uutta pelaajaa...")
            master_data['players'].extend(new_players)
            save_master_json(master_data)
            new_players = []
    
    # Add remaining new players
    if new_players:
        master_data['players'].extend(new_players)
    
    # Final save
    save_master_json(master_data)
    
    print(f"\n🏁 PROCESS MISSING CARDS VALMIS!")
    print(f"📊 Käsitelty {processed_count} uutta pelaajaa")
    print(f"📊 Master.json sisältää nyt {len(master_data['players'])} pelaajaa")

if __name__ == "__main__":
    process_missing_cards()