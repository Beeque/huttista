#!/usr/bin/env python3
"""
Enhanced Abilities Enrichment Script
Integrates with the main scraping pipeline to add player abilities
"""

import json
import sys
import time
import requests
import logging
from pathlib import Path
from bs4 import BeautifulSoup
from typing import List, Dict, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AbilitiesEnricher:
    def __init__(self, base_url: str = "https://nhlhutbuilder.com/player-stats.php?id={pid}"):
        self.base_url = base_url
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Referer': 'https://nhlhutbuilder.com/player-stats.php',
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def fetch_abilities(self, player_id: int, max_retries: int = 3) -> List[Dict]:
        """Fetch abilities for a specific player with retry logic"""
        url = self.base_url.format(pid=player_id)
        
        for attempt in range(max_retries):
            try:
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')
                abilities = self._parse_abilities(soup)
                logger.debug(f"Fetched {len(abilities)} abilities for player {player_id}")
                return abilities
                
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed for player {player_id}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    logger.error(f"Failed to fetch abilities for player {player_id} after {max_retries} attempts")
                    return []

    def _parse_abilities(self, soup: BeautifulSoup) -> List[Dict]:
        """Parse abilities from the HTML soup"""
        abilities = []
        
        # Method 1: Look for ability_info blocks
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
                except (ValueError, TypeError):
                    ap = None
            
            if name:
                abilities.append({'name': name, 'ap': ap})
        
        # Method 2: Fallback to player_abi icons if no descriptions found
        if not abilities:
            for icon in soup.select('.player_abi'):
                title = icon.get('title') or ''
                if title:
                    # Title format: "NAME: <p>description</p>"
                    name = title.split(':', 1)[0].strip()
                    if name:
                        abilities.append({'name': name, 'ap': None})
        
        # Method 3: Look for other ability patterns
        if not abilities:
            for ability_div in soup.select('[class*="ability"], [class*="skill"]'):
                text = ability_div.get_text(strip=True)
                if text and len(text) > 2:
                    abilities.append({'name': text, 'ap': None})
        
        return abilities

    def enrich_file(self, file_path: str, delay: float = 0.5) -> int:
        """Enrich a JSON file with abilities data"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            return 0
        
        logger.info(f"Enriching {file_path} with abilities...")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load {file_path}: {e}")
            return 0
        
        # Handle both direct array and metadata wrapper formats
        if isinstance(data, dict) and 'data' in data:
            records = data['data']
            is_wrapped = True
        else:
            records = data
            is_wrapped = False
        
        enriched_count = 0
        total_records = len(records)
        
        for i, record in enumerate(records, 1):
            player_id = record.get('player_id')
            if not player_id:
                logger.warning(f"Record {i} has no player_id, skipping")
                continue
            
            try:
                # Convert to int if it's a string
                if isinstance(player_id, str):
                    player_id = int(player_id)
                
                abilities = self.fetch_abilities(player_id)
                record['abilities'] = abilities
                enriched_count += 1
                
                logger.info(f"Progress: {i}/{total_records} - Enriched player {player_id} with {len(abilities)} abilities")
                
                # Rate limiting
                time.sleep(delay)
                
            except Exception as e:
                logger.error(f"Failed to enrich player {player_id}: {e}")
                record['abilities'] = []
                continue
        
        # Save enriched data
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"Successfully enriched {enriched_count} records in {file_path}")
        except Exception as e:
            logger.error(f"Failed to save enriched data: {e}")
            return 0
        
        return enriched_count

    def enrich_directory(self, directory: str, pattern: str = "*.json", delay: float = 0.5) -> Dict[str, int]:
        """Enrich all JSON files in a directory"""
        directory = Path(directory)
        
        if not directory.exists():
            logger.error(f"Directory not found: {directory}")
            return {}
        
        results = {}
        json_files = list(directory.glob(pattern))
        
        if not json_files:
            logger.warning(f"No JSON files found in {directory}")
            return {}
        
        logger.info(f"Found {len(json_files)} JSON files to enrich")
        
        for file_path in json_files:
            logger.info(f"Processing {file_path.name}...")
            count = self.enrich_file(file_path, delay)
            results[str(file_path)] = count
        
        return results

    def batch_enrich(self, file_paths: List[str], delay: float = 0.5) -> Dict[str, int]:
        """Enrich multiple files in batch"""
        results = {}
        
        for file_path in file_paths:
            logger.info(f"Processing {file_path}...")
            count = self.enrich_file(file_path, delay)
            results[file_path] = count
        
        return results

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Enhance NHL player data with abilities')
    parser.add_argument('input', help='Input JSON file or directory')
    parser.add_argument('--delay', type=float, default=0.5, help='Delay between requests (seconds)')
    parser.add_argument('--pattern', default='*.json', help='File pattern for directory processing')
    parser.add_argument('--batch', nargs='+', help='List of specific files to process')
    
    args = parser.parse_args()
    
    enricher = AbilitiesEnricher()
    
    try:
        if args.batch:
            # Batch processing of specific files
            results = enricher.batch_enrich(args.batch, args.delay)
        else:
            input_path = Path(args.input)
            
            if input_path.is_file():
                # Single file
                count = enricher.enrich_file(input_path, args.delay)
                print(f"Enriched {count} records in {input_path}")
            elif input_path.is_dir():
                # Directory processing
                results = enricher.enrich_directory(input_path, args.pattern, args.delay)
                total = sum(results.values())
                print(f"Enriched {total} records across {len(results)} files")
            else:
                print(f"Invalid input: {input_path}")
                sys.exit(1)
                
    except KeyboardInterrupt:
        logger.info("Enrichment interrupted by user")
    except Exception as e:
        logger.error(f"Enrichment failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()