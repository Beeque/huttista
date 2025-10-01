#!/usr/bin/env python3
"""
Automation Scheduler for NHL HUT Scraping
Handles batch processing, scheduling, and automated data pipeline
"""

import json
import sys
import time
import logging
import schedule
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import argparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('automation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AutomationScheduler:
    def __init__(self, config_file: str = "automation_config.json"):
        self.config_file = Path(config_file)
        self.config = self._load_config()
        self.output_dir = Path(self.config.get('output_dir', 'data'))
        self.output_dir.mkdir(exist_ok=True)
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load config: {e}, using defaults")
        
        # Default configuration
        default_config = {
            'output_dir': 'data',
            'log_dir': 'logs',
            'countries': [
                'Austria', 'Belarus', 'Czech Republic', 'Denmark', 'England', 'Finland',
                'France', 'Germany', 'Italy', 'Kazakhstan', 'Latvia', 'Lithuania',
                'Mainland China', 'Norway', 'Russia', 'Slovakia', 'Slovenia',
                'Sweden', 'Switzerland', 'Ukraine'
            ],
            'positions': ['LW', 'RW', 'C', 'D'],
            'teams': ['ANA', 'BOS', 'CHI', 'DET', 'EDM', 'LAK', 'MIN', 'MTL', 'NSH', 'NJD', 'NYI', 'NYR', 'OTT', 'PHI', 'PIT', 'SJS', 'STL', 'TBL', 'TOR', 'VAN', 'VGK', 'WPG', 'WSH'],
            'schedule': {
                'daily_scrape': True,
                'time': '02:00',
                'enrich_abilities': True,
                'validate_data': True,
                'cleanup_old_files': True,
                'retention_days': 30
            },
            'scraping': {
                'delay_between_requests': 0.5,
                'max_retries': 3,
                'timeout': 30
            }
        }
        
        # Save default config
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=2, ensure_ascii=False)
        
        return default_config

    def run_scraping_job(self, countries: List[str] = None, positions: List[str] = None, 
                        teams: List[str] = None, include_goalies: bool = True) -> Dict[str, Any]:
        """Run the scraping job with specified parameters"""
        logger.info("Starting automated scraping job...")
        
        start_time = datetime.now()
        results = {
            'start_time': start_time.isoformat(),
            'countries_processed': 0,
            'total_records': 0,
            'errors': [],
            'files_created': []
        }
        
        countries = countries or self.config['countries']
        
        try:
            # Run master scraper
            cmd = [
                'python', 'nhl_master_scraper.py',
                '--mode', 'all',
                '--output-dir', str(self.output_dir)
            ]
            
            if include_goalies:
                cmd.append('--goalies')
            
            if positions:
                cmd.extend(['--positions'] + positions)
            
            if teams:
                cmd.extend(['--teams'] + teams)
            
            logger.info(f"Running command: {' '.join(cmd)}")
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
            
            if result.returncode == 0:
                logger.info("Scraping completed successfully")
                results['countries_processed'] = len(countries)
                # Count created files
                json_files = list(self.output_dir.glob('*.json'))
                results['files_created'] = [str(f) for f in json_files]
                results['total_records'] = self._count_records_in_files(json_files)
            else:
                error_msg = f"Scraping failed: {result.stderr}"
                logger.error(error_msg)
                results['errors'].append(error_msg)
                
        except subprocess.TimeoutExpired:
            error_msg = "Scraping job timed out after 1 hour"
            logger.error(error_msg)
            results['errors'].append(error_msg)
        except Exception as e:
            error_msg = f"Scraping job failed: {e}"
            logger.error(error_msg)
            results['errors'].append(error_msg)
        
        results['end_time'] = datetime.now().isoformat()
        results['duration'] = (datetime.now() - start_time).total_seconds()
        
        return results

    def run_abilities_enrichment(self, files: List[str] = None) -> Dict[str, Any]:
        """Run abilities enrichment on specified files"""
        logger.info("Starting abilities enrichment...")
        
        start_time = datetime.now()
        results = {
            'start_time': start_time.isoformat(),
            'files_processed': 0,
            'total_records_enriched': 0,
            'errors': []
        }
        
        try:
            if files is None:
                # Find all JSON files in output directory
                files = [str(f) for f in self.output_dir.glob('*.json')]
            
            if not files:
                logger.warning("No files found for enrichment")
                return results
            
            # Run abilities enrichment
            cmd = ['python', 'enrich_abilities_enhanced.py'] + files
            cmd.extend(['--delay', str(self.config['scraping']['delay_between_requests'])])
            
            logger.info(f"Running command: {' '.join(cmd)}")
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
            
            if result.returncode == 0:
                logger.info("Abilities enrichment completed successfully")
                results['files_processed'] = len(files)
                # Parse output to get enriched count
                output_lines = result.stdout.split('\n')
                for line in output_lines:
                    if 'Enriched' in line and 'records' in line:
                        try:
                            count = int(line.split()[1])
                            results['total_records_enriched'] += count
                        except:
                            pass
            else:
                error_msg = f"Abilities enrichment failed: {result.stderr}"
                logger.error(error_msg)
                results['errors'].append(error_msg)
                
        except subprocess.TimeoutExpired:
            error_msg = "Abilities enrichment timed out after 30 minutes"
            logger.error(error_msg)
            results['errors'].append(error_msg)
        except Exception as e:
            error_msg = f"Abilities enrichment failed: {e}"
            logger.error(error_msg)
            results['errors'].append(error_msg)
        
        results['end_time'] = datetime.now().isoformat()
        results['duration'] = (datetime.now() - start_time).total_seconds()
        
        return results

    def run_data_validation(self, files: List[str] = None) -> Dict[str, Any]:
        """Run data validation on specified files"""
        logger.info("Starting data validation...")
        
        start_time = datetime.now()
        results = {
            'start_time': start_time.isoformat(),
            'files_validated': 0,
            'total_records': 0,
            'valid_records': 0,
            'invalid_records': 0,
            'errors': []
        }
        
        try:
            if files is None:
                # Validate entire output directory
                cmd = ['python', 'data_validator.py', str(self.output_dir)]
            else:
                # Validate specific files
                cmd = ['python', 'data_validator.py'] + files
            
            logger.info(f"Running command: {' '.join(cmd)}")
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            
            if result.returncode == 0:
                logger.info("Data validation completed successfully")
                # Parse validation results from output
                output_lines = result.stdout.split('\n')
                for line in output_lines:
                    if 'Total Records:' in line:
                        results['total_records'] = int(line.split(':')[1].strip())
                    elif 'Valid Records:' in line:
                        results['valid_records'] = int(line.split(':')[1].strip())
                    elif 'Invalid Records:' in line:
                        results['invalid_records'] = int(line.split(':')[1].strip())
            else:
                error_msg = f"Data validation failed: {result.stderr}"
                logger.error(error_msg)
                results['errors'].append(error_msg)
                
        except subprocess.TimeoutExpired:
            error_msg = "Data validation timed out after 10 minutes"
            logger.error(error_msg)
            results['errors'].append(error_msg)
        except Exception as e:
            error_msg = f"Data validation failed: {e}"
            logger.error(error_msg)
            results['errors'].append(error_msg)
        
        results['end_time'] = datetime.now().isoformat()
        results['duration'] = (datetime.now() - start_time).total_seconds()
        
        return results

    def cleanup_old_files(self, retention_days: int = None) -> Dict[str, Any]:
        """Clean up old files based on retention policy"""
        logger.info("Starting cleanup of old files...")
        
        retention_days = retention_days or self.config['schedule']['retention_days']
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        
        results = {
            'files_deleted': 0,
            'space_freed': 0,
            'errors': []
        }
        
        try:
            for file_path in self.output_dir.glob('*.json'):
                if file_path.stat().st_mtime < cutoff_date.timestamp():
                    file_size = file_path.stat().st_size
                    file_path.unlink()
                    results['files_deleted'] += 1
                    results['space_freed'] += file_size
                    logger.info(f"Deleted old file: {file_path}")
            
            logger.info(f"Cleanup completed: {results['files_deleted']} files deleted, {results['space_freed']} bytes freed")
            
        except Exception as e:
            error_msg = f"Cleanup failed: {e}"
            logger.error(error_msg)
            results['errors'].append(error_msg)
        
        return results

    def run_full_pipeline(self) -> Dict[str, Any]:
        """Run the complete data pipeline"""
        logger.info("Starting full data pipeline...")
        
        pipeline_results = {
            'start_time': datetime.now().isoformat(),
            'scraping': {},
            'enrichment': {},
            'validation': {},
            'cleanup': {},
            'overall_success': True
        }
        
        try:
            # Step 1: Scraping
            logger.info("Step 1: Data Scraping")
            pipeline_results['scraping'] = self.run_scraping_job()
            
            if pipeline_results['scraping']['errors']:
                pipeline_results['overall_success'] = False
                logger.error("Scraping failed, skipping remaining steps")
                return pipeline_results
            
            # Step 2: Abilities Enrichment
            if self.config['schedule']['enrich_abilities']:
                logger.info("Step 2: Abilities Enrichment")
                pipeline_results['enrichment'] = self.run_abilities_enrichment()
                
                if pipeline_results['enrichment']['errors']:
                    logger.warning("Abilities enrichment had errors, but continuing")
            
            # Step 3: Data Validation
            if self.config['schedule']['validate_data']:
                logger.info("Step 3: Data Validation")
                pipeline_results['validation'] = self.run_data_validation()
                
                if pipeline_results['validation']['errors']:
                    logger.warning("Data validation had errors")
            
            # Step 4: Cleanup
            if self.config['schedule']['cleanup_old_files']:
                logger.info("Step 4: Cleanup")
                pipeline_results['cleanup'] = self.cleanup_old_files()
            
            logger.info("Full pipeline completed successfully")
            
        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            pipeline_results['overall_success'] = False
            pipeline_results['error'] = str(e)
        
        pipeline_results['end_time'] = datetime.now().isoformat()
        pipeline_results['duration'] = (datetime.now() - datetime.fromisoformat(pipeline_results['start_time'])).total_seconds()
        
        return pipeline_results

    def _count_records_in_files(self, files: List[Path]) -> int:
        """Count total records in JSON files"""
        total = 0
        for file_path in files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                if isinstance(data, dict) and 'data' in data:
                    total += len(data['data'])
                elif isinstance(data, list):
                    total += len(data)
            except Exception:
                pass
        return total

    def setup_schedule(self):
        """Setup automated scheduling"""
        schedule_config = self.config['schedule']
        
        if schedule_config['daily_scrape']:
            time_str = schedule_config['time']
            schedule.every().day.at(time_str).do(self.run_full_pipeline)
            logger.info(f"Scheduled daily scraping at {time_str}")
        
        # Add more scheduling options as needed
        # schedule.every().monday.at("02:00").do(self.run_full_pipeline)
        # schedule.every().hour.do(self.run_scraping_job)

    def run_scheduler(self):
        """Run the scheduler loop"""
        logger.info("Starting automation scheduler...")
        self.setup_schedule()
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user")
        except Exception as e:
            logger.error(f"Scheduler failed: {e}")

