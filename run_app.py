#!/usr/bin/env python3
"""
Yksinkertainen käynnistysskripti NHL 26 HUT Team Builder -sovellukselle.
"""

import sys
import os

# Lisää src-kansio Python-polkuun
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from gui.main_window import MainWindow
    from database.database_manager import DatabaseManager
    from data.player_scraper import PlayerScraper
    from PyQt5.QtWidgets import QApplication
except ImportError as e:
    print(f"Virhe: {e}")
    print("Asenna tarvittavat riippuvuudet komennolla:")
    print("pip install PyQt5 requests beautifulsoup4 pandas numpy")
    sys.exit(1)

def main():
    """Pääfunktio sovelluksen käynnistämiseen."""
    print("NHL 26 HUT Team Builder")
    print("=" * 30)
    
    # Tarkista että tietokanta on olemassa
    db_manager = DatabaseManager()
    if not db_manager.database_exists():
        print("Tietokanta ei ole olemassa. Luodaan uusi tietokanta...")
        db_manager.create_database()
        
        # Hae pelaajakorttien tiedot (vaihtoehtoisesti käytä testidataa)
        print("Käytetään testidataa...")
        # scraper = PlayerScraper()
        # scraper.scrape_all_players()
        print("Tietokanta luotu!")
    else:
        print("Tietokanta löytyi!")
    
    # Käynnistä GUI
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    
    print("Sovellus käynnistetty!")
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()