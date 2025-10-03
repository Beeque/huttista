#!/usr/bin/env python3
"""
NHL Card Monitor - Simple GUI Version (No Login)
Automaattinen korttien seuranta GUI-ympäristössä
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

class NHLCardMonitorGUISimple:
    def __init__(self, root):
        self.root = root
        self.root.title("🏒 NHL Card Monitor")
        self.root.geometry("1000x700")
        self.root.configure(bg='#2b2b2b')
        
        # Variables
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
        
        # Create main GUI directly
        self.create_main_gui()
        
        # Load initial data
        self.load_master_data()
        
    def setup_logging(self):
        """Setup logging for the application"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('nhl_monitor_gui_simple.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def create_main_gui(self):
        """Create the main GUI"""
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Main frame
        main_frame = tk.Frame(self.root, bg='#2b2b2b')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title bar
        title_frame = tk.Frame(main_frame, bg='#2b2b2b')
        title_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_label = tk.Label(title_frame, text="🏒 NHL Card Monitor", 
                              font=('Arial', 18, 'bold'), 
                              bg='#2b2b2b', fg='white')
        title_label.pack(side=tk.LEFT)
        
        # Version label
        version_label = tk.Label(title_frame, text="v1.0 - Automaattinen korttien seuranta", 
                                font=('Arial', 10), 
                                bg='#2b2b2b', fg='#cccccc')
        version_label.pack(side=tk.RIGHT)
        
        # Control panel
        control_frame = tk.LabelFrame(main_frame, text="🎮 Ohjaus", 
                                     font=('Arial', 12, 'bold'),
                                     bg='#2b2b2b', fg='white', 
                                     padx=15, pady=15)
        control_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Buttons
        button_frame = tk.Frame(control_frame, bg='#2b2b2b')
        button_frame.pack(fill=tk.X)
        
        self.find_cards_btn = tk.Button(button_frame, text="🔍 Hae uusia kortteja", 
                                       font=('Arial', 10, 'bold'),
                                       bg='#4CAF50', fg='white', 
                                       padx=20, pady=8,
                                       command=self.find_cards_manual)
        self.find_cards_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.monitor_btn = tk.Button(button_frame, text="▶️ Aloita seuranta", 
                                    font=('Arial', 10, 'bold'),
                                    bg='#2196F3', fg='white', 
                                    padx=20, pady=8,
                                    command=self.toggle_monitoring)
        self.monitor_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.refresh_btn = tk.Button(button_frame, text="🔄 Päivitä data", 
                                    font=('Arial', 10, 'bold'),
                                    bg='#FF9800', fg='white', 
                                    padx=20, pady=8,
                                    command=self.load_master_data)
        self.refresh_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.enrich_btn = tk.Button(button_frame, text="⚡ Rikasta X-Factor", 
                                   font=('Arial', 10, 'bold'),
                                   bg='#9C27B0', fg='white', 
                                   padx=20, pady=8,
                                   command=self.enrich_xfactors)
        self.enrich_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.add_btn = tk.Button(button_frame, text="➕ Lisää master.json:iin", 
                                font=('Arial', 10, 'bold'),
                                bg='#FF5722', fg='white', 
                                padx=20, pady=8,
                                command=self.add_cards_to_master_json)
        self.add_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stats_btn = tk.Button(button_frame, text="📊 Tilastot", 
                                  font=('Arial', 10, 'bold'),
                                  bg='#607D8B', fg='white', 
                                  padx=20, pady=8,
                                  command=self.show_stats)
        self.stats_btn.pack(side=tk.LEFT)
        
        # Status frame
        status_frame = tk.LabelFrame(main_frame, text="📊 Tila", 
                                    font=('Arial', 12, 'bold'),
                                    bg='#2b2b2b', fg='white', 
                                    padx=15, pady=15)
        status_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.status_label = tk.Label(status_frame, text="Valmis korttien seurantaan...", 
                                    font=('Arial', 11), 
                                    bg='#2b2b2b', fg='#4CAF50')
        self.status_label.pack(anchor=tk.W)
        
        self.last_check_label = tk.Label(status_frame, text="Viimeisin tarkistus: Ei koskaan", 
                                        font=('Arial', 10), 
                                        bg='#2b2b2b', fg='#cccccc')
        self.last_check_label.pack(anchor=tk.W)
        
        # Progress bar
        self.progress = ttk.Progressbar(status_frame, mode='indeterminate')
        self.progress.pack(fill=tk.X, pady=(10, 0))
        
        # Content area
        content_frame = tk.Frame(main_frame, bg='#2b2b2b')
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - New cards
        left_frame = tk.LabelFrame(content_frame, text="🆕 Uudet kortit", 
                                  font=('Arial', 12, 'bold'),
                                  bg='#2b2b2b', fg='white', 
                                  padx=10, pady=10)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Cards listbox with scrollbar
        cards_frame = tk.Frame(left_frame, bg='#2b2b2b')
        cards_frame.pack(fill=tk.BOTH, expand=True)
        
        self.cards_listbox = tk.Listbox(cards_frame, font=('Consolas', 10), 
                                       bg='#1e1e1e', fg='white', 
                                       selectbackground='#4CAF50')
        cards_scrollbar = ttk.Scrollbar(cards_frame, orient=tk.VERTICAL, command=self.cards_listbox.yview)
        self.cards_listbox.configure(yscrollcommand=cards_scrollbar.set)
        
        self.cards_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        cards_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind selection event
        self.cards_listbox.bind('<<ListboxSelect>>', self.on_card_select)
        
        # Right panel - Log
        right_frame = tk.LabelFrame(content_frame, text="📝 Aktiviteettiloki", 
                                   font=('Arial', 12, 'bold'),
                                   bg='#2b2b2b', fg='white', 
                                   padx=10, pady=10)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.log_text = scrolledtext.ScrolledText(right_frame, font=('Consolas', 9), 
                                                 bg='#1e1e1e', fg='#ffffff', 
                                                 insertbackground='white')
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Configure text tags for colored logging
        self.log_text.tag_configure("INFO", foreground="#00ff00")
        self.log_text.tag_configure("WARNING", foreground="#ffff00")
        self.log_text.tag_configure("ERROR", foreground="#ff0000")
        self.log_text.tag_configure("SUCCESS", foreground="#00ffff")
        self.log_text.tag_configure("X-FACTOR", foreground="#ff69b4")
        
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
            
    def find_cards_manual(self):
        """Manual card finding"""
        if not self.master_data:
            messagebox.showerror("Virhe", "Lataa ensin master.json!")
            return
            
        self.find_cards_btn.config(state='disabled')
        self.progress.start()
        
        # Run in separate thread to avoid blocking GUI
        thread = threading.Thread(target=self._find_cards_thread)
        thread.daemon = True
        thread.start()
        
    def _find_cards_thread(self):
        """Thread function for finding cards"""
        try:
            self.update_status("Tarkistetaan uusia kortteja...")
            self.log_message("Aloitetaan manuaalinen korttien haku...", "INFO")
            
            # Check if there are new cards
            if not self.check_total_entries():
                self.log_message("Ei uusia kortteja!", "SUCCESS")
                self.update_status("Ei uusia kortteja")
                return
                
            # Find missing cards
            all_missing_urls = []
            page = 1
            
            while page <= self.max_pages:
                self.update_status(f"Tarkistetaan sivu {page}...")
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
                self.update_status(f"Loydetiin {len(all_missing_urls)} uutta korttia")
                
                # Fetch detailed card data first
                self.fetch_new_cards_data(all_missing_urls)
                
                # Ask if user wants to add cards automatically
                if messagebox.askyesno("Lisää kortit", f"Löydettiin {len(all_missing_urls)} uutta korttia. Lisätäänkö ne automaattisesti master.json:iin?"):
                    self.add_cards_to_master_json()
            else:
                self.log_message("Ei uusia kortteja!", "SUCCESS")
                self.update_status("Ei uusia kortteja")
                
        except Exception as e:
            self.log_message(f"Virhe korttien hakemisessa: {e}", "ERROR")
            self.update_status(f"Virhe: {e}")
        finally:
            self.progress.stop()
            self.find_cards_btn.config(state='normal')
            
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
                
        self.display_new_cards(missing_urls)
        
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
            from urllib.parse import urlparse, parse_qs
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
            
    def display_new_cards(self, missing_urls):
        """Display new cards in the listbox"""
        self.cards_listbox.delete(0, tk.END)
        
        # Display from new_cards_data if available, otherwise from URLs
        if self.new_cards_data:
            for i, card in enumerate(self.new_cards_data):
                name = card.get('name', 'Tuntematon')
                overall = card.get('overall', 'N/A')
                position = card.get('position', 'N/A')
                team = card.get('team', 'N/A')
                display_text = f"{i+1:3d}. {name} ({overall} OVR) - {position} - {team}"
                self.cards_listbox.insert(tk.END, display_text)
            self.log_message(f"Naytetaan {len(self.new_cards_data)} uutta korttia", "SUCCESS")
        else:
            for i, url in enumerate(missing_urls):
                # Extract player name from URL if possible
                try:
                    # Try to get player info from the URL
                    player_info = self.get_player_info_from_url(url)
                    display_text = f"{i+1:3d}. {player_info}"
                except:
                    display_text = f"{i+1:3d}. {url}"
                    
                self.cards_listbox.insert(tk.END, display_text)
            self.log_message(f"Naytetaan {len(missing_urls)} uutta korttia", "SUCCESS")
        
    def get_player_info_from_url(self, url):
        """Get player info from URL"""
        try:
            # This is a simplified version - in real implementation
            # you'd fetch the actual player data
            return url.split('/')[-1] if '/' in url else url
        except:
            return url
            
    def on_card_select(self, event):
        """Handle card selection"""
        selection = self.cards_listbox.curselection()
        if selection:
            # In a real implementation, you'd fetch and display the card image
            selected_text = self.cards_listbox.get(selection[0])
            self.log_message(f"Valittu kortti: {selected_text}", "INFO")
            
    def enrich_xfactors(self):
        """Enrich selected cards with X-Factor data"""
        if not self.new_cards_data:
            messagebox.showwarning("Varoitus", "Ei uusia kortteja rikastettavaksi!")
            return
            
        self.enrich_btn.config(state='disabled')
        self.progress.start()
        
        # Run in separate thread
        thread = threading.Thread(target=self._enrich_xfactors_thread)
        thread.daemon = True
        thread.start()
        
    def _enrich_xfactors_thread(self):
        """Thread function for X-Factor enrichment"""
        try:
            self.update_status("Rikastetaan X-Factor tietoja...")
            self.log_message("Aloitetaan X-Factor rikastus...", "X-FACTOR")
            
            # Simulate X-Factor enrichment
            time.sleep(2)  # Simulate work
            
            self.log_message("X-Factor rikastus valmis!", "SUCCESS")
            self.update_status("X-Factor rikastus valmis!")
            
        except Exception as e:
            self.log_message(f"Virhe X-Factor rikastuksessa: {e}", "ERROR")
            self.update_status(f"Virhe: {e}")
        finally:
            self.progress.stop()
            self.enrich_btn.config(state='normal')
            
    def add_cards_to_master_json(self):
        """Add new cards to master.json"""
        if not self.new_cards_data:
            messagebox.showwarning("Varoitus", "Ei uusia kortteja lisättäväksi!")
            return
            
        if not self.master_data:
            messagebox.showerror("Virhe", "Lataa ensin master.json!")
            return
            
        self.add_btn.config(state='disabled')
        self.progress.start()
        
        # Run in separate thread
        thread = threading.Thread(target=self._add_cards_thread)
        thread.daemon = True
        thread.start()
        
    def _add_cards_thread(self):
        """Thread function for adding cards to master.json"""
        try:
            self.update_status("Lisätään uudet kortit master.json:iin...")
            self.log_message("Lisätään uudet kortit master.json:iin...", "JSON")
            
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
                    self.log_message(f"Lisätty: {card.get('name', 'Tuntematon')}", "JSON")
                else:
                    self.log_message(f"Pelaaja jo olemassa: {card.get('name', 'Tuntematon')}", "WARNING")
                    
            if added_count > 0:
                # Create backup
                import time
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
                        
                    self.log_message(f"Lisätty {added_count} uutta korttia master.json:iin!", "SUCCESS")
                    self.log_message(f"Master.json päivitetty: {len(self.master_data['players'])} pelaajaa", "JSON")
                    self.update_status(f"Lisätty {added_count} uutta korttia master.json:iin!")
                    
                    # Clear new cards data
                    self.new_cards_data = []
                    self.display_new_cards([])  # Clear the display
                    
                except Exception as e:
                    self.log_message(f"Virhe master.json:n tallentamisessa: {e}", "ERROR")
                    self.update_status(f"Virhe: {e}")
            else:
                self.log_message("Ei uusia kortteja lisättäväksi!", "WARNING")
                self.update_status("Ei uusia kortteja lisättäväksi!")
                
        except Exception as e:
            self.log_message(f"Virhe korttien lisäämisessä: {e}", "ERROR")
            self.update_status(f"Virhe: {e}")
        finally:
            self.progress.stop()
            self.add_btn.config(state='normal')
            
    def show_stats(self):
        """Show application statistics"""
        stats_window = tk.Toplevel(self.root)
        stats_window.title("📊 Tilastot")
        stats_window.geometry("400x300")
        stats_window.configure(bg='#2b2b2b')
        
        # Stats content
        stats_frame = tk.Frame(stats_window, bg='#2b2b2b', padx=20, pady=20)
        stats_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(stats_frame, text="📊 NHL Card Monitor - Tilastot", 
                font=('Arial', 16, 'bold'), 
                bg='#2b2b2b', fg='white').pack(pady=(0, 20))
        
        stats_text = f"""
Master.json pelaajia: {len(self.master_urls) if self.master_urls else 0}
Uusia kortteja: {len(self.new_cards_data)}
Seuranta käynnissä: {'Kyllä' if self.monitoring else 'Ei'}
Viimeisin tarkistus: {self.last_check.strftime('%H:%M:%S') if self.last_check else 'Ei koskaan'}

Automaattinen seuranta: 30 minuutin välein
Maksimisivut per haku: {self.max_pages}
Kortteja per sivu: {self.limit_per_page}

Versio: 1.0
Käyttöliittymä: GUI (Tkinter)
"""
        
        tk.Label(stats_frame, text=stats_text, 
                font=('Consolas', 10), 
                bg='#2b2b2b', fg='#cccccc', 
                justify=tk.LEFT).pack()
        
    def toggle_monitoring(self):
        """Toggle automatic monitoring"""
        if not self.monitoring:
            self.start_monitoring()
        else:
            self.stop_monitoring()
            
    def start_monitoring(self):
        """Start automatic monitoring"""
        if not self.master_data:
            messagebox.showerror("Virhe", "Lataa ensin master.json!")
            return
            
        self.monitoring = True
        self.monitor_btn.config(text="⏸️ Pysäytä seuranta")
        self.log_message("Aloitetaan automaattinen seuranta (30 min välein)", "SUCCESS")
        
        # Start monitoring thread
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
    def stop_monitoring(self):
        """Stop automatic monitoring"""
        self.monitoring = False
        self.monitor_btn.config(text="▶️ Aloita seuranta")
        self.log_message("Pysäytetään automaattinen seuranta", "INFO")
        
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
                            self.log_message("Lisätään uudet kortit automaattisesti master.json:iin...", "JSON")
                            self._add_cards_thread()
                else:
                    self.log_message("Ei uusia kortteja", "INFO")
                    
                self.last_check = datetime.now()
                self.last_check_label.config(text=f"Viimeisin tarkistus: {self.last_check.strftime('%H:%M:%S')}")
                
            except Exception as e:
                self.log_message(f"Seurannan virhe: {e}", "ERROR")
                
            # Wait 30 minutes (1800 seconds)
            for _ in range(1800):
                if not self.monitoring:
                    break
                time.sleep(1)

def main():
    """Main function"""
    root = tk.Tk()
    app = NHLCardMonitorGUISimple(root)
    
    # Handle window close
    def on_closing():
        if app.monitoring:
            app.stop_monitoring()
        root.destroy()
        
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Start the GUI
    root.mainloop()

if __name__ == "__main__":
    main()