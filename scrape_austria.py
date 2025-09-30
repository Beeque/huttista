#!/usr/bin/env python3
import json
from nhl_scraper_final import NHLHUTScraperFinal

def main():
    scraper = NHLHUTScraperFinal()
    try:
        if not scraper.setup_driver():
            print("Failed to setup driver")
            return
        if not scraper.navigate_to_cards_page():
            print("Failed to navigate to cards page")
            return

        nationalities = scraper.get_available_nationalities()
        at = next((n for n in nationalities if n['text'].lower() == 'austria'), None)
        if not at:
            print("Austria nationality not found in dropdown")
            return

        cards = scraper.scrape_nationality(at['value'], at['text'])

        # Persist to JSON
        out_path = "/workspace/nhl_cards_enriched_at.json"
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(cards, f, ensure_ascii=False, indent=2)
        print(f"Saved {len(cards)} Austrian player cards to {out_path}")

    finally:
        scraper.close()

if __name__ == '__main__':
    main()

