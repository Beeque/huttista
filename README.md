# HUTTISTA Scraping & Data Pipeline

## Overview

This repository scrapes and normalizes NHL HUT Builder player data for downstream use. It includes:
- Selenium-based scrapers for interactive pages (cards, filters).
- A DataTables-based scraper for the Player Stats backend.
- Shared cleaning utilities to normalize output, remove HTML, and convert units to EU formats.
- **NHL Team Builder GUI** - Interactive team building application with player filtering and team management.

## 🏒 NHL Team Builder

The NHL Team Builder is a graphical application that allows you to build and manage NHL teams using the scraped player data.

### Quick Start

**Linux/macOS:**
```bash
./build_nhl_team_builder.sh
```

**Windows:**
```cmd
build_nhl_team_builder.bat
```

**Manual setup:**
```bash
# Install dependencies
pip install pillow requests

# Run the application (try py first, then python3, then python)
py nhl_team_builder.py
# OR
python3 nhl_team_builder.py
# OR
python nhl_team_builder.py
```

### Features

- **Team Filtering**: Filter players by NHL team (76 teams available)
- **Player Search**: Search players by name
- **Position Filtering**: Filter by position (LW, C, RW, LD, RD, G)
- **X-Factor Filtering**: Filter by X-Factor abilities
- **Team Building**: Drag and drop players to build your team
- **Budget Management**: Track salary cap and spending
- **Debug Tools**: Built-in debugging and testing tools

### Troubleshooting

If the team dropdown only shows "All":
1. Click the "🔧 Test Dropdowns" button
2. Use the BOS/TOR/All test buttons
3. Check the debug log at the bottom
4. Click the "🔄" refresh button next to the team dropdown

### Recent Fixes

- ✅ Fixed team dropdown to show all 76 NHL teams
- ✅ Added comprehensive debugging tools
- ✅ Improved UI with status labels and test buttons
- ✅ Enhanced error handling and logging

### Quick Start

**Linux/macOS:**
```bash
./build_nhl_team_builder.sh
```

**Windows:**
```cmd
build_nhl_team_builder.bat
```

**Manual setup:**
```bash
# Install Python 3 and required packages
pip install pillow requests

# Run the application
python3 nhl_team_builder.py
```

### Features

- **Team Filtering**: Filter players by NHL team (76 teams available)
- **Advanced Filters**: Filter by nationality, position, overall rating, and X-Factor abilities
- **Interactive Team Building**: Drag-and-drop interface for building lineups
- **Budget Management**: Track salary spending with visual budget indicators
- **Debug Tools**: Built-in debugging and testing tools for troubleshooting
- **Save/Load**: Save and load team configurations

### Troubleshooting

If the team dropdown shows only "All":
1. Click the "🔧 Test Dropdowns" button to debug
2. Use the "🔄" refresh button to reload team data
3. Check the debug log at the bottom of the application
4. Use the BOS/TOR/All test buttons to verify filtering works

## Key Files

- `nhl_scraper_final.py`, `nhl_scraper_working.py`, `nhl_scraper_simple.py`: experimental Selenium and requests scrapers for cards.
- `scrape_austria_datatables.py`: DataTables scraper (server-side) for fetching players filtered by nationality (Austria example).
- `utils_clean.py`: shared cleaning helpers (strip HTML, extract image src, numeric conversion for height/weight/salary/stats).
- `nhl_cards_enriched_au.json`, `nhl_cards_enriched_au_final.json`: example enriched AU datasets.

## Environment Setup

1. Ensure Python 3.13 is available.
2. Create a virtual environment and install deps:

```
python3 -m venv .venv
./.venv/bin/pip install -U pip
./.venv/bin/pip install requests beautifulsoup4 selenium webdriver-manager
```

Selenium requires a Chrome/Chromium binary and matching driver. If running headless in CI or on servers without Chrome, prefer the DataTables scraper.

## Scraping Rules (MUST)

