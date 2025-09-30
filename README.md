# HUTTISTA Scraping & Data Pipeline

## Overview

This repository scrapes and normalizes NHL HUT Builder player data for downstream use. It includes:
- Selenium-based scrapers for interactive pages (cards, filters).
- A DataTables-based scraper for the Player Stats backend.
- Shared cleaning utilities to normalize output, remove HTML, and convert units to EU formats.

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

## Notes

- If front-end scraping is required (cards pages), prefer Selenium scripts (`nhl_scraper_final.py`).
- For reliability, the DataTables backend is recommended; it returns structured JSON and filters server-side.
- Shared cleaning (`utils_clean.py`) must be applied to all outputs to maintain consistency across countries and runs.