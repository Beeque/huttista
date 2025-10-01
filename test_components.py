#!/usr/bin/env python3
"""
Test script for NHL HUT scraping components
Tests the new master scraper, validator, and enrichment components
"""

import json
import sys
import logging
from pathlib import Path
import subprocess
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_master_scraper():
    """Test the master scraper with a small dataset"""
    logger.info("Testing master scraper...")
    
    try:
        # Test single country scraping
        cmd = [
            'python', 'nhl_master_scraper.py',
            '--mode', 'single',
            '--nationality', 'Austria',
            '--output-dir', 'test_data'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            logger.info("✓ Master scraper test passed")
            
            # Check if output file was created
            output_file = Path('test_data/austria.json')
            if output_file.exists():
                with open(output_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                logger.info(f"✓ Created {output_file} with {len(data.get('data', []))} records")
                return True
            else:
                logger.error("✗ Output file not created")
                return False
        else:
            logger.error(f"✗ Master scraper test failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        logger.error("✗ Master scraper test timed out")
        return False
    except Exception as e:
        logger.error(f"✗ Master scraper test failed: {e}")
        return False

def test_data_validator():
    """Test the data validator"""
    logger.info("Testing data validator...")
    
    try:
        # Test validation on the created file
        cmd = [
            'python', 'data_validator.py',
            'test_data/austria.json'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            logger.info("✓ Data validator test passed")
            logger.info("Validation output:")
            print(result.stdout)
            return True
        else:
            logger.error(f"✗ Data validator test failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        logger.error("✗ Data validator test timed out")
        return False
    except Exception as e:
        logger.error(f"✗ Data validator test failed: {e}")
        return False

def test_abilities_enrichment():
    """Test the abilities enrichment (limited test)"""
    logger.info("Testing abilities enrichment...")
    
    try:
        # Test enrichment on the created file
        cmd = [
            'python', 'enrich_abilities_enhanced.py',
            'test_data/austria.json',
            '--delay', '1.0'  # Slower for testing
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            logger.info("✓ Abilities enrichment test passed")
            
            # Check if abilities were added
            with open('test_data/austria.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            records_with_abilities = 0
            for record in data.get('data', []):
                if 'abilities' in record and record['abilities']:
                    records_with_abilities += 1
            
            logger.info(f"✓ Enriched {records_with_abilities} records with abilities")
            return True
        else:
            logger.error(f"✗ Abilities enrichment test failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        logger.error("✗ Abilities enrichment test timed out")
        return False
    except Exception as e:
        logger.error(f"✗ Abilities enrichment test failed: {e}")
        return False

def test_automation_scheduler():
    """Test the automation scheduler (configuration only)"""
    logger.info("Testing automation scheduler...")
    
    try:
        # Test configuration loading
        cmd = [
            'python', 'automation_scheduler.py',
            '--mode', 'run',
            '--countries', 'Austria',
            '--config', 'test_automation_config.json'
        ]
        
        # Create test config
        test_config = {
            'output_dir': 'test_data',
            'countries': ['Austria'],
            'schedule': {
                'daily_scrape': False,
                'enrich_abilities': False,
                'validate_data': False,
                'cleanup_old_files': False
            }
        }
        
        with open('test_automation_config.json', 'w', encoding='utf-8') as f:
            json.dump(test_config, f, indent=2)
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            logger.info("✓ Automation scheduler test passed")
            return True
        else:
            logger.error(f"✗ Automation scheduler test failed: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"✗ Automation scheduler test failed: {e}")
        return False

def cleanup_test_files():
    """Clean up test files"""
    logger.info("Cleaning up test files...")
    
    test_files = [
        'test_data',
        'test_automation_config.json',
        'scraper.log',
        'automation.log'
    ]
    
    for file_path in test_files:
        path = Path(file_path)
        if path.exists():
            if path.is_dir():
                import shutil
                shutil.rmtree(path)
            else:
                path.unlink()
            logger.info(f"Removed {file_path}")

def main():
    """Run all component tests"""
    logger.info("Starting NHL HUT component tests...")
    
    # Create test data directory
    Path('test_data').mkdir(exist_ok=True)
    
    tests = [
        ("Master Scraper", test_master_scraper),
        ("Data Validator", test_data_validator),
        ("Abilities Enrichment", test_abilities_enrichment),
        ("Automation Scheduler", test_automation_scheduler)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        logger.info(f"\n{'='*50}")
        logger.info(f"Running {test_name} test...")
        logger.info(f"{'='*50}")
        
        try:
            success = test_func()
            results[test_name] = success
            if success:
                logger.info(f"✓ {test_name} test PASSED")
            else:
                logger.error(f"✗ {test_name} test FAILED")
        except Exception as e:
            logger.error(f"✗ {test_name} test FAILED with exception: {e}")
            results[test_name] = False
        
        time.sleep(2)  # Brief pause between tests
    
    # Summary
    logger.info(f"\n{'='*50}")
    logger.info("TEST SUMMARY")
    logger.info(f"{'='*50}")
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, success in results.items():
        status = "PASSED" if success else "FAILED"
        logger.info(f"{test_name}: {status}")
    
    logger.info(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All tests passed!")
    else:
        logger.warning(f"⚠️  {total - passed} tests failed")
    
    # Cleanup
    cleanup_test_files()
    
    return passed == total

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)