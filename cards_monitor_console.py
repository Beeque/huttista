#!/usr/bin/env python3
"""
NHL HUT Builder Cards Monitor - Console Version
Monitors the default view for new cards and automatically adds them to master.json
Console version for easier debugging and interaction
"""

import json
import time
import requests
import logging
import os
import sys
from datetime import datetime, timedelta
from collections import defaultdict
from utils_clean import clean_common_fields

# Configuration
MONITOR_INTERVAL = 30 * 60  # 30 minutes in seconds
LOG_FILE = "cards_monitor.log"
MASTER_JSON = "master.json"
BACKUP_DIR = "backups"

# API endpoint
DT_URL = "https://nhlhutbuilder.com/php/player_stats.php"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'X-Requested-With': 'XMLHttpRequest',
    'Referer': 'https://nhlhutbuilder.com/cards.php',
}

class CardsMonitorConsole:
    def __init__(self):
        self.setup_logging()
        self.setup_directories()
        self.last_check = None
        self.monitored_card_ids = set()
        self.load_existing_cards()
        
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(LOG_FILE, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info("🏒 NHL HUT Builder Cards Monitor (Console) started")
        
    def setup_directories(self):
        """Create necessary directories"""
        if not os.path.exists(BACKUP_DIR):
            os.makedirs(BACKUP_DIR)
            self.logger.info(f"📁 Created backup directory: {BACKUP_DIR}")
    
    def load_existing_cards(self):
        """Load existing card IDs from master.json"""
        try:
            if os.path.exists(MASTER_JSON):
                with open(MASTER_JSON, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                players = data.get('players', [])
                self.monitored_card_ids = {p.get('player_id') for p in players if p.get('player_id')}
                self.logger.info(f"📂 Loaded {len(self.monitored_card_ids)} existing card IDs")
            else:
                self.logger.warning(f"⚠️ Master JSON not found: {MASTER_JSON}")
        except Exception as e:
            self.logger.error(f"❌ Error loading existing cards: {e}")
    
    def fetch_default_cards(self, count=100):
        """Fetch cards from default view"""
        payload = {
            'draw': 1,
            'start': 0,
            'length': count,
            'search[value]': '',
            'search[regex]': 'false',
        }
        
        # Define all columns
        columns = [
            'card_art','card','nationality','league','team','division','salary','position','hand','weight','height','full_name','overall','aOVR',
            'acceleration','agility','balance','endurance','speed','slap_shot_accuracy','slap_shot_power','wrist_shot_accuracy','wrist_shot_power',
            'deking','off_awareness','hand_eye','passing','puck_control','body_checking','strength','aggression','durability','fighting_skill',
            'def_awareness','shot_blocking','stick_checking','faceoffs','discipline','date_added','date_updated'
        ]
        
        # Set up column definitions
        for idx, name in enumerate(columns):
            payload[f'columns[{idx}][data]'] = name
            payload[f'columns[{idx}][name]'] = name
            payload[f'columns[{idx}][searchable]'] = 'true'
            payload[f'columns[{idx}][orderable]'] = 'true'
            payload[f'columns[{idx}][search][value]'] = ''
            payload[f'columns[{idx}][search][regex]'] = 'false'
        
        # Default sorting: by date_added (most recent first)
        payload['order[0][column]'] = '35'  # date_added column index
        payload['order[0][dir]'] = 'desc'
        
        try:
            print(f"🔍 Fetching {count} cards from default view...")
            resp = requests.post(DT_URL, data=payload, headers=HEADERS, timeout=30)
            resp.raise_for_status()
            
            data = resp.json()
            cards = data.get('data', [])
            total = data.get('recordsTotal', 0)
            filtered = data.get('recordsFiltered', 0)
            
            print(f"✅ Fetched {len(cards)} cards (Total: {total}, Filtered: {filtered})")
            
            # Clean cards
            cleaned_cards = [clean_common_fields(card) for card in cards]
            
            return cleaned_cards
            
        except Exception as e:
            print(f"❌ Error fetching cards: {e}")
            return []
    
    def fetch_xfactors_for_card(self, player_id, is_goalie=False):
        """Fetch X-Factor abilities for a specific card"""
        try:
            if is_goalie:
                url = f"https://nhlhutbuilder.com/goalie-stats.php?id={player_id}"
            else:
                url = f"https://nhlhutbuilder.com/player-stats.php?id={player_id}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
            }
            
            resp = requests.get(url, headers=headers, timeout=10)
            resp.raise_for_status()
            
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            xfactors = []
            ability_infos = soup.select('.ability_info')
            
            for info in ability_infos:
                name_elem = info.select_one('.ability_name')
                ability_name = name_elem.get_text(strip=True) if name_elem else None
                
                ap_elem = info.select_one('.ap_amount')
                ap_cost = None
                if ap_elem:
                    try:
                        ap_cost = int(ap_elem.get_text(strip=True))
                    except:
                        pass
                
                cat_elem = info.select_one('.xfactor_category')
                category = cat_elem.get_text(strip=True) if cat_elem else None
                
                tier = "Unknown"
                if ap_cost == 1:
                    tier = "Specialist"
                elif ap_cost == 2:
                    tier = "All-Star"
                elif ap_cost == 3:
                    tier = "Elite"
                
                if ability_name:
                    xfactors.append({
                        'name': ability_name,
                        'ap_cost': ap_cost,
                        'tier': tier,
                        'category': category
                    })
            
            return xfactors
            
        except Exception as e:
            print(f"❌ Error fetching X-Factors for player {player_id}: {e}")
            return []
    
    def detect_new_cards(self, current_cards):
        """Detect new cards that aren't in our monitored set"""
        new_cards = []
        
        for card in current_cards:
            player_id = card.get('player_id')
            if player_id and player_id not in self.monitored_card_ids:
                new_cards.append(card)
                print(f"🆕 New card detected: {card.get('full_name', 'Unknown')} (ID: {player_id})")
        
        return new_cards
    
    def enrich_new_cards_with_xfactors(self, new_cards):
        """Enrich new cards with X-Factor abilities"""
        enriched_cards = []
        
        for card in new_cards:
            player_id = card.get('player_id')
            name = card.get('full_name', 'Unknown')
            
            if player_id:
                print(f"🔍 Fetching X-Factors for {name} (ID: {player_id})...")
                
                # Detect if it's a goalie
                is_goalie = self.is_goalie_card(card)
                
                # Fetch X-Factors
                xfactors = self.fetch_xfactors_for_card(player_id, is_goalie)
                
                # Add to card
                card['xfactors'] = xfactors
                card['url'] = f"https://nhlhutbuilder.com/player-stats.php?id={player_id}"
                
                if xfactors:
                    print(f"✅ Found {len(xfactors)} X-Factors for {name}")
                else:
                    print(f"ℹ️ No X-Factors found for {name}")
                
                # Small delay to be nice to the server
                time.sleep(0.5)
            
            enriched_cards.append(card)
        
        return enriched_cards
    
    def is_goalie_card(self, card):
        """Detect if a card is a goalie based on position or other indicators"""
        position = card.get('position', '')
        if position == 'G':
            return True
        
        # Check for goalie-specific stats
        goalie_stats = ['glove_high', 'stick_low', 'stick_high', 'glove_low']
        for stat in goalie_stats:
            if stat in card:
                return True
        
        return False
    
    def backup_master_json(self):
        """Create a backup of master.json before making changes"""
        try:
            if os.path.exists(MASTER_JSON):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_file = os.path.join(BACKUP_DIR, f"master_backup_{timestamp}.json")
                
                with open(MASTER_JSON, 'r', encoding='utf-8') as src:
                    with open(backup_file, 'w', encoding='utf-8') as dst:
                        dst.write(src.read())
                
                print(f"💾 Created backup: {backup_file}")
                return backup_file
        except Exception as e:
            print(f"❌ Error creating backup: {e}")
        return None
    
    def add_cards_to_master(self, new_cards):
        """Add new cards to master.json"""
        if not new_cards:
            return
        
        try:
            # Create backup
            self.backup_master_json()
            
            # Load current master.json
            if os.path.exists(MASTER_JSON):
                with open(MASTER_JSON, 'r', encoding='utf-8') as f:
                    master_data = json.load(f)
            else:
                master_data = {
                    'metadata': {
                        'total_players': 0,
                        'created_at': datetime.now().strftime('%Y-%m-%d'),
                        'description': 'NHL HUT Builder player database'
                    },
                    'players': []
                }
            
            # Add new cards
            current_count = len(master_data.get('players', []))
            master_data['players'].extend(new_cards)
            new_count = len(master_data['players'])
            
            # Update metadata
            if 'metadata' in master_data:
                master_data['metadata']['total_players'] = new_count
                master_data['metadata']['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                master_data['metadata']['last_added'] = len(new_cards)
            
            # Save updated master.json
            with open(MASTER_JSON, 'w', encoding='utf-8') as f:
                json.dump(master_data, f, ensure_ascii=False, indent=2)
            
            # Update monitored card IDs
            for card in new_cards:
                player_id = card.get('player_id')
                if player_id:
                    self.monitored_card_ids.add(player_id)
            
            print(f"✅ Added {len(new_cards)} new cards to master.json")
            print(f"📊 Total players: {current_count} → {new_count}")
            
            # Log added cards
            self.log_added_cards(new_cards)
            
        except Exception as e:
            print(f"❌ Error adding cards to master.json: {e}")
    
    def log_added_cards(self, new_cards):
        """Log details of added cards"""
        print(f"📝 Added cards details:")
        for i, card in enumerate(new_cards, 1):
            name = card.get('full_name', 'Unknown')
            card_type = card.get('card', 'Unknown')
            team = card.get('team', 'Unknown')
            overall = card.get('overall', '?')
            nationality = card.get('nationality', 'Unknown')
            position = card.get('position', '?')
            player_id = card.get('player_id', '?')
            xfactors = card.get('xfactors', [])
            
            print(f"  {i:2d}. {name:25s} | {card_type:4s} | {team:6s} | OVR:{overall:3d} | {nationality:10s} | {position:3s} | ID:{player_id}")
            
            if xfactors:
                xfactor_names = [xf.get('name', 'Unknown') for xf in xfactors]
                print(f"      X-Factors: {', '.join(xfactor_names)}")
    
    def run_monitoring_cycle(self):
        """Run one monitoring cycle"""
        try:
            print("🔄 Starting monitoring cycle...")
            
            # Fetch current cards from default view
            current_cards = self.fetch_default_cards(100)
            
            if not current_cards:
                print("⚠️ No cards fetched, skipping cycle")
                return
            
            # Detect new cards
            new_cards = self.detect_new_cards(current_cards)
            
            if new_cards:
                print(f"🆕 Found {len(new_cards)} new cards!")
                
                # Enrich with X-Factors
                enriched_cards = self.enrich_new_cards_with_xfactors(new_cards)
                
                # Add to master.json
                self.add_cards_to_master(enriched_cards)
            else:
                print("✅ No new cards found")
            
            # Update last check time
            self.last_check = datetime.now()
            print(f"⏰ Monitoring cycle completed at {self.last_check.strftime('%Y-%m-%d %H:%M:%S')}")
            
        except Exception as e:
            print(f"❌ Error in monitoring cycle: {e}")
    
    def run(self):
        """Main monitoring loop"""
        print(f"🚀 Starting NHL HUT Builder Cards Monitor (Console)")
        print(f"⏰ Monitoring interval: {MONITOR_INTERVAL // 60} minutes")
        print(f"📁 Master JSON: {MASTER_JSON}")
        print(f"📝 Log file: {LOG_FILE}")
        print(f"💾 Backup directory: {BACKUP_DIR}")
        print(f"🛑 Press Ctrl+C to stop the monitor")
        print("=" * 60)
        
        try:
            while True:
                self.run_monitoring_cycle()
                
                # Wait for next cycle
                print(f"😴 Sleeping for {MONITOR_INTERVAL // 60} minutes...")
                print(f"⏰ Next check at: {(datetime.now() + timedelta(seconds=MONITOR_INTERVAL)).strftime('%Y-%m-%d %H:%M:%S')}")
                print("-" * 60)
                time.sleep(MONITOR_INTERVAL)
                
        except KeyboardInterrupt:
            print("\n🛑 Monitor stopped by user")
        except Exception as e:
            print(f"❌ Fatal error: {e}")
            raise

def main():
    """Main entry point"""
    print("🏒 NHL HUT Builder Cards Monitor (Console Version)")
    print("=" * 60)
    print("This monitor will check for new cards every 30 minutes")
    print("and automatically add them to master.json")
    print("All activity will be displayed in this console")
    print("Press Ctrl+C to stop the monitor")
    print("=" * 60)
    
    monitor = CardsMonitorConsole()
    monitor.run()

if __name__ == '__main__':
    main()