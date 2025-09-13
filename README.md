# NHL 26 HUT Team Builder

NHL 26 Hockey Ultimate Team -kokoonpanojen optimointityökalu, joka auttaa rakentamaan mahdollisimman tehokkaan joukkueen vähällä vaivalla.

## Ominaisuudet

- **Pelaajakorttien tietojen haku**: Hakee automaattisesti pelaajakorttien tiedot NHL HUT Builder -sivustolta
- **Kemiat-systeemi**: Ottaa huomioon joukkueen, kansallisuuden ja muiden tekijöiden kemiat
- **Palkkakaton hallinta**: 100 miljoonan palkkakaton optimointi
- **AP-pisteiden laskenta**: Ability Points -pisteiden optimointi supertaitojen aktivoimiseen
- **Graafinen käyttöliittymä**: Helppokäyttöinen PyQt5-pohjainen käyttöliittymä
- **Windows executable**: Valmis .exe-tiedosto jakamista varten

## Asennus

### Kehitysympäristö

1. **Asenna Python 3.8+**
   - Lataa [Python](https://www.python.org/downloads/)
   - Varmista että pip on asennettu

2. **Kloonaa repositorio**
   ```bash
   git clone https://github.com/Beeque/huttista.git
   cd huttista
   ```

3. **Luo virtuaaliympäristö**
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # Linux/Mac:
   source venv/bin/activate
   ```

4. **Asenna riippuvuudet**
   ```bash
   pip install -r requirements.txt
   ```

5. **Käynnistä sovellus**
   ```bash
   python main.py
   ```

### Windows Executable

1. **Rakenna executable**
   ```bash
   python build_exe.py
   ```

2. **Löydä tiedosto**
   - Executable löytyy `dist/NHL26_HUT_Builder.exe`

## Käyttö

### 1. Ensimmäinen käynnistys

Sovellus hakee automaattisesti pelaajakorttien tiedot NHL HUT Builder -sivustolta ensimmäisellä käynnistyksellä. Tämä voi kestää muutaman minuutin.

### 2. Joukkueen optimointi

1. Mene "Joukkueen Optimointi" -välilehdelle
2. Aseta haluamasi asetukset:
   - Maksimipalkka (oletus: 100M$)
   - Minimikokonaisarvo (oletus: 80)
   - Suositellut joukkueet (valinnainen)
   - Suositellut kansallisuudet (valinnainen)
3. Klikkaa "Optimoi Joukkue"
4. Valitse haluamasi joukkue tuloksista

### 3. Kemiat-systeemi

Sovellus ottaa huomioon seuraavat kemiat:

- **Chicago Blackhawks + Suomi**: 2x Chicago + 1x Suomi hyökkäyskolmikossa → +2 OVR
- **Kolme suomalaista hyökkääjää**: 3x Suomi hyökkäyskolmikossa → +2M$ palkkakattoon
- **Sama joukkue puolustuksessa**: 2x sama joukkue puolustuksessa → +1 OVR
- **Kanadalainen puolustus**: 2x Kanada puolustuksessa → +1.5M$ palkkakattoon
- **Ruotsalainen maalivahti + puolustus**: 1x Ruotsi maalivahti + 2x Ruotsi puolustus → +3 AP
- **Yhdysvaltalainen hyökkäys**: 3x USA hyökkäyskolmikossa → +4 AP

### 4. Pelaajakorttien selaus

"Pelaajakortit" -välilehdellä voit:
- Selata kaikkia pelaajia
- Hakea hakusanalla
- Suodata aseman mukaan
- Suodata joukkueen mukaan

## Tekninen rakenne

```
huttista/
├── main.py                 # Pääohjelma
├── requirements.txt        # Python-riippuvuudet
├── setup.py               # Asennusasetukset
├── build_exe.py           # Executable-rakentaja
├── src/
│   ├── database/          # Tietokannan hallinta
│   │   └── database_manager.py
│   ├── data/              # Tietojen haku
│   │   └── player_scraper.py
│   ├── optimization/      # Optimointialgoritmit
│   │   ├── chemistry_system.py
│   │   └── team_optimizer.py
│   └── gui/               # Käyttöliittymä
│       └── main_window.py
└── README.md
```

## Kehitys

### Uusien kemioiden lisääminen

Lisää uusia kemioita `src/optimization/chemistry_system.py` -tiedostoon:

```python
self.boosts.append(ChemistryBoost(
    name="Uusi kemia",
    boost_type="ovr",  # tai "salary_cap" tai "ap"
    boost_value=2,
    requirements={
        "nationality_finland": 2,
        "position_forward": 2
    },
    description="2x Suomi hyökkäysparissa"
))
```

### Tietokannan päivittäminen

Päivitä pelaajakorttien tiedot:

```python
from src.data.player_scraper import PlayerScraper
scraper = PlayerScraper()
scraper.update_player_data()
```

## Ongelmat ja rajoitukset

- Pelaajakorttien tiedot haetaan ulkoisesta lähteestä, joten tiedot voivat olla vanhentuneita
- Optimointialgoritmi on yksinkertaistettu versio - todellinen optimointi voisi olla monimutkaisempi
- Kemiat-systeemi on perusversio - NHL 26:ssa voi olla monimutkaisempia kemioita

## Lisenssi

MIT License - katso LICENSE-tiedosto.

## Yhteystiedot

- GitHub: [Beeque/huttista](https://github.com/Beeque/huttista)
- Ongelmat: Luo issue GitHubissa

## Changelog

### v1.0.0
- Ensimmäinen versio
- Pelaajakorttien tietojen haku
- Peruskemiat-systeemi
- Graafinen käyttöliittymä
- Windows executable