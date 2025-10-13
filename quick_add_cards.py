#!/usr/bin/env python3
"""
Quick Add Cards - Test version
Hakee vain muutaman uuden kortin testatakseen järjestelmää
"""

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

# Import our existing modules
from update_missing_cards_final import (
    check_total_entries, load_master_json, get_master_urls, 
    find_missing_urls, fetch_cards_page, make_request_with_retry, config
)

class QuickCardAdder:
    def __init__(self):
        self.master_data = None
        self.master_urls = set()
        self.new_cards_data = []
        self.max_cards = 10  # Limit to 10 cards for testing
        
        # Setup logging
        self.setup_logging()
        
    def setup_logging(self):
        """Setup logging for the application"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('quick_add_cards.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def log_message(self, message, level="INFO"):
        """Log message with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"
        
        if level == "INFO":
            self.logger.info(formatted_message)
        elif level == "WARNING":
            self.logger.warning(formatted_message)
        elif level == "ERROR":
            self.logger.error(formatted_message)
        elif level == "SUCCESS":
            self.logger.info(f"✅ {formatted_message}")
            
    def load_master_data(self):
        """Load master.json data"""
        try:
            self.log_message("Ladataan master.json...", "INFO")
            self.master_data, players = load_master_json()
            if self.master_data:
                self.master_urls = get_master_urls(players)
                self.log_message(f"Ladattu {len(players)} pelaajaa master.json:sta", "SUCCESS")
                return True
            else:
                self.log_message("Epäonnistui master.json:n lataaminen", "ERROR")
                return False
        except Exception as e:
            self.log_message(f"Virhe master.json:n latauksessa: {e}", "ERROR")
            return False
            
    def find_and_add_cards(self):
        """Find new cards and add them to master.json (limited)"""
        if not self.master_data:
            self.log_message("Lataa ensin master.json!", "ERROR")
            return
            
        self.log_message("Aloitetaan uusien korttien haku (max 10 korttia)...", "INFO")
        
        # Check if there are new cards
        if not check_total_entries():
            self.log_message("Ei uusia kortteja!", "SUCCESS")
            return
            
        # Find missing cards (limited search)
        all_missing_urls = []
        page = 1
        max_pages = 5  # Only check first 5 pages
        
        while page <= max_pages and len(all_missing_urls) < self.max_cards:
            self.log_message(f"Tarkistetaan sivu {page}...", "INFO")
            
            cards_urls = fetch_cards_page(page)
            if not cards_urls:
                break
                
            missing_urls, found_urls = find_missing_urls(cards_urls, self.master_urls)
            
            # Limit to max_cards
            remaining_slots = self.max_cards - len(all_missing_urls)
            if len(missing_urls) > remaining_slots:
                missing_urls = missing_urls[:remaining_slots]
                
            all_missing_urls.extend(missing_urls)
            
            self.log_message(f"Sivu {page}: {len(found_urls)} löytyi, {len(missing_urls)} puuttuu", "INFO")
            
            if len(all_missing_urls) >= self.max_cards:
                self.log_message(f"Saavutettu maksimimäärä ({self.max_cards}) kortteja", "INFO")
                break
                
            page += 1
            time.sleep(config.page_delay)
            
        if all_missing_urls:
            self.log_message(f"Löydettiin {len(all_missing_urls)} uutta korttia!", "SUCCESS")
            self.fetch_and_add_cards(all_missing_urls)
        else:
            self.log_message("Ei uusia kortteja!", "SUCCESS")
            
    def fetch_and_add_cards(self, missing_urls):
        """Fetch detailed data for new cards and add to master.json"""
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
                
        # Add cards to master.json
        self.add_cards_to_master_json()
        
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
                
            response = make_request_with_retry(stats_url, {}, config.headers)
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
            
    def add_cards_to_master_json(self):
        """Add new cards to master.json"""
        if not self.new_cards_data:
            self.log_message("Ei uusia kortteja lisättäväksi!", "WARNING")
            return
            
        if not self.master_data:
            self.log_message("Lataa ensin master.json!", "ERROR")
            return
            
        self.log_message("Lisätään uudet kortit master.json:iin...", "INFO")
        
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
                self.log_message(f"Lisätty: {card.get('name', 'Tuntematon')}", "SUCCESS")
            else:
                self.log_message(f"Pelaaja jo olemassa: {card.get('name', 'Tuntematon')}", "WARNING")
                
        if added_count > 0:
            # Save updated master.json
            try:
                # Create backup
                backup_filename = f"master_backup_{int(time.time())}.json"
                with open(backup_filename, 'w', encoding='utf-8') as f:
                    json.dump(self.master_data, f, indent=2, ensure_ascii=False)
                self.log_message(f"Varmuuskopio luotu: {backup_filename}", "INFO")
                
                # Save updated master.json
                with open('master.json', 'w', encoding='utf-8') as f:
                    json.dump(self.master_data, f, indent=2, ensure_ascii=False)
                    
                self.log_message(f"Lisätty {added_count} uutta korttia master.json:iin!", "SUCCESS")
                self.log_message(f"Master.json päivitetty: {len(self.master_data['players'])} pelaajaa", "SUCCESS")
                
            except Exception as e:
                self.log_message(f"Virhe master.json:n tallentamisessa: {e}", "ERROR")
        else:
            self.log_message("Ei uusia kortteja lisättäväksi!", "WARNING")
            
    def run(self):
        """Main function"""
        self.log_message("🏒 QUICK CARD ADDER - Aloitetaan", "INFO")
        
        # Load initial data
        if not self.load_master_data():
            self.log_message("Ei voitu ladata master.json. Lopetetaan.", "ERROR")
            return
            
        # Find and add cards
        self.find_and_add_cards()
        
        self.log_message("🏒 QUICK CARD ADDER - Valmis!", "SUCCESS")

def main():
    """Main function"""
    adder = QuickCardAdder()
    adder.run()

if __name__ == "__main__":
    main()