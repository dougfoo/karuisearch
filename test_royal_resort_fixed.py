#!/usr/bin/env python3
"""
Test the fixed Royal Resort scraper
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from scrapers.royal_resort_scraper import RoyalResortScraper
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_royal_resort_fixed():
    """Test Royal Resort with stale element fixes"""
    logger.info("Testing fixed Royal Resort scraper...")
    
    try:
        # Create scraper with limited processing for testing
        config = {
            'base_url': 'https://www.royal-resort.co.jp',
            'headless': True,
            'wait_timeout': 15,
            'page_load_timeout': 30
        }
        
        scraper = RoyalResortScraper(config)
        
        # Run scraping (limited to 3 properties for testing)
        properties = scraper.scrape_listings()
        
        logger.info(f"Royal Resort extraction results: {len(properties)} properties")
        
        # Display results
        for i, prop in enumerate(properties, 1):
            logger.info(f"Property {i}:")
            logger.info(f"  Title: {prop.title}")
            logger.info(f"  Price: {prop.price}")
            logger.info(f"  Location: {prop.location}")
            logger.info(f"  Type: {prop.property_type}")
            logger.info(f"  Source: {prop.source_url}")
            logger.info("")
            
        if len(properties) > 0:
            logger.info("✅ SUCCESS: Royal Resort extraction working!")
        else:
            logger.warning("⚠️ No properties extracted - may need further fixes")
            
        return properties
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return []

if __name__ == "__main__":
    test_royal_resort_fixed()