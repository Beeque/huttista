#!/usr/bin/env python3
"""
Debug HTML structure of NHL HUT cards page
"""

import time
import os
import tempfile
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

class NHLHUTDebugger:
    def __init__(self):
        self.driver = None
        self.wait = None
        self.base_url = "https://nhlhutbuilder.com/cards.php"
        
    def setup_driver(self):
        """Setup Chrome WebDriver with appropriate options"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        # Create unique temp directory for each session
        temp_dir = tempfile.mkdtemp(prefix="chrome_")
        chrome_options.add_argument(f"--user-data-dir={temp_dir}")
        
        # Try to find Chrome binary
        possible_paths = [
            "/usr/bin/google-chrome",
            "/usr/bin/google-chrome-stable",
            "/usr/bin/chromium-browser",
            "/usr/bin/chromium"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                chrome_options.binary_location = path
                print(f"Using browser: {path}")
                break
        
        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.wait = WebDriverWait(self.driver, 15)
            print("✓ WebDriver initialized successfully")
            return True
        except Exception as e:
            print(f"✗ Failed to initialize WebDriver: {e}")
            return False
        
    def debug_page_structure(self):
        """Debug the page structure to understand card layout"""
        print("Debugging page structure...")
        
        try:
            self.driver.get(self.base_url)
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            time.sleep(3)
            
            # Get page source
            page_source = self.driver.page_source
            print(f"Page source length: {len(page_source)}")
            
            # Save page source for inspection
            with open("/workspace/page_source.html", "w", encoding="utf-8") as f:
                f.write(page_source)
            print("✓ Page source saved to page_source.html")
            
            # Look for various card-related elements
            selectors_to_try = [
                ".player-card",
                ".card",
                "[class*='card']",
                "[class*='player']",
                "tr",
                "td",
                ".dataTables_wrapper",
                ".table",
                "[id*='card']",
                "[id*='player']"
            ]
            
            for selector in selectors_to_try:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        print(f"Found {len(elements)} elements with selector: {selector}")
                        if len(elements) <= 5:  # Show details for small numbers
                            for i, elem in enumerate(elements):
                                try:
                                    text = elem.text.strip()
                                    if text:
                                        print(f"  Element {i+1}: {text[:100]}...")
                                except:
                                    pass
                except:
                    pass
                    
            # Try to find the actual data table
            try:
                table = self.driver.find_element(By.CSS_SELECTOR, "table")
                print(f"Found table with {len(table.find_elements(By.TAG_NAME, 'tr'))} rows")
                
                # Get first few rows
                rows = table.find_elements(By.TAG_NAME, "tr")[:5]
                for i, row in enumerate(rows):
                    cells = row.find_elements(By.TAG_NAME, "td")
                    if cells:
                        row_text = " | ".join([cell.text.strip() for cell in cells])
                        print(f"Row {i+1}: {row_text[:200]}...")
                        
            except:
                print("No table found")
                
        except Exception as e:
            print(f"Error debugging page: {e}")
            
    def debug_nationality_filter(self, nationality_value):
        """Debug nationality filtering"""
        print(f"\nDebugging nationality filter: {nationality_value}")
        
        try:
            # Find and select nationality
            nationality_dropdown = self.driver.find_element(By.NAME, "nationality")
            select = Select(nationality_dropdown)
            select.select_by_value(nationality_value)
            
            # Wait for results to load
            time.sleep(3)
            
            # Check what changed
            print("After filtering:")
            
            # Look for data table info
            try:
                info_elements = self.driver.find_elements(By.CSS_SELECTOR, ".dataTables_info, .pagination-info, [class*='info']")
                for elem in info_elements:
                    if elem.text.strip():
                        print(f"Info: {elem.text}")
            except:
                pass
                
            # Look for cards/rows
            try:
                table = self.driver.find_element(By.CSS_SELECTOR, "table")
                rows = table.find_elements(By.TAG_NAME, "tr")
                print(f"Table has {len(rows)} rows after filtering")
                
                # Show first few rows
                for i, row in enumerate(rows[:3]):
                    cells = row.find_elements(By.TAG_NAME, "td")
                    if cells:
                        row_text = " | ".join([cell.text.strip() for cell in cells])
                        print(f"Row {i+1}: {row_text[:200]}...")
                        
            except:
                print("No table found after filtering")
                
        except Exception as e:
            print(f"Error debugging nationality filter: {e}")
            
    def run_debug(self):
        """Run debugging session"""
        print("Starting NHL HUT Debug Session...")
        
        try:
            if not self.setup_driver():
                return
                
            # Debug page structure
            self.debug_page_structure()
            
            # Debug nationality filtering
            self.debug_nationality_filter("Finland")
            
        except Exception as e:
            print(f"Debug failed: {e}")
            
        finally:
            if self.driver:
                self.driver.quit()

if __name__ == "__main__":
    debugger = NHLHUTDebugger()
    debugger.run_debug()