#!/usr/bin/env python3
"""
NHL HUT Builder Web Scraper
Kerää NHL korttien tiedot osoitteesta https://nhlhutbuilder.com/cards.php
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

# Konfiguroi logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('nhl_scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class NHLScraper:
    def __init__(self, db_path: str = 'nhl_cards.db'):
        self.base_url = 'https://nhlhutbuilder.com'
        self.cards_url = 'https://nhlhutbuilder.com/cards.php'
        self.db_path = db_path
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Luo tietokanta ja taulut
        self.init_database()
    
    def init_database(self):
        """Luo tietokanta ja tarvittavat taulut"""
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
                FOREIGN KEY (card_id) REFERENCES cards (id)
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Tietokanta alustettu onnistuneesti")
    
    def get_page_content(self, url: str) -> Optional[BeautifulSoup]:
        """Hae sivun sisältö"""
        try:
            logger.info(f"Haetaan sivu: {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            # Lisää pieni viive rate limitingin välttämiseksi
            time.sleep(1)
            
            return BeautifulSoup(response.text, 'html.parser')
        except requests.RequestException as e:
            logger.error(f"Virhe sivun lataamisessa {url}: {e}")
            return None
    
    def extract_card_data(self, card_element) -> Dict:
        """Poimi kortin tiedot HTML-elementistä"""
        card_data = {}
        
        try:
            # Hae pelaajan linkki ja ID
            player_link = card_element.find('a', class_='advanced-stats view_player')
            if player_link:
                player_id = player_link.get('id')
                card_data['player_id'] = int(player_id) if player_id else None
                card_data['card_url'] = urljoin(self.base_url, player_link.get('href', ''))
                
                # Hae kortin kuva
                img_tag = player_link.find('img', class_='other_card_art')
                if img_tag:
                    card_data['image_url'] = urljoin(self.base_url, img_tag.get('src', ''))
            
            # Hae X-Factor kyvyt
            xfactor_divs = card_element.find_all('div', class_='abi')
            abilities = []
            
            for ability_div in xfactor_divs:
                ability_data = {
                    'name': ability_div.get('data-xfactor_name', ''),
                    'type': 'selected' if 'selected' in ability_div.get('class', []) else 'regular',
                    'description': ability_div.get('title', ''),
                    'icon_url': ''
                }
                
                # Hae kyvyn ikoni
                icon_img = ability_div.find('img')
                if icon_img:
                    ability_data['icon_url'] = urljoin(self.base_url, icon_img.get('src', ''))
                
                abilities.append(ability_data)
            
            card_data['abilities'] = abilities
            
            # Yritä hakea lisätietoja kortin kuvasta tai muista elementeistä
            card_data['player_name'] = self.extract_player_name(card_element)
            card_data['overall_rating'] = self.extract_overall_rating(card_element)
            
        except Exception as e:
            logger.error(f"Virhe kortin tietojen poiminnassa: {e}")
        
        return card_data
    
    def extract_player_name(self, card_element) -> Optional[str]:
        """Yritä poimia pelaajan nimi kortin elementistä"""
        # Tämä voi tarvita säätöä sivun rakenteen mukaan
        # Voit yrittää erilaisia selektoreita
        name_element = card_element.find('span', class_='player-name')
        if not name_element:
            name_element = card_element.find('div', class_='player-name')
        if not name_element:
            name_element = card_element.find('h3')
        
        return name_element.get_text(strip=True) if name_element else None
    
    def extract_overall_rating(self, card_element) -> Optional[int]:
        """Yritä poimia kortin kokonaisarvosana"""
        # Etsi rating-elementti
        rating_element = card_element.find('span', class_='rating')
        if not rating_element:
            rating_element = card_element.find('div', class_='rating')
        
        if rating_element:
            rating_text = rating_element.get_text(strip=True)
            # Poimi numero rating-tekstistä
            rating_match = re.search(r'(\d+)', rating_text)
            if rating_match:
                return int(rating_match.group(1))
        
        return None
    
    def save_card_to_database(self, card_data: Dict) -> Optional[int]:
        """Tallenna kortin tiedot tietokantaan"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        try:
            # Tallenna pääkortti
            c.execute('''
                INSERT OR REPLACE INTO cards 
                (player_id, player_name, image_url, card_url, overall_rating)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                card_data.get('player_id'),
                card_data.get('player_name'),
                card_data.get('image_url'),
                card_data.get('card_url'),
                card_data.get('overall_rating')
            ))
            
            card_db_id = c.lastrowid
            
            # Tallenna X-Factor kyvyt
            for ability in card_data.get('abilities', []):
                c.execute('''
                    INSERT INTO xfactor_abilities 
                    (card_id, ability_name, ability_type, description, icon_url)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    card_db_id,
                    ability.get('name'),
                    ability.get('type'),
                    ability.get('description'),
                    ability.get('icon_url')
                ))
            
            conn.commit()
            logger.info(f"Kortti tallennettu: {card_data.get('player_name', 'Tuntematon')} (ID: {card_data.get('player_id')})")
            return card_db_id
            
        except Exception as e:
            logger.error(f"Virhe kortin tallentamisessa: {e}")
            conn.rollback()
            return None
        finally:
            conn.close()
    
    def scrape_cards(self, max_cards: int = None) -> int:
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
                card_data = self.extract_card_data(card_element)
                if card_data.get('player_id'):
                    card_id = self.save_card_to_database(card_data)
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
        
        # Yleisimmät kyvyt
        c.execute('''
            SELECT ability_name, COUNT(*) as count 
            FROM xfactor_abilities 
            GROUP BY ability_name 
            ORDER BY count DESC 
            LIMIT 10
        ''')
        stats['top_abilities'] = c.fetchall()
        
        conn.close()
        return stats

def main():
    """Pääohjelma"""
    scraper = NHLScraper()
    
    # Kerää kortit (rajoita määrää testausta varten)
    cards_saved = scraper.scrape_cards(max_cards=50)  # Poista max_cards testauksen jälkeen
    
    # Näytä tilastot
    stats = scraper.get_database_stats()
    print("\n=== KERÄYSTULOKSET ===")
    print(f"Tallennettuja kortteja: {stats['total_cards']}")
    print(f"Yhteensä kyvyjä: {stats['total_abilities']}")
    
    if stats['top_abilities']:
        print("\nYleisimmät X-Factor kyvyt:")
        for ability, count in stats['top_abilities']:
            print(f"  {ability}: {count}")

if __name__ == "__main__":
    main()