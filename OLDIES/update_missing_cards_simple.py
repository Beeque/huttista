#!/usr/bin/env python3
"""
Update Missing Cards - Simple Version
Etsii puuttuvat kortit cards.php sivulta ja käyttää universal_country_fetcher.py logiikkaa
"""

import requests
import json
import time
from bs4 import BeautifulSoup
from utils_clean import clean_common_fields

# API endpoints
FIND_CARDS_URL = "https://nhlhutbuilder.com/php/find_cards.php"
SKATER_URL = "https://nhlhutbuilder.com/php/player_stats.php"
GOALIE_URL = "https://nhlhutbuilder.com/php/goalie_stats.php"

FIND_CARDS_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'X-Requested-With': 'XMLHttpRequest',
    'Referer': 'https://nhlhutbuilder.com/cards.php',
}

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

def fetch_all_players_from_api(is_goalie=False, timeout=30):
    """Hae kaikki pelaajat DataTables API:sta (kopioitu universal_country_fetcher.py:stä)"""
    url = GOALIE_URL if is_goalie else SKATER_URL
    headers = GOALIE_HEADERS if is_goalie else HEADERS
    
    all_players = []
    start = 0
    length = 100
    page = 1
    max_pages = 50  # Safety limit
    
    # Määritä sarakkeet riippuen siitä onko maalivahti vai kenttäpelaaja
    if is_goalie:
        columns = [
            'card_art','card','nationality','league','team','division','salary','hand','weight','height','full_name','overall','aOVR',
            'glove_high','glove_low','stick_high','stick_low','shot_recovery','aggression','agility','speed','positioning','breakaway',
            'vision','poke_check','rebound_control','passing','date_added','date_updated'
        ]
    else:
        columns = [
            'card_art','card','nationality','league','team','division','salary','position','hand','weight','height','full_name','overall','aOVR',
            'acceleration','agility','balance','endurance','speed','slap_shot_accuracy','slap_shot_power','wrist_shot_accuracy','wrist_shot_power',
            'deking','off_awareness','hand_eye','passing','puck_control','body_checking','strength','aggression','durability','fighting_skill',
            'def_awareness','shot_blocking','stick_checking','faceoffs','discipline','date_added','date_updated'
        ]
    
    while page <= max_pages:
        payload = {
            'draw': page,
            'start': start,
            'length': length,
            'search[value]': '',
            'search[regex]': 'false',
        }
        
        for idx, name in enumerate(columns):
            payload[f'columns[{idx}][data]'] = name
            payload[f'columns[{idx}][name]'] = name
            payload[f'columns[{idx}][searchable]'] = 'true'
            payload[f'columns[{idx}][orderable]'] = 'true'
            payload[f'columns[{idx}][search][value]'] = ''
            payload[f'columns[{idx}][search][regex]'] = 'false'
        
        try:
            resp = requests.post(url, data=payload, headers=headers, timeout=timeout)
            
            if resp.status_code != 200:
                print(f"   ❌ HTTP {resp.status_code}")
                break
                
            data = resp.json()
            
            if 'data' not in data:
                print(f"   ❌ Ei 'data' kenttää vastauksessa")
                break
                
            players = data['data']
            if not players:
                print(f"   ✅ Ei enempää pelaajia löytynyt")
                break
                
            all_players.extend(players)
            
            # Tarkista saimmeko vähemmän pelaajia kuin pyysimme (viimeinen sivu)
            if len(players) < length:
                print(f"   ✅ Viimeinen sivu saavutettu (saimme {len(players)} < {length})")
                break
                
            start += length
            page += 1
            
            # Pieni viive serverin suojaksi
            time.sleep(0.5)
            
        except requests.exceptions.Timeout:
            print(f"   ⏰ Timeout sivulla {page}, yritetään uudelleen...")
            time.sleep(2)
            continue
        except Exception as e:
            print(f"   ❌ Virhe sivulla {page}: {e}")
            break
    
    return all_players

def find_players_by_ids(missing_urls, timeout=30):
    """Etsi pelaajat ID:iden perusteella"""
    print(f"🔍 Etsitään {len(missing_urls)} pelaajaa ID:iden perusteella...")
    
    # Jaa kenttäpelaajat ja maalivahdit
    skater_ids = []
    goalie_ids = []
    
    for url in missing_urls:
        player_id = extract_player_id_from_url(url)
        is_goalie = is_goalie_url(url)
        
        if player_id:
            if is_goalie:
                goalie_ids.append(int(player_id))
            else:
                skater_ids.append(int(player_id))
    
    print(f"📊 Kenttäpelaajia: {len(skater_ids)}, Maalivahdeja: {len(goalie_ids)}")
    
    # Hae kaikki kenttäpelaajat
    all_skaters = []
    if skater_ids:
        print(f"🏒 Haetaan kaikki kenttäpelaajat...")
        all_skaters = fetch_all_players_from_api(is_goalie=False, timeout=timeout)
        print(f"✅ Haettu {len(all_skaters)} kenttäpelaajaa")
    
    # Hae kaikki maalivahdit
    all_goalies = []
    if goalie_ids:
        print(f"🥅 Haetaan kaikki maalivahdit...")
        all_goalies = fetch_all_players_from_api(is_goalie=True, timeout=timeout)
        print(f"✅ Haettu {len(all_goalies)} maalivahtia")
    
    # Etsi tarvittavat pelaajat
    found_players = []
    
    # Etsi kenttäpelaajat
    for player in all_skaters:
        if player.get('player_id') in skater_ids:
            found_players.append(player)
    
    # Etsi maalivahdit
    for player in all_goalies:
        if player.get('player_id') in goalie_ids:
            found_players.append(player)
    
    print(f"🎯 Löydettiin {len(found_players)}/{len(missing_urls)} pelaajaa")
    return found_players

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

def run_update_missing_cards_simple():
    """Pääfunktio"""
    print("🔄 UPDATE MISSING CARDS - SIMPLE VERSION")
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
        
        # Hae puuttuvat pelaajat
        found_players = find_players_by_ids(missing_urls)
        
        if found_players:
            # Käsittele löydetyt pelaajat
            new_players = []
            
            for i, player in enumerate(found_players, 1):
                player_id = player.get('player_id')
                is_goalie = is_goalie_url(f"https://nhlhutbuilder.com/player-stats.php?id={player_id}")
                
                print(f"  {i}/{len(found_players)}: Käsitellään {player.get('full_name', 'Unknown')} (ID: {player_id})")
                
                # Puhdista data
                cleaned_player = clean_common_fields(player)
                
                # Lisää URL käyttäen samaa logiikkaa kuin universal_country_fetcher.py
                if player_id:
                    # Tarkista onko tämä maalivahti position tai goalie-only kenttien perusteella
                    position = cleaned_player.get('position', '')
                    goalie_only_fields = ['glove_high', 'glove_low', 'stick_high', 'stick_low', 'shot_recovery', 'positioning', 'breakaway', 'vision', 'poke_check', 'rebound_control']
                    has_goalie_only_stats = any(field in cleaned_player for field in goalie_only_fields)
                    
                    if position == 'G' or has_goalie_only_stats:
                        # Tämä on maalivahti, käytä goalie-stats.php
                        cleaned_player['url'] = f"https://nhlhutbuilder.com/goalie-stats.php?id={player_id}"
                    else:
                        # Tämä on kenttäpelaaja, käytä player-stats.php
                        cleaned_player['url'] = f"https://nhlhutbuilder.com/player-stats.php?id={player_id}"
                
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
    run_update_missing_cards_simple()