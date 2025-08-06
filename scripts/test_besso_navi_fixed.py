#!/usr/bin/env python3
"""
Test the fixed Besso Navi scraper
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from scrapers.besso_navi_fixed_scraper import BessoNaviFixedScraper

def test_fixed_scraper():
    """Test the fixed Besso Navi scraper"""
    print("=== TESTING FIXED BESSO NAVI SCRAPER ===")
    
    try:
        # Create scraper instance
        scraper = BessoNaviFixedScraper()
        
        # Run scraping
        properties = scraper.scrape_listings()
        
        print(f"\nResults: {len(properties)} properties found")
        
        if properties:
            print("\nProperty Details:")
            for i, prop in enumerate(properties, 1):
                print(f"\n{i}. {prop.title}")
                print(f"   Price: {prop.price}")
                print(f"   Location: {prop.location}")
                print(f"   Type: {prop.property_type}")
                print(f"   Images: {len(prop.image_urls)}")
                print(f"   URL: {prop.source_url}")
                
                if prop.image_urls:
                    print(f"   First image: {prop.image_urls[0]}")
        
        return len(properties)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 0

if __name__ == "__main__":
    count = test_fixed_scraper()
    
    print(f"\n=== SUMMARY ===")
    print(f"Properties found: {count}")
    
    if count >= 4:
        print("SUCCESS: Found expected villa results!")
    elif count > 0:
        print(f"PARTIAL: Found {count} properties (expected ~4 villas)")
    else:
        print("FAILED: No properties found - needs investigation")