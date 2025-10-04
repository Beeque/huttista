#!/usr/bin/env python3
"""
NHL Card Monitor - Auto Version
Automaattinen korttien seuranta ja päivitys ilman käyttöliittymää
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import time
import json
import requests
from bs4 import BeautifulSoup
import logging
from datetime import datetime
import os
import sys
import re
from typing import List, Dict, Optional, Set
from urllib.parse import urlparse, parse_qs

class NHLCardMonitorAuto:
    def __init__(self, root):
        self.root = root
        self.root.title("🏒 NHL Card Monitor - Auto")
        self.root.geometry("800x600")
        self.root.configure(bg='#1e1e1e')
        
        # Variables
        self.monitoring = True  # Always monitoring
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
        
        # Create simple GUI
        self.create_simple_gui()
        
        # Load initial data
        self.load_master_data()
        
        # Start monitoring automatically
        self.start_monitoring()
        
    def setup_logging(self):
        """Setup logging for the application"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('nhl_monitor_auto.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def create_simple_gui(self):
        """Create simple GUI with just log"""
        # Main frame
        main_frame = tk.Frame(self.root, bg='#1e1e1e')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(main_frame, text="🏒 NHL Card Monitor - Auto", 
                              font=('Arial', 18, 'bold'), 
                              bg='#1e1e1e', fg='white')
        title_label.pack(pady=(0, 20))
        
        # Status
        self.status_label = tk.Label(main_frame, text="Ladataan master.json...", 
                                    font=('Arial', 12), 
                                    bg='#1e1e1e', fg='#4CAF50')
        self.status_label.pack(pady=(0, 10))
        
        # Last check
        self.last_check_label = tk.Label(main_frame, text="Viimeisin tarkistus: Ei koskaan", 
                                        font=('Arial', 10), 
                                        bg='#1e1e1e', fg='#cccccc')
        self.last_check_label.pack(pady=(0, 20))
        
        # Log area
        log_frame = tk.LabelFrame(main_frame, text="📝 Aktiviteettiloki", 
                                 font=('Arial', 12, 'bold'),
                                 bg='#2b2b2b', fg='white', 
                                 padx=10, pady=10)
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, font=('Consolas', 9), 
                                                 bg='#1e1e1e', fg='#ffffff', 
                                                 insertbackground='white')
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Configure text tags for colored logging
        self.log_text.tag_configure("INFO", foreground="#00ff00")
        self.log_text.tag_configure("WARNING", foreground="#ffff00")
        self.log_text.tag_configure("ERROR", foreground="#ff0000")
        self.log_text.tag_configure("SUCCESS", foreground="#00ffff")
        self.log_text.tag_configure("JSON", foreground="#ff69b4")
        
        # Close button
        close_btn = tk.Button(main_frame, text="🚪 Sulje", 
                             font=('Arial', 10, 'bold'),
                             bg='#f44336', fg='white', 
                             padx=20, pady=5,
                             command=self.on_closing)
        close_btn.pack(pady=(20, 0))
        
    def log_message(self, message, level="INFO"):
        """Add message to log display"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"
        
        self.log_text.insert(tk.END, formatted_message, level)
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
    def update_status(self, message):
        """Update status label"""
        self.status_label.config(text=message)
        self.root.update_idletasks()
        
    def make_request_with_retry(self, url: str, data: Dict, headers: Dict, timeout: int = None) -> Optional[requests.Response]:
        """Make HTTP request with retry logic"""
        timeout = timeout or self.timeout
        
        for attempt in range(self.retry_count):
            try:
                response = requests.post(url, data=data, headers=headers, timeout=timeout)
                response.raise_for_status()
                return response
            except requests.exceptions.RequestException as e:
                self.log_message(f"Request attempt {attempt + 1}/{self.retry_count} failed: {e}", "WARNING")
                if attempt < self.retry_count - 1:
                    time.sleep(self.retry_delay * (attempt + 1))  # Exponential backoff
                else:
                    self.log_message(f"All {self.retry_count} request attempts failed", "ERROR")
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
    
    def load_master_data(self):
        """Load master.json data"""
        try:
            self.update_status("Ladataan master.json...")
            self.log_message("Ladataan master.json...", "INFO")
            with open('master.json', 'r', encoding='utf-8') as f:
                self.master_data = json.load(f)
            players = self.master_data.get('players', [])
            self.master_urls = set()
            for player in players:
                url = player.get('url')
                if url:
                    self.master_urls.add(url)
            self.update_status(f"Ladattu {len(players)} pelaajaa master.json:sta")
            self.log_message(f"Ladattu {len(players)} pelaajaa master.json:sta", "SUCCESS")
        except Exception as e:
            self.update_status(f"Virhe master.json:n latauksessa: {e}")
            self.log_message(f"Virhe master.json:n latauksessa: {e}", "ERROR")
            
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
            # Create unique ID by combining player_id with goalie flag
            unique_id = f"{player_id}_{'goalie' if is_goalie else 'skater'}"
            card_data = {
                'url': url,
                'player_id': player_id,
                'unique_id': unique_id,  # Unique identifier
                'is_goalie': is_goalie
            }
            
            # Extract player name - try multiple methods
            # Method 1: Look for div with class="player_header" (THIS IS THE CORRECT ONE!)
            player_header = soup.find('div', class_='player_header')
            if player_header:
                name_text = player_header.get_text(strip=True)
                if (name_text and 
                    len(name_text) > 3 and
                    "NHL HUT Builder" not in name_text and
                    "Database" not in name_text and
                    "Goalie Stat" not in name_text and
                    "Player Stat" not in name_text):
                    card_data['name'] = name_text
            
            # Method 2: Look for h1 with player name (fallback)
            if 'name' not in card_data:
                h1_elem = soup.find('h1')
                if h1_elem:
                    h1_text = h1_elem.get_text(strip=True)
                    if (h1_text and 
                        "NHL HUT Builder" not in h1_text and
                        "Database" not in h1_text and
                        "Goalie Stat" not in h1_text and
                        "Player Stat" not in h1_text and
                        len(h1_text) > 3):
                        card_data['name'] = h1_text
            
            
            # Final fallback
            if 'name' not in card_data:
                card_data['name'] = f"Player {player_id}"
            
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
        skipped_count = 0
        
        for card in self.new_cards_data:
            # Check if player already exists (by unique_id, player_id+is_goalie, or URL)
            existing_player = None
            card_unique_id = card.get('unique_id')
            card_player_id = card.get('player_id')
            card_is_goalie = card.get('is_goalie')
            card_url = card.get('url')
            
            for player in self.master_data['players']:
                # Check by unique_id first
                if card_unique_id and player.get('unique_id') == card_unique_id:
                    existing_player = player
                    break
                # Check by player_id + is_goalie combination
                elif (player.get('player_id') == card_player_id and 
                      player.get('is_goalie') == card_is_goalie):
                    existing_player = player
                    break
                # Check by URL as fallback
                elif player.get('url') == card_url:
                    existing_player = player
                    break
                    
            if not existing_player:
                # Add new player
                self.master_data['players'].append(card)
                self.master_urls.add(card.get('url', ''))
                added_count += 1
                player_type = "Maalivahti" if card_is_goalie else "Kenttapelaaja"
                self.log_message(f"Lisatty: {card.get('name', 'Tuntematon')} (ID: {card_player_id}, {player_type})", "JSON")
            else:
                skipped_count += 1
                player_type = "Maalivahti" if card_is_goalie else "Kenttapelaaja"
                self.log_message(f"Pelaaja jo olemassa: {card.get('name', 'Tuntematon')} (ID: {card_player_id}, {player_type})", "WARNING")
                
        if added_count > 0:
            # Create backup
            backup_filename = f"master_backup_{int(time.time())}.json"
            try:
                with open(backup_filename, 'w', encoding='utf-8') as f:
                    json.dump(self.master_data, f, indent=2, ensure_ascii=False)
                self.log_message(f"Varmuuskopio luotu: {backup_filename}", "JSON")
            except Exception as e:
                self.log_message(f"Virhe varmuuskopion luomisessa: {e}", "ERROR")
            
            # Save updated master.json
            try:
                with open('master.json', 'w', encoding='utf-8') as f:
                    json.dump(self.master_data, f, indent=2, ensure_ascii=False)
                    
                self.log_message(f"Lisatty {added_count} uutta korttia master.json:iin!", "SUCCESS")
                if skipped_count > 0:
                    self.log_message(f"Hypatty {skipped_count} korttia (jo olemassa)", "WARNING")
                self.log_message(f"Master.json paivitetty: {len(self.master_data['players'])} pelaajaa", "JSON")
                self.update_status(f"Lisatty {added_count} uutta korttia master.json:iin!")
                
                # Clear new cards data
                self.new_cards_data = []
                
            except Exception as e:
                self.log_message(f"Virhe master.json:n tallentamisessa: {e}", "ERROR")
                self.update_status(f"Virhe: {e}")
        else:
            self.log_message("Ei uusia kortteja lisattavaksi!", "WARNING")
            self.update_status("Ei uusia kortteja lisattavaksi!")
            
    def start_monitoring(self):
        """Start automatic monitoring"""
        if not self.master_data:
            self.log_message("Lataa ensin master.json!", "ERROR")
            return
            
        self.monitoring = True
        self.log_message("Aloitetaan automaattinen seuranta (30 min vallein)", "SUCCESS")
        self.update_status("Automaattinen seuranta kaynnissa (30 min vallein)")
        
        # Start monitoring thread
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.monitoring:
            try:
                self.update_status("Tarkistetaan uusia kortteja...")
                self.log_message("Automaattinen tarkistus aloitettu...", "INFO")
                
                # Check for new cards
                if self.check_total_entries():
                    self.log_message("Uusia kortteja havaittu! Suoritetaan täysi haku...", "WARNING")
                    
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
                        
                        # Fetch detailed card data
                        self.fetch_new_cards_data(all_missing_urls)
                        
                        # Auto-add new cards if found
                        if self.new_cards_data:
                            self.log_message("Lisataan uudet kortit automaattisesti master.json:iin...", "JSON")
                            self.add_cards_to_master_json()
                else:
                    self.log_message("Ei uusia kortteja", "INFO")
                    self.update_status("Ei uusia kortteja")
                    
                self.last_check = datetime.now()
                self.last_check_label.config(text=f"Viimeisin tarkistus: {self.last_check.strftime('%H:%M:%S')}")
                
            except Exception as e:
                self.log_message(f"Seurannan virhe: {e}", "ERROR")
                
            # Wait 30 minutes (1800 seconds)
            for _ in range(1800):
                if not self.monitoring:
                    break
                time.sleep(1)
                
    def on_closing(self):
        """Handle window close"""
        if self.monitoring:
            self.monitoring = False
        self.root.destroy()

def main():
    """Main function"""
    root = tk.Tk()
    app = NHLCardMonitorAuto(root)
    
    # Handle window close
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    # Start the GUI
    root.mainloop()

if __name__ == "__main__":
    main()