#!/usr/bin/env python3
"""
Testiversio NHL 26 HUT Team Builder -sovelluksesta ilman GUI:ta.
"""

import sys
import os

# Lisää src-kansio Python-polkuun
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from database.database_manager import DatabaseManager
from optimization.chemistry_system import ChemistrySystem
from optimization.team_optimizer import TeamOptimizer

def main():
    """Pääfunktio testisovelluksen käynnistämiseen."""
    print("NHL 26 HUT Team Builder - Testiversio")
    print("=" * 40)
    
    # Alusta komponentit
    db_manager = DatabaseManager()
    chemistry_system = ChemistrySystem()
    team_optimizer = TeamOptimizer(db_manager, chemistry_system)
    
    # Tarkista tietokanta
    if not db_manager.database_exists():
        print("Tietokanta ei ole olemassa. Luodaan uusi tietokanta...")
        db_manager.create_database()
        print("Tietokanta luotu!")
    else:
        print("Tietokanta löytyi!")
    
    # Hae pelaajia
    print("\nHaetaan pelaajia...")
    players = db_manager.get_all_players()
    print(f"Löytyi {len(players)} pelaajaa")
    
    if len(players) == 0:
        print("Ei pelaajia tietokannassa. Suorita ensin: python3 test_data.py")
        return
    
    # Näytä top 5 pelaajaa
    print("\nTop 5 pelaajaa:")
    for i, player in enumerate(players[:5]):
        print(f"{i+1}. {player['name']} ({player['team']}) - {player['overall_rating']} OVR")
    
    # Testaa kemiat-systeemiä
    print("\nTestataan kemiat-systeemiä...")
    chemistries = chemistry_system.get_available_boosts()
    print(f"Löytyi {len(chemistries)} kemiaa:")
    for chem in chemistries:
        print(f"- {chem.name}: +{chem.boost_value} {chem.boost_type}")
    
    # Testaa joukkueen optimointia
    print("\nTestataan joukkueen optimointia...")
    try:
        teams = team_optimizer.find_optimal_team(max_salary=50000000, min_ovr=80)
        print(f"Löytyi {len(teams)} joukkuetta")
        
        if teams:
            best_team = teams[0]
            print(f"\nParas joukkue:")
            print(f"Kokonaisarvo: {best_team.overall_rating:.1f}")
            print(f"Kokonaispalkka: {best_team.total_salary:,} $")
            print(f"Kokonais-AP: {best_team.total_ap}")
            print(f"Kemiat: {best_team.chemistry_boosts}")
            
            print(f"\nPelaajat:")
            all_players = best_team.forwards + best_team.defense + [best_team.goalie]
            for player in all_players:
                print(f"- {player['name']} ({player['team']}) - {player['overall_rating']} OVR")
    
    except Exception as e:
        print(f"Virhe optimoinnissa: {e}")
        import traceback
        traceback.print_exc()
    
    print("\nTesti valmis!")

if __name__ == "__main__":
    main()