When scraping and exporting JSON:
- Numeric fields MUST be numbers (not strings):
  - `height` (cm), `weight` (kg), `overall`, and all stat fields (e.g., `speed`, `passing`, …).
  - `aOVR` is a float; `overall` is an int.
  - `salary` MUST be numeric (e.g., `$0.8M` → `800000`). Keep `salary_number` mirror as the same numeric value.
- EU units:
  - `height` stored as centimeters (int); a mirror `height_cm` is included.
  - `weight` stored as kilograms (int); a mirror `weight_kg` is included.
- HTML stripping:
  - Remove all HTML from text fields (`full_name`, `weight`, `height`, `salary`, etc.).
  - `card_art` MUST be only the image `src` path.
- Strict filters:
  - Enforce exact `nationality` and/or `team`/`league` filters server-side when possible (DataTables columns search).
  - Additionally enforce the same filters client-side before writing JSON.
- No empty keys:
  - Drop any empty keys like `"": "0"` from rows.
- Auto-push:
  - After any successful scrape/normalization, commit and push changes to GitHub.

These are enforced by `utils_clean.py` and should be reused across all scrapers.

## Running the Austria Scraper

```
./.venv/bin/python scrape_austria_datatables.py
```

Outputs:
- Raw: `nhl_players_austria.json`
- Cleaned: `nhl_players_austria_clean.json`

The cleaned output adheres to the Scraping Rules above.

## Extending To Other Nationalities

- Clone `scrape_austria_datatables.py` and change `nationality = 'Austria'` to the desired country, or make nationality a parameter.
- Always run rows through `utils_clean.clean_common_fields` prior to writing JSON.

## Auto-push Policy

- Any successful scraping/normalization run should be committed and pushed to GitHub (this branch or per-feature branch) to keep artifacts versioned.

Suggested workflow:

```
git add -A
git commit -m "data(nationality): refresh + EU units + numeric salary + numeric stats"
git push origin HEAD
```

## Data Collection Status

### 🇺🇸 USA: 633 players (Complete)
- **LW**: 95 players
- **RW**: 108 players  
- **LD**: 121 players
- **RD**: 93 players
- **C**: 156 players
- **G**: 60 players
- **X-Factor data**: ✅ Complete
- **All stats**: ✅ Complete

### 🇨🇦 Canada: 1,318 players (Complete)
- **LW**: 240 players
- **RW**: 186 players
- **C**: 357 players
- **LD**: 230 players
- **RD**: 165 players
- **G**: 140 players
- **X-Factor data**: ✅ Complete
- **All stats**: ✅ Complete

### 🇸🇪 Sweden: 192 players (Complete)
- **LW**: 37 players
- **RW**: 26 players
- **LD**: 48 players
- **RD**: 19 players
- **C**: 39 players
- **G**: 23 players
- **X-Factor data**: ✅ Complete
- **All stats**: ✅ Complete

### Other Countries: 393 players
- **Russia**: 96 players
- **Finland**: 95 players
- **Czechia**: 82 players
- **Slovakia**: 24 players
- **Switzerland**: 21 players
- **Germany**: 20 players
- **Latvia**: 13 players
- **Belarus**: 10 players
- **Denmark**: 9 players
- **Austria**: 6 players
- **Norway**: 3 players
- **Other countries**: 10 players

**Total**: 2,536 players across 25 countries

## Important API Notes

### 🔑 **Critical: Player ID Behavior**
- **Player IDs can be shared** between `player-stats.php` and `goalie-stats.php` APIs
- **Same ID ≠ Same Player** - they are completely different people
- Example: `player-stats?id=1034` = VIKTOR ARVIDSSON (skater)
- Example: `goalie-stats?id=1034` = JACOB MARKSTROM (goalie)
- **Never remove "duplicates"** based on shared IDs - they are valid separate players

### 📊 **API Endpoints**
- **Skaters**: `https://nhlhutbuilder.com/php/player_stats.php`
- **Goalies**: `https://nhlhutbuilder.com/php/goalie_stats.php`
- **Player Details**: `https://nhlhutbuilder.com/player-stats.php?id={pid}`

