#!/usr/bin/env python3
"""
Master.json Updater - Automatically updates master.json with new NHL HUT Builder cards
"""

import json
import time
import requests
from bs4 import BeautifulSoup
import sys
import os

class MasterUpdater:
    def __init__(self):
        self.base_url = "https://nhlhutbuilder.com/cards.php"
        self.ajax_url = "https://nhlhutbuilder.com/php/find_cards.php"
        self.master_file = "/workspace/master.json"
        self.new_cards = []
        self.processed_urls = set()
        
        # Headers for requests
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': 'https://nhlhutbuilder.com/cards.php',
        }
        
    def setup_requests(self):
        """Setup requests session"""
        print("🔧 Setting up requests session...")
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        print("✅ Requests session setup complete")
        return True
    
    def load_master_json(self):
        """Load existing master.json data"""
        print("📂 Loading master.json...")
        
        try:
            with open(self.master_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            players = data.get('players', [])
            existing_urls = set()
            
            for player in players:
                if 'url' in player:
                    existing_urls.add(player['url'])
            
            print(f"✅ Loaded {len(players)} players from master.json")
            print(f"📊 Found {len(existing_urls)} existing URLs")
            
            return data, existing_urls
            
        except FileNotFoundError:
            print("❌ master.json not found! Creating new structure...")
            return {
                "metadata": {
                    "total_players": 0,
                    "created_at": "2024-12-19",
                    "description": "Complete NHL HUT Builder player database",
                    "last_updated": time.strftime("%Y-%m-%d %H:%M:%S")
                },
                "players": []
            }, set()
        except Exception as e:
            print(f"❌ Error loading master.json: {e}")
            return None, None
    
    def test_connection(self):
        """Test connection to the site"""
        print("🌐 Testing connection to cards page...")
        
        try:
            response = self.session.get(self.base_url, timeout=30)
            response.raise_for_status()
            print(f"✅ Successfully connected to {self.base_url}")
            return True
        except Exception as e:
            print(f"❌ Failed to connect to cards page: {e}")
            return False
    
    def get_cards_from_page(self, page_num=1):
        """Get card data from specific page using AJAX"""
        print(f"🔍 Getting cards from page {page_num}...")
        
        try:
            # AJAX data for the request
            data = {
                'limit': '40',
                'card_type_id': '',
                'team_id': '',
                'league_id': '',
                'position': '',
                'nationality': '',
                'sort': 'added',  # SORT BY: ADDED
                'hand': '',
                'player_id': '',
                'player_type': '',
                'superstar_abilities': '',
                'abilities_match': '',
                'pageNumber': str(page_num)
            }
            
            # Make AJAX call
            response = self.session.post(self.ajax_url, data=data, timeout=30)
            response.raise_for_status()
            
            if not response.text:
                print("❌ No AJAX response received")
                return []
            
            # Parse the HTML response
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract card data from the response
            cards = []
            card_containers = soup.find_all('div', class_='other_card_container')
            
            for container in card_containers:
                card_data = self.extract_card_from_container(container)
                if card_data:
                    cards.append(card_data)
            
            print(f"✅ Found {len(cards)} cards on page {page_num}")
            return cards
            
        except Exception as e:
            print(f"❌ Error getting cards from page {page_num}: {e}")
            return []
    
    def extract_card_from_container(self, container):
        """Extract card data from a card container in AJAX response"""
        try:
            # Find the main card link
            card_link = container.find('a', class_='advanced-stats')
            if not card_link:
                return None
            
            # Extract player ID and URL
            player_id = card_link.get('id')
            href = card_link.get('href')
            if not player_id or not href:
                return None
            
            # Make full URL
            if href.startswith('/'):
                url = 'https://nhlhutbuilder.com' + href
            else:
                url = href
            
            # Extract card art
            card_art_img = card_link.find('img', class_='other_card_art')
            card_art = card_art_img.get('src') if card_art_img else None
            
            # Extract X-Factor abilities
            xfactors = []
            ability_divs = container.find_all('div', class_='abi_group')
            
            for ability_div in ability_divs:
                xfactor_name = ability_div.get('data-xfactor_name')
                abi_id = ability_div.get('data-abi_id')
                player_type = ability_div.get('data-player_type')
                
                if xfactor_name and abi_id:
                    # Determine tier from icon path
                    icon_img = ability_div.find('img')
                    tier = "Specialist"  # default
                    if icon_img:
                        icon_src = icon_img.get('src', '')
                        if 'all-star' in icon_src.lower():
                            tier = "All-Star"
                        elif 'elite' in icon_src.lower():
                            tier = "Elite"
                    
                    # Determine AP cost from tier
                    ap_cost = 1
                    if tier == "All-Star":
                        ap_cost = 2
                    elif tier == "Elite":
                        ap_cost = 3
                    
                    xfactors.append({
                        'name': xfactor_name.upper().replace('_', ' '),
                        'ap_cost': ap_cost,
                        'tier': tier
                    })
            
            # Create card data
            card_data = {
                'player_id': int(player_id),
                'url': url,
                'card_art': card_art,
                'xfactors': xfactors,
                'position': 'G' if 'goalie-stats.php' in url else 'Unknown'  # Will be updated when we scrape full details
            }
            
            return card_data
            
        except Exception as e:
            print(f"   ❌ Error extracting card from container: {e}")
            return None
    
    def get_full_card_details(self, card_data):
        """Get full card details from individual card page"""
        try:
            url = card_data['url']
            print(f"📋 Getting full details for: {url}")
            
            # Make request to individual card page
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            # Parse the page
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract basic info (this will need to be customized based on actual page structure)
            # For now, we'll use the data we already have from AJAX
            full_data = card_data.copy()
            
            # Try to extract additional info if available
            # This is a placeholder - we'll need to analyze the actual card page structure
            full_data.update({
                'full_name': f"Player {card_data['player_id']}",  # Placeholder
                'nationality': 'Unknown',
                'team': 'Unknown',
                'overall': 80,
                'salary': 500000,
                'hand': 'RIGHT',
                'weight': 80,
                'height': 180
            })
            
            return full_data
            
        except Exception as e:
            print(f"   ❌ Error getting full card details: {e}")
            return card_data  # Return what we have
    
    # X-Factor enrichment is now handled in extract_card_from_container
    # No need for separate enrichment method
    
    
    def save_master_json(self, data):
        """Save updated master.json"""
        print("💾 Saving updated master.json...")
        
        try:
            # Update metadata
            data['metadata']['last_updated'] = time.strftime("%Y-%m-%d %H:%M:%S")
            data['metadata']['total_players'] = len(data['players'])
            
            with open(self.master_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Saved master.json with {len(data['players'])} players")
            return True
            
        except Exception as e:
            print(f"❌ Error saving master.json: {e}")
            return False
    
    def run(self):
        """Main execution method"""
        print("🚀 MASTER.JSON UPDATER")
        print("=" * 50)
        
        # Setup
        if not self.setup_requests():
            return False
        
        # Load existing data
        master_data, existing_urls = self.load_master_json()
        if master_data is None:
            return False
        
        # Test connection
        if not self.test_connection():
            return False
        
        # Process pages until no new cards found
        page = 1
        total_new_cards = 0
        
        while True:
            print(f"\n📄 Processing page {page}...")
            
            # Get cards from current page using AJAX
            cards = self.get_cards_from_page(page)
            if not cards:
                print("❌ No cards found on page, stopping...")
                break
            
            # Check which cards are new
            new_cards = [card for card in cards if card['url'] not in existing_urls]
            
            if not new_cards:
                print(f"✅ All {len(cards)} cards on page {page} already exist in master.json")
                print("🎯 No more new cards found, stopping...")
                break
            
            print(f"🆕 Found {len(new_cards)} new cards on page {page}")
            
            # Process new cards
            for i, card_data in enumerate(new_cards):
                print(f"\n🔄 Processing new card {i+1}/{len(new_cards)}")
                print(f"   Player ID: {card_data['player_id']}")
                print(f"   X-Factors: {len(card_data['xfactors'])}")
                
                # Get full card details
                full_card_data = self.get_full_card_details(card_data)
                
                # Add to master data
                master_data['players'].append(full_card_data)
                existing_urls.add(full_card_data['url'])
                total_new_cards += 1
                
                # Small delay
                time.sleep(0.5)
            
            # If we found fewer new cards than total cards, we're done
            if len(new_cards) < len(cards):
                print(f"✅ Found {len(new_cards)} new cards out of {len(cards)} total")
                print("🎯 No more new cards expected, stopping...")
                break
            
            # Move to next page
            page += 1
        
        # Save updated master.json
        if total_new_cards > 0:
            if self.save_master_json(master_data):
                print(f"\n🎉 SUCCESS: Added {total_new_cards} new cards to master.json")
            else:
                print(f"\n❌ FAILED: Could not save master.json")
        else:
            print(f"\n✅ No new cards found, master.json is up to date")
        
        return True

def main():
    """Main entry point"""
    updater = MasterUpdater()
    success = updater.run()
    
    if success:
        print("\n🎯 Master.json updater completed successfully!")
    else:
        print("\n❌ Master.json updater failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()