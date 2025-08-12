#!/usr/bin/env python3
"""
Quick test for Resort Home scraper
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from scrapers.resort_home_scraper import ResortHomeScraper
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_resort_home():
    """Test Resort Home scraper"""
    logger.info("Testing Resort Home scraper...")
    
    try:
        scraper = ResortHomeScraper()
        properties = scraper.scrape_listings()
        
        logger.info(f"Found {len(properties)} properties")
        
        for i, prop in enumerate(properties[:3], 1):
            logger.info(f"Property {i}:")
            logger.info(f"  Title: {prop.title}")
            logger.info(f"  Price: {prop.price}")
            logger.info(f"  Location: {prop.location}")
            logger.info(f"  Type: {prop.property_type}")
            logger.info(f"  Source: {prop.source_url}")
            logger.info("")
            
        return properties
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
        return []

if __name__ == "__main__":
    test_resort_home()