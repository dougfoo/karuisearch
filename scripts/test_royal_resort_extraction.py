#!/usr/bin/env python3
"""
Royal Resort extraction test with extended timeout
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from scrapers.royal_resort_scraper import RoyalResortScraper

def test_royal_resort_extraction():
    print('ROYAL RESORT EXTRACTION TEST')
    print('=' * 50)
    print('Testing Royal Resort with extended timeout...')
    print()

    config = {
        'headless': True,
        'wait_timeout': 30,
        'page_load_timeout': 60
    }

    try:
        scraper = RoyalResortScraper(config)
        print('Starting Royal Resort property extraction...')
        
        # Run the full scraper
        properties = scraper.scrape_listings()
        
        print(f'\nEXTRACTION COMPLETE!')
        print(f'Total properties extracted: {len(properties)}')
        print()
        
        if properties:
            print('SUCCESS: Royal Resort properties extracted!')
            print('Sample extracted properties:')
            print('-' * 40)
            
            for i, prop in enumerate(properties[:5], 1):
                print(f'\nProperty {i}:')
                print(f'  Title: {prop.title}')
                print(f'  Price: {prop.price}')
                print(f'  Location: {prop.location}')
                print(f'  Type: {prop.property_type}')
                print(f'  Source: {prop.source_url}')
                print(f'  Valid: {hasattr(prop, "price") and bool(prop.price)}')
                
            print(f'\n[RESULT] Successfully extracted {len(properties)} Royal Resort properties!')
            return properties
            
        else:
            print('NO PROPERTIES EXTRACTED - Investigation needed')
            return []
            
    except Exception as e:
        print(f'ERROR: {e}')
        import traceback
        traceback.print_exc()
        return []

if __name__ == "__main__":
    properties = test_royal_resort_extraction()
    
    if properties:
        print(f'\n*** FINAL RESULT: {len(properties)} Royal Resort properties extracted successfully! ***')
    else:
        print('\n*** FINAL RESULT: Royal Resort extraction failed ***')