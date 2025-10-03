# 🏒 NHL Card Monitor - GUI .exe Luonti

## 🚀 Nopea tapa (Suositeltu)

### 1. Kaksoisklikkaa build-skriptiä
```cmd
build_exe_simple.bat
```

### 2. Odota että build valmistuu
- PyInstaller asennetaan automaattisesti
- .exe tiedosto luodaan `dist/` kansioon
- Valmis! 🎉

## 🔧 Manuaalinen tapa

### 1. Asenna PyInstaller
```cmd
pip install pyinstaller
```

### 2. Rakenna .exe
```cmd
pyinstaller --onefile --windowed --name "NHL_Card_Monitor_GUI" --add-data "master.json;." nhl_card_monitor_gui.py
```

### 3. Tarkista tulos
- **Sijainti**: `dist/NHL_Card_Monitor_GUI.exe`
- **Koko**: ~50-100 MB
- **Testaa**: Kaksoisklikkaa .exe tiedostoa

## 🎮 GUI Ominaisuudet

### 🔐 Login-ikkuna
- **Käyttäjänimi**: `admin`
- **Salasana**: `admin`
- **Demo-tila**: Ei kirjautumista tarvita

### 🎛️ Pääikkuna
- **🔍 Hae uusia kortteja** - Manuaalinen haku
- **▶️ Aloita seuranta** - Automaattinen seuranta 30 min välein
- **🔄 Päivitä data** - Lataa master.json uudelleen
- **⚡ Rikasta X-Factor** - Hae X-Factor tiedot

### 📊 Tila-paneeli
- **Nykyinen tila** - Mitä ohjelma tekee
- **Viimeisin tarkistus** - Milloin viimeksi tarkistettu
- **Edistymispalkki** - Näyttää työn edistymisen

### 🆕 Uudet kortit
- **Lista** - Näyttää löydetyt uudet kortit
- **Valinta** - Klikkaa korttia nähdäksesi tiedot
- **Automaattinen päivitys** - Päivittyy automaattisesti

### 📝 Aktiviteettiloki
- **Värikoodattu** - Eri värit eri tapahtumille
- **Reaaliaikainen** - Päivittyy heti
- **Täydellinen** - Kaikki tapahtumat lokissa

## 🎨 GUI Värit

### 🟢 Vihreä - Onnistumiset
- Korttien löytyminen
- Tietojen lataaminen
- Seurannan aloitus

### 🔵 Sininen - Tiedot
- Normaali toiminta
- Tila-päivitykset
- Automaattiset tarkistukset

### 🟡 Keltainen - Varoitukset
- Puuttuvat tiedostot
- Verkkovirheet
- Odottamattomat tilanteet

### 🔴 Punainen - Virheet
- Kriittiset virheet
- Verkko-ongelmat
- Tiedostovirheet

### 🩷 Pinkki - X-Factor
- X-Factor rikastus
- Kykyjen haku
- Tier-luokittelu

## 🔧 Vianmääritys

### .exe ei käynnisty
1. **Tarkista** että master.json on samassa kansiossa
2. **Kokeile** ajaa komentoriviltä: `NHL_Card_Monitor_GUI.exe`
3. **Tarkista** Windows Defender ei estä ohjelmaa

### Login ei toimi
- **Käyttäjänimi**: `admin`
- **Salasana**: `admin`
- **Tai** käytä "Demo-tila" nappia

### GUI ei näy
1. **Tarkista** että .exe on GUI-versio (ei console)
2. **Kokeile** uudelleenkäynnistää
3. **Tarkista** että Python on asennettuna

### Kortit eivät lataudu
1. **Klikkaa** "🔄 Päivitä data" nappia
2. **Tarkista** että master.json on olemassa
3. **Kokeile** "🔍 Hae uusia kortteja" nappia

## 📁 Tiedostot

### Tarvittavat tiedostot
- `nhl_card_monitor_gui.py` - GUI-ohjelma
- `master.json` - Pelaajien tietokanta
- `build_exe_simple.bat` - Build-skripti

### Luodut tiedostot
- `dist/NHL_Card_Monitor_GUI.exe` - Valmis .exe
- `nhl_monitor_gui.log` - Lokitiedosto
- `build/` - Build-tiedostot
- `dist/` - Valmiit .exe tiedostot

## 🚀 Jakelu

### Yksinkertainen jakelu
1. **Lataa** `NHL_Card_Monitor_GUI.exe`
2. **Lataa** `master.json`
3. **Aseta** samaan kansioon
4. **Käynnistä** .exe tiedosto

### Täydellinen paketti
- `NHL_Card_Monitor_GUI.exe` - Pääohjelma
- `master.json` - Tietokanta
- `README.txt` - Käyttöohje
- `LICENSE.txt` - Lisenssi

## 🎯 Erot konsoli-versioon

### ✅ GUI-versio
- **Moderni käyttöliittymä** - Helppo käyttää
- **Login-järjestelmä** - Turvallisuus
- **Värikoodattu loki** - Selkeä näkymä
- **Ei konsoli-ikkunaa** - Vain GUI
- **Automaattinen päivitys** - Reaaliaikainen

### 📱 Konsoli-versio
- **Komentorivi** - Teksti-pohjainen
- **Ei kirjautumista** - Suora käyttö
- **Yksinkertainen** - Vähän resursseja
- **Konsoli-ikkuna** - Teksti-loki
- **Manuaalinen** - Käyttäjä ohjaa

## 🔒 Turvallisuus

### Login-järjestelmä
- **Oletus-tunnukset**: admin/admin
- **Demo-tila**: Ei kirjautumista
- **Turvallinen**: Ei lähetä tietoja

### Tietojen käsittely
- **Vain luku** - Ei muokkaa tietoja
- **Paikallinen** - Ei lähetä verkkoon
- **Salattu** - HTTPS-yhteydet

---

**🏒 NHL Card Monitor GUI** - Valmis .exe tiedostoksi!