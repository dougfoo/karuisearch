#!/usr/bin/env python3
"""
Quick scrape with limited Royal Resort processing for faster results
"""

import sys
import os
import json
from datetime import datetime
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from scrapers.scraper_factory import ScraperFactory

def run_quick_scrape():
    """Run scraping with Royal Resort limited to 3 properties for speed"""
    print("🚀 Quick Scrape - Limited Royal Resort Processing")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    factory = ScraperFactory()
    all_properties = []
    
    # Scrape Mitsui (works fast)
    print("\n=== MITSUI ===")
    mitsui_properties = factory.scrape_site('mitsui')
    print(f"Mitsui: {len(mitsui_properties)} properties")
    all_properties.extend(mitsui_properties)
    
    # Quick Besso Navi test
    print("\n=== BESSO NAVI ===")
    besso_properties = factory.scrape_site('besso_navi')
    print(f"Besso Navi: {len(besso_properties)} properties")
    all_properties.extend(besso_properties)
    
    # Royal Resort with custom limit
    print("\n=== ROYAL RESORT (LIMITED) ===")
    royal_scraper = factory.create_scraper('royal_resort')
    
    # Patch the scraper to limit processing
    original_scrape = royal_scraper.scrape_listings
    
    def limited_royal_scrape():
        """Limited version that processes only 3 properties"""
        print("Starting LIMITED Royal Resort scraping")
        
        if not royal_scraper.setup_browser():
            print("Failed to setup browser")
            return []
        
        if not royal_scraper.navigate_to_page(royal_scraper.karuizawa_url):
            print("Failed to navigate")
            royal_scraper.close_browser()
            return []
        
        # Find properties but limit to 3
        properties = royal_scraper.find_property_listings()
        print(f"Found {len(properties)} total properties, processing first 3...")
        
        extracted = []
        for i, prop_element in enumerate(properties[:3], 1):
            print(f"Processing property {i}/3")
            try:
                prop_data = royal_scraper.extract_property_from_listing(prop_element)
                if prop_data and royal_scraper.validate_property_data(prop_data):
                    extracted.append(prop_data)
                    print(f"  ✓ Extracted: {prop_data.title[:50]}...")
                royal_scraper.simulate_human_delay(1.0, 2.0)
            except Exception as e:
                print(f"  ✗ Error: {e}")
                continue
        
        royal_scraper.close_browser()
        return extracted
    
    # Apply patch
    royal_scraper.scrape_listings = limited_royal_scrape
    royal_properties = royal_scraper.scrape_listings()
    print(f"Royal Resort: {len(royal_properties)} properties (limited)")
    all_properties.extend(royal_properties)
    
    # Summary
    print(f"\n=== SUMMARY ===")
    print(f"Total Properties: {len(all_properties)}")
    
    for prop in all_properties:
        print(f"  • {prop.title[:60]}...")
        print(f"    Price: {prop.price}, Images: {len(prop.image_urls)}")
    
    # Save to file
    output_file = "quick_scrape_results.json"
    results = []
    for prop in all_properties:
        results.append({
            "title": prop.title,
            "price": prop.price,
            "location": prop.location,
            "images": len(prop.image_urls),
            "source_url": prop.source_url
        })
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Results saved to: {output_file}")
    return len(all_properties)

if __name__ == "__main__":
    try:
        count = run_quick_scrape()
        print(f"\n✅ SUCCESS: {count} properties extracted!")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()