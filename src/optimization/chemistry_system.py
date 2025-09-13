"""
Kemiat/boostit -systeemi NHL 26 HUT Team Builder -sovellukselle.
"""

import json
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class ChemistryBoost:
    """Kemian boostin tiedot."""
    name: str
    boost_type: str  # 'ovr', 'salary_cap', 'ap'
    boost_value: int
    requirements: Dict
    description: str = ""

class ChemistrySystem:
    """Kemiat-systeemin hallinta."""
    
    def __init__(self):
        """Alustaa kemiat-systeemin."""
        self.boosts = []
        self._initialize_default_boosts()
    
    def _initialize_default_boosts(self):
        """Alustaa oletuskemiat."""
        # OVR-boostit
        self.boosts.append(ChemistryBoost(
            name="Chicago Blackhawks + Suomi",
            boost_type="ovr",
            boost_value=2,
            requirements={
                "team_blackhawks": 2,
                "nationality_finland": 1,
                "position_forward": 3
            },
            description="2x Chicago Blackhawks + 1x Suomi hyökkäyskolmikossa"
        ))
        
        self.boosts.append(ChemistryBoost(
            name="Sama joukkue puolustuksessa",
            boost_type="ovr",
            boost_value=1,
            requirements={
                "same_team": True,
                "position_defense": 2
            },
            description="2x sama joukkue puolustuksessa"
        ))
        
        # Salary Cap -boostit
        self.boosts.append(ChemistryBoost(
            name="Kolme suomalaista hyökkääjää",
            boost_type="salary_cap",
            boost_value=2000000,
            requirements={
                "nationality_finland": 3,
                "position_forward": 3
            },
            description="3x Suomi hyökkäyskolmikossa"
        ))
        
        self.boosts.append(ChemistryBoost(
            name="Kanadalainen puolustus",
            boost_type="salary_cap",
            boost_value=1500000,
            requirements={
                "nationality_canada": 2,
                "position_defense": 2
            },
            description="2x Kanada puolustuksessa"
        ))
        
        # AP-boostit
        self.boosts.append(ChemistryBoost(
            name="Ruotsalainen maalivahti + puolustus",
            boost_type="ap",
            boost_value=3,
            requirements={
                "nationality_sweden": 3,
                "position_goalie": 1,
                "position_defense": 2
            },
            description="1x Ruotsi maalivahti + 2x Ruotsi puolustus"
        ))
        
        self.boosts.append(ChemistryBoost(
            name="Yhdysvaltalainen hyökkäys",
            boost_type="ap",
            boost_value=4,
            requirements={
                "nationality_usa": 3,
                "position_forward": 3
            },
            description="3x USA hyökkäyskolmikossa"
        ))
    
    def calculate_team_boosts(self, team: List[Dict]) -> Dict[str, int]:
        """Laskee joukkueen saamat boostit.
        
        Args:
            team: Lista pelaajista sanakirjoina
            
        Returns:
            Sanakirja boosteista: {'ovr': kokonais_ovr_boost, 'salary_cap': kokonais_salary_cap_boost, 'ap': kokonais_ap_boost}
        """
        total_boosts = {
            'ovr': 0,
            'salary_cap': 0,
            'ap': 0
        }
        
        for boost in self.boosts:
            if self._check_boost_requirements(team, boost):
                total_boosts[boost.boost_type] += boost.boost_value
                print(f"Aktivoitu: {boost.name} (+{boost.boost_value} {boost.boost_type})")
        
        return total_boosts
    
    def _check_boost_requirements(self, team: List[Dict], boost: ChemistryBoost) -> bool:
        """Tarkistaa täyttääkö joukkue boostin vaatimukset.
        
        Args:
            team: Lista pelaajista sanakirjoina
            boost: Tarkistettava boost
            
        Returns:
            True jos vaatimukset täyttyvät, muuten False
        """
        requirements = boost.requirements
        
        # Tarkista joukkuekohtaiset vaatimukset
        if "team_blackhawks" in requirements:
            blackhawks_count = sum(1 for player in team if player['team'].lower() == 'chicago blackhawks')
            if blackhawks_count < requirements["team_blackhawks"]:
                return False
        
        # Tarkista kansallisuusvaatimukset
        for key, required_count in requirements.items():
            if key.startswith("nationality_"):
                nationality = key.replace("nationality_", "").title()
                nationality_count = sum(1 for player in team if player['nationality'].lower() == nationality.lower())
                if nationality_count < required_count:
                    return False
        
        # Tarkista asemavaatimukset
        for key, required_count in requirements.items():
            if key.startswith("position_"):
                position = key.replace("position_", "").upper()
                if position == "FORWARD":
                    forward_count = sum(1 for player in team if player['position'] in ['C', 'LW', 'RW'])
                    if forward_count < required_count:
                        return False
                elif position == "DEFENSE":
                    defense_count = sum(1 for player in team if player['position'] in ['LD', 'RD'])
                    if defense_count < required_count:
                        return False
                elif position == "GOALIE":
                    goalie_count = sum(1 for player in team if player['position'] == 'G')
                    if goalie_count < required_count:
                        return False
        
        # Tarkista sama joukkue -vaatimus
        if requirements.get("same_team", False):
            # Tarkista onko vaadittu määrä saman joukkueen pelaajia
            team_counts = {}
            for player in team:
                team_name = player['team']
                team_counts[team_name] = team_counts.get(team_name, 0) + 1
            
            max_same_team = max(team_counts.values()) if team_counts else 0
            required_same_team = requirements.get("position_defense", 2)
            if max_same_team < required_same_team:
                return False
        
        return True
    
    def get_available_boosts(self) -> List[ChemistryBoost]:
        """Palauttaa kaikki saatavilla olevat boostit.
        
        Returns:
            Lista boosteista
        """
        return self.boosts
    
    def get_boost_by_name(self, name: str) -> Optional[ChemistryBoost]:
        """Hakee boostin nimen perusteella.
        
        Args:
            name: Boostin nimi
            
        Returns:
            Boostin tiedot tai None
        """
        for boost in self.boosts:
            if boost.name == name:
                return boost
        return None
    
    def add_custom_boost(self, boost: ChemistryBoost):
        """Lisää mukautetun boostin.
        
        Args:
            boost: Lisättävä boost
        """
        self.boosts.append(boost)
    
    def remove_boost(self, name: str) -> bool:
        """Poistaa boostin.
        
        Args:
            name: Poistettavan boostin nimi
            
        Returns:
            True jos boost poistettiin, False jos ei löytynyt
        """
        for i, boost in enumerate(self.boosts):
            if boost.name == name:
                del self.boosts[i]
                return True
        return False