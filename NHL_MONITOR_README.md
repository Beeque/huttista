# 🏒 NHL Card Monitor - Windows Executable

Automaattinen NHL HUT Builder korttien seurantaohjelma Windows 11:lle.

## ✨ Ominaisuudet

### 🔄 Automaattinen seuranta
- **30 minuutin välein** tarkistaa uusia kortteja
- **Taustalla toimiva** seuranta
- **Automaattinen ilmoitus** uusista korteista

### 🆕 Uusien korttien haku
- **"Find New Cards"** nappi manuaaliseen hakemiseen
- **Reaaliaikainen** edistymisen seuranta
- **Yksityiskohtaiset** korttien tiedot

### ⚡ X-Factor rikastus
- **Automaattinen** X-Factor tietojen haku
- **Tier-luokittelu** (Specialist, All-Star, Elite)
- **AP-kustannukset** jokaiselle kyvyllä

### 🖼️ Korttien kuvat
- **Automaattinen** kuvien lataus
- **Resize** sopivaan kokoon
- **Nopea** kuvan näyttö

### 📝 Reaaliaikainen loggaus
- **Värikoodattu** log-näkymä
- **Aikaleimat** kaikille tapahtumille
- **Tiedostoon** tallentaminen

## 🚀 Asennus ja käyttö

### 1. Lataa ja asenna
```bash
# Lataa NHL_Card_Monitor.exe
# Aseta se haluamaasi kansioon
```

### 2. Ensimmäinen käynnistys
1. **Kaksoisklikkaa** `NHL_Card_Monitor.exe`
2. **Odota** että ohjelma lataa master.json
3. **Klikkaa** "🔄 Refresh Data" jos tarvitsee

### 3. Automaattinen seuranta
1. **Klikkaa** "▶️ Start Monitoring"
2. **Ohjelma tarkistaa** uusia kortteja 30 min välein
3. **Uudet kortit** näkyvät automaattisesti

### 4. Manuaalinen haku
1. **Klikkaa** "🔍 Find New Cards"
2. **Odota** että haku valmistuu
3. **Tarkastele** löydettyjä kortteja

### 5. X-Factor rikastus
1. **Kun uusia kortteja** löytyy
2. **Klikkaa** "⚡ Enrich X-Factors"
3. **Odota** että rikastus valmistuu

## 🎮 Käyttöliittymä

### Pääikkuna
- **🎮 Controls**: Napit ohjelman hallintaan
- **📊 Status**: Nykyinen tila ja edistyminen
- **🆕 New Cards**: Löydetyt uudet kortit
- **📝 Activity Log**: Reaaliaikainen loki

### Korttien tarkastelu
1. **Valitse kortti** listasta
2. **Katso tietoja** "Card Details" -osiossa
3. **Tarkastele kuvaa** "Card Image" -osiossa

### Log-näkymä
- **🟢 Vihreä**: Normaali info
- **🟡 Keltainen**: Varoitukset
- **🔴 Punainen**: Virheet
- **🔵 Sininen**: Onnistumiset
- **🩷 Pinkki**: X-Factor tiedot

## 📁 Tiedostot

### Ohjelman tiedostot
- `NHL_Card_Monitor.exe` - Pääohjelma
- `master.json` - Pelaajien tietokanta (tarvitaan)
- `nhl_monitor.log` - Lokitiedosto

### Vaihtoehtoiset tiedostot
- `missing_cards_urls.json` - Puuttuvat kortit (luodaan automaattisesti)

## ⚙️ Asetukset

### Automaattinen seuranta
- **Aikaväli**: 30 minuuttia
- **Maksimisivut**: 10 sivua per haku
- **Viive**: 1 sekunti sivujen välillä

### X-Factor rikastus
- **Timeout**: 10 sekuntia per pelaaja
- **Viive**: 0.5 sekuntia pelaajien välillä
- **Uudelleenyritykset**: 3 kertaa

## 🛠️ Kehittäjille

### Lähdekoodi
```bash
# Kloonaa repository
git clone <repo-url>

# Asenna riippuvuudet
pip install -r requirements.txt

# Aja ohjelma
python nhl_card_monitor_enhanced.py

# Rakenna executable
python build_executable.py
```

### Riippuvuudet
- `requests` - HTTP-pyynnöt
- `beautifulsoup4` - HTML-parsinta
- `Pillow` - Kuvien käsittely
- `tkinter` - GUI (sisäänrakennettuna Pythonissa)

## 🐛 Ongelmanratkaisu

### Ohjelma ei käynnisty
1. **Tarkista** että master.json on samassa kansiossa
2. **Kokeile** ajaa komentoriviltä virheiden näkemiseksi
3. **Tarkista** Windows Defender ei estä ohjelmaa

### Ei löydy uusia kortteja
1. **Klikkaa** "🔄 Refresh Data"
2. **Tarkista** että master.json on ajan tasalla
3. **Kokeile** manuaalista hakua

### Kuvat eivät lataudu
1. **Tarkista** internet-yhteys
2. **Kokeile** uudelleen valitsemalla kortti
3. **Tarkista** lokista virheviestit

### X-Factor rikastus epäonnistuu
1. **Odota** että rikastus valmistuu
2. **Tarkista** internet-yhteys
3. **Kokeile** uudelleen myöhemmin

## 📞 Tuki

### Lokitiedostot
- **Sijainti**: `nhl_monitor.log`
- **Sisältö**: Kaikki ohjelman toiminta
- **Koko**: Kasvaa ajan myötä

### Virheiden raportointi
1. **Kopioi** virheviesti lokista
2. **Kerro** mitä teit ennen virhettä
3. **Liitä** master.json koko (rivimäärä)

## 🔄 Päivitykset

### Automaattiset päivitykset
- **Ei automaattisia** päivityksiä
- **Manuaalinen** lataus uudesta versiosta
- **Säilytä** master.json tiedosto

### Tietojen synkronointi
- **master.json** päivittyy automaattisesti
- **Varmuuskopioi** tiedosto säännöllisesti
- **Jaa** tiedosto muiden kanssa

## 📊 Tilastot

### Seuranta
- **Tarkistukset**: 30 min välein
- **Maksimisivut**: 10 per haku
- **Kortteja per sivu**: 40

### Suorituskyky
- **Haku**: ~1-2 minuuttia
- **X-Factor rikastus**: ~0.5s per pelaaja
- **Kuvien lataus**: ~1-2s per kuva

---

**🏒 NHL Card Monitor** - Automaattinen korttien seuranta NHL HUT Builderille