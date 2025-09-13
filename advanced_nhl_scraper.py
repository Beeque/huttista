#!/usr/bin/env python3
"""
Edistynyt NHL HUT Builder Web Scraper
Kerää yksityiskohtaiset NHL korttien tiedot ja tilastot
"""

import requests
from bs4 import BeautifulSoup
import sqlite3
import time
import logging
from urllib.parse import urljoin, urlparse
import re
from typing import List, Dict, Optional
import json
from dataclasses import dataclass
import argparse

# Konfiguroi logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('advanced_nhl_scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class CardAbility:
    name: str
    ability_type: str  # 'selected' or 'regular'
    description: str
    icon_url: str

@dataclass
class CardStat:
    name: str
    value: int

@dataclass
class PlayerCard:
    player_id: int
    player_name: Optional[str]
    image_url: Optional[str]
    card_url: Optional[str]
    overall_rating: Optional[int]
    position: Optional[str]
    team: Optional[str]
    nationality: Optional[str]
    height: Optional[str]
    weight: Optional[int]
    handedness: Optional[str]
    abilities: List[CardAbility]
    stats: List[CardStat]

class AdvancedNHLScraper:
    def __init__(self, db_path: str = 'nhl_cards_advanced.db'):
        self.base_url = 'https://nhlhutbuilder.com'
        self.cards_url = 'https://nhlhutbuilder.com/cards.php'
        self.db_path = db_path
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        self.init_database()
    
    def init_database(self):
        """Luo laajennettu tietokanta rakenne"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Päätaulu korttien tiedoille
        c.execute('''
            CREATE TABLE IF NOT EXISTS cards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id INTEGER UNIQUE,
                player_name TEXT,
                image_url TEXT,
                card_url TEXT,
                overall_rating INTEGER,
                position TEXT,
                team TEXT,
                nationality TEXT,
                height TEXT,
                weight INTEGER,
                handedness TEXT,
                card_type TEXT,
                rarity TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Taulu X-Factor kyvyille
        c.execute('''
            CREATE TABLE IF NOT EXISTS xfactor_abilities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                card_id INTEGER,
                ability_name TEXT,
                ability_type TEXT,
                description TEXT,
                icon_url TEXT,
                is_selected BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (card_id) REFERENCES cards (id)
            )
        ''')
        
        # Taulu kortin tilastoille
        c.execute('''
            CREATE TABLE IF NOT EXISTS card_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                card_id INTEGER,
                stat_name TEXT,
                stat_value INTEGER,
                stat_category TEXT,
                FOREIGN KEY (card_id) REFERENCES cards (id)
            )
        ''')
        
        # Taulu pelaajan perustiedoille
        c.execute('''
            CREATE TABLE IF NOT EXISTS player_details (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                card_id INTEGER,
                birth_date TEXT,
                draft_year INTEGER,
                draft_round INTEGER,
                draft_pick INTEGER,
                contract_value TEXT,
                FOREIGN KEY (card_id) REFERENCES cards (id)
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Laajennettu tietokanta alustettu onnistuneesti")
    
    def get_page_content(self, url: str, retries: int = 3) -> Optional[BeautifulSoup]:
        """Hae sivun sisältö virheenkäsittelyllä"""
        for attempt in range(retries):
            try:
                logger.info(f"Haetaan sivu: {url} (yritys {attempt + 1}/{retries})")
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                
                # Tarkista että saimme HTML-sisältöä
                if 'text/html' not in response.headers.get('content-type', ''):
                    logger.warning(f"Ei-HTML sisältö saatu sivulta: {url}")
                    continue
                
                # Lisää pieni viive rate limitingin välttämiseksi
                time.sleep(2)
                
                return BeautifulSoup(response.text, 'html.parser')
                
            except requests.RequestException as e:
                logger.warning(f"Virhe sivun lataamisessa {url} (yritys {attempt + 1}): {e}")
                if attempt < retries - 1:
                    time.sleep(5)  # Odota pidemmin virheiden jälkeen
                else:
                    logger.error(f"Kaikki yritykset epäonnistuivat sivulle: {url}")
        
        return None
    
    def extract_card_from_list(self, card_element) -> Optional[PlayerCard]:
        """Poimi kortin perustiedot listasivulta"""
        try:
            # Hae pelaajan linkki ja ID
            player_link = card_element.find('a', class_='advanced-stats view_player')
            if not player_link:
                return None
            
            player_id = player_link.get('id')
            if not player_id:
                return None
            
            player_id = int(player_id)
            card_url = urljoin(self.base_url, player_link.get('href', ''))
            
            # Hae kortin kuva
            img_tag = player_link.find('img', class_='other_card_art')
            image_url = urljoin(self.base_url, img_tag.get('src', '')) if img_tag else None
            
            # Hae X-Factor kyvyt
            abilities = []
            xfactor_divs = card_element.find_all('div', class_='abi')
            
            for ability_div in xfactor_divs:
                ability_name = ability_div.get('data-xfactor_name', '')
                if not ability_name:
                    continue
                
                ability_type = 'selected' if 'selected' in ability_div.get('class', []) else 'regular'
                description = ability_div.get('title', '')
                
                # Puhdista HTML-tagit kuvauksesta
                description = re.sub(r'<[^>]+>', '', description)
                description = description.replace('&lt;', '<').replace('&gt;', '>')
                
                icon_url = ''
                icon_img = ability_div.find('img')
                if icon_img:
                    icon_url = urljoin(self.base_url, icon_img.get('src', ''))
                
                abilities.append(CardAbility(
                    name=ability_name,
                    ability_type=ability_type,
                    description=description,
                    icon_url=icon_url
                ))
            
            return PlayerCard(
                player_id=player_id,
                player_name=None,  # Haetaan myöhemmin yksityiskohtaisilta sivuilta
                image_url=image_url,
                card_url=card_url,
                overall_rating=None,
                position=None,
                team=None,
                nationality=None,
                height=None,
                weight=None,
                handedness=None,
                abilities=abilities,
                stats=[]
            )
            
        except Exception as e:
            logger.error(f"Virhe kortin tietojen poiminnassa: {e}")
            return None
    
    def scrape_detailed_card_info(self, card: PlayerCard) -> PlayerCard:
        """Hae yksityiskohtaiset tiedot kortin sivulta"""
        if not card.card_url:
            return card
        
        soup = self.get_page_content(card.card_url)
        if not soup:
            return card
        
        try:
            # Hae pelaajan nimi
            name_element = soup.find('h1') or soup.find('h2') or soup.find('div', class_='player-name')
            if name_element:
                card.player_name = name_element.get_text(strip=True)
            
            # Hae overall rating
            rating_element = soup.find('span', class_='overall-rating') or soup.find('div', class_='rating')
            if rating_element:
                rating_text = rating_element.get_text(strip=True)
                rating_match = re.search(r'(\d+)', rating_text)
                if rating_match:
                    card.overall_rating = int(rating_match.group(1))
            
            # Hae tilastot
            stats = []
            stat_elements = soup.find_all(['div', 'span'], class_=re.compile(r'stat|rating'))
            for stat_element in stat_elements:
                stat_text = stat_element.get_text(strip=True)
                # Yritä poimia stat-nimi ja arvo
                stat_match = re.search(r'([A-Za-z\s]+):?\s*(\d+)', stat_text)
                if stat_match:
                    stat_name = stat_match.group(1).strip()
                    stat_value = int(stat_match.group(2))
                    stats.append(CardStat(name=stat_name, value=stat_value))
            
            card.stats = stats
            
            logger.info(f"Yksityiskohtaiset tiedot haettu kortille: {card.player_name}")
            
        except Exception as e:
            logger.error(f"Virhe yksityiskohtaisten tietojen haussa kortille {card.player_id}: {e}")
        
        return card
    
    def save_card_to_database(self, card: PlayerCard) -> Optional[int]:
        """Tallenna kortin tiedot tietokantaan"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        try:
            # Tallenna pääkortti
            c.execute('''
                INSERT OR REPLACE INTO cards 
                (player_id, player_name, image_url, card_url, overall_rating, position, team, nationality, height, weight, handedness)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                card.player_id,
                card.player_name,
                card.image_url,
                card.card_url,
                card.overall_rating,
                card.position,
                card.team,
                card.nationality,
                card.height,
                card.weight,
                card.handedness
            ))
            
            card_db_id = c.lastrowid
            
            # Poista vanhat kyvyt ja tilastot
            c.execute('DELETE FROM xfactor_abilities WHERE card_id = ?', (card_db_id,))
            c.execute('DELETE FROM card_stats WHERE card_id = ?', (card_db_id,))
            
            # Tallenna X-Factor kyvyt
            for ability in card.abilities:
                c.execute('''
                    INSERT INTO xfactor_abilities 
                    (card_id, ability_name, ability_type, description, icon_url, is_selected)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    card_db_id,
                    ability.name,
                    ability.ability_type,
                    ability.description,
                    ability.icon_url,
                    ability.ability_type == 'selected'
                ))
            
            # Tallenna tilastot
            for stat in card.stats:
                c.execute('''
                    INSERT INTO card_stats 
                    (card_id, stat_name, stat_value)
                    VALUES (?, ?, ?)
                ''', (card_db_id, stat.name, stat.value))
            
            conn.commit()
            logger.info(f"Kortti tallennettu: {card.player_name or 'Tuntematon'} (ID: {card.player_id})")
            return card_db_id
            
        except Exception as e:
            logger.error(f"Virhe kortin tallentamisessa: {e}")
            conn.rollback()
            return None
        finally:
            conn.close()
    
    def scrape_cards(self, max_cards: int = None, detailed_info: bool = False) -> int:
        """Pääfunktio korttien keräämiseen"""
        logger.info("Aloitetaan NHL korttien kerääminen")
        
        soup = self.get_page_content(self.cards_url)
        if not soup:
            logger.error("Sivun lataus epäonnistui")
            return 0
        
        # Etsi kaikki korttielementit
        card_elements = soup.find_all('div', class_='other_card_container')
        logger.info(f"Löytyi {len(card_elements)} korttia")
        
        saved_count = 0
        
        for i, card_element in enumerate(card_elements):
            if max_cards and i >= max_cards:
                break
                
            try:
                card = self.extract_card_from_list(card_element)
                if not card:
                    continue
                
                # Hae yksityiskohtaiset tiedot jos pyydetty
                if detailed_info:
                    card = self.scrape_detailed_card_info(card)
                
                card_id = self.save_card_to_database(card)
                if card_id:
                    saved_count += 1
                
                # Näytä edistyminen
                if (i + 1) % 10 == 0:
                    logger.info(f"Käsitelty {i + 1}/{len(card_elements)} korttia")
                    
            except Exception as e:
                logger.error(f"Virhe kortin käsittelyssä {i + 1}: {e}")
                continue
        
        logger.info(f"Keräys valmis. Tallennettu {saved_count} korttia")
        return saved_count
    
    def export_to_json(self, output_file: str = 'nhl_cards.json'):
        """Vie tietokannan sisältö JSON-muotoon"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Hae kaikki kortit
        c.execute('''
            SELECT c.*, 
                   GROUP_CONCAT(xa.ability_name) as abilities,
                   GROUP_CONCAT(cs.stat_name || ':' || cs.stat_value) as stats
            FROM cards c
            LEFT JOIN xfactor_abilities xa ON c.id = xa.card_id
            LEFT JOIN card_stats cs ON c.id = cs.card_id
            GROUP BY c.id
        ''')
        
        cards_data = []
        for row in c.fetchall():
            card_data = {
                'player_id': row[1],
                'player_name': row[2],
                'image_url': row[3],
                'card_url': row[4],
                'overall_rating': row[5],
                'position': row[6],
                'team': row[7],
                'nationality': row[8],
                'height': row[9],
                'weight': row[10],
                'handedness': row[11],
                'abilities': row[12].split(',') if row[12] else [],
                'stats': dict(item.split(':') for item in row[13].split(',')) if row[13] else {}
            }
            cards_data.append(card_data)
        
        conn.close()
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(cards_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Tiedot vietiin tiedostoon: {output_file}")
    
    def get_database_stats(self) -> Dict:
        """Hae tietokannan tilastot"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        stats = {}
        
        # Korttien määrä
        c.execute('SELECT COUNT(*) FROM cards')
        stats['total_cards'] = c.fetchone()[0]
        
        # X-Factor kyvyjen määrä
        c.execute('SELECT COUNT(*) FROM xfactor_abilities')
        stats['total_abilities'] = c.fetchone()[0]
        
        # Tilastojen määrä
        c.execute('SELECT COUNT(*) FROM card_stats')
        stats['total_stats'] = c.fetchone()[0]
        
        # Yleisimmät kyvyt
        c.execute('''
            SELECT ability_name, COUNT(*) as count 
            FROM xfactor_abilities 
            GROUP BY ability_name 
            ORDER BY count DESC 
            LIMIT 10
        ''')
        stats['top_abilities'] = c.fetchall()
        
        # Korkeimmat ratingit
        c.execute('''
            SELECT player_name, overall_rating 
            FROM cards 
            WHERE overall_rating IS NOT NULL 
            ORDER BY overall_rating DESC 
            LIMIT 10
        ''')
        stats['top_ratings'] = c.fetchall()
        
        conn.close()
        return stats

