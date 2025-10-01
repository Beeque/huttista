#!/usr/bin/env python3
import argparse
import json
import sys
import time
import requests
from utils_clean import clean_common_fields

DT_URL = "https://nhlhutbuilder.com/php/player_stats.php"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'X-Requested-With': 'XMLHttpRequest',
    'Referer': 'https://nhlhutbuilder.com/player-stats.php',
}

def fetch_page(start: int, length: int, nationality: str, position: str = None):
    payload = {
        'draw': 1,
        'start': start,
        'length': length,
        'search[value]': '',
        'search[regex]': 'false',
        'nationality': nationality,
    }
    columns = [
        'card_art','card','nationality','league','team','division','salary','position','hand','weight','height','full_name','overall','aOVR',
        'acceleration','agility','balance','endurance','speed','slap_shot_accuracy','slap_shot_power','wrist_shot_accuracy','wrist_shot_power',
        'deking','off_awareness','hand_eye','passing','puck_control','body_checking','strength','aggression','durability','fighting_skill',
        'def_awareness','shot_blocking','stick_checking','faceoffs','discipline','date_added','date_updated'
    ]
    for idx, name in enumerate(columns):
        payload[f'columns[{idx}][data]'] = name
        payload[f'columns[{idx}][name]'] = name
        payload[f'columns[{idx}][searchable]'] = 'true'
        payload[f'columns[{idx}][orderable]'] = 'true'
        payload[f'columns[{idx}][search][value]'] = ''
        payload[f'columns[{idx}][search][regex]'] = 'false'
    payload['columns[2][search][value]'] = nationality
    payload['columns[2][search][regex]'] = 'false'
    
    # Add position filter if specified
    if position:
        payload['columns[7][search][value]'] = position  # position is column 7
        payload['columns[7][search][regex]'] = 'false'
    resp = requests.post(DT_URL, data=payload, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    return resp.json()

def run(nationality: str, out_path: str, position: str = None):
    start = 0
    length = 200
    all_rows = []

    # First page
    data = fetch_page(start, length, nationality, position)
    total = data.get('recordsFiltered') or data.get('recordsTotal') or 0
    rows = data.get('data') or []
    all_rows.extend(rows)
    print(f"Fetched {len(rows)} / {total}")

    while len(all_rows) < total:
        start += length
        time.sleep(0.3)
        data = fetch_page(start, length, nationality, position)
        rows = data.get('data') or []
        all_rows.extend(rows)
        print(f"Fetched {len(all_rows)} / {total}")

    cleaned = [clean_common_fields(r) for r in all_rows]
    cleaned = [r for r in cleaned if (r.get('nationality') or '').strip().lower() == nationality.lower()]

    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(cleaned, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(cleaned)} players to {out_path}")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--nationality', required=True, help='Exact nationality string (e.g., Austria, Belarus)')
    ap.add_argument('--out', required=True, help='Output JSON path (e.g., austria.json)')
    ap.add_argument('--position', help='Position filter (e.g., LW, RW, C, D, G)')
    args = ap.parse_args()
    try:
        run(args.nationality, args.out, args.position)
    except Exception as e:
        print(f"Failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()

