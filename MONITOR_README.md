# 🏒 NHL HUT Builder Cards Monitor

## Yleiskuvaus
Automaattinen Windows-sovellus, joka valvoo NHL HUT Builder -sivuston korttien default view -sivua ja lisää uudet kortit automaattisesti master.json -tietokantaan.

## 🎯 Ominaisuudet
- 🔍 **Automaattinen valvonta** - Tarkistaa uudet kortit 30 minuutin välein
- 🆕 **Uusien korttien havaitseminen** - Vertailee default view kortteja master.json:iin
- 📊 **X-Factor datan haku** - Hakee automaattisesti X-Factor kykyjen tiedot uusista korteista
- 💾 **Automaattiset varmuuskopiot** - Luo varmuuskopion ennen muutoksia
- 📝 **Yksityiskohtainen lokitus** - Kirjaa kaikki toiminnot ja virheet
- 🌍 **EU-standardi** - Noudattaa eurooppalaisia mittayksiköitä (cm, kg)
- 🔄 **Datan yhtenäisyys** - Käyttää samaa datanpuhdistuslogiikkaa kuin olemassa olevat skraaperit

## 📁 Tiedostot

### Pääskriptit
- **`cards_monitor.py`** - Taustapalveluversio (ei konsoli-ikkunaa)
- **`cards_monitor_console.py`** - Konsoliversio (näyttää toiminnan)
- **`utils_clean.py`** - Datanpuhdistusfunktiot (pakollinen)

### Testaus ja rakentaminen
- **`test_monitor.py`** - Testaa kaikki komponentit
- **`run_monitor_test.py`** - Suorittaa yhden valvontasyklin testinä
- **`build_executables.py`** - Luo Windows executable -tiedostot
- **`cards_comparator.py`** - Vertailee kortteja master.json:iin

## 🚀 Käyttöohjeet

### Vaihtoehto 1: Python-skriptinä
```bash
# Konsoliversio (suositeltu testaukseen)
python3 cards_monitor_console.py

# Taustapalveluversio
python3 cards_monitor.py
```

### Vaihtoehto 2: Windows Executable
```bash
# Luo executable-tiedostot
python3 build_executables.py

# Kopioi dist/ kansio haluttuun paikkaan ja aja:
# NHL_Cards_Monitor_Console.exe (konsoliversio)
# NHL_Cards_Monitor_Service.exe (taustapalveluversio)
```

## ⚙️ Konfiguraatio

### Valvontaasetukset
- **Valvontaväli**: 30 minuuttia
- **Kortteja per sykli**: 100 (uusimmat)
- **Automaattinen X-Factor haku**: Kyllä
- **EU-yksikkömuunnos**: Kyllä (pituus cm, paino kg)
- **Datanpuhdistus**: HTML-poisto, numeerinen muunnos

### Tiedostot
- **`master.json`** - Pelaajien tietokanta
- **`cards_monitor.log`** - Yksityiskohtainen lokitiedosto
- **`backups/`** - Automaattiset varmuuskopiot

## 📊 Datan standardit

Monitor noudattaa samoja datan standardeja kuin olemassa olevat skraaperit:

### Mittayksiköt
- **Pituus**: Senttimetreissä (cm)
- **Paino**: Kilogrammoissa (kg)
- **Palkka**: Numeerisessa muodossa (esim. 5000000 $5M:lle)

### Tiedot
- **Tilastot**: Kaikki numeerisina arvoina
- **HTML**: Poistettu kaikista tekstikentistä
- **X-Factor**: Täydet tiedot tasoineen (Specialist/All-Star/Elite)

## 🔧 Testaus

### Testaa kaikki komponentit
```bash
python3 test_monitor.py
```

### Testaa yksi valvontasykli
```bash
python3 run_monitor_test.py
```

### Vertaile kortteja
```bash
python3 cards_comparator.py
```

## 📝 Lokitus

Kaikki toiminnot kirjataan `cards_monitor.log` -tiedostoon:

### Lokitettavat tapahtumat
- Valvontasyklien alku/loput
- Uusien korttien havaitseminen
- X-Factor datan hakeminen
- Tietokantapäivitykset
- Virheenkäsittely ja palautuminen
- Varmuuskopioiden luominen

### Lokin esimerkki
```
2025-10-02 20:49:25 - INFO - 🏒 NHL HUT Builder Cards Monitor started
2025-10-02 20:49:25 - INFO - 📂 Loaded 2253 existing card IDs
2025-10-02 20:49:29 - INFO - 🔄 Starting monitoring cycle...
2025-10-02 20:49:29 - INFO - ✅ Fetched 100 cards (Total: 2247, Filtered: 2247)
2025-10-02 20:49:29 - INFO - ✅ No new cards found
```

## 🛡️ Virheenkäsittely

### Automaattinen palautuminen
- Yhteysvirheet: Yritetään uudelleen seuraavassa syklissä
- API-virheet: Kirjataan lokiin ja jatketaan
- Tiedostovirheet: Luodaan varmuuskopio ja yritetään korjata

### Varmuuskopiot
- Automaattinen varmuuskopio ennen muutoksia
- Varmuuskopiot `backups/` kansiossa
- Timestamp-nimetyt tiedostot

## 📋 Vaatimukset

### Järjestelmä
- Windows 10/11
- Internet-yhteys
- Kirjoitusoikeudet suoritushakemistoon

### Tiedostot
- `utils_clean.py` (pakollinen)
- `master.json` (luodaan automaattisesti jos puuttuu)

## 🔍 Vianmääritys

### Yleiset ongelmat
1. **Tarkista `cards_monitor.log`** yksityiskohtaisille virheilmoituksille
2. **Varmista internetyhteys** - monitor tarvitsee pääsyn NHL HUT Builder:iin
3. **Tarkista tiedostooikeudet** - monitor tarvitsee kirjoitusoikeudet
4. **Varmista pakolliset tiedostot** ovat samassa hakemistossa
5. **Tarkista virustorjunta** - saattaa estää executable:n

### Testaus
- Suorita `test_monitor.py` tarkistaaksesi kaikki komponentit
- Käytä konsoliversiota (`cards_monitor_console.py`) debuggausta varten
- Tarkista lokitiedosto virheiden löytämiseksi

## 🎉 Johtopäätös

NHL HUT Builder Cards Monitor on täysin toimiva järjestelmä, joka:

✅ **Toimii luotettavasti** - Kaikki testit menivät läpi  
✅ **Noudattaa standardeja** - Käyttää samaa logiikkaa kuin muut skraaperit  
✅ **Valvoo automaattisesti** - Ei vaadi manuaalista seurantaa  
✅ **Säilyttää datan laadun** - EU-yksiköt, numeeriset arvot, X-Factor tiedot  
✅ **Käsittelee virheet** - Automaattiset varmuuskopiot ja palautuminen  
✅ **Lokittaa kaiken** - Yksityiskohtainen seuranta kaikista toiminnoista  

Monitor on valmis käyttöön ja automaattisesti lisää uudet kortit master.json:iin 30 minuutin välein! 🚀