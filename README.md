# NHL HUT Builder Web Scraper

Tämä projekti sisältää web scraperit NHL HUT Builder -sivustolta korttien tietojen keräämiseen.

## Tiedostot

- `nhl_scraper.py` - Perusversio scraperista
- `advanced_nhl_scraper.py` - Edistynyt versio yksityiskohtaisilla tiedoilla
- `enhanced_nhl_scraper.py` - Parannettu versio joka hakee tiedot myös yksittäisiltä korttisivuilta
- `test_scraper.py` - Test-skripti scraperin toimivuuden tarkistamiseen
- `test_single_card.py` - Test-skripti yksittäisen kortin hakemiseen
- `scraper_ui.py` - Graafinen käyttöliittymä
- `requirements.txt` - Tarvittavat Python-kirjastot

## Asennus

1. Asenna tarvittavat kirjastot:
```bash
pip install -r requirements.txt
```

## Käyttö

### Perusversio

```bash
python nhl_scraper.py
```

### Edistynyt versio

```bash
# Kerää perustiedot 50 kortista
python advanced_nhl_scraper.py --max-cards 50

# Kerää yksityiskohtaiset tiedot 20 kortista
python advanced_nhl_scraper.py --max-cards 20 --detailed

# Vie tiedot JSON-muotoon
python advanced_nhl_scraper.py --export-json nhl_cards.json

# Näytä vain tietokannan tilastot
python advanced_nhl_scraper.py --stats-only
```

### Parannettu versio (suositus)

```bash
# Kerää yksityiskohtaiset tiedot 10 kortista (hakee myös yksittäisiltä sivuilta)
python enhanced_nhl_scraper.py --max-cards 10

# Hae yksittäinen kortti player ID:n perusteella
python enhanced_nhl_scraper.py --single-card 2062

# Testaa yksittäisen kortin hakemista
python test_single_card.py 2062

# Näytä tietokannan tilastot
python enhanced_nhl_scraper.py --stats-only
```

## Tietokanta rakenne

### Taulut

1. **cards** - Pääkorttien tiedot
   - player_id, player_name, image_url, card_url
   - overall_rating, position, team, nationality
   - height, weight, handedness

2. **xfactor_abilities** - X-Factor kyvyt
   - ability_name, ability_type, description, icon_url
   - is_selected (valittu kyky)

3. **card_stats** - Korttien tilastot
   - stat_name, stat_value, stat_category

4. **player_details** - Pelaajien lisätiedot
   - birth_date, draft_info, contract_value

## Kerätyt tiedot

### Perusversiot
- **Perustiedot**: Pelaajan nimi, ID, kuva, URL
- **X-Factor kyvyt**: Kyvyn nimi, tyyppi, kuvaus, ikoni

### Parannettu versio (enhanced_nhl_scraper.py)
- **Perustiedot**: Pelaajan nimi, ID, kuva, URL, kokonaisarvosana
- **Fyysiset tiedot**: Pituus, paino, kätisyys, ikä
- **Henkilötiedot**: Syntymäpäivä, syntymäpaikka, kansallisuus
- **Pelitiedot**: Pelipaikka, joukkue
- **X-Factor kyvyt**: Kyvyn nimi, tyyppi, kuvaus, ikoni
- **Yksityiskohtaiset tilastot**: 
  - Luistelu (skating, speed, acceleration, agility, balance)
  - Ammunta (shooting, wrist shot, slap shot, shot power)
  - Kädet (hands, passing, puck control, deking)
  - Puolustus (defense, checking, stick checking, faceoffs)
  - Fyysisyys (physical, body checking, strength)
  - Maalivahti (goaltending, glove high/low, five hole)

Parannettu versio hakee tiedot myös yksittäisiltä korttisivuilta (`player-stats.php?id=XXXX`), joten se kerää paljon yksityiskohtaisempia tietoja kuin perusversiot.

## Huomioita

- Scraper sisältää rate limitingin sivuston kuormituksen välttämiseksi
- Virheenkäsittely on toteutettu uudelleenyrityksillä
- Tiedot tallennetaan SQLite-tietokantaan
- JSON-vienti mahdollista analyysiä varten

## Eettinen käyttö

⚠️ **Tärkeää**: Tarkista NHL HUT Builder -sivuston käyttöehdot ennen scraperin käyttöä. Kunnioita sivuston rate limiting -sääntöjä ja älä käytä scraperia liian intensiivisesti.

## Kehitys

Scraper voidaan laajentaa keräämään:
- Korttien hinnat ja markkinatiedot
- Pelaajien ura-tilastoja
- Joukkue- ja liiga-tietoja
- Korttien harvinaisuusluokituksia