### 🏒 **X-Factor Data**
- X-Factor abilities are **NOT available** in the main API responses
- Must be fetched individually from player detail pages
- Each player requires a separate HTTP request to get X-Factor data
- X-Factor tiers: Specialist (1 AP), All-Star (2 AP), Elite (3 AP)

## Data Collection Challenges & Solutions

### 🚨 **Major Issues Encountered**

#### 1. **Shared Player ID Problem**
- **Issue**: Player IDs are shared between `player-stats.php` and `goalie-stats.php` APIs
- **Problem**: Same ID (e.g., 1034) refers to different players in different APIs
- **Solution**: Never treat shared IDs as duplicates - they are valid separate players
- **Impact**: Prevented data loss of ~23 goalies in Sweden dataset

#### 2. **X-Factor Data Missing from APIs**
- **Issue**: X-Factor abilities not available in main API responses
- **Problem**: Required individual HTTP requests to player detail pages
- **Solution**: Created `enrich_country_xfactors.py` with timeout protection
- **Performance**: ~0.5 seconds per player for X-Factor fetching

#### 3. **Goalie vs Skater URL Confusion**
- **Issue**: Goalies need `goalie-stats.php` URLs, not `player-stats.php`
- **Problem**: Wrong X-Factor data fetched (e.g., "WARRIOR" instead of "POST TO POST")
- **Solution**: Added `is_goalie` parameter to X-Factor fetcher
- **Detection**: Use goalie-specific fields (`glove_high`, `stick_low`, etc.)

#### 4. **"Unknown" Players in Large Datasets**
- **Issue**: Canada dataset had 140 players with `None` position
- **Problem**: Goalies not properly identified in skater API
- **Solution**: Separate goalie fetching using `goalie_stats.php` API
- **Result**: Clean separation of skaters vs goalies

#### 5. **Timeout and Rate Limiting**
- **Issue**: Large datasets (Canada: 1,318 players) caused timeouts
- **Problem**: Network issues and server load during X-Factor enrichment
- **Solution**: Added timeout protection, retry mechanisms, and progress updates
- **Performance**: Canada processed in chunks with real-time progress

### 🛠️ **Most Used Scripts**

#### **Primary Scrapers:**
1. **`universal_country_fetcher.py`** - Main scraper for all countries
   - Handles both skaters (`player_stats.php`) and goalies (`goalie_stats.php`)
   - Automatic data cleaning and URL generation
   - Used for: Australia, Austria, Belarus, Czechia, Denmark, England, Finland, France, Germany, Italy, Kazakhstan, Latvia, Lithuania, Mainland China, Norway, Russia, Slovakia, Slovenia, Switzerland, Ukraine

2. **Position-specific fetchers** - For large countries (USA, Canada)
   - `usa_lw_fetcher.py`, `usa_rw_fetcher.py`, etc.
   - `canada_lw_fetcher.py`, `canada_rw_fetcher.py`, etc.
   - Used for: USA (633 players), Canada (1,318 players)

#### **X-Factor Enrichment:**
3. **`enrich_country_xfactors.py`** - Universal X-Factor enricher
   - Handles both skaters and goalies with correct URLs
   - Timeout protection and progress tracking
   - Used for: All countries after initial data collection

#### **Data Processing:**
4. **`utils_clean.py`** - Shared data cleaning utilities
   - HTML stripping, unit conversion, numeric formatting
   - Used by: Every scraper for consistent data format

### 📊 **Performance Metrics**
- **Total players collected**: 2,536
- **Countries processed**: 25
- **X-Factor coverage**: 100% (all players)
- **Data quality**: All numeric fields properly formatted
- **Processing time**: ~2-3 hours for complete dataset

## Notes

- If front-end scraping is required (cards pages), prefer Selenium scripts (`nhl_scraper_final.py`).
- For reliability, the DataTables backend is recommended; it returns structured JSON and filters server-side.
- Shared cleaning (`utils_clean.py`) must be applied to all outputs to maintain consistency across countries and runs.
- **X-Factor enrichment is time-intensive** - expect ~0.5 seconds per player for X-Factor data fetching.