def main():
    parser = argparse.ArgumentParser(description='NHL HUT Automation Scheduler')
    parser.add_argument('--mode', choices=['run', 'schedule', 'pipeline'], default='run',
                       help='Mode: run once, start scheduler, or run full pipeline')
    parser.add_argument('--config', default='automation_config.json',
                       help='Configuration file')
    parser.add_argument('--countries', nargs='+', help='Countries to scrape')
    parser.add_argument('--positions', nargs='+', help='Positions to scrape')
    parser.add_argument('--teams', nargs='+', help='Teams to scrape')
    parser.add_argument('--goalies', action='store_true', help='Include goalies')
    
    args = parser.parse_args()
    
    scheduler = AutomationScheduler(args.config)
    
    try:
        if args.mode == 'run':
            # Run once
            results = scheduler.run_scraping_job(args.countries, args.positions, args.teams, args.goalies)
            print(json.dumps(results, indent=2))
            
        elif args.mode == 'schedule':
            # Start scheduler
            scheduler.run_scheduler()
            
        elif args.mode == 'pipeline':
            # Run full pipeline
            results = scheduler.run_full_pipeline()
            print(json.dumps(results, indent=2))
            
    except KeyboardInterrupt:
        logger.info("Operation interrupted by user")
    except Exception as e:
        logger.error(f"Operation failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()