#!/usr/bin/env python3
"""
NHL HUT Master Scraper
Comprehensive scraper for all countries, positions, and goalies with enhanced error handling
"""

import argparse
import json
import sys
import time
import requests
import logging
from datetime import datetime
from pathlib import Path
from utils_clean import clean_common_fields

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class NHLMasterScraper:
    def __init__(self, output_dir="data"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # API endpoints
        self.player_stats_url = "https://nhlhutbuilder.com/php/player_stats.php"
        self.goalie_stats_url = "https://nhlhutbuilder.com/php/goalie_stats.php"
        
        # Headers for requests
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': 'https://nhlhutbuilder.com/player-stats.php',
        }
        
        # Player columns
        self.player_columns = [
            'card_art','card','nationality','league','team','division','salary','position','hand','weight','height','full_name','overall','aOVR',
            'acceleration','agility','balance','endurance','speed','slap_shot_accuracy','slap_shot_power','wrist_shot_accuracy','wrist_shot_power',
            'deking','off_awareness','hand_eye','passing','puck_control','body_checking','strength','aggression','durability','fighting_skill',
            'def_awareness','shot_blocking','stick_checking','faceoffs','discipline','date_added','date_updated'
        ]
        
        # Goalie columns
        self.goalie_columns = [
            'card_art','card','nationality','league','team','division','salary','hand','weight','height','full_name','overall','aOVR',
            'glove_high','glove_low','stick_high','stick_low','shot_recovery','aggression','agility','speed','positioning','breakaway',
            'vision','poke_check','rebound_control','passing','date_added','date_updated'
        ]

    def fetch_page(self, start: int, length: int, nationality: str, position: str = None, team: str = None, is_goalie: bool = False):
        """Fetch a page of data with retry logic"""
        url = self.goalie_stats_url if is_goalie else self.player_stats_url
        columns = self.goalie_columns if is_goalie else self.player_columns
        
        payload = {
            'draw': 1,
            'start': start,
            'length': length,
            'search[value]': '',
            'search[regex]': 'false',
            'nationality': nationality,
        }
        
        # Configure columns
        for idx, name in enumerate(columns):
            payload[f'columns[{idx}][data]'] = name
            payload[f'columns[{idx}][name]'] = name
            payload[f'columns[{idx}][searchable]'] = 'true'
            payload[f'columns[{idx}][orderable]'] = 'true'
            payload[f'columns[{idx}][search][value]'] = ''
            payload[f'columns[{idx}][search][regex]'] = 'false'
        
        # Apply nationality filter
        payload['columns[2][search][value]'] = nationality
        payload['columns[2][search][regex]'] = 'false'
        
        # Apply position filter if specified
        if position and not is_goalie:
            payload['columns[7][search][value]'] = position
            payload['columns[7][search][regex]'] = 'false'
        
        # Apply team filter if specified
        if team:
            team_col_idx = 4
            payload[f'columns[{team_col_idx}][search][value]'] = team
            payload[f'columns[{team_col_idx}][search][regex]'] = 'false'
        
        # Retry logic
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = requests.post(url, data=payload, headers=self.headers, timeout=30)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    raise

    def scrape_nationality(self, nationality: str, position: str = None, team: str = None, is_goalie: bool = False):
        """Scrape all data for a specific nationality with optional filters"""
        logger.info(f"Scraping {nationality} - Position: {position}, Team: {team}, Goalie: {is_goalie}")
        
        start = 0
        length = 200
        all_rows = []
        
        try:
            # First page to get total count
            data = self.fetch_page(start, length, nationality, position, team, is_goalie)
            total = data.get('recordsFiltered') or data.get('recordsTotal') or 0
            rows = data.get('data') or []
            all_rows.extend(rows)
            logger.info(f"Fetched {len(rows)} / {total}")
            
            # Paginate through all pages
            while len(all_rows) < total:
                start += length
                time.sleep(0.5)  # Rate limiting
                data = self.fetch_page(start, length, nationality, position, team, is_goalie)
                rows = data.get('data') or []
                all_rows.extend(rows)
                logger.info(f"Fetched {len(all_rows)} / {total}")
            
            # Clean and validate data
            cleaned_rows = []
            for row in all_rows:
                try:
                    cleaned = clean_common_fields(row)
                    # Enforce nationality filter client-side
                    if (cleaned.get('nationality') or '').strip().lower() == nationality.lower():
                        cleaned_rows.append(cleaned)
                except Exception as e:
                    logger.warning(f"Error cleaning row: {e}")
                    continue
            
            logger.info(f"Successfully scraped {len(cleaned_rows)} records for {nationality}")
            return cleaned_rows
            
        except Exception as e:
            logger.error(f"Failed to scrape {nationality}: {e}")
            return []

    def save_data(self, data: list, filename: str):
        """Save data to JSON file with metadata"""
        output_path = self.output_dir / filename
        
        # Add metadata
        output_data = {
            'metadata': {
                'scraped_at': datetime.now().isoformat(),
                'total_records': len(data),
                'scraper_version': '1.0.0'
            },
            'data': data
        }
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, ensure_ascii=False, indent=2)
            logger.info(f"Saved {len(data)} records to {output_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save data: {e}")
            return False

    def scrape_all_countries(self, positions: list = None, teams: list = None, include_goalies: bool = True):
        """Scrape all available countries with optional filters"""
        # Common countries to scrape
        countries = [
            'Austria', 'Belarus', 'Czech Republic', 'Denmark', 'England', 'Finland', 
            'France', 'Germany', 'Italy', 'Kazakhstan', 'Latvia', 'Lithuania', 
            'Mainland China', 'Norway', 'Russia', 'Slovakia', 'Slovenia', 
            'Sweden', 'Switzerland', 'Ukraine'
        ]
        
        total_scraped = 0
        
        for country in countries:
            logger.info(f"Processing {country}...")
            
            # Scrape regular players
            players = self.scrape_nationality(country, None, None, False)
            if players:
                filename = f"{country.lower().replace(' ', '_')}.json"
                self.save_data(players, filename)
                total_scraped += len(players)
            
            # Scrape goalies if requested
            if include_goalies:
                goalies = self.scrape_nationality(country, None, None, True)
                if goalies:
                    filename = f"{country.lower().replace(' ', '_')}_goalies.json"
                    self.save_data(goalies, filename)
                    total_scraped += len(goalies)
            
            # Scrape by position if specified
            if positions:
                for position in positions:
                    pos_players = self.scrape_nationality(country, position, None, False)
                    if pos_players:
                        filename = f"{country.lower().replace(' ', '_')}_{position.lower()}.json"
                        self.save_data(pos_players, filename)
                        total_scraped += len(pos_players)
            
            # Scrape by team if specified
            if teams:
                for team in teams:
                    team_players = self.scrape_nationality(country, None, team, False)
                    if team_players:
                        filename = f"{country.lower().replace(' ', '_')}_{team.lower()}.json"
                        self.save_data(team_players, filename)
                        total_scraped += len(team_players)
            
            # Rate limiting between countries
            time.sleep(2)
        
        logger.info(f"Total records scraped: {total_scraped}")
        return total_scraped

    def run_single_scrape(self, nationality: str, position: str = None, team: str = None, is_goalie: bool = False):
        """Run a single scrape operation"""
        data = self.scrape_nationality(nationality, position, team, is_goalie)
        
        if data:
            # Generate filename
            filename_parts = [nationality.lower().replace(' ', '_')]
            if is_goalie:
                filename_parts.append('goalies')
            if position:
                filename_parts.append(position.lower())
            if team:
                filename_parts.append(team.lower())
            
            filename = '_'.join(filename_parts) + '.json'
            self.save_data(data, filename)
            return len(data)
        else:
            logger.warning(f"No data found for {nationality}")
            return 0

