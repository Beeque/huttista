#!/usr/bin/env python3
"""
Selenium-pohjainen NHL HUT Builder Web Scraper
Käyttää selain-automaatiota JavaScript-pohjaisille sivuille
"""

import sqlite3
import time
import logging
import re
from typing import List, Dict, Optional
from dataclasses import dataclass
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Konfiguroi logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('selenium_nhl_scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class CardAbility:
    name: str
    ability_type: str
    description: str
    icon_url: str

@dataclass
class CardStat:
    name: str
    value: int
    category: str

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
    player_details: Dict = None

class SeleniumNHLScraper:
    def __init__(self, db_path: str = 'nhl_cards_selenium.db', headless: bool = True):
        self.base_url = 'https://nhlhutbuilder.com'
        self.db_path = db_path
        self.headless = headless
        self.driver = None
        self.init_database()
    
    def init_database(self):
        """Luo tietokanta rakenne"""
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
        
        conn.commit()
        conn.close()
        logger.info("Tietokanta alustettu onnistuneesti")
    
    def setup_driver(self):
        """Aseta Selenium driver"""
        try:
            chrome_options = Options()
            if self.headless:
                chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.implicitly_wait(10)
            logger.info("Selenium driver asetettu onnistuneesti")
            
        except Exception as e:
            logger.error(f"Virhe Selenium driverin asettamisessa: {e}")
            raise
    
    def close_driver(self):
        """Sulje Selenium driver"""
        if self.driver:
            self.driver.quit()
            self.driver = None
            logger.info("Selenium driver suljettu")
    
    def get_page_content(self, url: str) -> bool:
        """Hae sivun sisältö Selenium:lla"""
        try:
            if not self.driver:
                self.setup_driver()
            
            logger.info(f"Haetaan sivu: {url}")
            self.driver.get(url)
            
            # Odota sivun latautumista
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Lisää pieni viive
            time.sleep(3)
            return True
            
        except TimeoutException:
            logger.error(f"Timeout sivun lataamisessa: {url}")
            return False
        except Exception as e:
            logger.error(f"Virhe sivun lataamisessa {url}: {e}")
            return False
    
    def scrape_single_card(self, player_id: int) -> Optional[PlayerCard]:
        """Hae yksittäinen kortti player ID:n perusteella"""
        card_url = f"{self.base_url}/player-stats.php?id={player_id}"
        
        # Hae sivun sisältö
        if not self.get_page_content(card_url):
            return None
        
        try:
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
                abilities=[],
                stats=[],
                player_details={}
            )
            
            # Poimi tiedot sivulta
            self.extract_basic_info(card)
            self.extract_stats(card)
            self.extract_abilities(card)
            
            logger.info(f"Kortti käsitelty: {card.player_name or 'Tuntematon'} (ID: {player_id})")
            return card if card.player_name else None
            
        except Exception as e:
            logger.error(f"Virhe kortin käsittelyssä {player_id}: {e}")
            return None
    
    def extract_basic_info(self, card: PlayerCard):
        """Hae perustiedot sivulta"""
        try:
            # Hae pelaajan nimi title-tagista
            title = self.driver.title
            if title and 'NHL HUT Builder' in title:
                card.player_name = title.replace('NHL HUT Builder - ', '').replace('Player Stat Database', '').strip()
            
            # Hae sivun tekstiä
            page_text = self.driver.find_element(By.TAG_NAME, "body").text
            
            # Hae pituus
            height_match = re.search(r'(\d+)\s*(?:ft|feet|\')\s*(\d+)\s*(?:in|inches|")', page_text, re.IGNORECASE)
            if height_match:
                feet = int(height_match.group(1))
                inches = int(height_match.group(2))
                card.height = f"{feet}'{inches}\""
            
            # Hae paino
            weight_match = re.search(r'(\d+)\s*(?:lbs?|pounds?)', page_text, re.IGNORECASE)
            if weight_match:
                card.weight = int(weight_match.group(1))
            
            # Hae ikä
            age_match = re.search(r'age:\s*(\d+)', page_text, re.IGNORECASE)
            if age_match:
                card.player_details['age'] = int(age_match.group(1))
            
            # Hae kätisyys
            handedness_match = re.search(r'(left|right)[\s-]?(handed|hand)', page_text, re.IGNORECASE)
            if handedness_match:
                card.handedness = handedness_match.group(1).lower()
            
            # Hae pelipaikka
            position_match = re.search(r'(C|LW|RW|D|G|Center|Left Wing|Right Wing|Defense|Goalie)', page_text, re.IGNORECASE)
            if position_match:
                card.position = position_match.group(1).upper()
            
            # Hae joukkue
            team_match = re.search(r'team:\s*([^,\n]+)', page_text, re.IGNORECASE)
            if team_match:
                card.team = team_match.group(1).strip()
            
        except Exception as e:
            logger.error(f"Virhe perustietojen haussa: {e}")
    
    def extract_stats(self, card: PlayerCard):
        """Hae tilastot sivulta"""
        stats = []
        
        try:
            # Hae sivun tekstiä
            page_text = self.driver.find_element(By.TAG_NAME, "body").text
            
            # Etsi tilastot tekstistä
            stat_patterns = [
                r'(skating|speed|acceleration|agility|balance):\s*(\d+)',
                r'(shooting|wrist shot|slap shot|shot power|shot accuracy):\s*(\d+)',
                r'(hands|passing|puck control|deking):\s*(\d+)',
                r'(defense|checking|stick checking|faceoffs):\s*(\d+)',
                r'(physical|body checking|strength|fighting):\s*(\d+)',
                r'(goaltending|glove high|glove low|five hole|stick low):\s*(\d+)',
                r'(endurance|durability|poise):\s*(\d+)'
            ]
            
            for pattern in stat_patterns:
                matches = re.finditer(pattern, page_text, re.IGNORECASE)
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
            logger.info(f"Löytyi {len(stats)} tilastoa")
            
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
    
    def extract_abilities(self, card: PlayerCard):
        """Hae X-Factor kyvyt sivulta"""
        abilities = []
        
        try:
            # Hae sivun tekstiä
            page_text = self.driver.find_element(By.TAG_NAME, "body").text
            
            # Etsi kykyjä tekstistä
            ability_patterns = [
                r'(TRUCULENCE|ROCKET|QUICK PICK|WHEELS|ELITE EDGES|BEAUTIFUL BACKHAND|QUICK DRAW|CLOSE QUARTERS|TAPE TO TAPE|BORN LEADER|HEATSEEKER|ONE TEE|BIG RIG|UNSTOPPABLE FORCE|LIGHT THE LAMP|SAW IT OFF|ANCHOR|BUTTERFLY|LIGHTNING QUICK|POST TO POST|SPONGE|LAST STAND|X-RAY|TRIGGER MAN|THIRD EYE|BREAKAWAY BOSS|CONTORTIONIST|DEEP DIVE|EXTRA MAGNET|OVERWHELMING|PUCK ON A STRING|SHOCK AND AWE|SILVER)',
                r'(X-Factor|X Factor)',
                r'(Ability|ability)'
            ]
            
            for pattern in ability_patterns:
                matches = re.finditer(pattern, page_text, re.IGNORECASE)
                for match in matches:
                    ability_name = match.group(1).strip()
                    if len(ability_name) > 2:  # Vältä liian lyhyitä
                        abilities.append(CardAbility(
                            name=ability_name,
                            ability_type='regular',
                            description='',
                            icon_url=''
                        ))
            
            card.abilities = abilities
            logger.info(f"Löytyi {len(abilities)} kykyä")
            
        except Exception as e:
            logger.error(f"Virhe kykyjen haussa: {e}")
    
    def save_card_to_database(self, card: PlayerCard) -> Optional[int]:
        """Tallenna kortin tiedot tietokantaan"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        try:
            # Tallenna pääkortti
            c.execute('''
                INSERT OR REPLACE INTO cards 
                (player_id, player_name, image_url, card_url, overall_rating, position, team, nationality, 
                 height, weight, handedness)
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
            
            # Poista vanhat tiedot
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
                    (card_id, stat_name, stat_value, stat_category)
                    VALUES (?, ?, ?, ?)
                ''', (card_db_id, stat.name, stat.value, stat.category))
            
            conn.commit()
            logger.info(f"Kortti tallennettu: {card.player_name or 'Tuntematon'} (ID: {card.player_id})")
            return card_db_id
            
        except Exception as e:
            logger.error(f"Virhe kortin tallentamisessa: {e}")
            conn.rollback()
            return None
        finally:
            conn.close()
    
    def scrape_multiple_cards(self, player_ids: List[int]) -> int:
        """Hae useita kortteja"""
        saved_count = 0
        
        for i, player_id in enumerate(player_ids):
            try:
                logger.info(f"Käsitellään kortti {i+1}/{len(player_ids)}: ID {player_id}")
                card = self.scrape_single_card(player_id)
                
                if card:
                    card_id = self.save_card_to_database(card)
                    if card_id:
                        saved_count += 1
                        logger.info(f"Kortti {player_id} tallennettu onnistuneesti")
                    else:
                        logger.warning(f"Kortin {player_id} tallentaminen epäonnistui")
                else:
                    logger.warning(f"Korttia {player_id} ei löytynyt")
                
                # Viive seuraavan kortin välillä
                time.sleep(5)
                
            except Exception as e:
                logger.error(f"Virhe kortin {player_id} käsittelyssä: {e}")
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
    """Pääohjelma"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Selenium NHL HUT Builder Web Scraper')
    parser.add_argument('--single-card', type=int, help='Hae yksittäinen kortti player ID:n perusteella')
    parser.add_argument('--multiple-cards', nargs='+', type=int, help='Hae useita kortteja player ID:iden perusteella')
    parser.add_argument('--stats-only', action='store_true', help='Näytä vain tietokannan tilastot')
    parser.add_argument('--headless', action='store_true', default=True, help='Käytä headless-moodia')
    
    args = parser.parse_args()
    
    scraper = SeleniumNHLScraper(headless=args.headless)
    
    try:
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
        
        if args.multiple_cards:
            # Hae useita kortteja
            print(f"Haetaan {len(args.multiple_cards)} korttia")
            saved_count = scraper.scrape_multiple_cards(args.multiple_cards)
            print(f"Tallennettu {saved_count} korttia")
            return
        
        print("Käytä --help nähdäksesi käyttöohjeet")
        
    finally:
        scraper.close_driver()

if __name__ == "__main__":
    main()