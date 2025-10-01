# NHL HUT Builder Scraping & Data Pipeline

## Overview

This repository provides a comprehensive scraping and data processing pipeline for NHL HUT Builder player data. It includes multiple scraping approaches, data validation, abilities enrichment, and automation capabilities.

## Key Features

- **Multiple Scraping Methods**: Selenium-based scrapers for interactive pages and DataTables-based scrapers for backend data
- **Master Scraper**: Unified scraper that handles all countries, positions, and goalies systematically
- **Data Validation**: Comprehensive validation with quality control and statistics
- **Abilities Enrichment**: Automated enrichment of player abilities from individual player pages
- **Automation**: Scheduled batch processing and pipeline automation
- **Data Cleaning**: Robust cleaning utilities with EU units, numeric conversion, and HTML stripping

## Architecture

### Core Components

1. **Master Scraper** (`nhl_master_scraper.py`) - Unified scraper for all data types
2. **Data Validator** (`data_validator.py`) - Quality control and validation
3. **Abilities Enricher** (`enrich_abilities_enhanced.py`) - Player abilities enrichment
4. **Automation Scheduler** (`automation_scheduler.py`) - Batch processing and scheduling
5. **Data Cleaning** (`utils_clean.py`) - Shared cleaning utilities

### Legacy Scrapers

- `nhl_scraper_final.py`, `nhl_scraper_complete.py` - Selenium-based scrapers
- `scrape_country_datatables.py` - DataTables scraper for specific countries
- `scrape_goalies_country_datatables.py` - Goalie-specific scraper

## Environment Setup

1. Ensure Python 3.13+ is available
2. Create a virtual environment and install dependencies:

```bash
python3 -m venv .venv
./.venv/bin/pip install -U pip
./.venv/bin/pip install requests beautifulsoup4 selenium webdriver-manager schedule
```

3. For Selenium scrapers, ensure Chrome/Chromium is available:
   - Linux: `sudo apt-get install google-chrome-stable` or `sudo apt-get install chromium-browser`
   - The scraper will auto-detect available browsers

## Quick Start

### Basic Scraping

```bash
# Scrape a single country
python nhl_master_scraper.py --mode single --nationality Finland --goalies

# Scrape all countries
python nhl_master_scraper.py --mode all --goalies

# Scrape specific positions
python nhl_master_scraper.py --mode all --positions LW RW C D
```

### Data Enrichment

```bash
# Enrich abilities for all files in data directory
python enrich_abilities_enhanced.py data/

# Enrich specific files
python enrich_abilities_enhanced.py finland.json austria.json
```

### Data Validation

```bash
# Validate all files in data directory
python data_validator.py data/

# Validate specific file
python data_validator.py finland.json --output validation_report.txt
```

### Automation

```bash
# Run full pipeline once
python automation_scheduler.py --mode pipeline

# Start automated scheduler
python automation_scheduler.py --mode schedule
```

## Data Format Standards

### Scraping Rules (MUST)

All scraped data must adhere to these standards:

- **Numeric Fields**: All stat fields must be numbers (not strings)
  - `height` (cm), `weight` (kg), `overall`, and all stat fields
  - `aOVR` is a float; `overall` is an int
  - `salary` must be numeric (e.g., `$0.8M` → `800000`)

- **EU Units**: 
  - `height` stored as centimeters (int) with `height_cm` mirror
  - `weight` stored as kilograms (int) with `weight_kg` mirror

- **HTML Stripping**:
  - Remove all HTML from text fields
  - `card_art` must be only the image `src` path

- **Data Quality**:
  - Enforce nationality/team/league filters server-side and client-side
  - Drop empty keys
  - Validate data types and ranges

### Output Format

```json
{
  "metadata": {
    "scraped_at": "2025-01-XX",
    "total_records": 150,
    "scraper_version": "1.0.0"
  },
  "data": [
    {
      "player_id": 1013,
      "full_name": "MIKAEL GRANLUND",
      "nationality": "Finland",
      "position": "C",
      "overall": 80,
      "weight": 84,
      "height": 178,
      "salary": 1000000,
      "abilities": [
        {"name": "Quick Draw", "ap": 2},
        {"name": "Sniper", "ap": 1}
      ],
      "weight_kg": 84,
      "height_cm": 178,
      "salary_number": 1000000
    }
  ]
}
```

## Advanced Usage

### Master Scraper Options

```bash
# Scrape specific countries with filters
python nhl_master_scraper.py --mode single --nationality Finland --position C --team ANA

# Scrape with custom output directory
python nhl_master_scraper.py --mode all --output-dir custom_data --goalies
```

### Automation Configuration

Create `automation_config.json`:

```json
{
  "output_dir": "data",
  "countries": ["Finland", "Sweden", "Germany"],
  "positions": ["LW", "RW", "C", "D"],
  "schedule": {
    "daily_scrape": true,
    "time": "02:00",
    "enrich_abilities": true,
    "validate_data": true,
    "cleanup_old_files": true,
    "retention_days": 30
  }
}
```

### Data Validation Reports

The validator provides comprehensive reports including:
- Record-level validation with specific issues
- Statistical analysis of data quality
- Position and nationality distributions
- Overall rating statistics

## File Structure

```
├── nhl_master_scraper.py          # Main unified scraper
├── data_validator.py               # Data validation and quality control
├── enrich_abilities_enhanced.py    # Abilities enrichment
├── automation_scheduler.py         # Automation and scheduling
├── utils_clean.py                  # Data cleaning utilities
├── data/                          # Output directory
│   ├── finland.json
│   ├── finland_goalies.json
│   └── ...
├── logs/                          # Log files
└── automation_config.json         # Automation configuration
```

## Error Handling

All components include robust error handling:
- Retry logic with exponential backoff
- Comprehensive logging
- Graceful degradation on failures
- Detailed error reporting

## Performance Considerations

- Rate limiting between requests (configurable)
- Batch processing for large datasets
- Memory-efficient processing
- Parallel processing where possible

## Contributing

When adding new scrapers or features:
1. Follow the data format standards
2. Use `utils_clean.py` for data cleaning
3. Add comprehensive error handling
4. Include logging and validation
5. Update documentation

## Notes

- DataTables backend is recommended for reliability
- Selenium scrapers are needed for interactive pages
- All outputs must use `utils_clean.py` for consistency
- Automation requires `schedule` package