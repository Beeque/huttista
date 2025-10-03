#!/usr/bin/env python3
"""
NHL Team Builder - GUI Application
Suunnittele kokoonpanoja ja peliketjuja master.json datan pohjalta
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, simpledialog, filedialog
import json
import requests
from PIL import Image, ImageTk
import io
import threading
import time
from typing import List, Dict, Optional, Set
import os
import sys

class NHLTeamBuilder:
    def __init__(self, root):
        self.root = root
        self.root.title("🏒 NHL Team Builder")
        self.root.geometry("1400x900")
        self.root.configure(bg='#1e1e1e')
        
        # Variables
        self.master_data = None
        self.players = []
        self.filtered_players = []
        self.current_team = {}
        self.budget = 100_000_000  # 100 million
        self.current_spend = 0
        
        # Team structure: 4 lines + 3 D pairs + 1 G pair
        self.team_slots = {
            # Forward lines (LW-C-RW)
            'line1_lw': None, 'line1_c': None, 'line1_rw': None,
            'line2_lw': None, 'line2_c': None, 'line2_rw': None,
            'line3_lw': None, 'line3_c': None, 'line3_rw': None,
            'line4_lw': None, 'line4_c': None, 'line4_rw': None,
            # Defense pairs (LD-RD)
            'pair1_ld': None, 'pair1_rd': None,
            'pair2_ld': None, 'pair2_rd': None,
            'pair3_ld': None, 'pair3_rd': None,
            # Goalie pair (G-G)
            'goalie1': None, 'goalie2': None
        }
        
        # Filters
        self.filters = {
            'nationality': set(),
            'team': set(),
            'min_overall': 0
        }
        
        # Load data
        self.load_master_data()
        
        # Create GUI
        self.create_gui()
        
        # Update initial display
        self.update_filtered_players()
        
    def load_master_data(self):
        """Load master.json data"""
        try:
            with open('master.json', 'r', encoding='utf-8') as f:
                self.master_data = json.load(f)
            self.players = self.master_data.get('players', [])
            print(f"Loaded {len(self.players)} players from master.json")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load master.json: {e}")
            
    def create_gui(self):
        """Create the main GUI"""
        # Main container
        main_frame = tk.Frame(self.root, bg='#1e1e1e')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(main_frame, text="🏒 NHL Team Builder", 
                              font=('Arial', 24, 'bold'), 
                              bg='#1e1e1e', fg='white')
        title_label.pack(pady=(0, 20))
        
        # Top toolbar
        self.create_toolbar(main_frame)
        
        # Main content area
        content_frame = tk.Frame(main_frame, bg='#1e1e1e')
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - Filters and player list
        self.create_left_panel(content_frame)
        
        # Right panel - Team builder
        self.create_right_panel(content_frame)
        
    def create_toolbar(self, parent):
        """Create top toolbar"""
        toolbar_frame = tk.Frame(parent, bg='#2b2b2b', padx=10, pady=10)
        toolbar_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Budget display
        self.budget_label = tk.Label(toolbar_frame, text=f"Budget: ${self.budget:,}", 
                                    font=('Arial', 12, 'bold'), 
                                    bg='#2b2b2b', fg='#4CAF50')
        self.budget_label.pack(side=tk.LEFT)
        
        # Spent display
        self.spent_label = tk.Label(toolbar_frame, text=f"Spent: ${self.current_spend:,}", 
                                   font=('Arial', 12), 
                                   bg='#2b2b2b', fg='#FF9800')
        self.spent_label.pack(side=tk.LEFT, padx=(20, 0))
        
        # Remaining display
        self.remaining_label = tk.Label(toolbar_frame, text=f"Remaining: ${self.budget - self.current_spend:,}", 
                                       font=('Arial', 12), 
                                       bg='#2b2b2b', fg='#2196F3')
        self.remaining_label.pack(side=tk.LEFT, padx=(20, 0))
        
        # Buttons
        button_frame = tk.Frame(toolbar_frame, bg='#2b2b2b')
        button_frame.pack(side=tk.RIGHT)
        
        save_btn = tk.Button(button_frame, text="💾 Save Team", 
                            font=('Arial', 10, 'bold'),
                            bg='#4CAF50', fg='white', 
                            padx=15, pady=5,
                            command=self.save_team)
        save_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        load_btn = tk.Button(button_frame, text="📂 Load Team", 
                            font=('Arial', 10, 'bold'),
                            bg='#2196F3', fg='white', 
                            padx=15, pady=5,
                            command=self.load_team)
        load_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        clear_btn = tk.Button(button_frame, text="🗑️ Clear Team", 
                             font=('Arial', 10, 'bold'),
                             bg='#f44336', fg='white', 
                             padx=15, pady=5,
                             command=self.clear_team)
        clear_btn.pack(side=tk.LEFT)
        
    def create_left_panel(self, parent):
        """Create left panel with filters and player list"""
        left_frame = tk.Frame(parent, bg='#2b2b2b', width=400)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_frame.pack_propagate(False)
        
        # Filters section
        filters_frame = tk.LabelFrame(left_frame, text="🔍 Filters", 
                                     font=('Arial', 12, 'bold'),
                                     bg='#2b2b2b', fg='white', 
                                     padx=10, pady=10)
        filters_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Min Overall filter
        tk.Label(filters_frame, text="Min Overall:", 
                font=('Arial', 10), bg='#2b2b2b', fg='white').pack(anchor=tk.W)
        self.min_overall_var = tk.IntVar(value=0)
        overall_scale = tk.Scale(filters_frame, from_=0, to=99, 
                                orient=tk.HORIZONTAL, variable=self.min_overall_var,
                                bg='#2b2b2b', fg='white', 
                                command=self.on_filter_change)
        overall_scale.pack(fill=tk.X, pady=(5, 10))
        
        # Nationality filter
        tk.Label(filters_frame, text="Nationality:", 
                font=('Arial', 10), bg='#2b2b2b', fg='white').pack(anchor=tk.W)
        self.nationality_var = tk.StringVar()
        
        # Get unique nationalities
        nationalities = set()
        for p in self.players:
            nat = p.get('nationality', '')
            if nat:
                nationalities.add(nat)
        
        nationality_combo = ttk.Combobox(filters_frame, textvariable=self.nationality_var,
                                        values=['All'] + sorted(list(nationalities)),
                                        state='readonly')
        nationality_combo.pack(fill=tk.X, pady=(5, 10))
        nationality_combo.set('All')
        nationality_combo.bind('<<ComboboxSelected>>', self.on_filter_change)
        
        # Team filter
        tk.Label(filters_frame, text="Team:", 
                font=('Arial', 10), bg='#2b2b2b', fg='white').pack(anchor=tk.W)
        self.team_var = tk.StringVar()
        
        # Get unique teams
        teams = set()
        for p in self.players:
            team = p.get('team', '')
            if team:
                teams.add(team)
        
        team_combo = ttk.Combobox(filters_frame, textvariable=self.team_var,
                                 values=['All'] + sorted(list(teams)),
                                 state='readonly')
        team_combo.pack(fill=tk.X, pady=(5, 10))
        team_combo.set('All')
        team_combo.bind('<<ComboboxSelected>>', self.on_filter_change)
        
        # Search box
        tk.Label(filters_frame, text="Search Player:", 
                font=('Arial', 10), bg='#2b2b2b', fg='white').pack(anchor=tk.W)
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(filters_frame, textvariable=self.search_var,
                               font=('Arial', 10), bg='#1e1e1e', fg='white')
        search_entry.pack(fill=tk.X, pady=(5, 10))
        search_entry.bind('<KeyRelease>', self.on_search_change)
        
        # Player list
        list_frame = tk.LabelFrame(left_frame, text="👥 Available Players", 
                                  font=('Arial', 12, 'bold'),
                                  bg='#2b2b2b', fg='white', 
                                  padx=10, pady=10)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Player listbox with scrollbar
        listbox_frame = tk.Frame(list_frame, bg='#2b2b2b')
        listbox_frame.pack(fill=tk.BOTH, expand=True)
        
        self.player_listbox = tk.Listbox(listbox_frame, font=('Consolas', 9), 
                                        bg='#1e1e1e', fg='white', 
                                        selectbackground='#4CAF50')
        player_scrollbar = ttk.Scrollbar(listbox_frame, orient=tk.VERTICAL, command=self.player_listbox.yview)
        self.player_listbox.configure(yscrollcommand=player_scrollbar.set)
        
        self.player_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        player_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind selection event
        self.player_listbox.bind('<<ListboxSelect>>', self.on_player_select)
        
    def create_right_panel(self, parent):
        """Create right panel with team builder"""
        right_frame = tk.Frame(parent, bg='#2b2b2b')
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Team builder title
        title_label = tk.Label(right_frame, text="🏒 Team Builder", 
                              font=('Arial', 16, 'bold'), 
                              bg='#2b2b2b', fg='white')
        title_label.pack(pady=(0, 20))
        
        # Team slots container
        self.team_frame = tk.Frame(right_frame, bg='#2b2b2b')
        self.team_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create team slots
        self.create_team_slots()
        
    def create_team_slots(self):
        """Create team slot layout"""
        # Clear existing slots
        for widget in self.team_frame.winfo_children():
            widget.destroy()
            
        # Forward lines
        for line_num in range(1, 5):
            line_frame = tk.Frame(self.team_frame, bg='#2b2b2b')
            line_frame.pack(fill=tk.X, pady=5)
            
            # Line label
            tk.Label(line_frame, text=f"Line {line_num}:", 
                    font=('Arial', 12, 'bold'), 
                    bg='#2b2b2b', fg='white', 
                    width=8).pack(side=tk.LEFT, padx=(0, 10))
            
            # Forward slots (LW-C-RW)
            for pos in ['lw', 'c', 'rw']:
                slot_id = f'line{line_num}_{pos}'
                self.create_player_slot(line_frame, slot_id, pos.upper())
                
            # Defense pair (only for lines 1-3)
            if line_num <= 3:
                tk.Label(line_frame, text="|", 
                        font=('Arial', 16), 
                        bg='#2b2b2b', fg='#666666').pack(side=tk.LEFT, padx=10)
                
                tk.Label(line_frame, text=f"Pair {line_num}:", 
                        font=('Arial', 12, 'bold'), 
                        bg='#2b2b2b', fg='white', 
                        width=8).pack(side=tk.LEFT, padx=(0, 10))
                
                for pos in ['ld', 'rd']:
                    slot_id = f'pair{line_num}_{pos}'
                    self.create_player_slot(line_frame, slot_id, pos.upper())
                    
        # Goalie pair
        goalie_frame = tk.Frame(self.team_frame, bg='#2b2b2b')
        goalie_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(goalie_frame, text="Goalies:", 
                font=('Arial', 12, 'bold'), 
                bg='#2b2b2b', fg='white', 
                width=8).pack(side=tk.LEFT, padx=(0, 10))
        
        for i in range(1, 3):
            slot_id = f'goalie{i}'
            self.create_player_slot(goalie_frame, slot_id, 'G')
            
    def create_player_slot(self, parent, slot_id, position):
        """Create a player slot"""
        slot_frame = tk.Frame(parent, bg='#1e1e1e', relief=tk.RAISED, bd=2)
        slot_frame.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Position label
        pos_label = tk.Label(slot_frame, text=position, 
                            font=('Arial', 10, 'bold'), 
                            bg='#1e1e1e', fg='#cccccc')
        pos_label.pack(pady=2)
        
        # Player card frame
        card_frame = tk.Frame(slot_frame, bg='#1e1e1e', width=120, height=160)
        card_frame.pack(pady=2)
        card_frame.pack_propagate(False)
        
        # Player info label
        info_label = tk.Label(card_frame, text="Empty", 
                             font=('Arial', 8), 
                             bg='#1e1e1e', fg='#666666',
                             wraplength=110)
        info_label.pack(expand=True)
        
        # Store references
        slot_frame.slot_id = slot_id
        slot_frame.card_frame = card_frame
        slot_frame.info_label = info_label
        slot_frame.player_data = None
        
        # Bind click event
        slot_frame.bind("<Button-1>", lambda e: self.on_slot_click(slot_id))
        card_frame.bind("<Button-1>", lambda e: self.on_slot_click(slot_id))
        info_label.bind("<Button-1>", lambda e: self.on_slot_click(slot_id))
        
    def on_filter_change(self, event=None):
        """Handle filter changes"""
        self.update_filtered_players()
        
    def on_search_change(self, event=None):
        """Handle search changes"""
        self.update_filtered_players()
        
    def update_filtered_players(self):
        """Update filtered player list"""
        # Get filter values
        min_overall = self.min_overall_var.get()
        nationality = self.nationality_var.get()
        team = self.team_var.get()
        search_text = self.search_var.get().lower()
        
        # Filter players
        self.filtered_players = []
        for player in self.players:
            # Overall filter
            if player.get('overall', 0) < min_overall:
                continue
                
            # Nationality filter
            if nationality != 'All' and player.get('nationality', '') != nationality:
                continue
                
            # Team filter
            if team != 'All' and player.get('team', '') != team:
                continue
                
            # Search filter
            if search_text:
                name = player.get('full_name', '').lower()
                if search_text not in name:
                    continue
                    
            self.filtered_players.append(player)
            
        # Update listbox
        self.player_listbox.delete(0, tk.END)
        for player in self.filtered_players:
            name = player.get('full_name', 'Unknown')
            overall = player.get('overall', 'N/A')
            position = player.get('position', 'N/A')
            team = player.get('team', 'N/A')
            display_text = f"{name} ({overall} OVR) - {position} - {team}"
            self.player_listbox.insert(tk.END, display_text)
            
    def on_player_select(self, event):
        """Handle player selection from list"""
        selection = self.player_listbox.curselection()
        if selection:
            player = self.filtered_players[selection[0]]
            self.selected_player = player
            print(f"Selected: {player.get('full_name', 'Unknown')}")
            
    def on_slot_click(self, slot_id):
        """Handle slot click"""
        if hasattr(self, 'selected_player'):
            self.assign_player_to_slot(slot_id, self.selected_player)
        else:
            messagebox.showinfo("Info", "Please select a player from the list first!")
            
    def assign_player_to_slot(self, slot_id, player):
        """Assign player to slot"""
        # Remove player from current slot if already assigned
        for sid, p in self.team_slots.items():
            if p and p.get('player_id') == player.get('player_id'):
                self.team_slots[sid] = None
                self.update_slot_display(sid)
                
        # Assign to new slot
        self.team_slots[slot_id] = player
        self.update_slot_display(slot_id)
        self.update_budget_display()
        
    def update_slot_display(self, slot_id):
        """Update slot display"""
        # Find the slot frame
        for widget in self.team_frame.winfo_children():
            if hasattr(widget, 'winfo_children'):
                for child in widget.winfo_children():
                    if hasattr(child, 'slot_id') and child.slot_id == slot_id:
                        self.update_slot_frame(child)
                        return
                        
    def update_slot_frame(self, slot_frame):
        """Update individual slot frame"""
        player = self.team_slots[slot_frame.slot_id]
        
        if player:
            name = player.get('full_name', 'Unknown')
            overall = player.get('overall', 'N/A')
            position = player.get('position', 'N/A')
            team = player.get('team', 'N/A')
            
            # Update info label
            info_text = f"{name}\n{overall} OVR\n{position}\n{team}"
            slot_frame.info_label.config(text=info_text, fg='white')
            
            # TODO: Load and display card image
            # self.load_card_image(slot_frame, player)
        else:
            slot_frame.info_label.config(text="Empty", fg='#666666')
            
    def update_budget_display(self):
        """Update budget display"""
        self.current_spend = 0
        for player in self.team_slots.values():
            if player:
                salary = player.get('salary', 0)
                if isinstance(salary, (int, float)):
                    self.current_spend += salary
                    
        self.spent_label.config(text=f"Spent: ${self.current_spend:,}")
        remaining = self.budget - self.current_spend
        self.remaining_label.config(text=f"Remaining: ${remaining:,}")
        
        # Change color based on budget
        if remaining < 0:
            self.remaining_label.config(fg='#f44336')
        elif remaining < 10_000_000:
            self.remaining_label.config(fg='#FF9800')
        else:
            self.remaining_label.config(fg='#2196F3')
            
    def save_team(self):
        """Save current team"""
        team_name = simpledialog.askstring("Save Team", "Enter team name:")
        if not team_name:
            return
            
        team_data = {
            'name': team_name,
            'players': self.team_slots,
            'budget': self.budget,
            'spent': self.current_spend,
            'timestamp': time.time()
        }
        
        filename = f"team_{team_name.replace(' ', '_')}.json"
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(team_data, f, indent=2, ensure_ascii=False)
            messagebox.showinfo("Success", f"Team saved as {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save team: {e}")
            
    def load_team(self):
        """Load saved team"""
        filename = filedialog.askopenfilename(
            title="Load Team",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if not filename:
            return
            
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                team_data = json.load(f)
                
            self.team_slots = team_data.get('players', {})
            self.budget = team_data.get('budget', 100_000_000)
            
            # Update all slot displays
            for slot_id in self.team_slots.keys():
                self.update_slot_display(slot_id)
                
            self.update_budget_display()
            messagebox.showinfo("Success", f"Team loaded: {team_data.get('name', 'Unknown')}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load team: {e}")
            
    def clear_team(self):
        """Clear current team"""
        if messagebox.askyesno("Clear Team", "Are you sure you want to clear the current team?"):
            self.team_slots = {slot_id: None for slot_id in self.team_slots.keys()}
            
            # Update all slot displays
            for slot_id in self.team_slots.keys():
                self.update_slot_display(slot_id)
                
            self.update_budget_display()

def main():
    """Main function"""
    root = tk.Tk()
    app = NHLTeamBuilder(root)
    
    # Handle window close
    def on_closing():
        root.destroy()
        
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Start the GUI
    root.mainloop()

if __name__ == "__main__":
    main()