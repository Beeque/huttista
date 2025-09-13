"""
Pelaajakorttien tietojen hakeminen NHL HUT Builder -sivustolta.
"""

import requests
from bs4 import BeautifulSoup
import time
import json
from typing import List, Dict, Optional
from ..database.database_manager import DatabaseManager

class PlayerScraper:
    """Pelaajakorttien tietojen hakeminen verkkosivustolta."""
    
    def __init__(self):
        """Alustaa scraperin."""
        self.base_url = "https://nhlhutbuilder.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.db_manager = DatabaseManager()
    
    def scrape_all_players(self):
        """Hakee kaikkien pelaajien tiedot."""
        print("Aloitetaan pelaajakorttien tietojen haku...")
        
        # Hae eri asemien pelaajat
        positions = ['C', 'LW', 'RW', 'LD', 'RD', 'G']
        
        for position in positions:
            print(f"Haetaan {position}-pelaajia...")
            players = self._scrape_players_by_position(position)
            
            for player in players:
                try:
                    self.db_manager.add_player(player)
                    print(f"Lisätty: {player['name']} ({player['team']}) - {player['overall_rating']} OVR")
                except Exception as e:
                    print(f"Virhe pelaajan {player['name']} lisäämisessä: {e}")
            
            # Odota hetki ennen seuraavaa pyyntöä
            time.sleep(1)
        
        print("Pelaajakorttien tietojen haku valmis!")
    
    def _scrape_players_by_position(self, position: str) -> List[Dict]:
        """Hakee tietyn aseman pelaajat.
        
        Args:
            position: Pelaajan asema
            
        Returns:
            Lista pelaajista sanakirjoina
        """
        players = []
        
        try:
            # Hae pelaajalista
            url = f"{self.base_url}/player-stats.php"
            params = {
                'position': position,
                'sort': 'overall',
                'order': 'desc'
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Etsi pelaajataulukko
            player_table = soup.find('table', {'class': 'player-stats-table'})
            if not player_table:
                print(f"Pelaajataulukkoa ei löytynyt asemalle {position}")
                return players
            
            # Jäsennä pelaajatiedot
            rows = player_table.find('tbody').find_all('tr')
            
            for row in rows:
                player_data = self._parse_player_row(row, position)
                if player_data:
                    players.append(player_data)
            
        except Exception as e:
            print(f"Virhe aseman {position} pelaajien hakemisessa: {e}")
        
        return players
    
    def _parse_player_row(self, row, position: str) -> Optional[Dict]:
        """Jäsennä pelaajan tiedot taulukkoriviltä.
        
        Args:
            row: BeautifulSoup-elementti taulukkoriville
            position: Pelaajan asema
            
        Returns:
            Pelaajan tiedot sanakirjana tai None
        """
        try:
            cells = row.find_all('td')
            if len(cells) < 6:
                return None
            
            # Oletetaan että taulukko on muodossa:
            # Nimi | Joukkue | Kansallisuus | OVR | Palkka | AP | Korttityyppi | Harvinaisuus
            name = cells[0].get_text(strip=True)
            team = cells[1].get_text(strip=True)
            nationality = cells[2].get_text(strip=True)
            overall_rating = int(cells[3].get_text(strip=True))
            salary = int(cells[4].get_text(strip=True).replace(',', ''))
            ap_points = int(cells[5].get_text(strip=True))
            
            card_type = cells[6].get_text(strip=True) if len(cells) > 6 else ""
            rarity = cells[7].get_text(strip=True) if len(cells) > 7 else ""
            
            return {
                'name': name,
                'team': team,
                'nationality': nationality,
                'position': position,
                'overall_rating': overall_rating,
                'salary': salary,
                'ap_points': ap_points,
                'card_type': card_type,
                'rarity': rarity
            }
            
        except (ValueError, IndexError) as e:
            print(f"Virhe rivin jäsentämisessä: {e}")
            return None
    
    def scrape_player_details(self, player_id: str) -> Optional[Dict]:
        """Hakee yksittäisen pelaajan yksityiskohtaiset tiedot.
        
        Args:
            player_id: Pelaajan ID
            
        Returns:
            Pelaajan yksityiskohtaiset tiedot tai None
        """
        try:
            url = f"{self.base_url}/player.php?id={player_id}"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Tämä voisi sisältää lisätietoja kuten statit, kuvat, jne.
            # Toteutetaan tarvittaessa myöhemmin
            
            return None
            
        except Exception as e:
            print(f"Virhe pelaajan {player_id} yksityiskohtaisten tietojen hakemisessa: {e}")
            return None
    
    def update_player_data(self):
        """Päivittää olemassa olevien pelaajien tiedot."""
        print("Päivitetään pelaajakorttien tiedot...")
        
        # Toteutetaan myöhemmin tarvittaessa
        # Tässä voisi olla logiikka joka tarkistaa onko korttien tiedot vanhentuneet
        
        pass