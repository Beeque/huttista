from bs4 import BeautifulSoup

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

def parse_salary_number(text: str):

    if not text:
        return None
    t = str(text).strip().lower().replace(',', '')
    # Extract first number
    num_str = ''
    for ch in t:
        if ch.isdigit() or ch == '.':
            num_str += ch
        elif num_str:
            break
    if not num_str:
        return None
    try:
        base = float(num_str)
    except Exception:
        return None
    if 'm' in t:
        return int(round(base * 1_000_000))
    if 'k' in t:
        return int(round(base * 1_000))
    return int(round(base))

def clean_common_fields(row: dict) -> dict:

    cleaned = {k: v for k, v in row.items() if isinstance(k, str) and k.strip() != ''}
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
    # EU units
    kg = parse_weight_kg(cleaned.get('weight', ''))
    if kg is not None:
        cleaned['weight_kg'] = kg
        cleaned['weight'] = f"{kg} kg"
    cm = parse_height_cm(cleaned.get('height', ''))
    if cm is not None:
        cleaned['height_cm'] = cm
        cleaned['height'] = f"{cm} cm"
    # Salary number
    salary_num = parse_salary_number(cleaned.get('salary', ''))
    if salary_num is not None:
        cleaned['salary'] = salary_num
        cleaned['salary_number'] = salary_num
    return cleaned

