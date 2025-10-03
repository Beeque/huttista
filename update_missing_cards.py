#!/usr/bin/env python3
"""
Update Missing Cards
Etsii puuttuvat kortit cards.php sivulta ja lisää ne master.json:iin
Yhdistää find_missing_cards.py ja process_missing_cards.py toiminnallisuuden
"""

import requests
import json
import time
from bs4 import BeautifulSoup
from utils_clean import clean_common_fields

# API endpoints
FIND_CARDS_URL = "https://nhlhutbuilder.com/php/find_cards.php"

FIND_CARDS_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'X-Requested-With': 'XMLHttpRequest',
    'Referer': 'https://nhlhutbuilder.com/cards.php',
}

PLAYER_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
}

def fetch_cards_page(page_number=1, limit=40):
    """Hae kortit cards.php sivulta"""
    print(f"📄 Haetaan sivu {page_number} ({limit} korttia)...")
    
    data = {
        'limit': limit,
        'sort': 'added',
        'card_type_id': '',
        'team_id': '',
        'league_id': '',
        'nationality': '',
        'position_search': '',
        'hand_search': '',
        'superstar_abilities': '',
        'abilities_match': 'all',
        'pageNumber': page_number
    }
    
    try:
        response = requests.post(FIND_CARDS_URL, data=data, headers=FIND_CARDS_HEADERS, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Etsi other_card_container divit
        card_containers = soup.find_all('div', class_='other_card_container')
        
        # Kerää URLit
        urls = []
        for container in card_containers:
            # Etsi a-elementti
            link = container.find('a', href=True)
            if link:
                href = link.get('href')
                if href:
                    full_url = f'https://nhlhutbuilder.com/{href}'
                    urls.append(full_url)
        
        print(f"✅ Löydettiin {len(urls)} URLia sivulta {page_number}")
        return urls
        
    except Exception as e:
        print(f"❌ Virhe sivun {page_number} hakemisessa: {e}")
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

def get_master_urls(players):
    """Luo set master.json URL:eista nopeaa vertailua varten"""
    master_urls = set()
    for player in players:
        url = player.get('url')
        if url:
            master_urls.add(url)
    return master_urls

def find_missing_urls(cards_urls, master_urls):
    """Etsi puuttuvat URLit"""
    missing_urls = []
    found_urls = []
    
    for url in cards_urls:
        if url in master_urls:
            found_urls.append(url)
        else:
            missing_urls.append(url)
    
    return missing_urls, found_urls

def extract_player_id_from_url(url):
    """Pura player_id URL:sta"""
    if 'id=' in url:
        return url.split('id=')[1]
    return None

def is_goalie_url(url):
    """Tarkista onko URL maalivahtien URL"""
    return 'goalie-stats.php' in url

def fetch_player_data(player_id, is_goalie=False, timeout=15):
    """Hae pelaajan tiedot suoraan player-stats.php sivulta"""
    player_page_url = f"https://nhlhutbuilder.com/{'goalie-stats.php' if is_goalie else 'player-stats.php'}?id={player_id}"
    
    try:
        page_response = requests.get(player_page_url, headers=PLAYER_HEADERS, timeout=timeout)
        page_response.raise_for_status()
        
        soup = BeautifulSoup(page_response.text, 'html.parser')
        
        # Alusta pelaajan tiedot
        player_data = {}
        
        # Etsi pelaajan nimi
        name_found = False
        for div in soup.find_all('div'):
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
        tables = soup.find_all('table')
        
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
    """Hae X-Factor kyvyt pelaajalle"""
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

def save_master_json(master_data):
    """Tallenna päivitetty master.json"""
    print("💾 Tallennetaan päivitetty master.json...")
    try:
        with open('master.json', 'w', encoding='utf-8') as f:
            json.dump(master_data, f, indent=2, ensure_ascii=False)
        print("✅ Master.json tallennettu!")
    except Exception as e:
        print(f"❌ Virhe master.json tallentamisessa: {e}")

def run_update_missing_cards():
    """Pääfunktio"""
    print("🔄 UPDATE MISSING CARDS")
    print("=" * 50)
    
    # Lataa master.json
    master_data, players = load_master_json()
    if not master_data:
        return
    
    # Luo URL-set nopeaa vertailua varten
    master_urls = get_master_urls(players)
    print(f"📊 Master.json sisältää {len(master_urls)} uniikkia URLia")
    
    # Algoritmi: käy läpi sivuja kunnes ei löydy puuttuvia
    page = 1
    total_added = 0
    max_pages = 10  # Turvallisuusrajoitus
    
    while page <= max_pages:
        print(f"\n--- SIVU {page} ---")
        
        # Hae kortit tältä sivulta
        cards_urls = fetch_cards_page(page, limit=40)
        
        if not cards_urls:
            print("❌ Ei löytynyt kortteja, lopetetaan.")
            break
        
        # Etsi puuttuvat URLit
        missing_urls, found_urls = find_missing_urls(cards_urls, master_urls)
        
        print(f"📊 Sivu {page}: {len(found_urls)} löytyi, {len(missing_urls)} puuttuu")
        
        # Jos ei puuttuvia, lopeta
        if not missing_urls:
            print("🎉 Kaikki kortit löytyvät jo master.json:sta!")
            print("✅ Algoritmi valmis - ei uusia kortteja.")
            break
        
        # Käsittele puuttuvat URL:it
        new_players = []
        
        for i, url in enumerate(missing_urls, 1):
            player_id = extract_player_id_from_url(url)
            is_goalie = is_goalie_url(url)
            
            if not player_id:
                print(f"⚠️ Ei voitu purkaa player_id URL:sta: {url}")
                continue
            
            print(f"  {i}/{len(missing_urls)}: Käsitellään {url}")
            print(f"     Player ID: {player_id} ({'maalivahti' if is_goalie else 'kenttäpelaaja'})")
            
            # Hae pelaajan tiedot
            player_data = fetch_player_data(player_id, is_goalie)
            
            if player_data:
                # Puhdista data
                cleaned_player = clean_common_fields(player_data)
                
                # Lisää URL
                cleaned_player['url'] = url
                
                # Varmista että position on oikein maalivahdeille
                if is_goalie:
                    cleaned_player['position'] = 'G'
                
                # Hae X-Factor tiedot
                print(f"     🔄 Haetaan X-Factor tiedot...")
                xfactors = fetch_xfactors_with_tiers(player_id, is_goalie=is_goalie)
                cleaned_player['xfactors'] = xfactors
                
                if xfactors:
                    print(f"     ✅ Löydettiin {len(xfactors)} X-Factor kykyä")
                else:
                    print(f"     ⚠️ Ei löytynyt X-Factor kykyjä")
                
                new_players.append(cleaned_player)
                print(f"     ✅ Lisätty: {cleaned_player.get('full_name', 'Unknown')}")
            else:
                print(f"     ❌ Ei löytynyt dataa player_id:lle {player_id}")
            
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
            
            # Päivitä paikalliset muuttujat
            players = updated_players
            master_urls = get_master_urls(players)
            
            total_added += len(new_players)
            print(f"✅ Lisätty {len(new_players)} uutta pelaajaa!")
            print(f"📊 Uusi kokonaismäärä: {len(updated_players)} pelaajaa")
        
        # Siirry seuraavalle sivulle
        page += 1
        
        # Pieni viive serverin suojaksi
        time.sleep(1)
    
    print(f"\n🏁 UPDATE MISSING CARDS VALMIS!")
    print(f"📊 Yhteensä lisätty: {total_added} uutta pelaajaa")
    print(f"📄 Käsitelty sivuja: {page - 1}")

if __name__ == "__main__":
    run_update_missing_cards()