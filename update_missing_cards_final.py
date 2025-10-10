#!/usr/bin/env python3
"""
Update Missing Cards - Final Version
Etsii puuttuvat kortit cards.php sivulta ja käyttää olemassa olevia skriptejä
"""

import requests
import json
import time
import logging
import re
from typing import List, Dict, Tuple, Optional, Set
from bs4 import BeautifulSoup
from dataclasses import dataclass

# Configuration
@dataclass
class Config:
    """Configuration settings for the missing cards updater"""
    find_cards_url: str = "https://nhlhutbuilder.com/php/find_cards.php"
    timeout: int = 30
    retry_count: int = 3
    retry_delay: float = 1.0
    page_delay: float = 1.0
    max_pages: int = 10
    limit_per_page: int = 40
    
    headers: Dict[str, str] = None
    
    def __post_init__(self):
        if self.headers is None:
            self.headers = {
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'X-Requested-With': 'XMLHttpRequest',
                'Referer': 'https://nhlhutbuilder.com/cards.php',
            }

# Global configuration
config = Config()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('update_missing_cards.log')
    ]
)
logger = logging.getLogger(__name__)

def make_request_with_retry(url: str, data: Dict, headers: Dict, timeout: int = None) -> Optional[requests.Response]:
    """Make HTTP request with retry logic"""
    timeout = timeout or config.timeout
    
    for attempt in range(config.retry_count):
        try:
            response = requests.post(url, data=data, headers=headers, timeout=timeout)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            logger.warning(f"Request attempt {attempt + 1}/{config.retry_count} failed: {e}")
            if attempt < config.retry_count - 1:
                time.sleep(config.retry_delay * (attempt + 1))  # Exponential backoff
            else:
                logger.error(f"All {config.retry_count} request attempts failed")
                return None

