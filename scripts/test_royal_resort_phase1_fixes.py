#!/usr/bin/env python3
"""
Test Royal Resort with Phase 1 crash fixes
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from scrapers.royal_resort_scraper import RoyalResortScraper

def test_phase1_fixes():
    print('=== ROYAL RESORT PHASE 1 FIXES TEST ===')
    print('Testing browser stability and crash recovery...')
    print()

    # Use optimized config for stability
    config = {
        'headless': True,
        'wait_timeout': 30,
        'page_load_timeout': 60
    }

    scraper = RoyalResortScraper(config)
    try:
        print('1. Testing browser setup with stability improvements...')
        if scraper.setup_browser():
            print('[OK] Browser setup successful with new stability flags')
            
            print('2. Testing navigation...')
            if scraper.navigate_to_page(scraper.karuizawa_url):
                print('[OK] Navigation successful')
                
                print('3. Testing property finding...')
                properties = scraper.find_property_listings_with_retry()
                print(f'[OK] Found {len(properties)} property elements')
                
                if properties:
                    print('4. Testing extraction with crash recovery (first 3 properties)...')
                    extracted_count = 0
                    
                    for i, prop_element in enumerate(properties[:3], 1):
                        print(f'   Testing property {i}/3...')
                        
                        try:
                            # Test the new crash-recovery extraction
                            result = scraper.safe_execute_with_recovery(
                                scraper.extract_property_from_listing, 
                                prop_element,
                                max_retries=1
                            )
                            
                            if result:
                                print(f'   [SUCCESS] Property {i} extracted!')
                                print(f'      Title: {result.title[:50]}...' if result.title else '      Title: No title')
                                print(f'      Price: {result.price}' if result.price else '      Price: No price')
                                extracted_count += 1
                            else:
                                print(f'   [WARNING] Property {i} extraction returned None')
                                
                        except Exception as e:
                            print(f'   [ERROR] Property {i} extraction failed: {e}')
                    
                    print(f'\\n5. EXTRACTION SUMMARY:')
                    print(f'   Properties found: {len(properties)}')
                    print(f'   Properties extracted: {extracted_count}/3')
                    print(f'   Success rate: {(extracted_count/3)*100:.1f}%')
                    
                    if extracted_count > 0:
                        print('\\n[SUCCESS] Phase 1 fixes are working!')
                        print('Royal Resort properties can now be extracted without crashes!')
                        return True
                    else:
                        print('\\n[FAILED] No properties extracted - needs more investigation')
                        return False
                        
                else:
                    print('[FAILED] No properties found')
                    return False
            else:
                print('[FAILED] Navigation failed')
                return False
        else:
            print('[FAILED] Browser setup failed')
            return False
            
    except Exception as e:
        print(f'[ERROR] Test failed: {e}')
        import traceback
        traceback.print_exc()
        return False
    finally:
        try:
            scraper.close_browser()
            print('\\nBrowser closed successfully')
        except:
            pass

if __name__ == "__main__":
    success = test_phase1_fixes()
    
    if success:
        print('\\n*** PHASE 1 FIXES WORKING - Ready for full scraper test! ***')
    else:
        print('\\n*** PHASE 1 FIXES NEED MORE WORK ***')