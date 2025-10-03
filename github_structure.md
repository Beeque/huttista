# 🏒 NHL Card Monitor - GitHub Repository Rakenne

## 📁 Repository Rakenne

```
nhl-card-monitor/
├── README.md
├── LICENSE
├── requirements.txt
├── 
├── src/
│   ├── nhl_card_monitor_console.py
│   ├── nhl_card_monitor_enhanced.py
│   ├── update_missing_cards_final.py
│   ├── enrich_country_xfactors.py
│   └── utils_clean.py
├── 
├── build/
│   ├── build_exe.bat
│   ├── nhl_monitor.spec
│   └── create_exe_instructions.md
├── 
├── releases/
│   ├── v1.0.0/
│   │   ├── NHL_Card_Monitor.exe
│   │   ├── master.json
│   │   └── INSTALL_WINDOWS.md
│   └── latest/
│       ├── NHL_Card_Monitor.exe
│       ├── master.json
│       └── INSTALL_WINDOWS.md
├── 
├── docs/
│   ├── INSTALL_WINDOWS.md
│   ├── NHL_MONITOR_README.md
│   └── API_DOCUMENTATION.md
├── 
└── scripts/
    ├── run_nhl_monitor.bat
    ├── run_nhl_monitor.ps1
    └── setup.py
```

## 📝 README.md Sisältö

```markdown
# 🏒 NHL Card Monitor

Automaattinen korttien seuranta NHL HUT Builderille Windows 11:lle.

## ✨ Ominaisuudet

- 🔄 **Automaattinen seuranta** - Tarkistaa uusia kortteja 30 min välein
- 🆕 **Uusien korttien haku** - Manuaalinen ja automaattinen haku
- ⚡ **X-Factor rikastus** - Automaattinen X-Factor tietojen haku
- 🖼️ **Korttien kuvat** - Näyttää uusien korttien kuvat
- 📝 **Reaaliaikainen loggaus** - Värikoodattu loki kaikista tapahtumista

## 🚀 Nopea Aloitus

### Windows Executable (Suositeltu)
1. Lataa [viimeisin release](https://github.com/username/nhl-card-monitor/releases/latest)
2. Pura `NHL_Card_Monitor.exe` haluamaasi kansioon
3. Kaksoisklikkaa käynnistääksesi

### Python Source Code
```bash
git clone https://github.com/username/nhl-card-monitor.git
cd nhl-card-monitor
pip install -r requirements.txt
python src/nhl_card_monitor_console.py
```

## 📋 Vaatimukset

- Windows 10/11
- Internet-yhteys
- Python 3.8+ (vain source code versiolle)

## 🎮 Käyttö

### Automaattinen seuranta
1. Käynnistä ohjelma
2. Valitse "▶️ Aloita automaattinen seuranta"
3. Ohjelma tarkistaa uusia kortteja 30 min välein

### Manuaalinen haku
1. Valitse "🔍 Hae uusia kortteja"
2. Odota että haku valmistuu
3. Tarkastele löydettyjä kortteja

### X-Factor rikastus
1. Kun uusia kortteja löytyy
2. Valitse "⚡ Rikasta X-Factor tiedot"
3. Odota että rikastus valmistuu

## 📊 Screenshot

[Kuva ohjelmasta toiminnassa]

## 🔧 Kehitys

### Rakenna .exe itse
```bash
cd build
build_exe.bat
```

### Testaa
```bash
python -m pytest tests/
```

## 📄 Lisenssi

MIT License - katso [LICENSE](LICENSE) tiedosto

## 🤝 Osallistu

1. Fork repository
2. Luo feature branch (`git checkout -b feature/amazing-feature`)
3. Commit muutokset (`git commit -m 'Add amazing feature'`)
4. Push branch (`git push origin feature/amazing-feature`)
5. Avaa Pull Request

## 📞 Tuki

- 🐛 [Bug Reports](https://github.com/username/nhl-card-monitor/issues)
- 💡 [Feature Requests](https://github.com/username/nhl-card-monitor/issues)
- 📧 Email: support@example.com

## 🙏 Kiitokset

- NHL HUT Builder - Data source
- Python community - Libraries
- Contributors - Code improvements

---

**🏒 NHL Card Monitor** - Automaattinen korttien seuranta NHL HUT Builderille
```

## 🏷️ Git Tags ja Releases

### Tagit
```bash
git tag -a v1.0.0 -m "Initial release"
git tag -a v1.1.0 -m "Added GUI version"
git tag -a v1.2.0 -m "Performance improvements"
```

### Release Template
```markdown
## 🆕 Uudet ominaisuudet
- Automaattinen korttien seuranta
- X-Factor kykyjen rikastus
- Korttien kuvien näyttö
- Reaaliaikainen loggaus

## 🔧 Tekniset parannukset
- Robusti virheenkäsittely
- Automaattiset uudelleenyritykset
- Threading ei-jäädyttävään käyttöliittymään

## 📋 Vaatimukset
- Windows 10/11
- Internet-yhteys
- Ei Python-asennusta tarvita

## 📥 Lataa
- `NHL_Card_Monitor.exe` - Pääohjelma
- `master.json` - Pelaajien tietokanta
- `INSTALL_WINDOWS.md` - Asennusohje
```

## 🔧 GitHub Actions (CI/CD)

### .github/workflows/build.yml
```yaml
name: Build Executable

on:
  push:
    tags:
      - 'v*'
  workflow_dispatch:

jobs:
  build:
    runs-on: windows-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pyinstaller
    
    - name: Build executable
      run: |
        pyinstaller --onefile --console --name "NHL_Card_Monitor" --add-data "src/update_missing_cards_final.py;." --add-data "src/enrich_country_xfactors.py;." --add-data "src/utils_clean.py;." --add-data "master.json;." src/nhl_card_monitor_console.py
    
    - name: Upload artifact
      uses: actions/upload-artifact@v3
      with:
        name: NHL_Card_Monitor
        path: dist/NHL_Card_Monitor.exe
    
    - name: Create Release
      if: startsWith(github.ref, 'refs/tags/')
      uses: softprops/action-gh-release@v1
      with:
        files: dist/NHL_Card_Monitor.exe
        generate_release_notes: true
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## 📊 GitHub Pages

### docs/index.md
```markdown
# 🏒 NHL Card Monitor Documentation

Tervetuloa NHL Card Monitorin dokumentaatioon!

## 📚 Sisältö

- [Asennusohje](INSTALL_WINDOWS.md)
- [Käyttöohje](NHL_MONITOR_README.md)
- [API Dokumentaatio](API_DOCUMENTATION.md)
- [Vianmääritys](TROUBLESHOOTING.md)

## 🚀 Nopea Aloitus

1. Lataa [viimeisin release](https://github.com/username/nhl-card-monitor/releases/latest)
2. Pura tiedostot
3. Käynnistä `NHL_Card_Monitor.exe`
4. Nauti automaattisesta korttien seurannasta!

## 📞 Tuki

- [GitHub Issues](https://github.com/username/nhl-card-monitor/issues)
- [Discussions](https://github.com/username/nhl-card-monitor/discussions)
```

## 🔒 Security

### .github/SECURITY.md
```markdown
# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.x.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

Please report security vulnerabilities to security@example.com

## Security Considerations

- The application only reads data from NHL HUT Builder
- No personal data is stored or transmitted
- All network connections use HTTPS
- No authentication credentials are required
```

---

**🏒 NHL Card Monitor** - Valmis GitHub-repository:ksi!