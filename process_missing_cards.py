#!/usr/bin/env python3
"""
Process Missing Cards
Käsittelee missing_cards_urls.json tiedoston ja hakee puuttuvat kortit
Hyödyntää universal_country_fetcher.py:n logiikkaa
"""

import requests
import json
import time
from utils_clean import clean_common_fields

# API endpoints (kopioitu universal_country_fetcher.py:stä)
SKATER_URL = "https://nhlhutbuilder.com/php/player_stats.php"
GOALIE_URL = "https://nhlhutbuilder.com/php/goalie_stats.php"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'X-Requested-With': 'XMLHttpRequest',
    'Referer': 'https://nhlhutbuilder.com/player-stats.php',
}

GOALIE_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'X-Requested-With': 'XMLHttpRequest',
    'Referer': 'https://nhlhutbuilder.com/goalie-stats.php',
}

def extract_player_id_from_url(url):
    """Pura player_id URL:sta"""
    if 'id=' in url:
        return url.split('id=')[1]
    return None

def is_goalie_url(url):
    """Tarkista onko URL maalivahtien URL"""
    return 'goalie-stats.php' in url

def fetch_player_by_id(player_id, is_goalie=False, timeout=15):
    """Hae pelaajan tiedot suoraan player-stats.php sivulta"""
    player_page_url = f"https://nhlhutbuilder.com/{'goalie-stats.php' if is_goalie else 'player-stats.php'}?id={player_id}"
    page_headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    }
    
    try:
        page_response = requests.get(player_page_url, headers=page_headers, timeout=timeout)
        page_response.raise_for_status()
        
        from bs4 import BeautifulSoup
        page_soup = BeautifulSoup(page_response.text, 'html.parser')
        
        # Alusta pelaajan tiedot
        player_data = {}
        
        # Etsi pelaajan nimi
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
        
        # Etsi pelaajan tiedot taulukoista
        tables = page_soup.find_all('table')
        
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 2:
                    key = cells[0].get_text().strip()
                    value = cells[1].get_text().strip()
                    
                    if key and value:
                        # Mappaa avaimet oikeisiin kenttänimiin
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
                        
                        # Lisää kaikki stat-tiedot
                        elif key in ['Acceleration', 'Agility', 'Balance', 'Endurance', 'Speed', 
                                   'Slap Shot Accuracy', 'Slap Shot Power', 'Wrist Shot Accuracy', 'Wrist Shot Power',
                                   'Deking', 'Offensive Awareness', 'Hand-Eye', 'Passing', 'Puck Control',
                                   'Body Checking', 'Strength', 'Aggression', 'Durability', 'Fighting Skill',
                                   'Defensive Awareness', 'Shot Blocking', 'Stick Checking', 'Face Offs', 'Discipline']:
                            # Muunna avain snake_case:ksi
                            stat_key = key.lower().replace(' ', '_').replace('-', '_')
                            player_data[stat_key] = int(value) if value.isdigit() else value
                        
                        # Maalivahtien stat-tiedot
                        elif key in ['Glove High', 'Glove Low', '5 Hole', 'Stick High', 'Stick Low', 
                                   'Shot Recovery', 'Positioning', 'Breakaway', 'Vision', 'Poke Check', 'Rebound Control']:
                            stat_key = key.lower().replace(' ', '_').replace('-', '_').replace('5_hole', 'five_hole')
                            player_data[stat_key] = int(value) if value.isdigit() else value
        
        # Lisää player_id
        player_data['player_id'] = int(player_id)
        
        # Lisää URL
        player_data['url'] = player_page_url
        
        return player_data
        
    except Exception as e:
        print(f"❌ Virhe pelaajan {player_id} datan hakemisessa: {e}")
        return None

def fetch_xfactors_with_tiers(player_id, timeout=10, is_goalie=False):
    """Hae X-Factor kyvyt pelaajalle (kopioitu enrich_country_xfactors.py:stä)"""
    try:
        if is_goalie:
            url = f"https://nhlhutbuilder.com/goalie-stats.php?id={player_id}"
        else:
            url = f"https://nhlhutbuilder.com/player-stats.php?id={player_id}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        
        resp = requests.get(url, headers=headers, timeout=timeout)
        
        if resp.status_code != 200:
            return []
        
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        xfactors = []
        
        # Etsi kaikki X-Factor kykyjen kontainerit
        ability_containers = soup.find_all('div', class_='ability_info')
        
        for container in ability_containers:
            # Hae kyvyn nimi
            name_elem = container.find('div', class_='ability_name')
            if not name_elem:
                continue
                
            ability_name = name_elem.get_text(strip=True)
            
            # Hae AP kustannus (taso)
            ap_elem = container.find('div', class_='ability_points')
            if ap_elem:
                ap_amount = ap_elem.find('div', class_='ap_amount')
                if ap_amount:
                    ap_cost = ap_amount.get_text(strip=True)
                    try:
                        ap_cost = int(ap_cost)
                    except:
                        ap_cost = 1
                else:
                    ap_cost = 1
            else:
                ap_cost = 1
            
            # Määritä taso AP kustannuksen perusteella
            if ap_cost == 1:
                tier = "Specialist"
            elif ap_cost == 2:
                tier = "All-Star"
            elif ap_cost == 3:
                tier = "Elite"
            else:
                tier = "Specialist"
            
            xfactors.append({
                'name': ability_name,
                'ap_cost': ap_cost,
                'tier': tier
            })
        
        return xfactors
        
    except Exception as e:
        print(f"   ❌ Virhe X-Factor tietojen hakemisessa {player_id}:lle: {e}")
        return []

