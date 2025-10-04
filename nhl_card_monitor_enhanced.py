#!/usr/bin/env python3
"""
NHL Card Monitor - Enhanced Version with Auto-Add to JSON
Automaattinen korttien seuranta ja lisäys master.json:iin
"""

import time
import json
import requests
from bs4 import BeautifulSoup
import logging
from datetime import datetime
import os
import sys
import threading
import re
from typing import List, Dict, Optional, Set
from urllib.parse import urlparse, parse_qs

# Configure console encoding for Windows
if sys.platform == "win32":
    try:
        import codecs
        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
        sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())
    except:
        pass

class NHLCardMonitorEnhanced:
    def __init__(self):
        self.monitoring = False
        self.monitor_thread = None
        self.last_check = None
        self.master_data = None
        self.master_urls = set()
        self.new_cards_data = []
        
        # Configuration
        self.find_cards_url = "https://nhlhutbuilder.com/php/find_cards.php"
        self.timeout = 30
        self.retry_count = 3
        self.retry_delay = 1.0
        self.page_delay = 1.0
        self.max_pages = 10
        self.limit_per_page = 40
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': 'https://nhlhutbuilder.com/cards.php',
        }
        
        # Setup logging
        self.setup_logging()
        
    def setup_logging(self):
        """Setup logging for the application with Windows compatibility"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('nhl_monitor_enhanced.log', encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def log_message(self, message, level="INFO"):
        """Log message with timestamp (Windows-safe)"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"
        
        # Use simple text instead of emojis for Windows compatibility
        if level == "INFO":
            self.logger.info(formatted_message)
        elif level == "WARNING":
            self.logger.warning(f"WARNING: {formatted_message}")
        elif level == "ERROR":
            self.logger.error(f"ERROR: {formatted_message}")
        elif level == "SUCCESS":
            self.logger.info(f"SUCCESS: {formatted_message}")
        elif level == "X-FACTOR":
            self.logger.info(f"X-FACTOR: {formatted_message}")
        elif level == "JSON":
            self.logger.info(f"JSON: {formatted_message}")
            
    def print_banner(self):
        """Print application banner (Windows-safe)"""
        print("=" * 60)
        print("NHL CARD MONITOR - ENHANCED VERSION")
        print("=" * 60)
        print("Automaattinen korttien seuranta ja lisays master.json:iin")
        print("=" * 60)
        
    def print_menu(self):
        """Print main menu (Windows-safe)"""
        print("\nVALIKKO:")
        print("1. [SEARCH] Hae uusia kortteja")
        print("2. [ADD] Lisaa uudet kortit master.json:iin")
        print("3. [START] Aloita automaattinen seuranta")
        print("4. [STOP]  Pysayta seuranta")
        print("5. [ENRICH] Rikasta X-Factor tiedot")
        print("6. [RELOAD] Lataa master.json uudelleen")
        print("7. [STATS] Nayta tilastot")
        print("8. [EXIT]  Lopeta")
        print("-" * 40)
        
    def make_request_with_retry(self, url: str, data: Dict, headers: Dict, timeout: int = None) -> Optional[requests.Response]:
        """Make HTTP request with retry logic"""
        timeout = timeout or self.timeout
        
        for attempt in range(self.retry_count):
            try:
                response = requests.post(url, data=data, headers=headers, timeout=timeout)
                response.raise_for_status()
                return response
            except requests.exceptions.RequestException as e:
                self.logger.warning(f"Request attempt {attempt + 1}/{self.retry_count} failed: {e}")
                if attempt < self.retry_count - 1:
                    time.sleep(self.retry_delay * (attempt + 1))  # Exponential backoff
                else:
                    self.logger.error(f"All {self.retry_count} request attempts failed")
                    return None
        
    def check_total_entries(self) -> bool:
        """Check if there are new cards by comparing entry_count with master.json"""
        self.log_message("Tarkistetaan onko uusia kortteja entry_count mukaan...", "INFO")
        
        data = {
            'limit': self.limit_per_page,
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
        
        response = self.make_request_with_retry(self.find_cards_url, data, self.headers)
        if not response:
            self.log_message("Failed to fetch cards data for entry count check", "ERROR")
            return True  # If we can't check, assume there are new cards
        
        try:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find entry_count element
            entry_count_div = soup.find('div', id='entry_count')
            if not entry_count_div:
                self.log_message("Ei loytynyt entry_count elementtia", "WARNING")
                return True  # If not found, continue search
            
            entry_text = entry_count_div.get_text().strip()
            self.log_message(f"Entry count teksti: '{entry_text}'", "INFO")
            
            # Parse total count (e.g. "Showing 1 to 40 of 2536 entries")
            match = re.search(r'of (\d+) entries', entry_text)
            if not match:
                self.log_message("Ei voitu parsia entry_count maaraa", "WARNING")
                return True  # If can't parse, continue search
            
            total_entries = int(match.group(1))
            self.log_message(f"Sivuston kokonaismaara: {total_entries} korttia", "INFO")
            
            # Load master.json and compare
            try:
                with open('master.json', 'r', encoding='utf-8') as f:
                    master_data = json.load(f)
                master_count = len(master_data['players'])
                self.log_message(f"Master.json maara: {master_count} pelaajaa", "INFO")
                
                if total_entries == master_count:
                    self.log_message("Maarat tasmaavat! Ei uusia kortteja.", "SUCCESS")
                    return False  # No new cards
                else:
                    new_cards = total_entries - master_count
                    self.log_message(f"Maarat eivat tasmaa! Uusia kortteja: {new_cards}", "SUCCESS")
                    return True   # There are new cards
                    
            except Exception as e:
                self.log_message(f"Virhe master.json:n lukemisessa: {e}", "ERROR")
                return True  # If can't read, continue search
                
        except Exception as e:
            self.log_message(f"Virhe entry_count tarkistuksessa: {e}", "ERROR")
            return True  # If error, continue search
    
    def fetch_cards_page(self, page_number: int = 1, limit: int = None) -> List[str]:
        """Fetch cards from cards.php page"""
        limit = limit or self.limit_per_page
        self.log_message(f"Haetaan sivu {page_number} ({limit} korttia)...", "INFO")
        
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
        
        response = self.make_request_with_retry(self.find_cards_url, data, self.headers)
        if not response:
            self.log_message(f"Virhe sivun {page_number} hakemisessa", "ERROR")
            return []
        
        try:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find other_card_container divs
            card_containers = soup.find_all('div', class_='other_card_container')
            
            # Collect URLs
            urls = []
            for container in card_containers:
                # Find a element
                link = container.find('a', href=True)
                if link:
                    href = link.get('href')
                    if href:
                        full_url = f'https://nhlhutbuilder.com/{href}'
                        urls.append(full_url)
            
            self.log_message(f"Loydetiin {len(urls)} URLia sivulta {page_number}", "SUCCESS")
            return urls
            
        except Exception as e:
            self.log_message(f"Virhe sivun {page_number} hakemisessa: {e}", "ERROR")
            return []
    
    def load_master_data(self) -> bool:
        """Load master.json data"""
        try:
            self.log_message("Ladataan master.json...", "INFO")
            with open('master.json', 'r', encoding='utf-8') as f:
                self.master_data = json.load(f)
            players = self.master_data.get('players', [])
            self.master_urls = set()
            for player in players:
                url = player.get('url')
                if url:
                    self.master_urls.add(url)
            self.log_message(f"Ladattu {len(players)} pelaajaa master.json:sta", "SUCCESS")
            return True
        except Exception as e:
            self.log_message(f"Virhe master.json:n latauksessa: {e}", "ERROR")
            return False
            
    def find_missing_urls(self, cards_urls: List[str], master_urls: Set[str]) -> tuple:
        """Find missing URLs"""
        missing_urls = []
        found_urls = []
        
        for url in cards_urls:
            if url in master_urls:
                found_urls.append(url)
            else:
                missing_urls.append(url)
        
        return missing_urls, found_urls
            
    def find_cards_manual(self):
        """Manual card finding"""
        if not self.master_data:
            self.log_message("Lataa ensin master.json!", "ERROR")
            return
            
        self.log_message("Aloitetaan manuaalinen korttien haku...", "INFO")
        
        # Check if there are new cards
        if not self.check_total_entries():
            self.log_message("Ei uusia kortteja!", "SUCCESS")
            return
            
        # Find missing cards
        all_missing_urls = []
        page = 1
        
        while page <= self.max_pages:
            self.log_message(f"Tarkistetaan sivu {page}...", "INFO")
            
            cards_urls = self.fetch_cards_page(page)
            if not cards_urls:
                break
                
            missing_urls, found_urls = self.find_missing_urls(cards_urls, self.master_urls)
            all_missing_urls.extend(missing_urls)
            
            self.log_message(f"Sivu {page}: {len(found_urls)} loytyi, {len(missing_urls)} puuttuu", "INFO")
            
            if not missing_urls:
                break
                
            page += 1
            time.sleep(self.page_delay)
            
        if all_missing_urls:
            self.log_message(f"Loydetiin {len(all_missing_urls)} uutta korttia!", "SUCCESS")
            self.fetch_new_cards_data(all_missing_urls)
        else:
            self.log_message("Ei uusia kortteja!", "SUCCESS")
            
    def fetch_new_cards_data(self, missing_urls):
        """Fetch detailed data for new cards"""
        self.log_message("Haetaan yksityiskohtaisia korttitietoja...", "INFO")
        self.new_cards_data = []
        
        for i, url in enumerate(missing_urls):
            try:
                self.log_message(f"Haetaan kortti {i+1}/{len(missing_urls)}...", "INFO")
                card_data = self.fetch_card_details(url)
                if card_data:
                    self.new_cards_data.append(card_data)
                    self.log_message(f"Haettu: {card_data.get('name', 'Tuntematon')}", "SUCCESS")
                    
            except Exception as e:
                self.log_message(f"Virhe kortin {i+1} hakemisessa: {e}", "ERROR")
                
        self.display_new_cards()
        
    def fetch_card_details(self, url):
        """Fetch detailed card information from URL"""
        try:
            # Extract player ID from URL
            player_id = self.extract_player_id_from_url(url)
            if not player_id:
                return None
                
            # Determine if it's a goalie or skater
            is_goalie = 'goalie' in url.lower()
            
            # Fetch player stats
            if is_goalie:
                stats_url = f"https://nhlhutbuilder.com/goalie-stats.php?id={player_id}"
            else:
                stats_url = f"https://nhlhutbuilder.com/player-stats.php?id={player_id}"
                
            response = self.make_request_with_retry(stats_url, {}, self.headers)
            if not response:
                return None
                
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract basic info
            card_data = {
                'url': url,
                'player_id': player_id,
                'is_goalie': is_goalie
            }
            
            # Extract player name
            name_elem = soup.find('h1') or soup.find('title')
            if name_elem:
                card_data['name'] = name_elem.get_text(strip=True)
            
            # Extract card image
            img_elem = soup.find('img', class_='card-image') or soup.find('img', src=True)
            if img_elem and img_elem.get('src'):
                img_src = img_elem.get('src')
                if not img_src.startswith('http'):
                    img_src = f"https://nhlhutbuilder.com/{img_src}"
                card_data['image_url'] = img_src
            
            # Extract stats from tables
            self.extract_player_stats(soup, card_data, is_goalie)
            
            return card_data
            
        except Exception as e:
            self.logger.error(f"Virhe korttitietojen hakemisessa: {e}")
            return None
            
    def extract_player_id_from_url(self, url):
        """Extract player ID from URL"""
        try:
            parsed = urlparse(url)
            params = parse_qs(parsed.query)
            if 'id' in params:
                return int(params['id'][0])
        except:
            pass
        return None
        
    def extract_player_stats(self, soup, card_data, is_goalie):
        """Extract player statistics from the page"""
        try:
            # Find stats tables
            tables = soup.find_all('table')
            
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2:
                        key = cells[0].get_text(strip=True).lower()
                        value = cells[1].get_text(strip=True)
                        
                        # Map common fields
                        if 'position' in key:
                            card_data['position'] = value
                        elif 'team' in key:
                            card_data['team'] = value
                        elif 'overall' in key or 'ovr' in key:
                            try:
                                card_data['overall'] = int(value)
                            except:
                                card_data['overall'] = value
                        elif 'nationality' in key:
                            card_data['nationality'] = value
                        elif 'height' in key:
                            card_data['height'] = value
                        elif 'weight' in key:
                            card_data['weight'] = value
                        elif 'hand' in key:
                            card_data['hand'] = value
                        elif 'salary' in key:
                            try:
                                # Parse salary (e.g., "$0.8M" -> 800000)
                                salary_str = value.replace('$', '').replace(',', '')
                                if 'M' in salary_str:
                                    salary_num = float(salary_str.replace('M', '')) * 1_000_000
                                elif 'K' in salary_str:
                                    salary_num = float(salary_str.replace('K', '')) * 1_000
                                else:
                                    salary_num = float(salary_str)
                                card_data['salary'] = int(salary_num)
                            except:
                                card_data['salary'] = value
                            
        except Exception as e:
            self.logger.error(f"Virhe tilastojen poiminnassa: {e}")
            
    def display_new_cards(self):
        """Display new cards in console"""
        if not self.new_cards_data:
            self.log_message("Ei uusia kortteja naytettavaksi", "INFO")
            return
            
        print(f"\nLOYDETYT UUDET KORTIT ({len(self.new_cards_data)} kpl):")
        print("=" * 80)
        
        for i, card in enumerate(self.new_cards_data, 1):
            print(f"\n{i:2d}. {card.get('name', 'Tuntematon')}")
            print(f"    Sijainti: {card.get('position', 'N/A')}")
            print(f"    Joukkue: {card.get('team', 'N/A')}")
            print(f"    Overall: {card.get('overall', 'N/A')}")
            print(f"    Kansallisuus: {card.get('nationality', 'N/A')}")
            print(f"    Pituus: {card.get('height', 'N/A')}")
            print(f"    Paino: {card.get('weight', 'N/A')}")
            print(f"    Katisyys: {card.get('hand', 'N/A')}")
            print(f"    Palkka: {card.get('salary', 'N/A')}")
            print(f"    ID: {card.get('player_id', 'N/A')}")
            print(f"    Tyyppi: {'Maalivahti' if card.get('is_goalie') else 'Kenttapelaaja'}")
                
        print("=" * 80)
        
    def add_cards_to_master_json(self):
        """Add new cards to master.json"""
        if not self.new_cards_data:
            self.log_message("Ei uusia kortteja lisattavaksi!", "WARNING")
            return
            
        if not self.master_data:
            self.log_message("Lataa ensin master.json!", "ERROR")
            return
            
        self.log_message("Lisataan uudet kortit master.json:iin...", "JSON")
        
        # Add new cards to master data
        added_count = 0
        for card in self.new_cards_data:
            # Check if player already exists (by player_id)
            existing_player = None
            for player in self.master_data['players']:
                if player.get('player_id') == card.get('player_id'):
                    existing_player = player
                    break
                    
            if not existing_player:
                # Add new player
                self.master_data['players'].append(card)
                self.master_urls.add(card.get('url', ''))
                added_count += 1
                self.log_message(f"Lisatty: {card.get('name', 'Tuntematon')}", "JSON")
            else:
                self.log_message(f"Pelaaja jo olemassa: {card.get('name', 'Tuntematon')}", "WARNING")
                
        if added_count > 0:
            # Save updated master.json
            try:
                # Create backup
                backup_filename = f"master_backup_{int(time.time())}.json"
                with open(backup_filename, 'w', encoding='utf-8') as f:
                    json.dump(self.master_data, f, indent=2, ensure_ascii=False)
                self.log_message(f"Varmuuskopio luotu: {backup_filename}", "JSON")
                
                # Save updated master.json
                with open('master.json', 'w', encoding='utf-8') as f:
                    json.dump(self.master_data, f, indent=2, ensure_ascii=False)
                    
                self.log_message(f"Lisatty {added_count} uutta korttia master.json:iin!", "SUCCESS")
                self.log_message(f"Master.json paivitetty: {len(self.master_data['players'])} pelaajaa", "JSON")
                
                # Clear new cards data
                self.new_cards_data = []
                
            except Exception as e:
                self.log_message(f"Virhe master.json:n tallentamisessa: {e}", "ERROR")
        else:
            self.log_message("Ei uusia kortteja lisattavaksi!", "WARNING")
            
    def enrich_xfactors(self):
        """Enrich selected cards with X-Factor data"""
        if not self.new_cards_data:
            self.log_message("Ei uusia kortteja rikastettavaksi!", "WARNING")
            return
            
        self.log_message("Aloitetaan X-Factor rikastus...", "X-FACTOR")
        
        enriched_count = 0
        for i, card in enumerate(self.new_cards_data):
            if 'xfactors' not in card or not card['xfactors']:
                self.log_message(f"Rikastetaan kortti {i+1}/{len(self.new_cards_data)}...", "X-FACTOR")
                
                player_id = card.get('player_id')
                is_goalie = card.get('is_goalie', False)
                
                if player_id:
                    xfactors = self.fetch_xfactors_with_tiers(player_id, is_goalie=is_goalie)
                    card['xfactors'] = xfactors
                    
                    if xfactors:
                        enriched_count += 1
                        self.log_message(f"Rikastettu {card.get('name', 'Tuntematon')} {len(xfactors)} X-Factor:lla", "X-FACTOR")
                    else:
                        self.log_message(f"Ei X-Factor kykyja {card.get('name', 'Tuntematon')}:lle", "WARNING")
                        
                time.sleep(0.5)  # Be nice to the server
                
        self.log_message(f"X-Factor rikastus valmis! Rikastettu {enriched_count} korttia", "SUCCESS")
        
    def fetch_xfactors_with_tiers(self, player_id, timeout=10, is_goalie=False):
        """Fetch X-Factor abilities for a player with timeout protection"""
        try:
            if is_goalie:
                url = f"https://nhlhutbuilder.com/goalie-stats.php?id={player_id}"
            else:
                url = f"https://nhlhutbuilder.com/player-stats.php?id={player_id}"
            
            resp = requests.get(url, headers=self.headers, timeout=timeout)
            
            if resp.status_code != 200:
                return []
            
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            xfactors = []
            
            # Find all X-Factor ability containers
            ability_containers = soup.find_all('div', class_='ability_info')
            
            for container in ability_containers:
                # Get ability name
                name_elem = container.find('div', class_='ability_name')
                if not name_elem:
                    continue
                    
                ability_name = name_elem.get_text(strip=True)
                
                # Get AP cost (tier)
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
                
                # Determine tier based on AP cost
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
            self.log_message(f"Error fetching X-Factors for {player_id}: {e}", "ERROR")
            return []
        
    def start_monitoring(self):
        """Start automatic monitoring"""
        if not self.master_data:
            self.log_message("Lataa ensin master.json!", "ERROR")
            return
            
        if self.monitoring:
            self.log_message("Seuranta on jo kaynnissa!", "WARNING")
            return
            
        self.monitoring = True
        self.log_message("Aloitetaan automaattinen seuranta (30 min vallein)", "SUCCESS")
        
        # Start monitoring thread
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
    def stop_monitoring(self):
        """Stop automatic monitoring"""
        if not self.monitoring:
            self.log_message("Seuranta ei ole kaynnissa!", "WARNING")
            return
            
        self.monitoring = False
        self.log_message("Pysaytetaan automaattinen seuranta", "INFO")
        
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.monitoring:
            try:
                self.log_message("Automaattinen tarkistus aloitettu...", "INFO")
                
                # Check for new cards
                if self.check_total_entries():
                    self.log_message("Uusia kortteja havaittu! Suoritetaan täysi haku...", "WARNING")
                    self.find_cards_manual()
                    
                    # Auto-add new cards to master.json
                    if self.new_cards_data:
                        self.log_message("Lisataan uudet kortit automaattisesti master.json:iin...", "JSON")
                        self.add_cards_to_master_json()
                else:
                    self.log_message("Ei uusia kortteja", "INFO")
                    
                self.last_check = datetime.now()
                
            except Exception as e:
                self.log_message(f"Seurannan virhe: {e}", "ERROR")
                
            # Wait 30 minutes (1800 seconds)
            for _ in range(1800):
                if not self.monitoring:
                    break
                time.sleep(1)
                
    def show_stats(self):
        """Show application statistics"""
        print("\nTILASTOT:")
        print("=" * 40)
        print(f"Master.json pelaajia: {len(self.master_urls) if self.master_urls else 0}")
        print(f"Uusia kortteja: {len(self.new_cards_data)}")
        print(f"Seuranta kaynnissa: {'Kyllä' if self.monitoring else 'Ei'}")
        if self.last_check:
            print(f"Viimeisin tarkistus: {self.last_check.strftime('%H:%M:%S')}")
        else:
            print("Viimeisin tarkistus: Ei koskaan")
        print("=" * 40)
        
    def run(self):
        """Main application loop"""
        self.print_banner()
        
        # Load initial data
        if not self.load_master_data():
            self.log_message("Ei voitu ladata master.json. Lopetetaan.", "ERROR")
            return
            
        while True:
            self.print_menu()
            
            try:
                choice = input("Valitse vaihtoehto (1-8): ").strip()
                
                if choice == '1':
                    self.find_cards_manual()
                elif choice == '2':
                    self.add_cards_to_master_json()
                elif choice == '3':
                    self.start_monitoring()
                elif choice == '4':
                    self.stop_monitoring()
                elif choice == '5':
                    self.enrich_xfactors()
                elif choice == '6':
                    self.load_master_data()
                elif choice == '7':
                    self.show_stats()
                elif choice == '8':
                    if self.monitoring:
                        self.stop_monitoring()
                    self.log_message("Lopetetaan ohjelma...", "INFO")
                    break
                else:
                    self.log_message("Virheellinen valinta!", "WARNING")
                    
            except KeyboardInterrupt:
                if self.monitoring:
                    self.stop_monitoring()
                self.log_message("Lopetetaan ohjelma...", "INFO")
                break
            except Exception as e:
                self.log_message(f"Virhe: {e}", "ERROR")

def main():
    """Main function"""
    monitor = NHLCardMonitorEnhanced()
    monitor.run()

if __name__ == "__main__":
    main()