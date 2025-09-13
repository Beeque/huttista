#!/bin/bash

echo "=== NHL Scraper Setup ==="

# Tarkista Python
if ! command -v python3 &> /dev/null; then
    echo "Python3 ei ole asennettu. Asenna Python3 ensin."
    exit 1
fi

# Asenna riippuvuudet
echo "Asennetaan Python-riippuvuudet..."
pip3 install -r requirements.txt

# Tee skriptit suoritettaviksi
chmod +x nhl_scraper.py
chmod +x advanced_nhl_scraper.py
chmod +x test_scraper.py
chmod +x scraper_ui.py

echo "Setup valmis!"
echo ""
echo "Käytettävissä olevat komennot:"
echo "  python3 test_scraper.py              - Testaa perus scraperia"
echo "  python3 test_single_card.py 2062     - Testaa yksittäisen kortin hakemista"
echo "  python3 enhanced_nhl_scraper.py      - Käynnistä parannettu scraper (suositus)"
echo "  python3 advanced_nhl_scraper.py      - Käynnistä edistynyt scraper"
echo "  python3 scraper_ui.py                - Käynnistä graafinen käyttöliittymä"
echo ""
echo "Esimerkkejä:"
echo "  python3 enhanced_nhl_scraper.py --max-cards 5     # Kerää 5 korttia yksityiskohtaisilla tiedoilla"
echo "  python3 enhanced_nhl_scraper.py --single-card 2062 # Hae yksittäinen kortti"
echo "  python3 enhanced_nhl_scraper.py --stats-only       # Näytä tietokannan tilastot"
echo ""
echo "Käynnistä graafinen käyttöliittymä:"
echo "  python3 scraper_ui.py"