#!/usr/bin/env python3
"""
Test SUUMO scraper implementation
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from scrapers.suumo_scraper import SUUMOScraper
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_suumo():
    """Test SUUMO scraper"""
    logger.info("Testing SUUMO scraper...")
    
    try:
        # Create scraper with limited processing for testing
        config = {
            'base_url': 'https://suumo.jp',
            'headless': True,
            'wait_timeout': 20,
            'page_load_timeout': 40
        }
        
        scraper = SUUMOScraper(config)
        
        # Run scraping (limited processing for testing)
        properties = scraper.scrape_listings()
        
        logger.info(f"SUUMO extraction results: {len(properties)} properties")
        
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
            logger.info("✅ SUCCESS: SUUMO extraction working!")
        else:
            logger.warning("⚠️ No properties extracted - may need further refinement")
            
        return properties
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return []

if __name__ == "__main__":
    test_suumo()