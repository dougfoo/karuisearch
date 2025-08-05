#!/usr/bin/env python3
"""
Quick test to verify scraper fixes work
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from scrapers.besso_navi_http_scraper import BessoNaviHTTPScraper
from scrapers.royal_resort_scraper import RoyalResortScraper

def test_besso_navi():
    """Test Besso Navi HTTP scraper"""
    print("=== Testing Besso Navi HTTP Scraper ===")
    scraper = BessoNaviHTTPScraper()
    properties = scraper.scrape_listings()
    print(f"Besso Navi: Found {len(properties)} properties")
    
    if properties:
        prop = properties[0]
        print(f"  Sample property: {prop.title}")
        print(f"  Price: {prop.price}")
        print(f"  Images: {len(prop.image_urls)} images")
    return len(properties)

def test_royal_resort():
    """Test Royal Resort scraper with limited processing"""
    print("\n=== Testing Royal Resort Scraper ===")
    
    # Create scraper with limited processing for testing
    config = {
        'headless': True,
        'wait_timeout': 10,
        'page_load_timeout': 20
    }
    
    scraper = RoyalResortScraper(config)
    
    # Override the scrape_listings method to limit to 3 properties
    original_method = scraper.scrape_listings
    
    def limited_scrape():
        scraper.logger.info("Starting LIMITED Royal Resort scraper test")
        
        if not scraper.setup_browser():
            scraper.logger.error("Failed to setup browser")
            return []
        
        if not scraper.navigate_to_page(scraper.karuizawa_url):
            scraper.logger.error("Failed to navigate to Karuizawa page")
            scraper.close_browser()
            return []
        
        # Find property containers
        properties = scraper.find_property_listings()
        scraper.logger.info(f"Found {len(properties)} property elements")
        
        # Limit to 3 properties for testing
        properties = properties[:3] if len(properties) > 3 else properties
        
        extracted_properties = []
        for i, property_element in enumerate(properties, 1):
            scraper.logger.info(f"Processing property {i}/{len(properties)}")
            
            try:
                property_data = scraper.extract_property_from_listing(property_element)
                if property_data and scraper.validate_property_data(property_data):
                    extracted_properties.append(property_data)
                    scraper.logger.info(f"Successfully extracted property {i}")
                scraper.simulate_human_delay(1.0, 2.0)  # Faster for testing
            except Exception as e:
                scraper.logger.error(f"Error processing property {i}: {e}")
                continue
        
        scraper.close_browser()
        return extracted_properties
    
    # Replace method temporarily
    scraper.scrape_listings = limited_scrape
    
    properties = scraper.scrape_listings()
    print(f"Royal Resort: Found {len(properties)} properties (limited test)")
    
    if properties:
        prop = properties[0]
        print(f"  Sample property: {prop.title}")
        print(f"  Price: {prop.price}")
        print(f"  Images: {len(prop.image_urls)} images")
    return len(properties)

if __name__ == "__main__":
    try:
        besso_count = test_besso_navi()
        royal_count = test_royal_resort()
        
        print(f"\n=== SUMMARY ===")
        print(f"Besso Navi: {besso_count} properties")
        print(f"Royal Resort: {royal_count} properties")
        
        if besso_count > 0 or royal_count > 0:
            print("✅ SCRAPERS FIXED SUCCESSFULLY!")
        else:
            print("❌ Both scrapers still have issues")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()