#!/usr/bin/env python3
"""
NHL Card Monitor - Console Version
Automaattinen korttien seuranta konsoli-ympäristössä
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
from typing import List, Dict, Optional

# Import our existing modules
from update_missing_cards_final import (
    check_total_entries, load_master_json, get_master_urls, 
    find_missing_urls, fetch_cards_page, make_request_with_retry, config
)
from enrich_country_xfactors import fetch_xfactors_with_tiers

class NHLCardMonitorConsole:
    def __init__(self):
        self.monitoring = False
        self.monitor_thread = None
        self.last_check = None
        self.master_data = None
        self.master_urls = set()
        self.new_cards_data = []
        
        # Setup logging
        self.setup_logging()
        
    def setup_logging(self):
        """Setup logging for the application"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('nhl_monitor_console.log'),
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
        elif level == "X-FACTOR":
            self.logger.info(f"⚡ {formatted_message}")
            
    def print_banner(self):
        """Print application banner"""
        print("=" * 60)
        print("🏒 NHL CARD MONITOR - CONSOLE VERSION")
        print("=" * 60)
        print("Automaattinen korttien seuranta NHL HUT Builderille")
        print("=" * 60)
        
    def print_menu(self):
        """Print main menu"""
        print("\n📋 VALIKKO:")
        print("1. 🔍 Hae uusia kortteja")
        print("2. ▶️  Aloita automaattinen seuranta")
        print("3. ⏸️  Pysäytä seuranta")
        print("4. ⚡ Rikasta X-Factor tiedot")
        print("5. 🔄 Lataa master.json uudelleen")
        print("6. 📊 Näytä tilastot")
        print("7. 🚪 Lopeta")
        print("-" * 40)
        
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
            
    def find_cards_manual(self):
        """Manual card finding"""
        if not self.master_data:
            self.log_message("Lataa ensin master.json!", "ERROR")
            return
            
        self.log_message("Aloitetaan manuaalinen korttien haku...", "INFO")
        
        # Check if there are new cards
        if not check_total_entries():
            self.log_message("Ei uusia kortteja!", "SUCCESS")
            return
            
        # Find missing cards
        all_missing_urls = []
        page = 1
        
        while page <= config.max_pages:
            self.log_message(f"Tarkistetaan sivu {page}...", "INFO")
            
            cards_urls = fetch_cards_page(page)
            if not cards_urls:
                break
                
            missing_urls, found_urls = find_missing_urls(cards_urls, self.master_urls)
            all_missing_urls.extend(missing_urls)
            
            self.log_message(f"Sivu {page}: {len(found_urls)} löytyi, {len(missing_urls)} puuttuu", "INFO")
            
            if not missing_urls:
                break
                
            page += 1
            time.sleep(config.page_delay)
            
        if all_missing_urls:
            self.log_message(f"Löydettiin {len(all_missing_urls)} uutta korttia!", "SUCCESS")
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
                            
        except Exception as e:
            self.logger.error(f"Virhe tilastojen poiminnassa: {e}")
            
    def display_new_cards(self):
        """Display new cards in console"""
        if not self.new_cards_data:
            self.log_message("Ei uusia kortteja näytettäväksi", "INFO")
            return
            
        print(f"\n🆕 LÖYDETYT UUDET KORTIT ({len(self.new_cards_data)} kpl):")
        print("=" * 80)
        
        for i, card in enumerate(self.new_cards_data, 1):
            print(f"\n{i:2d}. {card.get('name', 'Tuntematon')}")
            print(f"    📍 Sijainti: {card.get('position', 'N/A')}")
            print(f"    🏒 Joukkue: {card.get('team', 'N/A')}")
            print(f"    ⭐ Overall: {card.get('overall', 'N/A')}")
            print(f"    🌍 Kansallisuus: {card.get('nationality', 'N/A')}")
            print(f"    📏 Pituus: {card.get('height', 'N/A')}")
            print(f"    ⚖️  Paino: {card.get('weight', 'N/A')}")
            print(f"    ✋ Kätisyys: {card.get('hand', 'N/A')}")
            print(f"    🆔 ID: {card.get('player_id', 'N/A')}")
            print(f"    🥅 Tyyppi: {'Maalivahti' if card.get('is_goalie') else 'Kenttäpelaaja'}")
            
            # X-Factor info
            if 'xfactors' in card and card['xfactors']:
                print(f"    ⚡ X-Factor kyvyt ({len(card['xfactors'])} kpl):")
                for xf in card['xfactors']:
                    print(f"       • {xf.get('name', 'Tuntematon')} ({xf.get('tier', 'N/A')})")
            else:
                print(f"    ⚡ X-Factor kyvyt: Ei ladattu")
                
        print("=" * 80)
        
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
                    xfactors = fetch_xfactors_with_tiers(player_id, is_goalie=is_goalie)
                    card['xfactors'] = xfactors
                    
                    if xfactors:
                        enriched_count += 1
                        self.log_message(f"Rikastettu {card.get('name', 'Tuntematon')} {len(xfactors)} X-Factor:lla", "X-FACTOR")
                    else:
                        self.log_message(f"Ei X-Factor kykyjä {card.get('name', 'Tuntematon')}:lle", "WARNING")
                        
                time.sleep(0.5)  # Be nice to the server
                
        self.log_message(f"X-Factor rikastus valmis! Rikastettu {enriched_count} korttia", "SUCCESS")
        
    def start_monitoring(self):
        """Start automatic monitoring"""
        if not self.master_data:
            self.log_message("Lataa ensin master.json!", "ERROR")
            return
            
        if self.monitoring:
            self.log_message("Seuranta on jo käynnissä!", "WARNING")
            return
            
        self.monitoring = True
        self.log_message("Aloitetaan automaattinen seuranta (30 min välein)", "SUCCESS")
        
        # Start monitoring thread
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
    def stop_monitoring(self):
        """Stop automatic monitoring"""
        if not self.monitoring:
            self.log_message("Seuranta ei ole käynnissä!", "WARNING")
            return
            
        self.monitoring = False
        self.log_message("Pysäytetään automaattinen seuranta", "INFO")
        
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.monitoring:
            try:
                self.log_message("Automaattinen tarkistus aloitettu...", "INFO")
                
                # Check for new cards
                if check_total_entries():
                    self.log_message("Uusia kortteja havaittu! Suoritetaan täysi haku...", "WARNING")
                    self.find_cards_manual()
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
        print("\n📊 TILASTOT:")
        print("=" * 40)
        print(f"Master.json pelaajia: {len(self.master_urls) if self.master_urls else 0}")
        print(f"Uusia kortteja: {len(self.new_cards_data)}")
        print(f"Seuranta käynnissä: {'Kyllä' if self.monitoring else 'Ei'}")
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
                choice = input("Valitse vaihtoehto (1-7): ").strip()
                
                if choice == '1':
                    self.find_cards_manual()
                elif choice == '2':
                    self.start_monitoring()
                elif choice == '3':
                    self.stop_monitoring()
                elif choice == '4':
                    self.enrich_xfactors()
                elif choice == '5':
                    self.load_master_data()
                elif choice == '6':
                    self.show_stats()
                elif choice == '7':
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
    monitor = NHLCardMonitorConsole()
    monitor.run()

if __name__ == "__main__":
    main()