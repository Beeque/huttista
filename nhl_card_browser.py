#!/usr/bin/env python3
"""
NHL HUT Builder Card Browser
Windows desktop application for browsing and managing NHL cards
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
import threading
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging
from PIL import Image, ImageTk
import requests
from io import BytesIO

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataManager:
    """Manages JSON data loading and caching"""
    
    def __init__(self):
        self.data = {}
        self.cards = []
        self.filtered_cards = []
        self.current_index = 0
        
    def load_data(self, directory: str = "data"):
        """Load all JSON files from directory"""
        self.data = {}
        self.cards = []
        
        data_path = Path(directory)
        if not data_path.exists():
            logger.warning(f"Data directory {directory} not found")
            return False
        
        json_files = list(data_path.glob("*.json"))
        logger.info(f"Found {len(json_files)} JSON files")
        
        for file_path in json_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    file_data = json.load(f)
                
                # Handle both direct array and metadata wrapper formats
                if isinstance(file_data, dict) and 'data' in file_data:
                    cards = file_data['data']
                    metadata = file_data.get('metadata', {})
                else:
                    cards = file_data
                    metadata = {}
                
                # Add source info to each card
                for card in cards:
                    card['_source_file'] = file_path.name
                    card['_metadata'] = metadata
                
                self.data[file_path.stem] = cards
                self.cards.extend(cards)
                
                logger.info(f"Loaded {len(cards)} cards from {file_path.name}")
                
            except Exception as e:
                logger.error(f"Failed to load {file_path}: {e}")
        
        logger.info(f"Total cards loaded: {len(self.cards)}")
        self.filtered_cards = self.cards.copy()
        return True
    
    def filter_cards(self, filters: Dict[str, Any]) -> List[Dict]:
        """Filter cards based on criteria"""
        filtered = self.cards.copy()
        
        for key, value in filters.items():
            if value and value != "All":
                if key == "nationality":
                    filtered = [c for c in filtered if c.get('nationality', '').lower() == value.lower()]
                elif key == "team":
                    filtered = [c for c in filtered if c.get('team', '').upper() == value.upper()]
                elif key == "league":
                    filtered = [c for c in filtered if c.get('league', '').upper() == value.upper()]
                elif key == "position":
                    filtered = [c for c in filtered if c.get('position', '').upper() == value.upper()]
                elif key == "hand":
                    filtered = [c for c in filtered if c.get('hand', '').upper() == value.upper()]
                elif key == "card_type":
                    filtered = [c for c in filtered if c.get('card', '').upper() == value.upper()]
                elif key == "x_factors":
                    if value == "Yes":
                        filtered = [c for c in filtered if c.get('abilities') and len(c.get('abilities', [])) > 0]
                    elif value == "No":
                        filtered = [c for c in filtered if not c.get('abilities') or len(c.get('abilities', [])) == 0]
        
        # Sort cards
        sort_by = filters.get('sort_by', 'overall')
        if sort_by == 'overall':
            filtered.sort(key=lambda x: x.get('overall', 0), reverse=True)
        elif sort_by == 'name':
            filtered.sort(key=lambda x: x.get('full_name', ''))
        elif sort_by == 'team':
            filtered.sort(key=lambda x: x.get('team', ''))
        elif sort_by == 'salary':
            filtered.sort(key=lambda x: x.get('salary', 0), reverse=True)
        
        self.filtered_cards = filtered
        self.current_index = 0
        return filtered
    
    def get_current_card(self) -> Optional[Dict]:
        """Get current card"""
        if 0 <= self.current_index < len(self.filtered_cards):
            return self.filtered_cards[self.current_index]
        return None
    
    def next_card(self):
        """Move to next card"""
        if self.current_index < len(self.filtered_cards) - 1:
            self.current_index += 1
    
    def prev_card(self):
        """Move to previous card"""
        if self.current_index > 0:
            self.current_index -= 1
    
    def get_card_count(self) -> int:
        """Get total number of filtered cards"""
        return len(self.filtered_cards)

class CardDisplay:
    """Handles card image display with overlapping effect"""
    
    def __init__(self, parent):
        self.parent = parent
        self.canvas = tk.Canvas(parent, width=800, height=600, bg='#1a1a1a')
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        self.card_images = {}
        self.card_objects = []
        
    def load_card_image(self, card: Dict) -> Optional[ImageTk.PhotoImage]:
        """Load card image from URL or file"""
        if not card:
            return None
        
        # Try to get image from card_art field
        image_url = card.get('card_art', '')
        if not image_url:
            return None
        
        # Convert relative URL to absolute
        if image_url.startswith('images/'):
            image_url = f"https://nhlhutbuilder.com/{image_url}"
        
        try:
            # Check cache first
            if image_url in self.card_images:
                return self.card_images[image_url]
            
            # Download image
            response = requests.get(image_url, timeout=10)
            response.raise_for_status()
            
            # Create PIL Image
            pil_image = Image.open(BytesIO(response.content))
            
            # Resize to card size (150x200)
            pil_image = pil_image.resize((150, 200), Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage
            photo = ImageTk.PhotoImage(pil_image)
            
            # Cache the image
            self.card_images[image_url] = photo
            
            return photo
            
        except Exception as e:
            logger.warning(f"Failed to load image for {card.get('full_name', 'Unknown')}: {e}")
            return None
    
    def display_cards(self, cards: List[Dict], current_index: int):
        """Display cards with overlapping effect"""
        self.canvas.delete("all")
        self.card_objects = []
        
        if not cards:
            self.canvas.create_text(400, 300, text="No cards found", fill="white", font=("Arial", 16))
            return
        
        # Calculate positions for overlapping cards
        center_x = 400
        center_y = 300
        
        # Show current card and a few cards behind it
        start_idx = max(0, current_index - 2)
        end_idx = min(len(cards), current_index + 3)
        
        for i in range(start_idx, end_idx):
            card = cards[i]
            is_current = (i == current_index)
            
            # Calculate position with offset
            offset_x = (i - current_index) * 20
            offset_y = (i - current_index) * 10
            
            x = center_x + offset_x
            y = center_y + offset_y
            
            # Load card image
            image = self.load_card_image(card)
            
            if image:
                # Create card object
                card_obj = self.canvas.create_image(x, y, image=image, anchor=tk.CENTER)
                self.card_objects.append(card_obj)
                
                # Add card info text
                name = card.get('full_name', 'Unknown')
                overall = card.get('overall', 0)
                position = card.get('position', '')
                
                # Card info background
                info_bg = self.canvas.create_rectangle(
                    x - 75, y + 100, x + 75, y + 130,
                    fill='black', outline='white', width=2
                )
                
                # Card info text
                info_text = f"{name}\n{overall} {position}"
                self.canvas.create_text(
                    x, y + 115, text=info_text, fill='white',
                    font=("Arial", 10, "bold"), justify=tk.CENTER
                )
                
                # Highlight current card
                if is_current:
                    self.canvas.create_rectangle(
                        x - 80, y - 110, x + 80, y + 110,
                        outline='#00ff00', width=3
                    )
            else:
                # Fallback: show text card
                self.canvas.create_rectangle(
                    x - 75, y - 100, x + 75, y + 100,
                    fill='#333333', outline='white', width=2
                )
                
                name = card.get('full_name', 'Unknown')
                overall = card.get('overall', 0)
                position = card.get('position', '')
                
                self.canvas.create_text(
                    x, y, text=f"{name}\n{overall} {position}",
                    fill='white', font=("Arial", 12, "bold"),
                    justify=tk.CENTER
                )

class FilterPanel:
    """Filter controls panel"""
    
    def __init__(self, parent, data_manager: DataManager, on_filter_change):
        self.parent = parent
        self.data_manager = data_manager
        self.on_filter_change = on_filter_change
        
        self.frame = ttk.Frame(parent)
        self.frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.filters = {}
        self.create_filters()
    
    def create_filters(self):
        """Create filter controls"""
        # Sort by
        ttk.Label(self.frame, text="Sort by:").grid(row=0, column=0, padx=5, sticky=tk.W)
        self.filters['sort_by'] = ttk.Combobox(self.frame, values=['overall', 'name', 'team', 'salary'], width=10)
        self.filters['sort_by'].set('overall')
        self.filters['sort_by'].grid(row=0, column=1, padx=5)
        
        # Card Type
        ttk.Label(self.frame, text="Card Type:").grid(row=0, column=2, padx=5, sticky=tk.W)
        self.filters['card_type'] = ttk.Combobox(self.frame, values=['All'], width=10)
        self.filters['card_type'].set('All')
        self.filters['card_type'].grid(row=0, column=3, padx=5)
        
        # Team
        ttk.Label(self.frame, text="Team:").grid(row=0, column=4, padx=5, sticky=tk.W)
        self.filters['team'] = ttk.Combobox(self.frame, values=['All'], width=10)
        self.filters['team'].set('All')
        self.filters['team'].grid(row=0, column=5, padx=5)
        
        # League
        ttk.Label(self.frame, text="League:").grid(row=1, column=0, padx=5, sticky=tk.W)
        self.filters['league'] = ttk.Combobox(self.frame, values=['All'], width=10)
        self.filters['league'].set('All')
        self.filters['league'].grid(row=1, column=1, padx=5)
        
        # Nationality
        ttk.Label(self.frame, text="Nationality:").grid(row=1, column=2, padx=5, sticky=tk.W)
        self.filters['nationality'] = ttk.Combobox(self.frame, values=['All'], width=10)
        self.filters['nationality'].set('All')
        self.filters['nationality'].grid(row=1, column=3, padx=5)
        
        # Position
        ttk.Label(self.frame, text="Position:").grid(row=1, column=4, padx=5, sticky=tk.W)
        self.filters['position'] = ttk.Combobox(self.frame, values=['All', 'LW', 'RW', 'C', 'D', 'G'], width=10)
        self.filters['position'].set('All')
        self.filters['position'].grid(row=1, column=5, padx=5)
        
        # Hand
        ttk.Label(self.frame, text="Hand:").grid(row=2, column=0, padx=5, sticky=tk.W)
        self.filters['hand'] = ttk.Combobox(self.frame, values=['All', 'LEFT', 'RIGHT'], width=10)
        self.filters['hand'].set('All')
        self.filters['hand'].grid(row=2, column=1, padx=5)
        
        # X-Factors
        ttk.Label(self.frame, text="X-Factors:").grid(row=2, column=2, padx=5, sticky=tk.W)
        self.filters['x_factors'] = ttk.Combobox(self.frame, values=['All', 'Yes', 'No'], width=10)
        self.filters['x_factors'].set('All')
        self.filters['x_factors'].grid(row=2, column=3, padx=5)
        
        # Apply button
        apply_btn = ttk.Button(self.frame, text="Apply Filters", command=self.apply_filters)
        apply_btn.grid(row=2, column=4, padx=5)
        
        # Clear button
        clear_btn = ttk.Button(self.frame, text="Clear All", command=self.clear_filters)
        clear_btn.grid(row=2, column=5, padx=5)
    
    def update_filter_options(self):
        """Update filter options based on loaded data"""
        if not self.data_manager.cards:
            return
        
        # Get unique values for each filter
        teams = sorted(set(card.get('team', '') for card in self.data_manager.cards if card.get('team')))
        nationalities = sorted(set(card.get('nationality', '') for card in self.data_manager.cards if card.get('nationality')))
        leagues = sorted(set(card.get('league', '') for card in self.data_manager.cards if card.get('league')))
        card_types = sorted(set(card.get('card', '') for card in self.data_manager.cards if card.get('card')))
        
        # Debug: print available options
        print(f"Teams: {teams[:10]}...")  # Show first 10
        print(f"Nationalities: {nationalities[:10]}...")
        print(f"Leagues: {leagues}")
        print(f"Card Types: {card_types}")
        
        # Update comboboxes
        self.filters['team']['values'] = ['All'] + teams
        self.filters['nationality']['values'] = ['All'] + nationalities
        self.filters['league']['values'] = ['All'] + leagues
        self.filters['card_type']['values'] = ['All'] + card_types
    
    def apply_filters(self):
        """Apply current filters"""
        filter_values = {}
        for key, widget in self.filters.items():
            filter_values[key] = widget.get()
        
        self.data_manager.filter_cards(filter_values)
        self.on_filter_change()
    
    def clear_filters(self):
        """Clear all filters"""
        for widget in self.filters.values():
            if isinstance(widget, ttk.Combobox):
                widget.set('All')
        self.apply_filters()

class QueueManager:
    """Manages scraping queue"""
    
    def __init__(self, parent):
        self.parent = parent
        self.queue = []
        self.is_running = False
        self.current_progress = 0
        self.total_progress = 0
        
        self.create_ui()
    
    def create_ui(self):
        """Create queue management UI"""
        self.frame = ttk.LabelFrame(self.parent, text="Scraping Queue", padding=10)
        self.frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Queue status
        self.status_label = ttk.Label(self.frame, text="Queue: 0 items")
        self.status_label.pack(anchor=tk.W)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X, pady=5)
        
        # Control buttons
        btn_frame = ttk.Frame(self.frame)
        btn_frame.pack(fill=tk.X, pady=5)
        
        self.start_btn = ttk.Button(btn_frame, text="Start Scraping", command=self.start_scraping)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.pause_btn = ttk.Button(btn_frame, text="Pause", command=self.pause_scraping, state=tk.DISABLED)
        self.pause_btn.pack(side=tk.LEFT, padx=5)
        
        self.clear_btn = ttk.Button(btn_frame, text="Clear Queue", command=self.clear_queue)
        self.clear_btn.pack(side=tk.LEFT, padx=5)
        
        # Queue list
        self.queue_listbox = tk.Listbox(self.frame, height=6)
        self.queue_listbox.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Remove selected button
        self.remove_btn = ttk.Button(self.frame, text="Remove Selected", command=self.remove_selected)
        self.remove_btn.pack(anchor=tk.W)
    
    def add_to_queue(self, item: Dict):
        """Add item to queue"""
        self.queue.append(item)
        self.update_display()
    
    def remove_selected(self):
        """Remove selected items from queue"""
        selected = self.queue_listbox.curselection()
        for index in reversed(selected):
            if 0 <= index < len(self.queue):
                del self.queue[index]
        self.update_display()
    
    def clear_queue(self):
        """Clear all items from queue"""
        self.queue.clear()
        self.update_display()
    
    def update_display(self):
        """Update queue display"""
        self.status_label.config(text=f"Queue: {len(self.queue)} items")
        
        self.queue_listbox.delete(0, tk.END)
        for i, item in enumerate(self.queue):
            self.queue_listbox.insert(tk.END, f"{i+1}. {item.get('name', 'Unknown')} ({item.get('count', 0)} cards)")
    
    def start_scraping(self):
        """Start scraping process"""
        if not self.queue:
            messagebox.showwarning("Warning", "Queue is empty")
            return
        
        self.is_running = True
        self.start_btn.config(state=tk.DISABLED)
        self.pause_btn.config(state=tk.NORMAL)
        
        # Start scraping in separate thread
        thread = threading.Thread(target=self._scraping_worker)
        thread.daemon = True
        thread.start()
    
    def pause_scraping(self):
        """Pause scraping process"""
        self.is_running = False
        self.start_btn.config(state=tk.NORMAL)
        self.pause_btn.config(state=tk.DISABLED)
    
    def _scraping_worker(self):
        """Scraping worker thread"""
        self.total_progress = len(self.queue)
        self.current_progress = 0
        
        for i, item in enumerate(self.queue):
            if not self.is_running:
                break
            
            # Update progress
            self.current_progress = i + 1
            progress = (self.current_progress / self.total_progress) * 100
            
            # Update UI in main thread
            self.parent.after(0, lambda p=progress: self.progress_var.set(p))
            
            # Simulate scraping work
            time.sleep(2)
            
            logger.info(f"Scraped {item.get('name', 'Unknown')}")
        
        # Reset UI
        self.parent.after(0, self._scraping_finished)
    
    def _scraping_finished(self):
        """Called when scraping is finished"""
        self.is_running = False
        self.start_btn.config(state=tk.NORMAL)
        self.pause_btn.config(state=tk.DISABLED)
        self.progress_var.set(0)
        
        messagebox.showinfo("Complete", "Scraping completed!")

class NHLCardBrowser:
    """Main application class"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("NHL HUT Builder - Card Browser")
        self.root.geometry("1200x800")
        self.root.configure(bg='#2b2b2b')
        
        # Initialize components
        self.data_manager = DataManager()
        self.card_display = None
        self.filter_panel = None
        self.queue_manager = None
        
        self.create_ui()
        self.load_data()
    
    def create_ui(self):
        """Create main UI"""
        # Menu bar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Load Data", command=self.load_data)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Filter panel
        self.filter_panel = FilterPanel(main_frame, self.data_manager, self.on_filter_change)
        
        # Card display
        self.card_display = CardDisplay(main_frame)
        
        # Navigation controls
        nav_frame = ttk.Frame(main_frame)
        nav_frame.pack(fill=tk.X, pady=5)
        
        self.prev_btn = ttk.Button(nav_frame, text="◀ Previous", command=self.prev_card)
        self.prev_btn.pack(side=tk.LEFT, padx=5)
        
        self.next_btn = ttk.Button(nav_frame, text="Next ▶", command=self.next_card)
        self.next_btn.pack(side=tk.LEFT, padx=5)
        
        self.card_info_label = ttk.Label(nav_frame, text="Card 0 of 0")
        self.card_info_label.pack(side=tk.LEFT, padx=20)
        
        # Queue manager
        self.queue_manager = QueueManager(main_frame)
        
        # Bind keyboard shortcuts
        self.root.bind('<Left>', lambda e: self.prev_card())
        self.root.bind('<Right>', lambda e: self.next_card())
        self.root.bind('<space>', lambda e: self.next_card())
    
    def load_data(self):
        """Load data from JSON files"""
        directory = filedialog.askdirectory(title="Select Data Directory", initialdir="data")
        if directory:
            if self.data_manager.load_data(directory):
                self.filter_panel.update_filter_options()
                self.on_filter_change()
                messagebox.showinfo("Success", f"Loaded {len(self.data_manager.cards)} cards")
            else:
                messagebox.showerror("Error", "Failed to load data")
    
    def on_filter_change(self):
        """Called when filters change"""
        self.update_display()
    
    def update_display(self):
        """Update card display"""
        if self.data_manager.filtered_cards:
            self.card_display.display_cards(
                self.data_manager.filtered_cards,
                self.data_manager.current_index
            )
            self.update_navigation()
        else:
            self.card_display.canvas.delete("all")
            self.card_display.canvas.create_text(400, 300, text="No cards found", fill="white", font=("Arial", 16))
    
    def update_navigation(self):
        """Update navigation controls"""
        total = self.data_manager.get_card_count()
        current = self.data_manager.current_index + 1
        self.card_info_label.config(text=f"Card {current} of {total}")
        
        # Update button states
        self.prev_btn.config(state=tk.NORMAL if self.data_manager.current_index > 0 else tk.DISABLED)
        self.next_btn.config(state=tk.NORMAL if self.data_manager.current_index < total - 1 else tk.DISABLED)
    
    def prev_card(self):
        """Go to previous card"""
        self.data_manager.prev_card()
        self.update_display()
    
    def next_card(self):
        """Go to next card"""
        self.data_manager.next_card()
        self.update_display()
    
    def run(self):
        """Start the application"""
        self.root.mainloop()

def main():
    """Main entry point"""
    try:
        app = NHLCardBrowser()
        app.run()
    except Exception as e:
        logger.error(f"Application failed: {e}")
        messagebox.showerror("Error", f"Application failed: {e}")

if __name__ == "__main__":
    main()