def check_total_entries() -> bool:
    """
    Tarkista onko uusia kortteja vertaamalla entry_count elementtiä master.json määrään
    
    Returns:
        bool: True if there are new cards, False if no new cards
    """
    logger.info("🔍 Tarkistetaan onko uusia kortteja entry_count mukaan...")
    
    data = {
        'limit': config.limit_per_page,
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
    
    response = make_request_with_retry(config.find_cards_url, data, config.headers)
    if not response:
        logger.error("Failed to fetch cards data for entry count check")
        return True  # If we can't check, assume there are new cards
    
    try:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Etsi entry_count elementti
        entry_count_div = soup.find('div', id='entry_count')
        if not entry_count_div:
            logger.warning("⚠️ Ei löytynyt entry_count elementtiä")
            return True  # Jos ei löydy, jatka hakua
        
        entry_text = entry_count_div.get_text().strip()
        logger.info(f"📊 Entry count teksti: '{entry_text}'")
        
        # Parsi kokonaismäärä (esim. "Showing 1 to 40 of 2536 entries")
        match = re.search(r'of (\d+) entries', entry_text)
        if not match:
            logger.warning("⚠️ Ei voitu parsia entry_count määrää")
            return True  # Jos ei voi parsia, jatka hakua
        
        total_entries = int(match.group(1))
        logger.info(f"📊 Sivuston kokonaismäärä: {total_entries} korttia")
        
        # Lataa master.json ja vertaa
        try:
            with open('master.json', 'r', encoding='utf-8') as f:
                master_data = json.load(f)
            master_count = len(master_data['players'])
            logger.info(f"📊 Master.json määrä: {master_count} pelaajaa")
            
            if total_entries == master_count:
                logger.info("✅ Määrät täsmäävät! Ei uusia kortteja.")
                return False  # Ei uusia kortteja
            else:
                new_cards = total_entries - master_count
                logger.info(f"🆕 Määrät eivät täsmää! Uusia kortteja: {new_cards}")
                return True   # On uusia kortteja
                
        except Exception as e:
            logger.error(f"⚠️ Virhe master.json:n lukemisessa: {e}")
            return True  # Jos ei voi lukea, jatka hakua
            
    except Exception as e:
        logger.error(f"⚠️ Virhe entry_count tarkistuksessa: {e}")
        return True  # Jos virhe, jatka hakua

def fetch_cards_page(page_number: int = 1, limit: int = None) -> List[str]:
    """
    Hae kortit cards.php sivulta
    
    Args:
        page_number: Sivun numero
        limit: Korttien määrä per sivu
        
    Returns:
        List[str]: Lista URL:eista
    """
    limit = limit or config.limit_per_page
    logger.info(f"📄 Haetaan sivu {page_number} ({limit} korttia)...")
    
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
    
    response = make_request_with_retry(config.find_cards_url, data, config.headers)
    if not response:
        logger.error(f"❌ Virhe sivun {page_number} hakemisessa")
        return []
    
    try:
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
        
        logger.info(f"✅ Löydettiin {len(urls)} URLia sivulta {page_number}")
        return urls
        
    except Exception as e:
        logger.error(f"❌ Virhe sivun {page_number} hakemisessa: {e}")
        return []

def load_master_json() -> Tuple[Optional[Dict], List[Dict]]:
    """
    Lataa master.json
    
    Returns:
        Tuple[Optional[Dict], List[Dict]]: Master data and players list
    """
    logger.info("📂 Ladataan master.json...")
    try:
        with open('master.json', 'r', encoding='utf-8') as f:
            master_data = json.load(f)
        players = master_data.get('players', [])
        logger.info(f"✅ Master.json ladattu: {len(players)} pelaajaa")
        return master_data, players
    except Exception as e:
        logger.error(f"❌ Virhe master.json latauksessa: {e}")
        return None, []

def get_master_urls(players: List[Dict]) -> Set[str]:
    """
    Luo set master.json URL:eista nopeaa vertailua varten
    
    Args:
        players: Lista pelaajista
        
    Returns:
        Set[str]: Set URL:eista
    """
    master_urls = set()
    for player in players:
        url = player.get('url')
        if url:
            master_urls.add(url)
    return master_urls

def find_missing_urls(cards_urls: List[str], master_urls: Set[str]) -> Tuple[List[str], List[str]]:
    """
    Etsi puuttuvat URLit
    
    Args:
        cards_urls: Lista korttien URL:eista
        master_urls: Set master.json URL:eista
        
    Returns:
        Tuple[List[str], List[str]]: Puuttuvat ja löydetyt URL:it
    """
    missing_urls = []
    found_urls = []
    
    for url in cards_urls:
        if url in master_urls:
            found_urls.append(url)
        else:
            missing_urls.append(url)
    
    return missing_urls, found_urls

def save_missing_urls(missing_urls: List[str], filename: str = 'missing_cards_urls.json') -> None:
    """
    Tallenna puuttuvat URL:it tiedostoon
    
    Args:
        missing_urls: Lista puuttuvista URL:eista
        filename: Tiedoston nimi
    """
    if missing_urls:
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(missing_urls, f, indent=2, ensure_ascii=False)
            logger.info(f"💾 Puuttuvat URL:it tallennettu {filename} tiedostoon")
        except Exception as e:
            logger.error(f"❌ Virhe tallentaessa {filename}: {e}")
    else:
        logger.info("✅ Ei puuttuvia URL:eja tallennettavaksi")

def print_progress_summary(page: int, total_pages: int, found_count: int, missing_count: int, total_missing: int) -> None:
    """Print progress summary"""
    progress_percent = (page / total_pages) * 100 if total_pages > 0 else 0
    logger.info(f"📊 Edistyminen: {page}/{total_pages} ({progress_percent:.1f}%) | "
                f"Löytyi: {found_count} | Puuttuu: {missing_count} | Yhteensä puuttuu: {total_missing}")

def run_update_missing_cards_final() -> None:
    """Pääfunktio - päivittää puuttuvat kortit"""
    start_time = time.time()
    logger.info("🔄 UPDATE MISSING CARDS - FINAL VERSION")
    logger.info("=" * 50)
    
    # Tarkista ensin onko uusia kortteja entry_count mukaan
    if not check_total_entries():
        logger.info("\n🏁 LOPETETAAN: Ei uusia kortteja entry_count mukaan!")
        return
    
    # Lataa master.json
    master_data, players = load_master_json()
    if not master_data:
        logger.error("❌ Ei voitu ladata master.json, lopetetaan")
        return
    
    # Luo URL-set nopeaa vertailua varten
    master_urls = get_master_urls(players)
    logger.info(f"📊 Master.json sisältää {len(master_urls)} uniikkia URLia")
    
    # Algoritmi: käy läpi sivuja kunnes ei löydy puuttuvia
    page = 1
    all_missing_urls = []
    total_cards_processed = 0
    
    while True:  # Continue until no more cards or 50 pages without missing cards
        logger.info(f"\n--- SIVU {page} ---")
        
        # Hae kortit tältä sivulta
        cards_urls = fetch_cards_page(page)
        
        if not cards_urls:
            logger.warning("❌ Ei löytynyt kortteja, lopetetaan.")
            break
        
        total_cards_processed += len(cards_urls)
        
        # Etsi puuttuvat URLit
        missing_urls, found_urls = find_missing_urls(cards_urls, master_urls)
        
        # Lisää puuttuvat URL:it kokonaismäärään
        all_missing_urls.extend(missing_urls)
        
        # Näytä edistyminen
        print_progress_summary(page, 999, len(found_urls), len(missing_urls), len(all_missing_urls))
        
        # Continue searching even if no missing URLs found on this page
        # because new cards might be on later pages
        # No hard limit - fetch all missing cards in one run
        
        # If we've checked 50 pages and found no missing cards, stop
        # This prevents infinite searching when all cards are already in master.json
        if page >= 50 and len(all_missing_urls) == 0:
            logger.info(f"Tarkistettu {page} sivua, ei puuttuvia kortteja. Lopetetaan hakeminen.")
            break
        
        # Siirry seuraavalle sivulle
        page += 1
        
        # Pieni viive serverin suojaksi
        time.sleep(config.page_delay)
    
    # Tallenna kaikki puuttuvat URL:it
    save_missing_urls(all_missing_urls)
    
    # Lopetussumma
    end_time = time.time()
    duration = end_time - start_time
    
    logger.info(f"\n🏁 UPDATE MISSING CARDS VALMIS!")
    logger.info(f"⏱️  Kesto: {duration:.2f} sekuntia")
    logger.info(f"📊 Yhteensä puuttuvia URL:eja: {len(all_missing_urls)}")
    logger.info(f"📄 Käsitelty sivuja: {page - 1}")
    logger.info(f"🎯 Käsitelty kortteja: {total_cards_processed}")
    
    if all_missing_urls:
        logger.info(f"\n📋 Seuraavat vaiheet:")
        logger.info(f"1. Käytä universal_country_fetcher.py hakemaan puuttuvat kortit")
        logger.info(f"2. Käytä enrich_country_xfactors.py rikastamaan X-Factor tiedot")
        logger.info(f"3. Yhdistä uudet kortit master.json:iin")
    else:
        logger.info("🎉 Kaikki kortit ovat jo tallennettuna!")

if __name__ == "__main__":
    run_update_missing_cards_final()