#!/usr/bin/env python3
import json
import sys
import time
import requests
from bs4 import BeautifulSoup

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
        'search[value]': '',
        'search[regex]': 'false',
        # Top-level fallback param some backends honor
        'nationality': nationality,
    }
    # Define columns similar to DataTables config in page_source_stats.html
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
    # Apply nationality filter on column 2
    payload['columns[2][search][value]'] = nationality
    payload['columns[2][search][regex]'] = 'false'
    resp = requests.post(DT_URL, data=payload, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    return resp.json()

def extract_text(html: str) -> str:
    if html is None:
        return ''
    if not isinstance(html, str):
        return str(html)
    soup = BeautifulSoup(html, 'html.parser')
    return soup.get_text(strip=True)

def extract_img_src(html: str) -> str:
    if not isinstance(html, str):
        return ''
    soup = BeautifulSoup(html, 'html.parser')
    img = soup.find('img')
    if img and img.get('src'):
        return img['src']
    return ''

def clean_row(row: dict) -> dict:
    cleaned = dict(row)
    # Strip HTML from known fields
    for key in ['full_name', 'team', 'league', 'division', 'nationality', 'position', 'hand', 'height', 'weight', 'salary', 'card']:
        if key in cleaned:
            cleaned[key] = extract_text(cleaned[key])
    # Card art -> image src only
    if 'card_art' in cleaned:
        cleaned['card_art'] = extract_img_src(cleaned['card_art'])
    # Normalize weight/height units spacing
    if 'weight' in cleaned:
        cleaned['weight'] = cleaned['weight'].replace('\u00a0', ' ').replace('  ', ' ').strip()
    if 'height' in cleaned:
        cleaned['height'] = cleaned['height'].replace('\u00a0', ' ').replace('  ', ' ').strip()

    # Convert to metric (EU): height -> cm, weight -> kg
    def to_int_safe(val):
        try:
            return int(round(float(val)))
        except Exception:
            return None

    def parse_weight_kg(text: str):
        if not text:
            return None
        lower = text.lower()
        # Extract first number
        num = None
        tmp = ''
        for ch in lower:
            if ch.isdigit() or ch == '.':
                tmp += ch
            elif tmp:
                break
        if tmp:
            try:
                num = float(tmp)
            except Exception:
                num = None
        if num is None:
            return None
        if 'kg' in lower:
            return to_int_safe(num)
        # assume pounds by default
        kg = num * 0.45359237
        return to_int_safe(kg)

    def parse_height_cm(text: str):
        if not text:
            return None
        lower = text.lower().replace(' ', '')
        # cm case
        if 'cm' in lower:
            digits = ''.join(ch for ch in lower if ch.isdigit() or ch == '.')
            if digits:
                try:
                    return to_int_safe(float(digits))
                except Exception:
                    return None
        # ft'in" case like 5'9" or 5'9
        ft = None
        inch = 0
        if "'" in lower:
            parts = lower.split("'")
            try:
                ft = int(parts[0])
            except Exception:
                ft = None
            if ft is not None and len(parts) > 1:
                rest = parts[1]
                digits = ''
                for ch in rest:
                    if ch.isdigit():
                        digits += ch
                    else:
                        if digits:
                            break
                if digits:
                    try:
                        inch = int(digits)
                    except Exception:
                        inch = 0
        if ft is not None:
            total_in = ft * 12 + inch
            cm = total_in * 2.54
            return to_int_safe(cm)
        return None

    kg = parse_weight_kg(cleaned.get('weight', ''))
    if kg is not None:
        cleaned['weight_kg'] = kg
        cleaned['weight'] = f"{kg} kg"
    cm = parse_height_cm(cleaned.get('height', ''))
    if cm is not None:
        cleaned['height_cm'] = cm
        cleaned['height'] = f"{cm} cm"
    return cleaned

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

        # Clean rows
        cleaned_rows = [clean_row(r) for r in all_rows]
        # Enforce nationality client-side as well
        cleaned_rows = [r for r in cleaned_rows if (r.get('nationality') or '').strip().lower() == 'austria']

        # Save both raw and cleaned
        out_raw = "/workspace/nhl_players_austria.json"
        out_clean = "/workspace/nhl_players_austria_clean.json"
        with open(out_raw, 'w', encoding='utf-8') as f:
            json.dump(all_rows, f, ensure_ascii=False, indent=2)
        with open(out_clean, 'w', encoding='utf-8') as f:
            json.dump(cleaned_rows, f, ensure_ascii=False, indent=2)
        print(f"Saved {len(all_rows)} Austrian players to {out_raw} and cleaned to {out_clean}")
    except Exception as e:
        print(f"Failed to fetch Austrian players: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()

