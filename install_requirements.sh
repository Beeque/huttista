#!/bin/bash
# Asennusskripti NHL 26 HUT Team Builder -sovellukselle

echo "NHL 26 HUT Team Builder - Asennus"
echo "=================================="

# Tarkista Python
if ! command -v python3 &> /dev/null; then
    echo "Virhe: Python3 ei ole asennettu"
    exit 1
fi

echo "Python3 löytyi: $(python3 --version)"

# Luo virtuaaliympäristö
echo "Luodaan virtuaaliympäristö..."
python3 -m venv venv

# Aktivoi virtuaaliympäristö
echo "Aktivoidaan virtuaaliympäristö..."
source venv/bin/activate

# Asenna riippuvuudet
echo "Asennetaan riippuvuudet..."
pip install -r requirements.txt

# Luo tietokanta ja testidata
echo "Luodaan tietokanta ja testidata..."
python3 test_data.py

echo ""
echo "Asennus valmis!"
echo ""
echo "Käynnistä sovellus:"
echo "  CLI-versio: python3 cli_app.py"
echo "  Testiversio: python3 test_app.py"
echo ""
echo "GUI-versio vaatii PyQt5:n asennuksen:"
echo "  pip install PyQt5"
echo "  python3 run_app.py"