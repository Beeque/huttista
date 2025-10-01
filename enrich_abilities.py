#!/usr/bin/env python3
import json
import sys
import time
import requests
from bs4 import BeautifulSoup

BASE = "https://nhlhutbuilder.com/player-stats.php?id={pid}"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Referer': 'https://nhlhutbuilder.com/player-stats.php',
}

def fetch_abilities(pid: int):
    url = BASE.format(pid=pid)
    resp = requests.get(url, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'html.parser')
    abilities = []
    # Ability blocks patterned as .player_abi selected with accompanying #abi_desc_* entries
    # We scan descriptions area for name and AP
    for info in soup.select('.ability_info'):
        name = None
        ap = None
        name_el = info.select_one('.ability_name')
        if name_el:
            name = name_el.get_text(strip=True)
        ap_el = info.select_one('.ability_points .ap_amount')
        if ap_el:
            try:
                ap = int(ap_el.get_text(strip=True))
            except Exception:
                ap = None
        if name:
            abilities.append({'name': name, 'ap': ap})
    # Fallback scan for icons if descriptions absent
    if not abilities:
        for ico in soup.select('.player_abi'):
            title = ico.get('title') or ''
            if title:
                # title contains NAME: <p>desc</p>
                name = title.split(':', 1)[0].strip()
                if name:
                    abilities.append({'name': name, 'ap': None})
    return abilities

def enrich_file(path: str):
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    for row in data:
        pid = row.get('player_id')
        if not pid:
            continue
        try:
            row['abilities'] = fetch_abilities(int(pid))
            time.sleep(0.5)
        except Exception:
            row['abilities'] = []
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return len(data)

def main():
    if len(sys.argv) < 2:
        print('Usage: enrich_abilities.py <path-to-json>')
        sys.exit(1)
    total = enrich_file(sys.argv[1])
    print(f"Enriched abilities for {total} records in {sys.argv[1]}")

if __name__ == '__main__':
    main()

