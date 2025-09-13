#!/usr/bin/env python3
"""
Komentoriviversio NHL 26 HUT Team Builder -sovelluksesta.
"""

import sys
import os

# Lisää src-kansio Python-polkuun
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from database.database_manager import DatabaseManager
from optimization.chemistry_system import ChemistrySystem
from optimization.team_optimizer import TeamOptimizer

def print_team(team, index=1):
    """Tulostaa joukkueen tiedot."""
    print(f"\n--- Joukkue {index} ---")
    print(f"Kokonaisarvo: {team.overall_rating:.1f}")
    print(f"Kokonaispalkka: {team.total_salary:,} $")
    print(f"Kokonais-AP: {team.total_ap}")
    print(f"Kemiat:")
    for boost_type, value in team.chemistry_boosts.items():
        if value > 0:
            print(f"  - {boost_type}: +{value}")
    
    print(f"\nPelaajat:")
    all_players = team.forwards + team.defense + [team.goalie]
    for player in all_players:
        print(f"  - {player['name']} ({player['team']}) - {player['overall_rating']} OVR - {player['position']}")

def main():
    """Pääfunktio CLI-sovelluksen käynnistämiseen."""
    print("NHL 26 HUT Team Builder - CLI")
    print("=" * 35)
    
    # Alusta komponentit
    db_manager = DatabaseManager()
    chemistry_system = ChemistrySystem()
    team_optimizer = TeamOptimizer(db_manager, chemistry_system)
    
    # Tarkista tietokanta
    if not db_manager.database_exists():
        print("Tietokanta ei ole olemassa. Luodaan uusi tietokanta...")
        db_manager.create_database()
        print("Tietokanta luotu!")
        print("Suorita ensin: python3 test_data.py")
        return
    else:
        print("Tietokanta löytyi!")
    
    # Hae pelaajia
    players = db_manager.get_all_players()
    print(f"Löytyi {len(players)} pelaajaa")
    
    if len(players) == 0:
        print("Ei pelaajia tietokannassa. Suorita ensin: python3 test_data.py")
        return
    
    # Kysy asetuksia
    print("\nOptimointiasetukset:")
    
    try:
        max_salary = input("Maksimipalkka (miljoonaa $, oletus 100): ").strip()
        max_salary = int(max_salary) * 1000000 if max_salary else 100000000
        
        min_ovr = input("Minimikokonaisarvo (oletus 80): ").strip()
        min_ovr = int(min_ovr) if min_ovr else 80
        
        preferred_teams = input("Suositellut joukkueet (pilkuilla eroteltuna, tyhjä = kaikki): ").strip()
        preferred_teams = [t.strip() for t in preferred_teams.split(',')] if preferred_teams else None
        
        preferred_nationalities = input("Suositellut kansallisuudet (pilkuilla eroteltuna, tyhjä = kaikki): ").strip()
        preferred_nationalities = [n.strip() for n in preferred_nationalities.split(',')] if preferred_nationalities else None
        
    except ValueError:
        print("Virheellinen syöte, käytetään oletusarvoja")
        max_salary = 100000000
        min_ovr = 80
        preferred_teams = None
        preferred_nationalities = None
    
    # Optimoi joukkueet
    print(f"\nOptimoidaan joukkueita...")
    print(f"Maksimipalkka: {max_salary:,} $")
    print(f"Minimikokonaisarvo: {min_ovr}")
    if preferred_teams:
        print(f"Suositellut joukkueet: {', '.join(preferred_teams)}")
    if preferred_nationalities:
        print(f"Suositellut kansallisuudet: {', '.join(preferred_nationalities)}")
    
    try:
        teams = team_optimizer.find_optimal_team(
            max_salary=max_salary,
            min_ovr=min_ovr,
            preferred_teams=preferred_teams,
            preferred_nationalities=preferred_nationalities
        )
        
        print(f"\nLöytyi {len(teams)} joukkuetta")
        
        if teams:
            # Näytä top 5 joukkuetta
            for i, team in enumerate(teams[:5]):
                print_team(team, i + 1)
            
            if len(teams) > 5:
                print(f"\n... ja {len(teams) - 5} muuta joukkuetta")
        else:
            print("Ei löytynyt kelvollisia joukkueita annetuilla kriteereillä")
    
    except Exception as e:
        print(f"Virhe optimoinnissa: {e}")
        import traceback
        traceback.print_exc()
    
    print("\nKiitos käytöstä!")

if __name__ == "__main__":
    main()