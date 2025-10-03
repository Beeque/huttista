#!/usr/bin/env python3
"""
Explore cards.php page structure to understand how to scrape it
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def explore_cards_page():
    """Explore the cards.php page structure"""
    print("🔍 Exploring cards.php page structure...")
    
    # Setup Chrome WebDriver
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        wait = WebDriverWait(driver, 10)
        
        # Navigate to cards page
        print("🌐 Loading cards.php...")
        driver.get("https://nhlhutbuilder.com/cards.php")
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        time.sleep(3)
        
        print("✅ Page loaded successfully")
        
        # Look for sort options
        print("\n🔍 Looking for sort options...")
        try:
            # Try different selectors for sort dropdown
            sort_selectors = [
                "select[name='sort']",
                "select[id='sort']",
                ".sort-select",
                "[name*='sort']",
                "select"
            ]
            
            for selector in sort_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        print(f"✅ Found {len(elements)} elements with selector: {selector}")
                        for i, elem in enumerate(elements):
                            print(f"   Element {i+1}: {elem.tag_name} - {elem.get_attribute('name')} - {elem.get_attribute('id')}")
                            
                            # Try to get options
                            if elem.tag_name == 'select':
                                select = Select(elem)
                                options = select.options
                                print(f"   Options ({len(options)}):")
                                for opt in options[:10]:  # First 10 options
                                    print(f"     - {opt.text} (value: {opt.get_attribute('value')})")
                                if len(options) > 10:
                                    print(f"     ... and {len(options) - 10} more")
                    else:
                        print(f"❌ No elements found with selector: {selector}")
                except Exception as e:
                    print(f"❌ Error with selector {selector}: {e}")
        except Exception as e:
            print(f"❌ Error looking for sort options: {e}")
        
        # Look for card elements
        print("\n🔍 Looking for card elements...")
        card_selectors = [
            ".card",
            ".player-card",
            ".card-item",
            "[class*='card']",
            "a[href*='player-stats.php']",
            "a[href*='goalie-stats.php']",
            ".player-link"
        ]
        
        for selector in card_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    print(f"✅ Found {len(elements)} elements with selector: {selector}")
                    
                    # Show first few examples
                    for i, elem in enumerate(elements[:3]):
                        print(f"   Element {i+1}:")
                        print(f"     Tag: {elem.tag_name}")
                        print(f"     Class: {elem.get_attribute('class')}")
                        print(f"     Href: {elem.get_attribute('href')}")
                        print(f"     Text: {elem.text[:100]}...")
                else:
                    print(f"❌ No elements found with selector: {selector}")
            except Exception as e:
                print(f"❌ Error with selector {selector}: {e}")
        
        # Look for pagination
        print("\n🔍 Looking for pagination...")
        pagination_selectors = [
            ".pagination",
            ".page-nav",
            "[class*='page']",
            "a[href*='page=']",
            ".next",
            ".prev"
        ]
        
        for selector in pagination_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    print(f"✅ Found {len(elements)} elements with selector: {selector}")
                    for i, elem in enumerate(elements[:5]):
                        print(f"   Element {i+1}: {elem.text} - {elem.get_attribute('href')}")
                else:
                    print(f"❌ No elements found with selector: {selector}")
            except Exception as e:
                print(f"❌ Error with selector {selector}: {e}")
        
        # Get page source for manual inspection
        print("\n📄 Saving page source for manual inspection...")
        with open("/workspace/cards_page_source.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print("✅ Page source saved to cards_page_source.html")
        
        # Cleanup
        driver.quit()
        print("\n✅ Exploration complete!")
        
    except Exception as e:
        print(f"❌ Error during exploration: {e}")

if __name__ == "__main__":
    explore_cards_page()