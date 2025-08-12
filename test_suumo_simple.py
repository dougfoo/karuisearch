#!/usr/bin/env python3
"""
Test simplified SUUMO scraper
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from scrapers.suumo_simple import SUUMOSimpleScraper
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_suumo_simple():
    """Test simplified SUUMO scraper"""
    logger.info("Testing simplified SUUMO scraper...")
    
    try:
        config = {
            'headless': True,
            'wait_timeout': 15,
            'page_load_timeout': 30
        }
        
        scraper = SUUMOSimpleScraper(config)
        properties = scraper.scrape_listings()
        
        logger.info(f"SUUMO simple extraction results: {len(properties)} properties")
        
        for i, prop in enumerate(properties, 1):
            logger.info(f"Property {i}:")
            logger.info(f"  Title: {prop.title}")
            logger.info(f"  Price: {prop.price}")
            logger.info(f"  Location: {prop.location}")
            logger.info(f"  Type: {prop.property_type}")
            logger.info(f"  Source: {prop.source_url}")
            logger.info("")
            
        if len(properties) > 0:
            logger.info("✅ SUCCESS: SUUMO simple scraper working!")
        else:
            logger.warning("⚠️ No properties found")
            
        return properties
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return []

if __name__ == "__main__":
    test_suumo_simple()