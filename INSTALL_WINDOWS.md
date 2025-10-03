# 🏒 NHL Card Monitor - Windows Asennusohje

## 📋 Vaatimukset

### Python 3.8+ (Pakollinen)
1. **Lataa Python**: https://www.python.org/downloads/
2. **Asenna Python**: ✅ Merkitse "Add Python to PATH"
3. **Tarkista asennus**: Avaa Command Prompt ja kirjoita `python --version`

### Tarvittavat tiedostot
- `nhl_card_monitor_console.py` - Pääohjelma
- `update_missing_cards_final.py` - Korttien haku
- `enrich_country_xfactors.py` - X-Factor rikastus
- `utils_clean.py` - Apufunktiot
- `master.json` - Pelaajien tietokanta
- `run_nhl_monitor.bat` - Windows käynnistys
- `run_nhl_monitor.ps1` - PowerShell käynnistys

## 🚀 Asennus

### Vaihe 1: Lataa tiedostot
1. **Lataa kaikki tiedostot** samaan kansioon
2. **Varmista** että `master.json` on mukana
3. **Luo kansio** esim. `C:\NHL_Monitor\`

### Vaihe 2: Asenna Python-paketit
Avaa Command Prompt kansiossa ja aja:
```cmd
pip install requests beautifulsoup4
```

### Vaihe 3: Testaa asennus
```cmd
python nhl_card_monitor_console.py
```

## 🎮 Käyttö

### Käynnistys
1. **Kaksoisklikkaa** `run_nhl_monitor.bat`
2. **Tai** avaa Command Prompt ja aja:
   ```cmd
   python nhl_card_monitor_console.py
   ```

### Valikko
```
📋 VALIKKO:
1. 🔍 Hae uusia kortteja
2. ▶️  Aloita automaattinen seuranta
3. ⏸️  Pysäytä seuranta
4. ⚡ Rikasta X-Factor tiedot
5. 🔄 Lataa master.json uudelleen
6. 📊 Näytä tilastot
7. 🚪 Lopeta
```

## ⚙️ Automaattinen seuranta

### Käynnistä seuranta
1. **Valitse** vaihtoehto `2` valikosta
2. **Ohjelma tarkistaa** uusia kortteja 30 min välein
3. **Uudet kortit** näkyvät automaattisesti

### Pysäytä seuranta
1. **Valitse** vaihtoehto `3` valikosta
2. **Tai** paina `Ctrl+C`

## 🔧 Vianmääritys

### Python ei löydy
```
ERROR: Python is not installed or not in PATH
```
**Ratkaisu**: Asenna Python uudelleen ja merkitse "Add Python to PATH"

### master.json puuttuu
```
WARNING: master.json not found
```
**Ratkaisu**: Lataa `master.json` samaan kansioon

### Paketit puuttuvat
```
ModuleNotFoundError: No module named 'requests'
```
**Ratkaisu**: Aja `pip install requests beautifulsoup4`

### Verkkovirhe
```
Error fetching cards: Connection timeout
```
**Ratkaisu**: Tarkista internet-yhteys ja kokeile uudelleen

## 📁 Tiedostot

### Ohjelman tiedostot
- `nhl_card_monitor_console.py` - Pääohjelma
- `nhl_monitor_console.log` - Lokitiedosto
- `missing_cards_urls.json` - Puuttuvat kortit (luodaan automaattisesti)

### Vaihtoehtoiset tiedostot
- `run_nhl_monitor.bat` - Windows käynnistys
- `run_nhl_monitor.ps1` - PowerShell käynnistys

## 🔄 Päivitykset

### Ohjelman päivitys
1. **Lataa uudet** Python-tiedostot
2. **Korvaa vanhat** tiedostot
3. **Säilytä** `master.json` ja lokitiedostot

### Tietojen päivitys
- **master.json** päivittyy automaattisesti
- **Varmuuskopioi** tiedosto säännöllisesti

## 📊 Suorituskyky

### Odotettu suoritusaika
- **Korttien haku**: 1-2 minuuttia
- **X-Factor rikastus**: 0.5s per pelaaja
- **Automaattinen tarkistus**: 10-30 sekuntia

### Resurssien käyttö
- **RAM**: ~50-100 MB
- **Verkkoliikenne**: ~1-5 MB per haku
- **Levytila**: ~10-50 MB (lokeineen)

## 🛡️ Turvallisuus

### Windows Defender
- **Sallittu** - Ohjelma on turvallinen
- **Jos estetty**: Lisää poikkeus Windows Defenderiin

### Verkko
- **Vain luku** - Ohjelma ei lähetä tietoja
- **HTTPS** - Kaikki yhteydet salatut
- **Ei evästeitä** - Ei tallenna henkilötietoja

## 📞 Tuki

### Lokitiedostot
- **Sijainti**: `nhl_monitor_console.log`
- **Sisältö**: Kaikki ohjelman toiminta
- **Koko**: Kasvaa ajan myötä

### Virheiden raportointi
1. **Kopioi** virheviesti lokista
2. **Kerro** mitä teit ennen virhettä
3. **Liitä** master.json koko (rivimäärä)

---

**🏒 NHL Card Monitor** - Automaattinen korttien seuranta Windows 11:lle