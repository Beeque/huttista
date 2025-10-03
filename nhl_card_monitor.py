#!/usr/bin/env python3
"""
NHL Card Monitor - Windows GUI Application
Automaattinen korttien seuranta ja X-Factor rikastus
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

# Import our existing modules
from update_missing_cards_final import (
    check_total_entries, load_master_json, get_master_urls, 
    find_missing_urls, fetch_cards_page, make_request_with_retry, config
)
from enrich_country_xfactors import fetch_xfactors_with_tiers

class NHLCardMonitor:
    def __init__(self, root):
        self.root = root
        self.root.title("NHL Card Monitor - Automatic Card Tracker")
        self.root.geometry("1200x800")
        self.root.configure(bg='#2b2b2b')
        
        # Variables
        self.monitoring = False
        self.monitor_thread = None
        self.last_check = None
        self.master_data = None
        self.master_urls = set()
        
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
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = ttk.Label(main_frame, text="🏒 NHL Card Monitor", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Control panel
        control_frame = ttk.LabelFrame(main_frame, text="Controls", padding=10)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(fill=tk.X)
        
        self.find_cards_btn = ttk.Button(button_frame, text="🔍 Find New Cards", 
                                        command=self.find_cards_manual)
        self.find_cards_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.monitor_btn = ttk.Button(button_frame, text="▶️ Start Monitoring", 
                                     command=self.toggle_monitoring)
        self.monitor_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.refresh_btn = ttk.Button(button_frame, text="🔄 Refresh Data", 
                                     command=self.load_master_data)
        self.refresh_btn.pack(side=tk.LEFT)
        
        # Status frame
        status_frame = ttk.LabelFrame(main_frame, text="Status", padding=10)
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.status_label = ttk.Label(status_frame, text="Ready to monitor cards...")
        self.status_label.pack(anchor=tk.W)
        
        self.last_check_label = ttk.Label(status_frame, text="Last check: Never")
        self.last_check_label.pack(anchor=tk.W)
        
        # Progress bar
        self.progress = ttk.Progressbar(status_frame, mode='indeterminate')
        self.progress.pack(fill=tk.X, pady=(5, 0))
        
        # Content area
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - New cards
        left_frame = ttk.LabelFrame(content_frame, text="New Cards Found", padding=10)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Cards listbox with scrollbar
        cards_frame = ttk.Frame(left_frame)
        cards_frame.pack(fill=tk.BOTH, expand=True)
        
        self.cards_listbox = tk.Listbox(cards_frame, font=('Consolas', 10))
        cards_scrollbar = ttk.Scrollbar(cards_frame, orient=tk.VERTICAL, command=self.cards_listbox.yview)
        self.cards_listbox.configure(yscrollcommand=cards_scrollbar.set)
        
        self.cards_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        cards_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Card image frame
        self.image_frame = ttk.LabelFrame(left_frame, text="Card Image", padding=10)
        self.image_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.image_label = ttk.Label(self.image_frame, text="Select a card to view image")
        self.image_label.pack()
        
        # Bind selection event
        self.cards_listbox.bind('<<ListboxSelect>>', self.on_card_select)
        
        # Right panel - Log
        right_frame = ttk.LabelFrame(content_frame, text="Activity Log", padding=10)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        self.log_text = scrolledtext.ScrolledText(right_frame, font=('Consolas', 9), 
                                                 bg='#1e1e1e', fg='#ffffff', 
                                                 insertbackground='white')
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Configure text tags for colored logging
        self.log_text.tag_configure("INFO", foreground="#00ff00")
        self.log_text.tag_configure("WARNING", foreground="#ffff00")
        self.log_text.tag_configure("ERROR", foreground="#ff0000")
        self.log_text.tag_configure("SUCCESS", foreground="#00ffff")
        
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
                self.display_new_cards(all_missing_urls)
            else:
                self.log_message("No new cards found!", "SUCCESS")
                self.update_status("No new cards found")
                
        except Exception as e:
            self.log_message(f"Error finding cards: {e}", "ERROR")
            self.update_status(f"Error: {e}")
        finally:
            self.progress.stop()
            self.find_cards_btn.config(state='normal')
            
    def display_new_cards(self, missing_urls):
        """Display new cards in the listbox"""
        self.cards_listbox.delete(0, tk.END)
        
        for i, url in enumerate(missing_urls):
            # Extract player name from URL if possible
            try:
                # Try to get player info from the URL
                player_info = self.get_player_info_from_url(url)
                display_text = f"{i+1:3d}. {player_info}"
            except:
                display_text = f"{i+1:3d}. {url}"
                
            self.cards_listbox.insert(tk.END, display_text)
            
        self.log_message(f"Displayed {len(missing_urls)} new cards", "SUCCESS")
        
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
            self.image_label.config(text="Card image would be displayed here")
            
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
    app = NHLCardMonitor(root)
    
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