def load_missing_urls(filename='missing_cards_urls.json'):
    """Lataa puuttuvat URL:it tiedostosta"""
    print(f"📂 Ladataan {filename}...")
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            missing_urls = json.load(f)
        print(f"✅ Ladattu {len(missing_urls)} puuttuvaa URL:ia")
        return missing_urls
    except Exception as e:
        print(f"❌ Virhe {filename} latauksessa: {e}")
        return []

def load_master_json():
    """Lataa master.json"""
    print("📂 Ladataan master.json...")
    try:
        with open('master.json', 'r', encoding='utf-8') as f:
            master_data = json.load(f)
        players = master_data.get('players', [])
        print(f"✅ Master.json ladattu: {len(players)} pelaajaa")
        return master_data, players
    except Exception as e:
        print(f"❌ Virhe master.json latauksessa: {e}")
        return None, []

def save_master_json(master_data):
    """Tallenna päivitetty master.json"""
    print("💾 Tallennetaan päivitetty master.json...")
    try:
        with open('master.json', 'w', encoding='utf-8') as f:
            json.dump(master_data, f, indent=2, ensure_ascii=False)
        print("✅ Master.json tallennettu!")
    except Exception as e:
        print(f"❌ Virhe master.json tallentamisessa: {e}")

def process_missing_cards():
    """Pääfunktio"""
    print("🔄 PROCESS MISSING CARDS")
    print("=" * 50)
    
    # Lataa puuttuvat URL:it
    missing_urls = load_missing_urls()
    if not missing_urls:
        print("❌ Ei puuttuvia URL:eja käsiteltäväksi!")
        return
    
    # Lataa master.json
    master_data, players = load_master_json()
    if not master_data:
        return
    
    # Käsittele puuttuvat URL:it
    new_players = []
    processed_count = 0
    
    for i, url in enumerate(missing_urls, 1):
        player_id = extract_player_id_from_url(url)
        is_goalie = is_goalie_url(url)
        
        if not player_id:
            print(f"⚠️ Ei voitu purkaa player_id URL:sta: {url}")
            continue
        
        print(f"\n{i}/{len(missing_urls)}: Käsitellään {url}")
        print(f"   Player ID: {player_id} ({'maalivahti' if is_goalie else 'kenttäpelaaja'})")
        
        # Hae pelaajan tiedot
        player_data = fetch_player_by_id(player_id, is_goalie)
        
        if player_data:
            # Puhdista data
            cleaned_player = clean_common_fields(player_data)
            
            # Lisää URL
            cleaned_player['url'] = url
            
            # Varmista että position on oikein maalivahdeille
            if is_goalie:
                cleaned_player['position'] = 'G'
            
            # Hae X-Factor tiedot
            print(f"   🔄 Haetaan X-Factor tiedot...")
            xfactors = fetch_xfactors_with_tiers(player_id, is_goalie=is_goalie)
            cleaned_player['xfactors'] = xfactors
            
            if xfactors:
                print(f"   ✅ Löydettiin {len(xfactors)} X-Factor kykyä")
            else:
                print(f"   ⚠️ Ei löytynyt X-Factor kykyjä")
            
            new_players.append(cleaned_player)
            processed_count += 1
            print(f"   ✅ Lisätty: {cleaned_player.get('full_name', 'Unknown')}")
        else:
            print(f"   ❌ Ei löytynyt dataa player_id:lle {player_id}")
        
        # Pieni viive serverin suojaksi
        time.sleep(0.5)
    
    # Lisää uudet pelaajat master.json:iin
    if new_players:
        updated_players = players + new_players
        
        # Päivitä master_data
        updated_master_data = master_data.copy()
        updated_master_data['players'] = updated_players
        updated_master_data['metadata']['total_players'] = len(updated_players)
        updated_master_data['metadata']['last_updated'] = time.strftime('%Y-%m-%d %H:%M:%S')
        
        # Tallenna päivitetty master.json
        save_master_json(updated_master_data)
        
        print(f"\n✅ Lisätty {len(new_players)} uutta pelaajaa!")
        print(f"📊 Uusi kokonaismäärä: {len(updated_players)} pelaajaa")
    else:
        print(f"\n❌ Ei uusia pelaajia lisätty!")
    
    print(f"\n🏁 PROCESS MISSING CARDS VALMIS!")
    print(f"📊 Käsitelty: {processed_count}/{len(missing_urls)} URL:ia")

if __name__ == "__main__":
    process_missing_cards()