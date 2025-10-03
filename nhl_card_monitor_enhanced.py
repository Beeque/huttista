#!/usr/bin/env python3
"""
NHL Card Monitor - Enhanced Windows GUI Application
Automaattinen korttien seuranta, X-Factor rikastus ja kuvien näyttö
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import time
import json
import requests
from bs4 import BeautifulSoup
from PIL import Image, ImageTk
import io
import logging
from datetime import datetime
import os
import sys
import re
from urllib.parse import urlparse, parse_qs

# Import our existing modules
from update_missing_cards_final import (
    check_total_entries, load_master_json, get_master_urls, 
    find_missing_urls, fetch_cards_page, make_request_with_retry, config
)
from enrich_country_xfactors import fetch_xfactors_with_tiers

class NHLCardMonitorEnhanced:
    def __init__(self, root):
        self.root = root
        self.root.title("🏒 NHL Card Monitor - Automatic Card Tracker")
        self.root.geometry("1400x900")
        self.root.configure(bg='#1e1e1e')
        
        # Variables
        self.monitoring = False
        self.monitor_thread = None
        self.last_check = None
        self.master_data = None
        self.master_urls = set()
        self.new_cards_data = []  # Store new cards with full data
        self.current_card_image = None
        
        # Setup logging
        self.setup_logging()
        
        # Create GUI
        self.create_widgets()
        
        # Load initial data
        self.load_master_data()
        
    def setup_logging(self):
        """Setup logging for the application"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('nhl_monitor.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def create_widgets(self):
        """Create the main GUI widgets"""
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Title.TLabel', font=('Arial', 18, 'bold'), background='#1e1e1e', foreground='white')
        style.configure('Header.TLabel', font=('Arial', 12, 'bold'), background='#1e1e1e', foreground='#00ffff')
        
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = ttk.Label(main_frame, text="🏒 NHL Card Monitor - Automatic Card Tracker", 
                               style='Title.TLabel')
        title_label.pack(pady=(0, 20))
        
        # Control panel
        control_frame = ttk.LabelFrame(main_frame, text="🎮 Controls", padding=15)
        control_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(fill=tk.X)
        
        self.find_cards_btn = ttk.Button(button_frame, text="🔍 Find New Cards", 
                                        command=self.find_cards_manual, width=15)
        self.find_cards_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.monitor_btn = ttk.Button(button_frame, text="▶️ Start Monitoring", 
                                     command=self.toggle_monitoring, width=15)
        self.monitor_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.refresh_btn = ttk.Button(button_frame, text="🔄 Refresh Data", 
                                     command=self.load_master_data, width=15)
        self.refresh_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.enrich_btn = ttk.Button(button_frame, text="⚡ Enrich X-Factors", 
                                    command=self.enrich_xfactors, width=15)
        self.enrich_btn.pack(side=tk.LEFT)
        
        # Status frame
        status_frame = ttk.LabelFrame(main_frame, text="📊 Status", padding=10)
        status_frame.pack(fill=tk.X, pady=(0, 15))
        
        status_grid = ttk.Frame(status_frame)
        status_grid.pack(fill=tk.X)
        
        self.status_label = ttk.Label(status_grid, text="Ready to monitor cards...", 
                                     style='Header.TLabel')
        self.status_label.grid(row=0, column=0, sticky=tk.W, padx=(0, 20))
        
        self.last_check_label = ttk.Label(status_grid, text="Last check: Never", 
                                         style='Header.TLabel')
        self.last_check_label.grid(row=0, column=1, sticky=tk.W)
        
        # Progress bar
        self.progress = ttk.Progressbar(status_frame, mode='indeterminate')
        self.progress.pack(fill=tk.X, pady=(10, 0))
        
        # Content area
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - New cards
        left_frame = ttk.LabelFrame(content_frame, text="🆕 New Cards Found", padding=10)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Cards treeview
        cards_frame = ttk.Frame(left_frame)
        cards_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create treeview for cards
        columns = ('Name', 'Position', 'Team', 'Overall')
        self.cards_tree = ttk.Treeview(cards_frame, columns=columns, show='headings', height=15)
        
        # Define headings
        self.cards_tree.heading('Name', text='Player Name')
        self.cards_tree.heading('Position', text='Position')
        self.cards_tree.heading('Team', text='Team')
        self.cards_tree.heading('Overall', text='Overall')
        
        # Configure column widths
        self.cards_tree.column('Name', width=200)
        self.cards_tree.column('Position', width=80)
        self.cards_tree.column('Team', width=120)
        self.cards_tree.column('Overall', width=80)
        
        # Scrollbar for treeview
        cards_scrollbar = ttk.Scrollbar(cards_frame, orient=tk.VERTICAL, command=self.cards_tree.yview)
        self.cards_tree.configure(yscrollcommand=cards_scrollbar.set)
        
        self.cards_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        cards_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Card details frame
        details_frame = ttk.LabelFrame(left_frame, text="📋 Card Details", padding=10)
        details_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.details_text = scrolledtext.ScrolledText(details_frame, height=8, font=('Consolas', 9),
                                                     bg='#2b2b2b', fg='#ffffff', 
                                                     insertbackground='white')
        self.details_text.pack(fill=tk.X)
        
        # Card image frame
        self.image_frame = ttk.LabelFrame(left_frame, text="🖼️ Card Image", padding=10)
        self.image_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.image_label = ttk.Label(self.image_frame, text="Select a card to view image and details")
        self.image_label.pack()
        
        # Bind selection event
        self.cards_tree.bind('<<TreeviewSelect>>', self.on_card_select)
        
        # Right panel - Log
        right_frame = ttk.LabelFrame(content_frame, text="📝 Activity Log", padding=10)
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
        
    def load_master_data(self):
        """Load master.json data"""
        try:
            self.update_status("Loading master.json...")
            self.master_data, players = load_master_json()
            if self.master_data:
                self.master_urls = get_master_urls(players)
                self.update_status(f"Loaded {len(players)} players from master.json")
                self.log_message(f"Loaded {len(players)} players from master.json", "SUCCESS")
            else:
                self.update_status("Failed to load master.json")
                self.log_message("Failed to load master.json", "ERROR")
        except Exception as e:
            self.update_status(f"Error loading master.json: {e}")
            self.log_message(f"Error loading master.json: {e}", "ERROR")
            
    def find_cards_manual(self):
        """Manual card finding"""
        if not self.master_data:
            messagebox.showerror("Error", "Please load master.json first!")
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
            self.update_status("Checking for new cards...")
            self.log_message("Starting manual card search...", "INFO")
            
            # Check if there are new cards
            if not check_total_entries():
                self.log_message("No new cards found!", "SUCCESS")
                self.update_status("No new cards found")
                return
                
            # Find missing cards
            all_missing_urls = []
            page = 1
            
            while page <= config.max_pages:
                self.update_status(f"Checking page {page}...")
                self.log_message(f"Checking page {page}...", "INFO")
                
                cards_urls = fetch_cards_page(page)
                if not cards_urls:
                    break
                    
                missing_urls, found_urls = find_missing_urls(cards_urls, self.master_urls)
                all_missing_urls.extend(missing_urls)
                
                if not missing_urls:
                    break
                    
                page += 1
                time.sleep(config.page_delay)
                
            if all_missing_urls:
                self.log_message(f"Found {len(all_missing_urls)} new cards!", "SUCCESS")
                self.update_status(f"Found {len(all_missing_urls)} new cards")
                self.fetch_new_cards_data(all_missing_urls)
            else:
                self.log_message("No new cards found!", "SUCCESS")
                self.update_status("No new cards found")
                
        except Exception as e:
            self.log_message(f"Error finding cards: {e}", "ERROR")
            self.update_status(f"Error: {e}")
        finally:
            self.progress.stop()
            self.find_cards_btn.config(state='normal')
            
    def fetch_new_cards_data(self, missing_urls):
        """Fetch detailed data for new cards"""
        self.log_message("Fetching detailed card data...", "INFO")
        self.new_cards_data = []
        
        for i, url in enumerate(missing_urls):
            try:
                self.update_status(f"Fetching card {i+1}/{len(missing_urls)}...")
                card_data = self.fetch_card_details(url)
                if card_data:
                    self.new_cards_data.append(card_data)
                    self.log_message(f"Fetched: {card_data.get('name', 'Unknown')}", "SUCCESS")
                    
            except Exception as e:
                self.log_message(f"Error fetching card {i+1}: {e}", "ERROR")
                
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
            self.logger.error(f"Error fetching card details: {e}")
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
                            
        except Exception as e:
            self.logger.error(f"Error extracting stats: {e}")
            
    def display_new_cards(self):
        """Display new cards in the treeview"""
        # Clear existing items
        for item in self.cards_tree.get_children():
            self.cards_tree.delete(item)
            
        # Add new cards
        for card in self.new_cards_data:
            self.cards_tree.insert('', 'end', values=(
                card.get('name', 'Unknown'),
                card.get('position', 'N/A'),
                card.get('team', 'N/A'),
                card.get('overall', 'N/A')
            ))
            
        self.log_message(f"Displayed {len(self.new_cards_data)} new cards", "SUCCESS")
        
    def on_card_select(self, event):
        """Handle card selection"""
        selection = self.cards_tree.selection()
        if selection:
            item = self.cards_tree.item(selection[0])
            card_name = item['values'][0]
            
            # Find the selected card data
            selected_card = None
            for card in self.new_cards_data:
                if card.get('name') == card_name:
                    selected_card = card
                    break
                    
            if selected_card:
                self.display_card_details(selected_card)
                self.load_card_image(selected_card)
                
    def display_card_details(self, card):
        """Display detailed card information"""
        self.details_text.delete(1.0, tk.END)
        
        details = f"Player: {card.get('name', 'Unknown')}\n"
        details += f"Position: {card.get('position', 'N/A')}\n"
        details += f"Team: {card.get('team', 'N/A')}\n"
        details += f"Overall: {card.get('overall', 'N/A')}\n"
        details += f"Nationality: {card.get('nationality', 'N/A')}\n"
        details += f"Height: {card.get('height', 'N/A')}\n"
        details += f"Weight: {card.get('weight', 'N/A')}\n"
        details += f"Hand: {card.get('hand', 'N/A')}\n"
        details += f"Player ID: {card.get('player_id', 'N/A')}\n"
        details += f"Type: {'Goalie' if card.get('is_goalie') else 'Skater'}\n"
        
        # Add X-Factor info if available
        if 'xfactors' in card and card['xfactors']:
            details += f"\nX-Factor Abilities ({len(card['xfactors'])}):\n"
            for xf in card['xfactors']:
                details += f"  • {xf.get('name', 'Unknown')} ({xf.get('tier', 'N/A')})\n"
        else:
            details += "\nX-Factor Abilities: Not loaded\n"
            
        self.details_text.insert(1.0, details)
        
    def load_card_image(self, card):
        """Load and display card image"""
        try:
            image_url = card.get('image_url')
            if not image_url:
                self.image_label.config(text="No image available")
                return
                
            # Download image
            response = requests.get(image_url, timeout=10)
            if response.status_code == 200:
                # Load image with PIL
                image = Image.open(io.BytesIO(response.content))
                
                # Resize image to fit in the frame
                max_size = (200, 300)
                image.thumbnail(max_size, Image.Resampling.LANCZOS)
                
                # Convert to PhotoImage
                self.current_card_image = ImageTk.PhotoImage(image)
                self.image_label.config(image=self.current_card_image, text="")
            else:
                self.image_label.config(text="Failed to load image")
                
        except Exception as e:
            self.log_message(f"Error loading image: {e}", "ERROR")
            self.image_label.config(text="Error loading image")
            
    def enrich_xfactors(self):
        """Enrich selected cards with X-Factor data"""
        if not self.new_cards_data:
            messagebox.showwarning("Warning", "No new cards to enrich!")
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
            self.update_status("Enriching X-Factor data...")
            self.log_message("Starting X-Factor enrichment...", "X-FACTOR")
            
            enriched_count = 0
            for i, card in enumerate(self.new_cards_data):
                if 'xfactors' not in card or not card['xfactors']:
                    self.update_status(f"Enriching card {i+1}/{len(self.new_cards_data)}...")
                    
                    player_id = card.get('player_id')
                    is_goalie = card.get('is_goalie', False)
                    
                    if player_id:
                        xfactors = fetch_xfactors_with_tiers(player_id, is_goalie=is_goalie)
                        card['xfactors'] = xfactors
                        
                        if xfactors:
                            enriched_count += 1
                            self.log_message(f"Enriched {card.get('name', 'Unknown')} with {len(xfactors)} X-Factors", "X-FACTOR")
                        else:
                            self.log_message(f"No X-Factors found for {card.get('name', 'Unknown')}", "WARNING")
                            
                    time.sleep(0.5)  # Be nice to the server
                    
            self.log_message(f"X-Factor enrichment complete! Enriched {enriched_count} cards", "SUCCESS")
            self.update_status(f"X-Factor enrichment complete! Enriched {enriched_count} cards")
            
        except Exception as e:
            self.log_message(f"Error during X-Factor enrichment: {e}", "ERROR")
            self.update_status(f"Error: {e}")
        finally:
            self.progress.stop()
            self.enrich_btn.config(state='normal')
            
    def toggle_monitoring(self):
        """Toggle automatic monitoring"""
        if not self.monitoring:
            self.start_monitoring()
        else:
            self.stop_monitoring()
            
    def start_monitoring(self):
        """Start automatic monitoring"""
        if not self.master_data:
            messagebox.showerror("Error", "Please load master.json first!")
            return
            
        self.monitoring = True
        self.monitor_btn.config(text="⏸️ Stop Monitoring")
        self.log_message("Started automatic monitoring (every 30 minutes)", "SUCCESS")
        
        # Start monitoring thread
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
    def stop_monitoring(self):
        """Stop automatic monitoring"""
        self.monitoring = False
        self.monitor_btn.config(text="▶️ Start Monitoring")
        self.log_message("Stopped automatic monitoring", "INFO")
        
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.monitoring:
            try:
                self.update_status("Checking for new cards...")
                self.log_message("Automatic check started...", "INFO")
                
                # Check for new cards
                if check_total_entries():
                    self.log_message("New cards detected! Running full scan...", "WARNING")
                    self._find_cards_thread()
                else:
                    self.log_message("No new cards found", "INFO")
                    
                self.last_check = datetime.now()
                self.last_check_label.config(text=f"Last check: {self.last_check.strftime('%H:%M:%S')}")
                
            except Exception as e:
                self.log_message(f"Monitoring error: {e}", "ERROR")
                
            # Wait 30 minutes (1800 seconds)
            for _ in range(1800):
                if not self.monitoring:
                    break
                time.sleep(1)

def main():
    """Main function"""
    root = tk.Tk()
    app = NHLCardMonitorEnhanced(root)
    
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