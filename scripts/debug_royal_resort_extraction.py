#!/usr/bin/env python3
"""
Debug Royal Resort extraction process
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from scrapers.royal_resort_scraper import RoyalResortScraper

def debug_royal_resort_extraction():
    print('=== ROYAL RESORT EXTRACTION DEBUG ===')
    print('Testing just the property extraction step...')

    scraper = RoyalResortScraper({'headless': True})
    try:
        print('1. Setting up browser...')
        scraper.setup_browser()
        
        print('2. Navigating...')
        if scraper.navigate_to_page(scraper.karuizawa_url):
            print('3. Finding properties...')
            properties = scraper.find_property_listings_with_retry()
            print(f'   Found {len(properties)} property elements')
            
            if properties and len(properties) > 0:
                print('4. Testing extraction on first property...')
                test_element = properties[0]
                
                # Test the extraction method directly
                try:
                    result = scraper.extract_property_from_listing(test_element)
                    print(f'   Extraction result type: {type(result)}')
                    if result:
                        print(f'   Title: {getattr(result, "title", "NO TITLE")}')
                        print(f'   Price: {getattr(result, "price", "NO PRICE")}')
                        print(f'   Location: {getattr(result, "location", "NO LOCATION")}')
                        print(f'   Property Type: {getattr(result, "property_type", "NO TYPE")}')
                    else:
                        print('   Extraction returned None!')
                        
                    # Test validation
                    if result:
                        valid = scraper.validate_property_data(result)
                        print(f'   Validation result: {valid}')
                        
                except Exception as e:
                    print(f'   EXTRACTION ERROR: {e}')
                    import traceback
                    traceback.print_exc()
            else:
                print('   No property elements found for testing')
        else:
            print('   Navigation failed')
            
    except Exception as e:
        print(f'ERROR: {e}')
        import traceback
        traceback.print_exc()
    finally:
        try:
            scraper.close_browser()
            print('Browser closed')
        except:
            pass

if __name__ == "__main__":
    debug_royal_resort_extraction()