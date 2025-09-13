"""
Joukkueen optimointialgoritmi NHL 26 HUT Team Builder -sovellukselle.
"""

import itertools
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from .chemistry_system import ChemistrySystem

@dataclass
class TeamConfiguration:
    """Joukkueen kokoonpano."""
    forwards: List[Dict]  # 3 hyökkääjää
    defense: List[Dict]   # 2 puolustajaa
    goalie: Dict          # 1 maalivahti
    total_salary: int
    total_ap: int
    chemistry_boosts: Dict[str, int]
    overall_rating: float

class TeamOptimizer:
    """Joukkueen optimointialgoritmi."""
    
    def __init__(self, db_manager, chemistry_system: ChemistrySystem):
        """Alustaa optimoijan.
        
        Args:
            db_manager: Tietokannan hallintaluokka
            chemistry_system: Kemiat-systeemi
        """
        self.db_manager = db_manager
        self.chemistry_system = chemistry_system
        self.salary_cap = 100000000  # 100 miljoonaa
        self.max_combinations = 10000  # Maksimi yhdistelmien määrä
    
    def find_optimal_team(self, 
                         max_salary: Optional[int] = None,
                         min_ovr: Optional[int] = None,
                         preferred_teams: Optional[List[str]] = None,
                         preferred_nationalities: Optional[List[str]] = None) -> List[TeamConfiguration]:
        """Etsii optimaalisia joukkuekokoonpanoja.
        
        Args:
            max_salary: Maksimipalkka (default: salary_cap)
            min_ovr: Minimikokonaisarvo
            preferred_teams: Suositellut joukkueet
            preferred_nationalities: Suositellut kansallisuudet
            
        Returns:
            Lista parhaista joukkuekokoonpanoista
        """
        if max_salary is None:
            max_salary = self.salary_cap
        
        print("Haetaan pelaajia tietokannasta...")
        
        # Hae pelaajat asemittain
        forwards = self.db_manager.get_players_by_position('C') + \
                  self.db_manager.get_players_by_position('LW') + \
                  self.db_manager.get_players_by_position('RW')
        
        defense = self.db_manager.get_players_by_position('LD') + \
                 self.db_manager.get_players_by_position('RD')
        
        goalies = self.db_manager.get_players_by_position('G')
        
        print(f"Löytyi {len(forwards)} hyökkääjää, {len(defense)} puolustajaa, {len(goalies)} maalivahtia")
        
        # Suodata suositukset
        if preferred_teams:
            forwards = [p for p in forwards if p['team'] in preferred_teams or not preferred_teams]
            defense = [p for p in defense if p['team'] in preferred_teams or not preferred_teams]
            goalies = [p for p in goalies if p['team'] in preferred_teams or not preferred_teams]
        
        if preferred_nationalities:
            forwards = [p for p in forwards if p['nationality'] in preferred_nationalities or not preferred_nationalities]
            defense = [p for p in defense if p['nationality'] in preferred_nationalities or not preferred_nationalities]
            goalies = [p for p in goalies if p['nationality'] in preferred_nationalities or not preferred_nationalities]
        
        # Järjestä OVR:n mukaan
        forwards.sort(key=lambda x: x['overall_rating'], reverse=True)
        defense.sort(key=lambda x: x['overall_rating'], reverse=True)
        goalies.sort(key=lambda x: x['overall_rating'], reverse=True)
        
        # Rajoita hakemista tehokkuuden vuoksi
        forwards = forwards[:50]  # Top 50 hyökkääjää
        defense = defense[:30]    # Top 30 puolustajaa
        goalies = goalies[:20]    # Top 20 maalivahtia
        
        print("Aloitetaan joukkueiden optimointi...")
        
        best_teams = []
        
        # Generoi joukkuekokoonpanoja
        team_count = 0
        for forward_combo in itertools.combinations(forwards, 3):
            if team_count >= self.max_combinations:
                break
                
            for defense_combo in itertools.combinations(defense, 2):
                if team_count >= self.max_combinations:
                    break
                    
                for goalie in goalies:
                    team_count += 1
                    
                    # Luo joukkue
                    team = list(forward_combo) + list(defense_combo) + [goalie]
                    
                    # Laske perustiedot
                    total_salary = sum(p['salary'] for p in team)
                    total_ap = sum(p['ap_points'] for p in team)
                    
                    # Tarkista palkkaraja
                    if total_salary > max_salary:
                        continue
                    
                    # Laske kemiat
                    chemistry_boosts = self.chemistry_system.calculate_team_boosts(team)
                    
                    # Laske kokonaisarvo (mukaan lukien boostit)
                    base_ovr = sum(p['overall_rating'] for p in team)
                    boosted_ovr = base_ovr + chemistry_boosts['ovr']
                    
                    # Tarkista minimiarvo
                    if min_ovr and boosted_ovr < min_ovr:
                        continue
                    
                    # Luo joukkuekokoonpano
                    config = TeamConfiguration(
                        forwards=list(forward_combo),
                        defense=list(defense_combo),
                        goalie=goalie,
                        total_salary=total_salary,
                        total_ap=total_ap + chemistry_boosts['ap'],
                        chemistry_boosts=chemistry_boosts,
                        overall_rating=boosted_ovr
                    )
                    
                    best_teams.append(config)
        
        # Järjestä parhaat ensin
        best_teams.sort(key=lambda x: x.overall_rating, reverse=True)
        
        print(f"Löytyi {len(best_teams)} kelvollista joukkuetta")
        
        return best_teams[:10]  # Palauta top 10
    
    def find_team_by_budget(self, budget: int) -> List[TeamConfiguration]:
        """Etsii parhaan joukkueen tietyllä budjetilla.
        
        Args:
            budget: Budjetti
            
        Returns:
            Lista parhaista joukkueista budjetilla
        """
        return self.find_optimal_team(max_salary=budget)
    
    def find_team_by_chemistry(self, chemistry_requirements: Dict[str, int]) -> List[TeamConfiguration]:
        """Etsii joukkueita tietyillä kemioilla.
        
        Args:
            chemistry_requirements: Kemioiden vaatimukset
            
        Returns:
            Lista joukkueista
        """
        # Toteutetaan myöhemmin tarvittaessa
        # Tässä voisi olla logiikka joka etsii joukkueita tietyillä kemioilla
        return self.find_optimal_team()
    
    def calculate_team_value(self, team: List[Dict]) -> Dict[str, float]:
        """Laskee joukkueen arvon eri kriteerien mukaan.
        
        Args:
            team: Lista pelaajista
            
        Returns:
            Sanakirja arvoista
        """
        total_salary = sum(p['salary'] for p in team)
        total_ap = sum(p['ap_points'] for p in team)
        base_ovr = sum(p['overall_rating'] for p in team)
        
        chemistry_boosts = self.chemistry_system.calculate_team_boosts(team)
        boosted_ovr = base_ovr + chemistry_boosts['ovr']
        
        # Laske tehokkuus (OVR per miljoona palkkaa)
        efficiency = boosted_ovr / (total_salary / 1000000) if total_salary > 0 else 0
        
        return {
            'total_salary': total_salary,
            'total_ap': total_ap + chemistry_boosts['ap'],
            'base_ovr': base_ovr,
            'boosted_ovr': boosted_ovr,
            'chemistry_boosts': chemistry_boosts,
            'efficiency': efficiency
        }
    
    def suggest_improvements(self, team: List[Dict]) -> List[Dict]:
        """Ehdottaa joukkueen parannuksia.
        
        Args:
            team: Nykyinen joukkue
            
        Returns:
            Lista parannusehdotuksista
        """
        suggestions = []
        
        # Laske nykyinen arvo
        current_value = self.calculate_team_value(team)
        
        # Etsi parempia vaihtoehtoja jokaiselle asemalle
        for i, player in enumerate(team):
            position = player['position']
            
            # Hae parempia pelaajia samasta asemasta
            if position in ['C', 'LW', 'RW']:
                alternatives = self.db_manager.get_players_by_position(position)
            elif position in ['LD', 'RD']:
                alternatives = self.db_manager.get_players_by_position(position)
            elif position == 'G':
                alternatives = self.db_manager.get_players_by_position('G')
            else:
                continue
            
            # Suodata paremmat vaihtoehdot
            better_alternatives = [
                alt for alt in alternatives
                if alt['overall_rating'] > player['overall_rating'] and
                   alt['salary'] <= player['salary'] + 1000000  # Max 1M enemmän
            ]
            
            for alt in better_alternatives[:3]:  # Top 3 vaihtoehtoa
                # Luo uusi joukkue vaihtoehdolla
                new_team = team.copy()
                new_team[i] = alt
                
                # Laske uusi arvo
                new_value = self.calculate_team_value(new_team)
                
                if new_value['boosted_ovr'] > current_value['boosted_ovr']:
                    suggestions.append({
                        'position': position,
                        'current_player': player,
                        'suggested_player': alt,
                        'ovr_improvement': new_value['boosted_ovr'] - current_value['boosted_ovr'],
                        'salary_change': alt['salary'] - player['salary']
                    })
        
        # Järjestä parhaimmat ensin
        suggestions.sort(key=lambda x: x['ovr_improvement'], reverse=True)
        
        return suggestions[:5]  # Top 5 ehdotusta