#!/usr/bin/env python3
"""
NHL 26 HUT Team Builder
=======================

Työkalu NHL 26 Hockey Ultimate Team -kokoonpanojen optimointiin.
Ottaa huomioon kemiat, palkkakaton ja AP-pisteet.
"""

import sys
import os
from PyQt5.QtWidgets import QApplication
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from gui.main_window import MainWindow
from database.database_manager import DatabaseManager
from data.player_scraper import PlayerScraper

def main():
    """Pääfunktio sovelluksen käynnistämiseen."""
    # Tarkista että tietokanta on olemassa
    db_manager = DatabaseManager()
    if not db_manager.database_exists():
        print("Tietokanta ei ole olemassa. Luodaan uusi tietokanta...")
        db_manager.create_database()
        
        # Hae pelaajakorttien tiedot
        print("Haetaan pelaajakorttien tiedot...")
        scraper = PlayerScraper()
        scraper.scrape_all_players()
        print("Pelaajakorttien tiedot haettu!")
    
    # Käynnistä GUI
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()