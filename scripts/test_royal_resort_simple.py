#!/usr/bin/env python3
"""
Simple test for Royal Resort fixes
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from scrapers.royal_resort_scraper import RoyalResortScraper

def test_royal_resort_fixes():
    print('Testing Royal Resort with Fix #1 improvements...')
    print('=' * 50)

    config = {
        'headless': True,
        'wait_timeout': 30,
        'page_load_timeout': 60
    }

    scraper = RoyalResortScraper(config)
    try:
        print('Setting up browser...')
        if scraper.setup_browser():
            print('[OK] Browser setup successful')
            
            print('Testing navigation with retry logic...')
            success = False
            for attempt in range(3):
                print(f'Navigation attempt {attempt + 1}...')
                if scraper.navigate_to_page(scraper.karuizawa_url):
                    print('[OK] Navigation successful!')
                    success = True
                    break
                else:
                    print('[FAIL] Navigation failed, retrying...')
                    
            if success:
                print('Looking for property elements...')
                properties = scraper.find_property_listings_with_retry()
                print(f'Found {len(properties)} property elements')
                
                if properties:
                    print('[SUCCESS] Royal Resort fixes working!')
                    print(f'Ready to extract up to {min(len(properties), 10)} properties')
                    return True
                else:
                    print('[FAIL] No property elements found')
                    return False
            else:
                print('[FAIL] Navigation completely failed')
                return False
                
        else:
            print('[FAIL] Browser setup failed')
            return False
            
    except Exception as e:
        print(f'[ERROR] {e}')
        return False
    finally:
        try:
            scraper.close_browser()
            print('Browser closed')
        except:
            pass

if __name__ == "__main__":
    success = test_royal_resort_fixes()
    if success:
        print('\n[SUCCESS] Royal Resort fixes are working!')
    else:
        print('\n[WARNING] Royal Resort still needs more work')