def main():
    parser = argparse.ArgumentParser(description='NHL HUT Master Scraper')
    parser.add_argument('--mode', choices=['single', 'all'], default='single',
                       help='Scraping mode: single country or all countries')
    parser.add_argument('--nationality', help='Nationality to scrape (for single mode)')
    parser.add_argument('--position', help='Position filter (e.g., LW, RW, C, D, G)')
    parser.add_argument('--team', help='Team filter (e.g., ANA, BOS, CHI)')
    parser.add_argument('--goalies', action='store_true', help='Include goalies')
    parser.add_argument('--output-dir', default='data', help='Output directory')
    parser.add_argument('--positions', nargs='+', help='Multiple positions to scrape (for all mode)')
    parser.add_argument('--teams', nargs='+', help='Multiple teams to scrape (for all mode)')
    
    args = parser.parse_args()
    
    scraper = NHLMasterScraper(args.output_dir)
    
    try:
        if args.mode == 'single':
            if not args.nationality:
                logger.error("Nationality is required for single mode")
                sys.exit(1)
            
            count = scraper.run_single_scrape(
                args.nationality, 
                args.position, 
                args.team, 
                args.goalies
            )
            logger.info(f"Scraped {count} records")
            
        elif args.mode == 'all':
            count = scraper.scrape_all_countries(
                args.positions, 
                args.teams, 
                args.goalies
            )
            logger.info(f"Total scraped: {count} records")
            
    except KeyboardInterrupt:
        logger.info("Scraping interrupted by user")
    except Exception as e:
        logger.error(f"Scraping failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()