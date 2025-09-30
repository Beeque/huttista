#!/usr/bin/env python3
import json
import sys
import time
import requests

DT_URL = "https://nhlhutbuilder.com/php/player_stats.php"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'X-Requested-With': 'XMLHttpRequest',
    'Referer': 'https://nhlhutbuilder.com/player-stats.php',
}

def fetch_page(start: int, length: int, nationality: str):
    # Minimal DataTables server-side payload; filter nationality column via columns search or global search
    payload = {
        'draw': 1,
        'start': start,
        'length': length,
        # Column index for nationality per page_source_stats.html shows column order
        # We also send a global search to be safe
        'search[value]': '',
        'search[regex]': 'false',
        # Nationality column index is 2 in the DataTables config (0-based: card_art, card, nationality)
        'columns[2][data]': 'nationality',
        'columns[2][searchable]': 'true',
        'columns[2][orderable]': 'true',
        'columns[2][search][value]': nationality,
        'columns[2][search][regex]': 'false',
    }
    resp = requests.post(DT_URL, data=payload, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    return resp.json()

def main():
    nationality = 'Austria'
    start = 0
    length = 100
    all_rows = []

    try:
        # First page to get total
        data = fetch_page(start, length, nationality)
        total = data.get('recordsFiltered') or data.get('recordsTotal') or 0
        rows = data.get('data') or []
        all_rows.extend(rows)
        print(f"Fetched {len(rows)} / {total}")

        # Paginate if needed
        while len(all_rows) < total:
            start += length
            time.sleep(0.5)
            data = fetch_page(start, length, nationality)
            rows = data.get('data') or []
            all_rows.extend(rows)
            print(f"Fetched {len(all_rows)} / {total}")

        # Save
        out_path = "/workspace/nhl_players_austria.json"
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(all_rows, f, ensure_ascii=False, indent=2)
        print(f"Saved {len(all_rows)} Austrian players to {out_path}")
    except Exception as e:
        print(f"Failed to fetch Austrian players: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()

