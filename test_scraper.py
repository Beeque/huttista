#!/usr/bin/env python3
"""
Test-skripti NHL scraperille
"""

import sys
import os
from advanced_nhl_scraper import AdvancedNHLScraper

def test_scraper():
    """Testaa scraperin perustoiminnallisuutta"""
    print("=== NHL SCRAPER TESTI ===\n")
    
    try:
        # Luo scraper-instanssi
        scraper = AdvancedNHLScraper('test_nhl_cards.db')
        print("✓ Scraper luotu onnistuneesti")
        
        # Testaa sivun latausta
        print("Testataan sivun latausta...")
        soup = scraper.get_page_content('https://nhlhutbuilder.com/cards.php')
        if soup:
            print("✓ Sivun lataus onnistui")
            
            # Etsi korttielementit
            card_elements = soup.find_all('div', class_='other_card_container')
            print(f"✓ Löytyi {len(card_elements)} korttia")
            
            if card_elements:
                # Testaa yhden kortin käsittelyä
                print("\nTestataan kortin käsittelyä...")
                test_card = scraper.extract_card_from_list(card_elements[0])
                
                if test_card:
                    print(f"✓ Kortin käsittely onnistui:")
                    print(f"  - Player ID: {test_card.player_id}")
                    print(f"  - Image URL: {test_card.image_url[:50]}...")
                    print(f"  - Abilities: {len(test_card.abilities)}")
                    
                    # Testaa tietokantaan tallentamista
                    print("\nTestataan tietokantaan tallentamista...")
                    card_id = scraper.save_card_to_database(test_card)
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
                    print("✗ Kortin käsittely epäonnistui")
            else:
                print("✗ Korttielementtejä ei löytynyt")
        else:
            print("✗ Sivun lataus epäonnistui")
            
    except Exception as e:
        print(f"✗ Testi epäonnistui: {e}")
        return False
    
    print("\n=== TESTI VALMIS ===")
    return True

if __name__ == "__main__":
    success = test_scraper()
    sys.exit(0 if success else 1)