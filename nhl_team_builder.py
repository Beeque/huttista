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
from datetime import datetime

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
        
        
    
    def log_message(self, message, level="INFO"):
        """Add message to log display"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"
        
        # If we have a log text widget, use it
        if hasattr(self, 'log_text'):
            self.log_text.insert(tk.END, formatted_message, level)
            self.log_text.see(tk.END)
            self.root.update_idletasks()
        else:
            # Fallback to print for console
            print(formatted_message.strip())
        
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
        clear_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        
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
        invalid_nationalities = {'Age', 'N/A', '', 'Unknown', 'None', 'null'}
        
        for p in self.players:
            nat = p.get('nationality', '')
            if nat and nat not in invalid_nationalities and len(nat) > 1:
                nationalities.add(nat)
        
        nationality_combo = ttk.Combobox(filters_frame, textvariable=self.nationality_var,
                                        values=['All'] + sorted(list(nationalities)),
                                        state='readonly')
        nationality_combo.pack(fill=tk.X, pady=(5, 10))
        nationality_combo.set('All')
        nationality_combo.bind('<<ComboboxSelected>>', self.on_filter_change)
        
        # Team filter
        tk.Label(filters_frame, text="Team:", 
                font=('Arial', 10, 'bold'), bg='#2b2b2b', fg='white').pack(anchor=tk.W)
        self.team_var = tk.StringVar()
        
        # Get unique teams
        teams = set()
        invalid_teams = {'N/A', '', 'Unknown', 'None', 'null', 'Age'}
        
        for p in self.players:
            team = p.get('team', '')
            if team and team not in invalid_teams and len(team) > 1:
                teams.add(team)
        
        team_values = ['All'] + sorted(list(teams))
        
        # Create team combobox with better styling
        team_frame = tk.Frame(filters_frame, bg='#2b2b2b')
        team_frame.pack(fill=tk.X, pady=(5, 10))
        
        team_combo = ttk.Combobox(team_frame, textvariable=self.team_var,
                                 values=team_values,
                                 state='readonly',
                                 width=25,
                                 font=('Arial', 10))
        team_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        team_combo.set('All')
        team_combo.bind('<<ComboboxSelected>>', self.on_filter_change)
        
        
        # Store reference for debugging
        self.team_combo = team_combo
        
        
        # X-Factor filter
        tk.Label(filters_frame, text="X-Factor Ability:", 
                font=('Arial', 10), bg='#2b2b2b', fg='white').pack(anchor=tk.W)
        self.xfactor_var = tk.StringVar()
        
        # Get unique X-Factor abilities
        xfactors = set()
        
        try:
            for p in self.players:
                try:
                    # Try different X-Factor field names
                    xf_list = p.get('xfactors', []) or p.get('x_factor', []) or p.get('xfactor', []) or p.get('superstar_ability', [])
                    
                    # Handle both list and string formats
                    if isinstance(xf_list, list):
                        for xf in xf_list:
                            try:
                                # Make sure xf is a string and not a dict
                                if isinstance(xf, str) and xf not in {'N/A', '', 'Unknown', 'None', 'null'}:
                                    xfactors.add(xf)
                                elif isinstance(xf, dict):
                                    # If it's a dict, try to get the name or ability field
                                    xf_name = xf.get('name') or xf.get('ability') or xf.get('x_factor')
                                    if xf_name and isinstance(xf_name, str) and xf_name not in {'N/A', '', 'Unknown', 'None', 'null'}:
                                        xfactors.add(xf_name)
                                    else:
                                        # If name is not a string, try to convert to string
                                        try:
                                            xf_str = str(xf_name) if xf_name else str(xf)
                                            if xf_str not in {'N/A', '', 'Unknown', 'None', 'null', '{}'}:
                                                xfactors.add(xf_str)
                                        except:
                                            pass
                            except Exception:
                                continue
                    elif isinstance(xf_list, str) and xf_list not in {'N/A', '', 'Unknown', 'None', 'null'}:
                        xfactors.add(xf_list)
                except Exception:
                    continue
        except Exception:
            pass
        
        # Sort X-Factors by AP tier (AP1, AP2, AP3)
        def sort_xfactors(xf):
            if 'AP1' in xf or 'Specialist' in xf:
                return (1, xf)  # AP1 first
            elif 'AP2' in xf or 'All-Star' in xf:
                return (2, xf)  # AP2 second
            elif 'AP3' in xf or 'Elite' in xf:
                return (3, xf)  # AP3 third
            else:
                return (4, xf)  # Others last
        
        sorted_xfactors = sorted(list(xfactors), key=sort_xfactors)
        
        xfactor_combo = ttk.Combobox(filters_frame, textvariable=self.xfactor_var,
                                     values=['All'] + sorted_xfactors,
                                     state='readonly')
        xfactor_combo.pack(fill=tk.X, pady=(5, 10))
        xfactor_combo.set('All')
        xfactor_combo.bind('<<ComboboxSelected>>', self.on_filter_change)
        
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
        
        # Log area
        log_frame = tk.LabelFrame(left_frame, text="📝 Debug Log", 
                                 font=('Arial', 10, 'bold'),
                                 bg='#2b2b2b', fg='white', 
                                 padx=5, pady=5)
        log_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.log_text = scrolledtext.ScrolledText(log_frame, font=('Consolas', 8), 
                                                 bg='#1e1e1e', fg='#ffffff', 
                                                 insertbackground='white',
                                                 height=6)
        self.log_text.pack(fill=tk.X)
        
        # Configure text tags for colored logging
        self.log_text.tag_configure("INFO", foreground="#00ff00")
        self.log_text.tag_configure("WARNING", foreground="#ffff00")
        self.log_text.tag_configure("ERROR", foreground="#ff0000")
        self.log_text.tag_configure("SUCCESS", foreground="#00ffff")
        
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
        
        # Instructions
        instructions = tk.Label(right_frame, 
                               text="💡 Click a player from the list, then click a slot to assign them", 
                               font=('Arial', 10), 
                               bg='#2b2b2b', fg='#cccccc')
        instructions.pack(pady=(0, 10))
        
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
            
            # Goalies (only for line 4)
            if line_num == 4:
                tk.Label(line_frame, text="|", 
                        font=('Arial', 16), 
                        bg='#2b2b2b', fg='#666666').pack(side=tk.LEFT, padx=10)
                
                tk.Label(line_frame, text="Goalies:", 
                        font=('Arial', 12, 'bold'), 
                        bg='#2b2b2b', fg='white', 
                        width=8).pack(side=tk.LEFT, padx=(0, 10))
                
                for i in range(1, 3):
                    slot_id = f'goalie{i}'
                    self.create_player_slot(line_frame, slot_id, 'G')
                    
        # Add some spacing after team slots
        spacer_frame = tk.Frame(self.team_frame, bg='#2b2b2b', height=20)
        spacer_frame.pack(fill=tk.X)
            
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
        
        # Card image label - fills the entire card frame
        image_label = tk.Label(card_frame, text="", 
                              bg='#1e1e1e', fg='#666666')
        image_label.pack(fill=tk.BOTH, expand=True)
        
        # Player info label - overlay on top of image
        info_label = tk.Label(card_frame, text="Empty", 
                             font=('Arial', 8, 'bold'), 
                             bg='#1e1e1e', fg='white',
                             wraplength=110)
        info_label.place(relx=0.5, rely=0.9, anchor='s')  # Position at bottom center
        
        # Store references
        slot_frame.slot_id = slot_id
        slot_frame.card_frame = card_frame
        slot_frame.info_label = info_label
        slot_frame.image_label = image_label
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
        xfactor = self.xfactor_var.get()
        search_text = self.search_var.get().lower()
        
        
        # Filter players
        self.filtered_players = []
        for player in self.players:
            # Overall filter - handle both string and int
            overall = player.get('overall', 0)
            try:
                overall_num = int(overall) if overall else 0
            except (ValueError, TypeError):
                overall_num = 0
                
            if overall_num < min_overall:
                continue
                
            # Nationality filter
            if nationality != 'All' and player.get('nationality', '') != nationality:
                continue
                
            # Team filter
            if team != 'All' and player.get('team', '') != team:
                continue
                
            # X-Factor filter
            if xfactor != 'All':
                # Get X-Factor abilities from player
                xf_list = player.get('xfactors', []) or player.get('x_factor', []) or player.get('xfactor', []) or player.get('superstar_ability', [])
                
                # Check if player has the selected X-Factor (with or without AP tier info)
                has_xf = False
                if isinstance(xf_list, list):
                    for xf in xf_list:
                        if isinstance(xf, str):
                            # Check exact match or match without AP tier info
                            if (xf == xfactor or 
                                xf == xfactor.replace(' (AP1)', '').replace(' (AP2)', '').replace(' (AP3)', '') or
                                xfactor in xf):
                                has_xf = True
                                break
                        elif isinstance(xf, dict):
                            # Check if dict contains the X-Factor
                            xf_name = xf.get('name') or xf.get('ability') or xf.get('x_factor')
                            if xf_name:
                                xf_str = str(xf_name)
                                if (xf_str == xfactor or 
                                    xf_str == xfactor.replace(' (AP1)', '').replace(' (AP2)', '').replace(' (AP3)', '') or
                                    xfactor in xf_str):
                                    has_xf = True
                                    break
                elif isinstance(xf_list, str):
                    xf_str = xf_list
                    has_xf = (xf_str == xfactor or 
                             xf_str == xfactor.replace(' (AP1)', '').replace(' (AP2)', '').replace(' (AP3)', '') or
                             xfactor in xf_str)
                    
                if not has_xf:
                    continue
                
            # Search filter
            if search_text:
                # Try different name fields for search
                name = (player.get('full_name', '') or 
                       player.get('name', '') or 
                       player.get('player_name', '')).lower()
                if search_text not in name:
                    continue
                    
            self.filtered_players.append(player)
            
            
        # Update listbox
        self.player_listbox.delete(0, tk.END)
        for player in self.filtered_players:
            # Try different name fields
            name = (player.get('full_name') or 
                   player.get('name') or 
                   player.get('player_name') or 
                   'Unknown')
            
            overall = player.get('overall', 'N/A')
            # Ensure overall is displayed as string
            if isinstance(overall, (int, float)):
                overall = str(overall)
            position = player.get('position', 'N/A')
            team = player.get('team', 'N/A')
            
            # Get X-Factor abilities
            xf_list = player.get('xfactors', []) or player.get('x_factor', []) or player.get('xfactor', []) or player.get('superstar_ability', [])
            
            # Format X-Factor display with AP tiers
            if isinstance(xf_list, list) and xf_list:
                # Convert dict objects to strings and add AP tier info
                xf_strings = []
                for xf in xf_list:
                    if isinstance(xf, str):
                        # Add AP tier info if not already present
                        if 'AP1' in xf or 'Specialist' in xf:
                            xf_strings.append(f"{xf} (AP1)")
                        elif 'AP2' in xf or 'All-Star' in xf:
                            xf_strings.append(f"{xf} (AP2)")
                        elif 'AP3' in xf or 'Elite' in xf:
                            xf_strings.append(f"{xf} (AP3)")
                        else:
                            xf_strings.append(xf)
                    elif isinstance(xf, dict):
                        # Try to get name or ability from dict
                        xf_name = xf.get('name') or xf.get('ability') or xf.get('x_factor')
                        if xf_name:
                            xf_str = str(xf_name)
                            # Add AP tier info if not already present
                            if 'AP1' in xf_str or 'Specialist' in xf_str:
                                xf_strings.append(f"{xf_str} (AP1)")
                            elif 'AP2' in xf_str or 'All-Star' in xf_str:
                                xf_strings.append(f"{xf_str} (AP2)")
                            elif 'AP3' in xf_str or 'Elite' in xf_str:
                                xf_strings.append(f"{xf_str} (AP3)")
                            else:
                                xf_strings.append(xf_str)
                
                if xf_strings:
                    xf_text = f" [{', '.join(xf_strings)}]"
                else:
                    xf_text = ""
            elif isinstance(xf_list, str) and xf_list not in {'N/A', '', 'Unknown'}:
                # Add AP tier info if not already present
                if 'AP1' in xf_list or 'Specialist' in xf_list:
                    xf_text = f" [{xf_list} (AP1)]"
                elif 'AP2' in xf_list or 'All-Star' in xf_list:
                    xf_text = f" [{xf_list} (AP2)]"
                elif 'AP3' in xf_list or 'Elite' in xf_list:
                    xf_text = f" [{xf_list} (AP3)]"
                else:
                    xf_text = f" [{xf_list}]"
            else:
                xf_text = ""
            
            display_text = f"{name} ({overall} OVR) - {position} - {team}{xf_text}"
            self.player_listbox.insert(tk.END, display_text)
            
    def on_player_select(self, event):
        """Handle player selection from list"""
        selection = self.player_listbox.curselection()
        if selection:
            player = self.filtered_players[selection[0]]
            self.selected_player = player
            
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
            # Try different name fields
            name = (player.get('full_name') or 
                   player.get('name') or 
                   player.get('player_name') or 
                   'Unknown')
            
            overall = player.get('overall', 'N/A')
            # Ensure overall is displayed as string
            if isinstance(overall, (int, float)):
                overall = str(overall)
            position = player.get('position', 'N/A')
            team = player.get('team', 'N/A')
            
            # Update info label with better visibility
            info_text = f"{name}\n{overall} OVR\n{position}\n{team}"
            slot_frame.info_label.config(text=info_text, fg='white', 
                                       bg='#000000',  # Black background for better visibility
                                       relief=tk.RAISED, bd=1)
            
            # Load and display card image
            self.load_card_image(slot_frame, player)
        else:
            slot_frame.info_label.config(text="Empty", fg='#666666')
            # Clear image when slot is empty
            slot_frame.image_label.config(image='', text='')
            
    def load_card_image(self, slot_frame, player):
        """Load and display card image"""
        try:
            # Try different image URL fields
            image_url = (player.get('image_url', '') or 
                        player.get('card_image', '') or 
                        player.get('image', '') or 
                        player.get('card_art', ''))
            
            # If we have a relative path, make it absolute
            if image_url and not image_url.startswith('http'):
                if image_url.startswith('images/'):
                    image_url = f"https://nhlhutbuilder.com/{image_url}"
                else:
                    image_url = f"https://nhlhutbuilder.com/{image_url}"
            
            if not image_url:
                # Try to get image from URL field
                url = player.get('url', '')
                if url:
                    # Extract player ID and construct image URL
                    player_id = self.extract_player_id_from_url(url)
                    if player_id:
                        image_url = f"https://nhlhutbuilder.com/card_images/{player_id}.png"
                
            if image_url:
                # Load image in background thread
                threading.Thread(target=self._load_image_thread, 
                               args=(slot_frame, image_url), 
                               daemon=True).start()
            else:
                # Show placeholder
                slot_frame.image_label.config(text="No Image", fg='#666666')
                
        except Exception:
            slot_frame.image_label.config(text="Error", fg='#ff0000')
            
    def _load_image_thread(self, slot_frame, image_url):
        """Load image in background thread"""
        try:
            response = requests.get(image_url, timeout=10)
            
            if response.status_code == 200:
                # Load image with PIL
                image = Image.open(io.BytesIO(response.content))
                
                # Resize to fit slot (120x160 to fill the entire card)
                image.thumbnail((120, 160), Image.Resampling.LANCZOS)
                
                # Convert to PhotoImage
                photo = ImageTk.PhotoImage(image)
                
                # Update UI in main thread
                self.root.after(0, self._update_image, slot_frame, photo)
            else:
                self.root.after(0, self._update_image_error, slot_frame)
                
        except Exception:
            self.root.after(0, self._update_image_error, slot_frame)
            
    def _update_image(self, slot_frame, photo):
        """Update image in main thread"""
        try:
            slot_frame.image_label.config(image=photo, text='')
            # Keep reference to prevent garbage collection
            slot_frame.image_label.photo = photo
            
            # Hide info text when image is loaded
            slot_frame.info_label.config(text='')
        except Exception:
            pass
            
    def _update_image_error(self, slot_frame):
        """Update image error in main thread"""
        slot_frame.image_label.config(image='', text="No Image", fg='#666666')
        
        # Show player info when image fails to load
        player = self.team_slots[slot_frame.slot_id]
        if player:
            name = (player.get('full_name') or 
                   player.get('name') or 
                   player.get('player_name') or 
                   'Unknown')
            overall = player.get('overall', 'N/A')
            if isinstance(overall, (int, float)):
                overall = str(overall)
            position = player.get('position', 'N/A')
            team = player.get('team', 'N/A')
            
            info_text = f"{name}\n{overall} OVR\n{position}\n{team}"
            slot_frame.info_label.config(text=info_text, fg='white', 
                                       bg='#000000', relief=tk.RAISED, bd=1)
        
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
            
    def update_budget_display(self):
        """Update budget display"""
        self.current_spend = 0
        for player in self.team_slots.values():
            if player:
                salary = player.get('salary', 0)
                try:
                    # Handle both string and numeric salaries
                    if isinstance(salary, str):
                        # Remove currency symbols and convert
                        salary_str = salary.replace('$', '').replace(',', '').replace('M', '').replace('K', '')
                        if 'M' in str(salary):
                            salary_num = float(salary_str) * 1_000_000
                        elif 'K' in str(salary):
                            salary_num = float(salary_str) * 1_000
                        else:
                            salary_num = float(salary_str)
                    else:
                        salary_num = float(salary) if salary else 0
                    self.current_spend += salary_num
                except (ValueError, TypeError):
                    # If can't parse salary, assume 0
                    pass
                    
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