def main():
    """Pääohjelma komentoriviparametreilla"""
    parser = argparse.ArgumentParser(description='NHL HUT Builder Web Scraper')
    parser.add_argument('--max-cards', type=int, help='Maksimimäärä kerättäviä kortteja')
    parser.add_argument('--detailed', action='store_true', help='Hae yksityiskohtaiset tiedot jokaiselta kortin sivulta')
    parser.add_argument('--export-json', type=str, help='Vie tiedot JSON-tiedostoon')
    parser.add_argument('--stats-only', action='store_true', help='Näytä vain tietokannan tilastot')
    
    args = parser.parse_args()
    
    scraper = AdvancedNHLScraper()
    
    if args.stats_only:
        # Näytä vain tilastot
        stats = scraper.get_database_stats()
        print("\n=== TIETOKANNAN TILASTOT ===")
        print(f"Tallennettuja kortteja: {stats['total_cards']}")
        print(f"Yhteensä kyvyjä: {stats['total_abilities']}")
        print(f"Yhteensä tilastoja: {stats['total_stats']}")
        
        if stats['top_abilities']:
            print("\nYleisimmät X-Factor kyvyt:")
            for ability, count in stats['top_abilities']:
                print(f"  {ability}: {count}")
        
        if stats['top_ratings']:
            print("\nKorkeimmat ratingit:")
            for name, rating in stats['top_ratings']:
                print(f"  {name}: {rating}")
        
        return
    
    # Kerää kortit
    cards_saved = scraper.scrape_cards(
        max_cards=args.max_cards,
        detailed_info=args.detailed
    )
    
    # Näytä tilastot
    stats = scraper.get_database_stats()
    print("\n=== KERÄYSTULOKSET ===")
    print(f"Tallennettuja kortteja: {stats['total_cards']}")
    print(f"Yhteensä kyvyjä: {stats['total_abilities']}")
    print(f"Yhteensä tilastoja: {stats['total_stats']}")
    
    # Vie JSON:ään jos pyydetty
    if args.export_json:
        scraper.export_to_json(args.export_json)

if __name__ == "__main__":
    main()