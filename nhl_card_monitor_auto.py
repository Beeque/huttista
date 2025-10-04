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
            # Extract image URL - look for card_art images first
            card_art_img = soup.find('img', src=lambda x: x and 'card_art' in x.lower())
            if card_art_img and card_art_img.get('src'):
                img_src = card_art_img.get('src')
                if not img_src.startswith('http'):
                    img_src = f"https://nhlhutbuilder.com/{img_src}"
                card_data['image_url'] = img_src
            else:
                # Fallback to any img with card in alt text
                img_elem = soup.find('img', class_='card-image') or soup.find('img', src=True)
                if img_elem and img_elem.get('src'):
                    img_src = img_elem.get('src')
                    if not img_src.startswith('http'):
                        img_src = f"https://nhlhutbuilder.com/{img_src}"
                    card_data['image_url'] = img_src
                else:
                    card_data['image_url'] = "https://nhlhutbuilder.com//images/logo-small.png"
            
            # Extract stats from tables
            self.extract_player_stats(soup, card_data, is_goalie)
            
            # Log X-Factor abilities found
            if 'xfactors' in card_data and card_data['xfactors']:
                xfactor_names = [xf['name'] for xf in card_data['xfactors']]
                self.log_message(f"X-Factor kyvyt: {', '.join(xfactor_names)}", "INFO")
            else:
                self.log_message("Ei X-Factor kykyjä", "WARNING")
            
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
                for i, row in enumerate(rows):
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2:
                        key = cells[0].get_text(strip=True)
                        value = cells[1].get_text(strip=True)
                        
                        # Special handling for the first table which has values on next row
                        if key == 'Overall':
                            # The actual overall value is on the next row (first cell)
                            if i + 1 < len(rows):
                                next_row = rows[i + 1]
                                next_cells = next_row.find_all(['td', 'th'])
                                if len(next_cells) >= 1:
                                    overall_value = next_cells[0].get_text(strip=True)
                                    try:
                                        card_data['overall'] = int(overall_value)
                                    except:
                                        card_data['overall'] = overall_value
                                # Card type is on the next row (second cell)
                                if len(next_cells) >= 2:
                                    card_data['card'] = next_cells[1].get_text(strip=True)
                            # Fallback: Card type is in the same row (second cell)
                            if 'card' not in card_data:
                                card_data['card'] = value
                        elif key == 'Nationality':
                            # The actual nationality is on the next row (first cell)
                            if i + 1 < len(rows):
                                next_row = rows[i + 1]
                                next_cells = next_row.find_all(['td', 'th'])
                                if len(next_cells) >= 1:
                                    card_data['nationality'] = next_cells[0].get_text(strip=True)
                            # Age is in the same row (second cell)
                            try:
                                card_data['age'] = int(value)
                            except:
                                pass
                        elif key == 'Position':
                            # The actual position is on the next row (first cell)
                            if i + 1 < len(rows):
                                next_row = rows[i + 1]
                                next_cells = next_row.find_all(['td', 'th'])
                                if len(next_cells) >= 1:
                                    card_data['position'] = next_cells[0].get_text(strip=True)
                                # Hand is on the next row (second cell)
                                if len(next_cells) >= 2:
                                    card_data['hand'] = next_cells[1].get_text(strip=True)
                            # Fallback: Hand is in the same row (second cell)
                            if 'hand' not in card_data:
                                card_data['hand'] = value
                        elif key == 'Weight':
                            # The actual weight is on the next row (first cell)
                            if i + 1 < len(rows):
                                next_row = rows[i + 1]
                                next_cells = next_row.find_all(['td', 'th'])
                                if len(next_cells) >= 1:
                                    weight_value = next_cells[0].get_text(strip=True)
                                    card_data['weight'] = weight_value
                                # Height is on the next row (second cell)
                                if len(next_cells) >= 2:
                                    card_data['height'] = next_cells[1].get_text(strip=True)
                            # Fallback: Height is in the same row (second cell)
                            if 'height' not in card_data:
                                card_data['height'] = value
                        elif key == 'Height':
                            # This is the actual height value
                            card_data['height'] = value
                        elif key == 'Salary':
                            # The actual salary is on the next row (first cell)
                            if i + 1 < len(rows):
                                next_row = rows[i + 1]
                                next_cells = next_row.find_all(['td', 'th'])
                                if len(next_cells) >= 1:
                                    salary_value = next_cells[0].get_text(strip=True)
                                    try:
                                        # Parse salary (e.g., "$0.6M" -> 600000)
                                        salary_str = salary_value.replace('$', '').replace(',', '')
                                        if 'M' in salary_str:
                                            salary_num = float(salary_str.replace('M', '')) * 1_000_000
                                        elif 'K' in salary_str:
                                            salary_num = float(salary_str.replace('K', '')) * 1_000
                                        else:
                                            salary_num = float(salary_str)
                                        card_data['salary'] = int(salary_num)
                                    except:
                                        card_data['salary'] = salary_value
                            # Division is in the same row (second cell)
                            card_data['division'] = value
                        elif key == 'Average Overall':
                            try:
                                card_data['aOVR'] = float(value)
                            except:
                                pass
                        elif key == 'Adjusted Overall':
                            try:
                                card_data['adjusted_overall'] = float(value)
                            except:
                                pass
                        # Player stats
                        elif key == 'Acceleration':
                            try:
                                card_data['acceleration'] = int(value)
                            except:
                                pass
                        elif key == 'Agility':
                            try:
                                card_data['agility'] = int(value)
                            except:
                                pass
                        elif key == 'Balance':
                            try:
                                card_data['balance'] = int(value)
                            except:
                                pass
                        elif key == 'Endurance':
                            try:
                                card_data['endurance'] = int(value)
                            except:
                                pass
                        elif key == 'Speed':
                            try:
                                card_data['speed'] = int(value)
                            except:
                                pass
                        elif key == 'Slap Shot Accuracy':
                            try:
                                card_data['slap_shot_accuracy'] = int(value)
                            except:
                                pass
                        elif key == 'Slap Shot Power':
                            try:
                                card_data['slap_shot_power'] = int(value)
                            except:
                                pass
                        elif key == 'Wrist Shot Accuracy':
                            try:
                                card_data['wrist_shot_accuracy'] = int(value)
                            except:
                                pass
                        elif key == 'Wrist Shot Power':
                            try:
                                card_data['wrist_shot_power'] = int(value)
                            except:
                                pass
                        elif key == 'Deking':
                            try:
                                card_data['deking'] = int(value)
                            except:
                                pass
                        elif key == 'Offensive Awareness':
                            try:
                                card_data['off_awareness'] = int(value)
                            except:
                                pass
                        elif key == 'Hand-Eye':
                            try:
                                card_data['hand_eye'] = int(value)
                            except:
                                pass
                        elif key == 'Passing':
                            try:
                                card_data['passing'] = int(value)
                            except:
                                pass
                        elif key == 'Puck Control':
                            try:
                                card_data['puck_control'] = int(value)
                            except:
                                pass
                        elif key == 'Body Checking':
                            try:
                                card_data['body_checking'] = int(value)
                            except:
                                pass
                        elif key == 'Strength':
                            try:
                                card_data['strength'] = int(value)
                            except:
                                pass
                        elif key == 'Aggression':
                            try:
                                card_data['aggression'] = int(value)
                            except:
                                pass
                        elif key == 'Durability':
                            try:
                                card_data['durability'] = int(value)
                            except:
                                pass
                        elif key == 'Fighting Skill':
                            try:
                                card_data['fighting_skill'] = int(value)
                            except:
                                pass
                        elif key == 'Defensive Awareness':
                            try:
                                card_data['def_awareness'] = int(value)
                            except:
                                pass
                        elif key == 'Shot Blocking':
                            try:
                                card_data['shot_blocking'] = int(value)
                            except:
                                pass
                        elif key == 'Stick Checking':
                            try:
                                card_data['stick_checking'] = int(value)
                            except:
                                pass
                        elif key == 'Face Offs':
                            try:
                                card_data['faceoffs'] = int(value)
                            except:
                                pass
                        elif key == 'Discipline':
                            try:
                                card_data['discipline'] = int(value)
                            except:
                                pass
            
            # Extract X-Factors from the page
            self.extract_xfactors(soup, card_data)
            
            # Add missing fields with defaults
            # Check if division is valid (not "Division" or empty)
            if 'division' in card_data and (card_data['division'] == 'Division' or not card_data['division'].strip()):
                # If division is invalid, remove both division and league
                card_data.pop('division', None)
                card_data.pop('league', None)
            elif 'league' not in card_data:
                card_data['league'] = 'NHL'
            if 'date_added' not in card_data:
                from datetime import datetime
                card_data['date_added'] = datetime.now().strftime('%Y-%m-%d')
            if 'date_updated' not in card_data:
                card_data['date_updated'] = '0000-00-00'
            if 'full_name' not in card_data and 'name' in card_data:
                card_data['full_name'] = card_data['name']
            
            # Convert weight and height to European format (kg/cm) as numbers
            if 'weight' in card_data and isinstance(card_data['weight'], str):
                try:
                    # Extract number from "198lb" -> convert to kg
                    weight_str = card_data['weight'].replace('lb', '').strip()
                    weight_lbs = int(weight_str)
                    # Convert to kg: 1 lb = 0.453592 kg
                    weight_kg = int(weight_lbs * 0.453592)
                    card_data['weight'] = weight_kg  # Store as kg (European)
                    card_data['weight_kg'] = weight_kg
                except:
                    pass
                    
            if 'height' in card_data and isinstance(card_data['height'], str):
                try:
                    # Convert "6' 2\"" to cm
                    height_str = card_data['height'].replace('"', '').replace("'", ' ').strip()
                    parts = height_str.split()
                    if len(parts) >= 2:
                        feet = int(parts[0])
                        inches = int(parts[1])
                        total_inches = feet * 12 + inches
                        cm = int(total_inches * 2.54)
                        card_data['height'] = cm  # Store as cm (European)
                        card_data['height_cm'] = cm
                except:
                    pass
            
            # Add salary_number if salary exists
            if 'salary' in card_data and isinstance(card_data['salary'], int):
                card_data['salary_number'] = card_data['salary']
                            
        except Exception as e:
            self.logger.error(f"Virhe tilastojen poiminnassa: {e}")
            
    def extract_xfactors(self, soup, card_data):
        """Extract X-Factor abilities from the page"""
        try:
            xfactors = []
            
            # Look for ability_title_wrapper divs which contain X-Factor abilities
            ability_wrappers = soup.find_all('div', class_='ability_title_wrapper')
            
            for wrapper in ability_wrappers:
                ability_name_elem = wrapper.find('div', class_='ability_name')
                xfactor_category_elem = wrapper.find('div', class_='xfactor_category')
                ap_amount_elem = wrapper.find('div', class_='ap_amount')
                
                if ability_name_elem:
                    ability_name = ability_name_elem.get_text(strip=True)
                    if ability_name and len(ability_name) > 2:  # Filter out empty or too short names
                        # Determine tier based on category
                        tier = "Specialist"  # Default
                        if xfactor_category_elem:
                            category = xfactor_category_elem.get_text(strip=True)
                            if "Elite" in category or "Superstar" in category:
                                tier = "Elite"
                            elif "Specialist" in category:
                                tier = "Specialist"
                        
                        # Get AP cost
                        ap_cost = 1  # Default
                        if ap_amount_elem:
                            try:
                                ap_cost = int(ap_amount_elem.get_text(strip=True))
                            except:
                                ap_cost = 1
                        
                        xfactors.append({
                            "name": ability_name,
                            "ap_cost": ap_cost,
                            "tier": tier
                        })
            
            # If no abilities found with the new method, try the old method as fallback
            if not xfactors:
                xfactor_names = [
                    'BIG RIG', 'TRUCULENCE', 'WHEELS', 'SPARK PLUG', 'WARRIOR', 'SPONGE',
                    'CLOSE QUARTERS', 'ONE-TEE', 'BEAUTY BACKHAND', 'QUICK DRAW',
                    'THREAD THE NEEDLE', 'PUCK ON A STRING', 'HEAT SEEKER', 'SHOCK AND AWE'
                ]
                
                for name in xfactor_names:
                    if soup.find(string=lambda text: text and name.upper() in text.upper()):
                        xfactors.append({
                            "name": name,
                            "ap_cost": 1,
                            "tier": "Specialist"
                        })
            
            if xfactors:
                card_data['xfactors'] = xfactors
                
        except Exception as e:
            self.logger.error(f"Virhe X-Factor poiminnassa: {e}")
            
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
            # Create backup BEFORE modifying master.json
            backup_filename = f"master_backup_{int(time.time())}.json"
            try:
                # Load original master.json for backup
                with open('master.json', 'r', encoding='utf-8') as f:
                    original_data = json.load(f)
                with open(backup_filename, 'w', encoding='utf-8') as f:
                    json.dump(original_data, f, indent=2, ensure_ascii=False)
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