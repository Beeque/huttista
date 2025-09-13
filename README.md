# NHL HUT Builder Web Scraper

Tämä projekti sisältää web scraperit NHL HUT Builder -sivustolta korttien tietojen keräämiseen.

## Tiedostot

- `nhl_scraper.py` - Perusversio scraperista
- `advanced_nhl_scraper.py` - Edistynyt versio yksityiskohtaisilla tiedoilla
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

Scraper kerää seuraavat tiedot NHL korteista:

- **Perustiedot**: Pelaajan nimi, ID, kuva, URL
- **X-Factor kyvyt**: Kyvyn nimi, tyyppi, kuvaus, ikoni
- **Tilastot**: Erilaiset pelitilastot (jos saatavilla)
- **Fyysiset tiedot**: Pituus, paino, kätisyys

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