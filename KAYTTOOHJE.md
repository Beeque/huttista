# NHL 26 HUT Team Builder - Käyttöohje

## Pika-aloitus

### 1. Asenna riippuvuudet
```bash
# Linux/Mac
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Windows
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Luo testidata
```bash
python3 test_data.py
```

### 3. Käynnistä sovellus
```bash
# CLI-versio (suositeltu)
python3 cli_app.py

# Testiversio
python3 test_app.py

# GUI-versio (vaatii PyQt5:n)
python3 run_app.py
```

## Käyttö

### CLI-versio (cli_app.py)

1. Käynnistä sovellus: `python3 cli_app.py`
2. Syötä optimointiasetukset:
   - Maksimipalkka (miljoonaa $)
   - Minimikokonaisarvo
   - Suositellut joukkueet (valinnainen)
   - Suositellut kansallisuudet (valinnainen)
3. Sovellus etsii optimaalisia joukkueita
4. Näet top 5 parasta joukkuetta

### GUI-versio (run_app.py)

1. Asenna PyQt5: `pip install PyQt5`
2. Käynnistä: `python3 run_app.py`
3. Käytä graafista käyttöliittymää joukkueiden optimointiin

## Kemiat-systeemi

Sovellus ottaa huomioon seuraavat kemiat:

- **Chicago Blackhawks + Suomi**: 2x Chicago + 1x Suomi hyökkäyskolmikossa → +2 OVR
- **Kolme suomalaista hyökkääjää**: 3x Suomi hyökkäyskolmikossa → +2M$ palkkakattoon
- **Sama joukkue puolustuksessa**: 2x sama joukkue puolustuksessa → +1 OVR
- **Kanadalainen puolustus**: 2x Kanada puolustuksessa → +1.5M$ palkkakattoon
- **Ruotsalainen maalivahti + puolustus**: 1x Ruotsi maalivahti + 2x Ruotsi puolustus → +3 AP
- **Yhdysvaltalainen hyökkäys**: 3x USA hyökkäyskolmikossa → +4 AP

## Windows Executable

Luo Windows .exe-tiedosto:

```bash
pip install pyinstaller
python build_exe.py
```

Executable löytyy `dist/NHL26_HUT_Builder.exe`

## Ongelmat

### "Python3 ei löydy"
- Asenna Python 3.8+ osoitteesta python.org
- Varmista että python3 on PATH:ssa

### "PyQt5 ei löydy"
- Asenna: `pip install PyQt5`
- Jos ongelmia, kokeile: `pip install PyQt5-tools`

### "Tietokanta ei löydy"
- Suorita: `python3 test_data.py`

### "Ei pelaajia tietokannassa"
- Suorita: `python3 test_data.py`
- Tarkista että `hut_players.db` on olemassa

## Kehitys

### Lisää uusia kemioita
Muokkaa `src/optimization/chemistry_system.py`:

```python
self.boosts.append(ChemistryBoost(
    name="Uusi kemia",
    boost_type="ovr",
    boost_value=2,
    requirements={
        "nationality_finland": 2,
        "position_forward": 2
    },
    description="2x Suomi hyökkäysparissa"
))
```

### Päivitä pelaajakorttien tiedot
```python
from src.data.player_scraper import PlayerScraper
scraper = PlayerScraper()
scraper.update_player_data()
```

## Tuki

- GitHub: https://github.com/Beeque/huttista
- Luo issue GitHubissa ongelmista
- Tarkista README.md lisätietoja varten