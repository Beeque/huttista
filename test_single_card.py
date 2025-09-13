#!/usr/bin/env python3
"""
Test-skripti yksittäisen kortin hakemiseen player-stats.php?id=XXXX -tyyppisestä URL:sta
"""

import sys
from enhanced_nhl_scraper import EnhancedNHLScraper

def test_single_card(player_id: int):
    """Testaa yksittäisen kortin hakemista"""
    print(f"=== TESTI: YKSITTÄINEN KORTTI ID: {player_id} ===\n")
    
    try:
        # Luo scraper-instanssi
        scraper = EnhancedNHLScraper('test_single_card.db')
        print("✓ Scraper luotu onnistuneesti")
        
        # Hae yksittäinen kortti
        print(f"Haetaan kortti ID:llä {player_id}...")
        card = scraper.scrape_single_card(player_id)
        
        if card:
            print(f"✓ Kortti löytyi: {card.player_name}")
            print(f"  - Player ID: {card.player_id}")
            print(f"  - Card URL: {card.card_url}")
            print(f"  - Overall Rating: {card.overall_rating}")
            print(f"  - Position: {card.position}")
            print(f"  - Team: {card.team}")
            print(f"  - Height: {card.height}")
            print(f"  - Weight: {card.weight}")
            print(f"  - Handedness: {card.handedness}")
            print(f"  - Nationality: {card.nationality}")
            
            if card.player_details:
                print(f"  - Age: {card.player_details.get('age')}")
                print(f"  - Birth Date: {card.player_details.get('birth_date')}")
                print(f"  - Birth Place: {card.player_details.get('birth_place')}")
            
            print(f"  - Abilities: {len(card.abilities)}")
            for ability in card.abilities[:3]:  # Näytä ensimmäiset 3
                print(f"    * {ability.name} ({ability.ability_type})")
            
            print(f"  - Stats: {len(card.stats)}")
            for stat in card.stats[:5]:  # Näytä ensimmäiset 5
                print(f"    * {stat.name}: {stat.value} ({stat.category})")
            
            # Tallenna tietokantaan
            print("\nTallennetaan tietokantaan...")
            card_id = scraper.save_card_to_database(card)
            if card_id:
                print(f"✓ Kortti tallennettu tietokantaan (ID: {card_id})")
                
                # Näytä tilastot
                stats = scraper.get_database_stats()
                print(f"\nTietokannan tilastot:")
                print(f"  - Kortteja: {stats['total_cards']}")
                print(f"  - Kyvyjä: {stats['total_abilities']}")
                print(f"  - Tilastoja: {stats['total_stats']}")
            else:
                print("✗ Kortin tallentaminen epäonnistui")
        else:
            print("✗ Korttia ei löytynyt")
            return False
            
    except Exception as e:
        print(f"✗ Testi epäonnistui: {e}")
        return False
    
    print("\n=== TESTI VALMIS ===")
    return True

def main():
    """Pääohjelma"""
    if len(sys.argv) != 2:
        print("Käyttö: python3 test_single_card.py <player_id>")
        print("Esimerkki: python3 test_single_card.py 2062")
        sys.exit(1)
    
    try:
        player_id = int(sys.argv[1])
    except ValueError:
        print("Virhe: Player ID:n on oltava numero")
        sys.exit(1)
    
    success = test_single_card(player_id)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()