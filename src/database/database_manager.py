"""
Tietokannan hallinta NHL 26 HUT Team Builder -sovellukselle.
"""

import sqlite3
import os
from typing import List, Dict, Optional

class DatabaseManager:
    """SQLite-tietokannan hallintaluokka."""
    
    def __init__(self, db_path: str = "hut_players.db"):
        """Alustaa tietokannan hallintaluokan.
        
        Args:
            db_path: Tietokantatiedoston polku
        """
        self.db_path = db_path
        self.connection = None
    
    def connect(self):
        """Yhdistää tietokantaan."""
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row
    
    def disconnect(self):
        """Sulkee tietokantayhteyden."""
        if self.connection:
            self.connection.close()
    
    def database_exists(self) -> bool:
        """Tarkistaa onko tietokanta olemassa."""
        return os.path.exists(self.db_path)
    
    def create_database(self):
        """Luo tietokannan ja taulut."""
        self.connect()
        
        # Pelaajataulu
        self.connection.execute("""
            CREATE TABLE IF NOT EXISTS players (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                team TEXT NOT NULL,
                nationality TEXT NOT NULL,
                position TEXT NOT NULL,
                overall_rating INTEGER NOT NULL,
                salary INTEGER NOT NULL,
                ap_points INTEGER NOT NULL,
                card_type TEXT,
                rarity TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Kemiat-taulu
        self.connection.execute("""
            CREATE TABLE IF NOT EXISTS chemistries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                boost_type TEXT NOT NULL, -- 'ovr', 'salary_cap', 'ap'
                boost_value INTEGER NOT NULL,
                requirements TEXT NOT NULL, -- JSON-muodossa
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Lisää oletuskemiat
        self._insert_default_chemistries()
        
        self.connection.commit()
        self.disconnect()
    
    def _insert_default_chemistries(self):
        """Lisää oletuskemiat tietokantaan."""
        chemistries = [
            {
                'name': 'Chicago Blackhawks + Suomi',
                'description': '2x Chicago Blackhawks + 1x Suomi hyökkäyskolmikossa',
                'boost_type': 'ovr',
                'boost_value': 2,
                'requirements': '{"team_blackhawks": 2, "nationality_finland": 1, "position_forward": 3}'
            },
            {
                'name': 'Kolme suomalaista hyökkääjää',
                'description': '3x Suomi hyökkäyskolmikossa',
                'boost_type': 'salary_cap',
                'boost_value': 2000000,
                'requirements': '{"nationality_finland": 3, "position_forward": 3}'
            },
            {
                'name': 'Sama joukkue puolustuksessa',
                'description': '2x sama joukkue puolustuksessa',
                'boost_type': 'ap',
                'boost_value': 5,
                'requirements': '{"position_defense": 2, "same_team": true}'
            }
        ]
        
        for chem in chemistries:
            self.connection.execute("""
                INSERT INTO chemistries (name, description, boost_type, boost_value, requirements)
                VALUES (?, ?, ?, ?, ?)
            """, (chem['name'], chem['description'], chem['boost_type'], 
                  chem['boost_value'], chem['requirements']))
    
    def add_player(self, player_data: Dict) -> int:
        """Lisää pelaajan tietokantaan.
        
        Args:
            player_data: Pelaajan tiedot sanakirjana
            
        Returns:
            Lisätyn pelaajan ID
        """
        self.connect()
        
        cursor = self.connection.execute("""
            INSERT INTO players (name, team, nationality, position, overall_rating, 
                               salary, ap_points, card_type, rarity)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            player_data['name'],
            player_data['team'],
            player_data['nationality'],
            player_data['position'],
            player_data['overall_rating'],
            player_data['salary'],
            player_data['ap_points'],
            player_data.get('card_type', ''),
            player_data.get('rarity', '')
        ))
        
        player_id = cursor.lastrowid
        self.connection.commit()
        self.disconnect()
        
        return player_id
    
    def get_all_players(self) -> List[Dict]:
        """Hakee kaikki pelaajat tietokannasta.
        
        Returns:
            Lista pelaajista sanakirjoina
        """
        self.connect()
        
        cursor = self.connection.execute("SELECT * FROM players ORDER BY overall_rating DESC")
        players = [dict(row) for row in cursor.fetchall()]
        
        self.disconnect()
        return players
    
    def get_players_by_position(self, position: str) -> List[Dict]:
        """Hakee pelaajat aseman mukaan.
        
        Args:
            position: Pelaajan asema ('C', 'LW', 'RW', 'LD', 'RD', 'G')
            
        Returns:
            Lista pelaajista sanakirjoina
        """
        self.connect()
        
        cursor = self.connection.execute(
            "SELECT * FROM players WHERE position = ? ORDER BY overall_rating DESC",
            (position,)
        )
        players = [dict(row) for row in cursor.fetchall()]
        
        self.disconnect()
        return players
    
    def get_players_by_team(self, team: str) -> List[Dict]:
        """Hakee pelaajat joukkueen mukaan.
        
        Args:
            team: Joukkueen nimi
            
        Returns:
            Lista pelaajista sanakirjoina
        """
        self.connect()
        
        cursor = self.connection.execute(
            "SELECT * FROM players WHERE team = ? ORDER BY overall_rating DESC",
            (team,)
        )
        players = [dict(row) for row in cursor.fetchall()]
        
        self.disconnect()
        return players
    
    def get_players_by_nationality(self, nationality: str) -> List[Dict]:
        """Hakee pelaajat kansallisuuden mukaan.
        
        Args:
            nationality: Kansallisuus
            
        Returns:
            Lista pelaajista sanakirjoina
        """
        self.connect()
        
        cursor = self.connection.execute(
            "SELECT * FROM players WHERE nationality = ? ORDER BY overall_rating DESC",
            (nationality,)
        )
        players = [dict(row) for row in cursor.fetchall()]
        
        self.disconnect()
        return players
    
    def search_players(self, query: str) -> List[Dict]:
        """Hakee pelaajia hakusanalla.
        
        Args:
            query: Hakusana
            
        Returns:
            Lista pelaajista sanakirjoina
        """
        self.connect()
        
        cursor = self.connection.execute(
            "SELECT * FROM players WHERE name LIKE ? ORDER BY overall_rating DESC",
            (f"%{query}%",)
        )
        players = [dict(row) for row in cursor.fetchall()]
        
        self.disconnect()
        return players
    
    def get_chemistries(self) -> List[Dict]:
        """Hakee kaikki kemiat tietokannasta.
        
        Returns:
            Lista kemioista sanakirjoina
        """
        self.connect()
        
        cursor = self.connection.execute("SELECT * FROM chemistries")
        chemistries = [dict(row) for row in cursor.fetchall()]
        
        self.disconnect()
        return chemistries