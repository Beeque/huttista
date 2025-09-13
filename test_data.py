"""
Testidatan luonti NHL 26 HUT Team Builder -sovellukselle.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from database.database_manager import DatabaseManager

def create_test_data():
    """Luo testidataa tietokantaan."""
    db_manager = DatabaseManager()
    
    # Luo tietokanta jos se ei ole olemassa
    if not db_manager.database_exists():
        db_manager.create_database()
    
    # Testipelaajia
    test_players = [
        # Hyökkääjät
        {
            'name': 'Connor McDavid',
            'team': 'Edmonton Oilers',
            'nationality': 'Canada',
            'position': 'C',
            'overall_rating': 99,
            'salary': 15000000,
            'ap_points': 15,
            'card_type': 'TOTY',
            'rarity': 'Legendary'
        },
        {
            'name': 'Leon Draisaitl',
            'team': 'Edmonton Oilers',
            'nationality': 'Germany',
            'position': 'C',
            'overall_rating': 95,
            'salary': 12000000,
            'ap_points': 12,
            'card_type': 'TOTY',
            'rarity': 'Legendary'
        },
        {
            'name': 'Aleksander Barkov',
            'team': 'Florida Panthers',
            'nationality': 'Finland',
            'position': 'C',
            'overall_rating': 92,
            'salary': 10000000,
            'ap_points': 10,
            'card_type': 'TOTY',
            'rarity': 'Epic'
        },
        {
            'name': 'Mikko Rantanen',
            'team': 'Colorado Avalanche',
            'nationality': 'Finland',
            'position': 'RW',
            'overall_rating': 91,
            'salary': 9500000,
            'ap_points': 9,
            'card_type': 'TOTY',
            'rarity': 'Epic'
        },
        {
            'name': 'Sebastian Aho',
            'team': 'Carolina Hurricanes',
            'nationality': 'Finland',
            'position': 'C',
            'overall_rating': 89,
            'salary': 8500000,
            'ap_points': 8,
            'card_type': 'TOTY',
            'rarity': 'Rare'
        },
        {
            'name': 'Patrick Kane',
            'team': 'Chicago Blackhawks',
            'nationality': 'USA',
            'position': 'RW',
            'overall_rating': 88,
            'salary': 8000000,
            'ap_points': 7,
            'card_type': 'TOTY',
            'rarity': 'Rare'
        },
        {
            'name': 'Jonathan Toews',
            'team': 'Chicago Blackhawks',
            'nationality': 'Canada',
            'position': 'C',
            'overall_rating': 87,
            'salary': 7500000,
            'ap_points': 6,
            'card_type': 'TOTY',
            'rarity': 'Rare'
        },
        {
            'name': 'Alex DeBrincat',
            'team': 'Chicago Blackhawks',
            'nationality': 'USA',
            'position': 'LW',
            'overall_rating': 86,
            'salary': 7000000,
            'ap_points': 6,
            'card_type': 'TOTY',
            'rarity': 'Rare'
        },
        
        # Puolustajat
        {
            'name': 'Cale Makar',
            'team': 'Colorado Avalanche',
            'nationality': 'Canada',
            'position': 'RD',
            'overall_rating': 96,
            'salary': 13000000,
            'ap_points': 13,
            'card_type': 'TOTY',
            'rarity': 'Legendary'
        },
        {
            'name': 'Victor Hedman',
            'team': 'Tampa Bay Lightning',
            'nationality': 'Sweden',
            'position': 'LD',
            'overall_rating': 93,
            'salary': 11000000,
            'ap_points': 11,
            'card_type': 'TOTY',
            'rarity': 'Epic'
        },
        {
            'name': 'Erik Karlsson',
            'team': 'San Jose Sharks',
            'nationality': 'Sweden',
            'position': 'RD',
            'overall_rating': 90,
            'salary': 9000000,
            'ap_points': 9,
            'card_type': 'TOTY',
            'rarity': 'Epic'
        },
        {
            'name': 'Rasmus Dahlin',
            'team': 'Buffalo Sabres',
            'nationality': 'Sweden',
            'position': 'LD',
            'overall_rating': 88,
            'salary': 8000000,
            'ap_points': 8,
            'card_type': 'TOTY',
            'rarity': 'Rare'
        },
        {
            'name': 'Seth Jones',
            'team': 'Chicago Blackhawks',
            'nationality': 'USA',
            'position': 'RD',
            'overall_rating': 85,
            'salary': 7000000,
            'ap_points': 7,
            'card_type': 'TOTY',
            'rarity': 'Rare'
        },
        
        # Maalivahdit
        {
            'name': 'Andrei Vasilevskiy',
            'team': 'Tampa Bay Lightning',
            'nationality': 'Russia',
            'position': 'G',
            'overall_rating': 94,
            'salary': 12000000,
            'ap_points': 12,
            'card_type': 'TOTY',
            'rarity': 'Epic'
        },
        {
            'name': 'Henrik Lundqvist',
            'team': 'New York Rangers',
            'nationality': 'Sweden',
            'position': 'G',
            'overall_rating': 89,
            'salary': 9000000,
            'ap_points': 9,
            'card_type': 'TOTY',
            'rarity': 'Rare'
        },
        {
            'name': 'Tuukka Rask',
            'team': 'Boston Bruins',
            'nationality': 'Finland',
            'position': 'G',
            'overall_rating': 87,
            'salary': 8000000,
            'ap_points': 8,
            'card_type': 'TOTY',
            'rarity': 'Rare'
        }
    ]
    
    print("Lisätään testipelaajia...")
    
    for player in test_players:
        try:
            player_id = db_manager.add_player(player)
            print(f"Lisätty: {player['name']} ({player['team']}) - {player['overall_rating']} OVR")
        except Exception as e:
            print(f"Virhe pelaajan {player['name']} lisäämisessä: {e}")
    
    print(f"Lisätty {len(test_players)} testipelaajaa!")

if __name__ == "__main__":
    create_test_data()