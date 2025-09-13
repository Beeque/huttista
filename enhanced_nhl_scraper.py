#!/usr/bin/env python3
"""
Parannettu NHL HUT Builder Web Scraper
Kerää yksityiskohtaiset tiedot myös yksittäisiltä korttisivuilta (player-stats.php?id=XXXX)
"""

import requests
from bs4 import BeautifulSoup
import sqlite3
import time
import logging
from urllib.parse import urljoin, urlparse, parse_qs
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
        logging.FileHandler('enhanced_nhl_scraper.log'),
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
    category: str = "general"

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
    card_type: Optional[str]
    rarity: Optional[str]
    abilities: List[CardAbility]
    stats: List[CardStat]
    player_details: Dict = None

class EnhancedNHLScraper:
    def __init__(self, db_path: str = 'nhl_cards_enhanced.db'):
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
                age INTEGER,
                birth_date TEXT,
                birth_place TEXT,
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
        
        # Taulu kortin tilastoille (laajennettu)
        c.execute('''
            CREATE TABLE IF NOT EXISTS card_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                card_id INTEGER,
                stat_name TEXT,
                stat_value INTEGER,
                stat_category TEXT,
                stat_type TEXT,
                FOREIGN KEY (card_id) REFERENCES cards (id)
            )
        ''')
        
        # Taulu pelaajan ura-tiedoille
        c.execute('''
            CREATE TABLE IF NOT EXISTS player_career (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                card_id INTEGER,
                season TEXT,
                team TEXT,
                games_played INTEGER,
                goals INTEGER,
                assists INTEGER,
                points INTEGER,
                plus_minus INTEGER,
                pim INTEGER,
                FOREIGN KEY (card_id) REFERENCES cards (id)
            )
        ''')
        
        # Taulu kortin hintatiedoille (jos saatavilla)
        c.execute('''
            CREATE TABLE IF NOT EXISTS card_prices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                card_id INTEGER,
                platform TEXT,
                price_type TEXT,
                price_value INTEGER,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
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
                card_type=None,
                rarity=None,
                abilities=abilities,
                stats=[],
                player_details={}
            )
            
        except Exception as e:
            logger.error(f"Virhe kortin tietojen poiminnassa: {e}")
            return None
    
    def scrape_detailed_card_info(self, card: PlayerCard) -> PlayerCard:
        """Hae yksityiskohtaiset tiedot kortin sivulta (player-stats.php?id=XXXX)"""
        if not card.card_url:
            return card
        
        soup = self.get_page_content(card.card_url)
        if not soup:
            return card
        
        try:
            logger.info(f"Käsitellään yksityiskohtaisia tietoja kortille {card.player_id}")
            
            # Hae pelaajan nimi - useita mahdollisia paikkoja
            name_selectors = [
                'h1.player-name', 'h2.player-name', 'h1', 'h2',
                '.player-info h1', '.player-info h2', '.card-title',
                'title', '.player-title'
            ]
            
            for selector in name_selectors:
                name_element = soup.select_one(selector)
                if name_element:
                    name_text = name_element.get_text(strip=True)
                    # Poista sivun otsikko jos se sisältää "Stats" tms.
                    if 'stats' not in name_text.lower() and len(name_text) > 2:
                        card.player_name = name_text
                        break
            
            # Hae overall rating - useita mahdollisia paikkoja
            rating_selectors = [
                '.overall-rating', '.rating', '.card-rating', '.player-rating',
                '[class*="rating"]', '[class*="overall"]'
            ]
            
            for selector in rating_selectors:
                rating_element = soup.select_one(selector)
                if rating_element:
                    rating_text = rating_element.get_text(strip=True)
                    rating_match = re.search(r'(\d+)', rating_text)
                    if rating_match:
                        card.overall_rating = int(rating_match.group(1))
                        break
            
            # Hae perustiedot
            self.extract_basic_info(soup, card)
            
            # Hae tilastot
            self.extract_stats(soup, card)
            
            # Hae X-Factor kyvyt (jos ei jo haettu)
            if not card.abilities:
                self.extract_abilities(soup, card)
            
            # Hae ura-tiedot
            self.extract_career_stats(soup, card)
            
            logger.info(f"Yksityiskohtaiset tiedot haettu kortille: {card.player_name}")
            
        except Exception as e:
            logger.error(f"Virhe yksityiskohtaisten tietojen haussa kortille {card.player_id}: {e}")
        
        return card
    
    def extract_basic_info(self, soup: BeautifulSoup, card: PlayerCard):
        """Hae perustiedot kortin sivulta"""
        try:
            # Hae tekstiä joka sisältää perustietoja
            text_content = soup.get_text()
            
            # Pituus
            height_match = re.search(r'(\d+)\s*(?:ft|feet|')\s*(\d+)\s*(?:in|inches|")', text_content, re.IGNORECASE)
            if height_match:
                feet = int(height_match.group(1))
                inches = int(height_match.group(2))
                card.height = f"{feet}'{inches}\""
            
            # Paino
            weight_match = re.search(r'(\d+)\s*(?:lbs?|pounds?)', text_content, re.IGNORECASE)
            if weight_match:
                card.weight = int(weight_match.group(1))
            
            # Ikä
            age_match = re.search(r'age:\s*(\d+)', text_content, re.IGNORECASE)
            if age_match:
                card.player_details['age'] = int(age_match.group(1))
            
            # Syntymäpäivä
            birth_match = re.search(r'born:\s*([^,\n]+)', text_content, re.IGNORECASE)
            if birth_match:
                card.player_details['birth_date'] = birth_match.group(1).strip()
            
            # Syntymäpaikka
            birthplace_match = re.search(r'born[^,\n]*,\s*([^,\n]+)', text_content, re.IGNORECASE)
            if birthplace_match:
                card.player_details['birth_place'] = birthplace_match.group(1).strip()
            
            # Kätisyys
            handedness_match = re.search(r'(left|right)[\s-]?(handed|hand)', text_content, re.IGNORECASE)
            if handedness_match:
                card.handedness = handedness_match.group(1).lower()
            
            # Pelipaikka
            position_match = re.search(r'(C|LW|RW|D|G|Center|Left Wing|Right Wing|Defense|Goalie)', text_content, re.IGNORECASE)
            if position_match:
                card.position = position_match.group(1).upper()
            
            # Joukkue
            team_match = re.search(r'team:\s*([^,\n]+)', text_content, re.IGNORECASE)
            if team_match:
                card.team = team_match.group(1).strip()
            
            # Kansallisuus
            nationality_match = re.search(r'(canadian|american|swedish|finnish|russian|german|swiss|danish|norwegian|czech)', text_content, re.IGNORECASE)
            if nationality_match:
                card.nationality = nationality_match.group(1).capitalize()
            
        except Exception as e:
            logger.error(f"Virhe perustietojen haussa: {e}")
    
    def extract_stats(self, soup: BeautifulSoup, card: PlayerCard):
        """Hae tilastot kortin sivulta"""
        stats = []
        
        try:
            # Etsi tilastotaulukoita
            stat_tables = soup.find_all(['table', 'div'], class_=re.compile(r'stat|rating'))
            
            for table in stat_tables:
                # Etsi tilastorivejä
                rows = table.find_all(['tr', 'div'], class_=re.compile(r'row|stat'))
                
                for row in rows:
                    cells = row.find_all(['td', 'span', 'div'])
                    if len(cells) >= 2:
                        stat_name = cells[0].get_text(strip=True)
                        stat_value_text = cells[1].get_text(strip=True)
                        
                        # Poimi numero tilastosta
                        stat_match = re.search(r'(\d+)', stat_value_text)
                        if stat_match and len(stat_name) > 0:
                            stat_value = int(stat_match.group(1))
                            
                            # Määrittele tilaston kategoria
                            category = self.categorize_stat(stat_name)
                            
                            stats.append(CardStat(
                                name=stat_name,
                                value=stat_value,
                                category=category
                            ))
            
            # Jos ei löytynyt taulukoita, etsi tekstistä
            if not stats:
                text_content = soup.get_text()
                stat_patterns = [
                    r'(skating|speed|acceleration|agility|balance):\s*(\d+)',
                    r'(shooting|wrist shot|slap shot|shot power|shot accuracy):\s*(\d+)',
                    r'(hands|passing|puck control|deking):\s*(\d+)',
                    r'(defense|checking|stick checking|faceoffs):\s*(\d+)',
                    r'(physical|body checking|strength|fighting):\s*(\d+)',
                    r'(goaltending|glove high|glove low|five hole|stick low):\s*(\d+)'
                ]
                
                for pattern in stat_patterns:
                    matches = re.finditer(pattern, text_content, re.IGNORECASE)
                    for match in matches:
                        stat_name = match.group(1).title()
                        stat_value = int(match.group(2))
                        category = self.categorize_stat(stat_name)
                        
                        stats.append(CardStat(
                            name=stat_name,
                            value=stat_value,
                            category=category
                        ))
            
            card.stats = stats
            logger.info(f"Löytyi {len(stats)} tilastoa kortille {card.player_id}")
            
        except Exception as e:
            logger.error(f"Virhe tilastojen haussa: {e}")
    
    def categorize_stat(self, stat_name: str) -> str:
        """Määrittele tilaston kategoria"""
        stat_name_lower = stat_name.lower()
        
        if any(word in stat_name_lower for word in ['skating', 'speed', 'acceleration', 'agility', 'balance']):
            return 'skating'
        elif any(word in stat_name_lower for word in ['shooting', 'shot', 'wrist', 'slap']):
            return 'shooting'
        elif any(word in stat_name_lower for word in ['hands', 'passing', 'puck', 'deking']):
            return 'hands'
        elif any(word in stat_name_lower for word in ['defense', 'checking', 'stick', 'faceoff']):
            return 'defense'
        elif any(word in stat_name_lower for word in ['physical', 'body', 'strength', 'fighting']):
            return 'physical'
        elif any(word in stat_name_lower for word in ['goaltending', 'glove', 'five hole', 'stick']):
            return 'goaltending'
        else:
            return 'general'
    
    def extract_abilities(self, soup: BeautifulSoup, card: PlayerCard):
        """Hae X-Factor kyvyt sivulta"""
        abilities = []
        
        try:
            # Etsi kyky-elementtejä
            ability_elements = soup.find_all(['div', 'span'], class_=re.compile(r'ability|x-factor|xfactor'))
            
            for element in ability_elements:
                ability_name = element.get('data-xfactor_name', '') or element.get_text(strip=True)
                if not ability_name:
                    continue
                
                ability_type = 'selected' if 'selected' in element.get('class', []) else 'regular'
                description = element.get('title', '') or element.get('data-description', '')
                
                # Puhdista kuvaus
                description = re.sub(r'<[^>]+>', '', description)
                description = description.replace('&lt;', '<').replace('&gt;', '>')
                
                # Hae ikoni
                icon_url = ''
                icon_img = element.find('img')
                if icon_img:
                    icon_url = urljoin(self.base_url, icon_img.get('src', ''))
                
                abilities.append(CardAbility(
                    name=ability_name,
                    ability_type=ability_type,
                    description=description,
                    icon_url=icon_url
                ))
            
            if abilities:
                card.abilities = abilities
                logger.info(f"Löytyi {len(abilities)} kykyä kortille {card.player_id}")
            
        except Exception as e:
            logger.error(f"Virhe kykyjen haussa: {e}")
    
    def extract_career_stats(self, soup: BeautifulSoup, card: PlayerCard):
        """Hae ura-tilastot sivulta"""
        try:
            # Tämä voidaan laajentaa hakemaan ura-tilastoja jos ne ovat saatavilla
            # Tällä hetkellä tallennetaan vain perustiedot
            pass
        except Exception as e:
            logger.error(f"Virhe ura-tilastojen haussa: {e}")
    
    def save_card_to_database(self, card: PlayerCard) -> Optional[int]:
        """Tallenna kortin tiedot tietokantaan"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        try:
            # Tallenna pääkortti
            c.execute('''
                INSERT OR REPLACE INTO cards 
                (player_id, player_name, image_url, card_url, overall_rating, position, team, nationality, 
                 height, weight, handedness, age, birth_date, birth_place)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                card.handedness,
                card.player_details.get('age') if card.player_details else None,
                card.player_details.get('birth_date') if card.player_details else None,
                card.player_details.get('birth_place') if card.player_details else None
            ))
            
            card_db_id = c.lastrowid
            
            # Poista vanhat tiedot
            c.execute('DELETE FROM xfactor_abilities WHERE card_id = ?', (card_db_id,))
            c.execute('DELETE FROM card_stats WHERE card_id = ?', (card_db_id,))
            c.execute('DELETE FROM player_career WHERE card_id = ?', (card_db_id,))
            
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
                    (card_id, stat_name, stat_value, stat_category, stat_type)
                    VALUES (?, ?, ?, ?, ?)
                ''', (card_db_id, stat.name, stat.value, stat.category, 'detailed'))
            
            conn.commit()
            logger.info(f"Kortti tallennettu: {card.player_name or 'Tuntematon'} (ID: {card.player_id})")
            return card_db_id
            
        except Exception as e:
            logger.error(f"Virhe kortin tallentamisessa: {e}")
            conn.rollback()
            return None
        finally:
            conn.close()
    
    def scrape_single_card(self, player_id: int) -> Optional[PlayerCard]:
        """Hae yksittäinen kortti player ID:n perusteella"""
        card_url = f"{self.base_url}/player-stats.php?id={player_id}"
        
        # Luo peruskortti
        card = PlayerCard(
            player_id=player_id,
            player_name=None,
            image_url=None,
            card_url=card_url,
            overall_rating=None,
            position=None,
            team=None,
            nationality=None,
            height=None,
            weight=None,
            handedness=None,
            card_type=None,
            rarity=None,
            abilities=[],
            stats=[],
            player_details={}
        )
        
        # Hae yksityiskohtaiset tiedot
        card = self.scrape_detailed_card_info(card)
        
        return card if card.player_name else None
    
    def scrape_cards(self, max_cards: int = None, detailed_info: bool = True) -> int:
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
                
                # Hae yksityiskohtaiset tiedot
                if detailed_info:
                    card = self.scrape_detailed_card_info(card)
                
                card_id = self.save_card_to_database(card)
                if card_id:
                    saved_count += 1
                
                # Näytä edistyminen
                if (i + 1) % 5 == 0:  # Pienempi intervalli koska yksityiskohtaiset tiedot vievät aikaa
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
        
        # Tilastokategoriat
        c.execute('''
            SELECT stat_category, COUNT(*) as count 
            FROM card_stats 
            GROUP BY stat_category 
            ORDER BY count DESC
        ''')
        stats['stat_categories'] = c.fetchall()
        
        conn.close()
        return stats

def main():
    """Pääohjelma komentoriviparametreilla"""
    parser = argparse.ArgumentParser(description='Enhanced NHL HUT Builder Web Scraper')
    parser.add_argument('--max-cards', type=int, help='Maksimimäärä kerättäviä kortteja')
    parser.add_argument('--single-card', type=int, help='Hae yksittäinen kortti player ID:n perusteella')
    parser.add_argument('--stats-only', action='store_true', help='Näytä vain tietokannan tilastot')
    
    args = parser.parse_args()
    
    scraper = EnhancedNHLScraper()
    
    if args.stats_only:
        # Näytä vain tilastot
        stats = scraper.get_database_stats()
        print("\n=== TIETOKANNAN TILASTOT ===")
        print(f"Tallennettuja kortteja: {stats['total_cards']}")
        print(f"Yhteensä kyvyjä: {stats['total_abilities']}")
        print(f"Yhteensä tilastoja: {stats['total_stats']}")
        
        if stats['stat_categories']:
            print("\nTilastokategoriat:")
            for category, count in stats['stat_categories']:
                print(f"  {category}: {count}")
        
        if stats['top_abilities']:
            print("\nYleisimmät X-Factor kyvyt:")
            for ability, count in stats['top_abilities']:
                print(f"  {ability}: {count}")
        
        if stats['top_ratings']:
            print("\nKorkeimmat ratingit:")
            for name, rating in stats['top_ratings']:
                print(f"  {name}: {rating}")
        
        return
    
    if args.single_card:
        # Hae yksittäinen kortti
        print(f"Haetaan kortti ID:llä {args.single_card}")
        card = scraper.scrape_single_card(args.single_card)
        if card:
            print(f"Kortti löytyi: {card.player_name}")
            card_id = scraper.save_card_to_database(card)
            if card_id:
                print(f"Kortti tallennettu tietokantaan (ID: {card_id})")
        else:
            print("Korttia ei löytynyt")
        return
    
    # Kerää kortit
    cards_saved = scraper.scrape_cards(max_cards=args.max_cards, detailed_info=True)
    
    # Näytä tilastot
    stats = scraper.get_database_stats()
    print("\n=== KERÄYSTULOKSET ===")
    print(f"Tallennettuja kortteja: {stats['total_cards']}")
    print(f"Yhteensä kyvyjä: {stats['total_abilities']}")
    print(f"Yhteensä tilastoja: {stats['total_stats']}")

if __name__ == "__main__":
    main()