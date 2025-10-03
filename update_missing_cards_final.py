#!/usr/bin/env python3
"""
Update Missing Cards - Final Version
Etsii puuttuvat kortit cards.php sivulta ja käyttää olemassa olevia skriptejä
"""

import requests
import json
import time
from bs4 import BeautifulSoup

# API endpoint
FIND_CARDS_URL = "https://nhlhutbuilder.com/php/find_cards.php"

FIND_CARDS_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'X-Requested-With': 'XMLHttpRequest',
    'Referer': 'https://nhlhutbuilder.com/cards.php',
}

def check_total_entries():
    """Tarkista onko uusia kortteja vertaamalla entry_count elementtiä master.json määrään"""
    print("🔍 Tarkistetaan onko uusia kortteja entry_count mukaan...")
    
    data = {
        'limit': 40,
        'sort': 'added',
        'card_type_id': '',
        'team_id': '',
        'league_id': '',
        'nationality': '',
        'position_search': '',
        'hand_search': '',
        'superstar_abilities': '',
        'abilities_match': 'all',
        'pageNumber': 1
    }
    
    try:
        response = requests.post(FIND_CARDS_URL, data=data, headers=FIND_CARDS_HEADERS, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Etsi entry_count elementti
        entry_count_div = soup.find('div', id='entry_count')
        if entry_count_div:
            entry_text = entry_count_div.get_text().strip()
            print(f"📊 Entry count teksti: '{entry_text}'")
            
            # Parsi kokonaismäärä (esim. "Showing 1 to 40 of 2536 entries")
            import re
            match = re.search(r'of (\d+) entries', entry_text)
            if match:
                total_entries = int(match.group(1))
                print(f"📊 Sivuston kokonaismäärä: {total_entries} korttia")
                
                # Lataa master.json ja vertaa
                try:
                    with open('master.json', 'r', encoding='utf-8') as f:
                        master_data = json.load(f)
                    master_count = len(master_data['players'])
                    print(f"📊 Master.json määrä: {master_count} pelaajaa")
                    
                    if total_entries == master_count:
                        print("✅ Määrät täsmäävät! Ei uusia kortteja.")
                        return False  # Ei uusia kortteja
                    else:
                        print(f"🆕 Määrät eivät täsmää! Uusia kortteja: {total_entries - master_count}")
                        return True   # On uusia kortteja
                        
                except Exception as e:
                    print(f"⚠️ Virhe master.json:n lukemisessa: {e}")
                    return True  # Jos ei voi lukea, jatka hakua
            else:
                print("⚠️ Ei voitu parsia entry_count määrää")
                return True  # Jos ei voi parsia, jatka hakua
        else:
            print("⚠️ Ei löytynyt entry_count elementtiä")
            return True  # Jos ei löydy, jatka hakua
            
    except Exception as e:
        print(f"⚠️ Virhe entry_count tarkistuksessa: {e}")
        return True  # Jos virhe, jatka hakua

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

def save_missing_urls(missing_urls, filename='missing_cards_urls.json'):
    """Tallenna puuttuvat URL:it tiedostoon"""
    if missing_urls:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(missing_urls, f, indent=2, ensure_ascii=False)
        print(f"💾 Puuttuvat URL:it tallennettu {filename} tiedostoon")
    else:
        print("✅ Ei puuttuvia URL:eja tallennettavaksi")

def run_update_missing_cards_final():
    """Pääfunktio"""
    print("🔄 UPDATE MISSING CARDS - FINAL VERSION")
    print("=" * 50)
    
    # Tarkista ensin onko uusia kortteja entry_count mukaan
    if not check_total_entries():
        print("\n🏁 LOPETETAAN: Ei uusia kortteja entry_count mukaan!")
        return
    
    # Lataa master.json
    master_data, players = load_master_json()
    if not master_data:
        return
    
    # Luo URL-set nopeaa vertailua varten
    master_urls = get_master_urls(players)
    print(f"📊 Master.json sisältää {len(master_urls)} uniikkia URLia")
    
    # Algoritmi: käy läpi sivuja kunnes ei löydy puuttuvia
    page = 1
    all_missing_urls = []
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
        
        # Lisää puuttuvat URL:it kokonaismäärään
        all_missing_urls.extend(missing_urls)
        
        # Jos ei puuttuvia, lopeta
        if not missing_urls:
            print("🎉 Kaikki kortit löytyvät jo master.json:sta!")
            print("✅ Algoritmi valmis - ei uusia kortteja.")
            break
        
        # Siirry seuraavalle sivulle
        page += 1
        
        # Pieni viive serverin suojaksi
        time.sleep(1)
    
    # Tallenna kaikki puuttuvat URL:it
    save_missing_urls(all_missing_urls)
    
    print(f"\n🏁 UPDATE MISSING CARDS VALMIS!")
    print(f"📊 Yhteensä puuttuvia URL:eja: {len(all_missing_urls)}")
    print(f"📄 Käsitelty sivuja: {page - 1}")
    
    if all_missing_urls:
        print(f"\n📋 Seuraavat vaiheet:")
        print(f"1. Käytä universal_country_fetcher.py hakemaan puuttuvat kortit")
        print(f"2. Käytä enrich_country_xfactors.py rikastamaan X-Factor tiedot")
        print(f"3. Yhdistä uudet kortit master.json:iin")

if __name__ == "__main__":
    run_update_missing_cards_final()