"""
Test script for Tokyu Resort scraper
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from scrapers.scraper_factory import ScraperFactory
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_tokyu_resort_scraper():
    """Test the Tokyu Resort scraper"""
    logger.info("Starting Tokyu Resort scraper test...")
    
    try:
        # Create scraper factory
        factory = ScraperFactory()
        
        # Test Tokyu Resort scraper specifically
        logger.info("Testing Tokyu Resort scraper...")
        properties = factory.scrape_single_site('tokyu_resort')
        
        logger.info(f"[SUCCESS] Tokyu Resort: Found {len(properties)} properties")
        
        # Display results
        for i, prop in enumerate(properties, 1):
            logger.info(f"Property {i}:")
            logger.info(f"  Title: {prop.title}")
            logger.info(f"  Price: {prop.price}")
            logger.info(f"  Location: {prop.location}")
            logger.info(f"  Type: {prop.property_type}")
            logger.info(f"  Source: {prop.source_url}")
            logger.info(f"  Images: {len(prop.image_urls)} images")
            if prop.rooms:
                logger.info(f"  Rooms: {prop.rooms}")
            if prop.size_info:
                logger.info(f"  Size: {prop.size_info}")
            logger.info("")
        
        # Get scraping stats
        stats = factory.get_scraping_stats()
        if 'tokyu_resort' in stats:
            stat = stats['tokyu_resort']
            logger.info(f"Scraping Stats:")
            logger.info(f"  Duration: {stat['scrape_duration']:.1f}s")
            logger.info(f"  Success: {stat['success']}")
            logger.info(f"  Properties: {stat['properties_found']}")
        
        return properties
        
    except Exception as e:
        logger.error(f"[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        return []

if __name__ == "__main__":
    test_tokyu_resort_scraper()