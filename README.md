# HUTTISTA Scraping & Data Pipeline

## Overview

This repository scrapes and normalizes NHL HUT Builder player data for downstream use. It includes:
- Selenium-based scrapers for interactive pages (cards, filters).
- A DataTables-based scraper for the Player Stats backend.
- Shared cleaning utilities to normalize output, remove HTML, and convert units to EU formats.

## Key Files

- `nhl_scraper_final.py`, `nhl_scraper_working.py`, `nhl_scraper_simple.py`: experimental Selenium and requests scrapers for cards.
- `scrape_austria_datatables.py`: DataTables scraper (server-side) for fetching players filtered by nationality (Austria example).
- `utils_clean.py`: shared cleaning helpers (strip HTML, extract image src, convert height/weight to EU units, salary to numeric, drop empty keys).
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

## Running the Austria Scraper

```
./.venv/bin/python scrape_austria_datatables.py
```

Outputs:
- Raw: `nhl_players_austria.json`
- Cleaned: `nhl_players_austria_clean.json`

The cleaned output enforces:
- nationality = "Austria" strictly
- HTML removed from text fields (`full_name`, `weight`, `card_art`, etc.)
- `card_art` becomes the bare image `src`
- EU units:
  - `height_cm` and `weight_kg` numeric fields
  - `height` updated to "### cm"
  - `weight` updated to "### kg"
- `salary` converted to numeric (e.g., `$0.8M` -> `800000`) with `salary_number`
- Empty keys are dropped

## Extending To Other Nationalities

- Clone `scrape_austria_datatables.py` and change `nationality = 'Austria'` to the desired country.
- Or parameterize nationality via CLI/env and reuse the same module.

## Auto-push Policy

- Any successful scraping/normalization run should be committed and pushed to GitHub (this branch or per-feature branch) to keep artifacts versioned.
- Suggested workflow:

```
git add -A
git commit -m "data(nationality): refresh + EU units + numeric salary"
git push origin HEAD
```

## Notes

- If front-end scraping is required (cards pages), prefer Selenium scripts (`nhl_scraper_final.py`).
- For reliability, the DataTables backend is recommended; it returns structured JSON and filters server-side.
- Shared cleaning (`utils_clean.py`) should be applied to all outputs to maintain consistency across countries and runs.