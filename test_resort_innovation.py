"""
Test script for Resort Innovation scraper
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from scrapers.scraper_factory import ScraperFactory
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_resort_innovation_scraper():
    """Test the Resort Innovation scraper"""
    logger.info("Starting Resort Innovation scraper test...")
    
    try:
        # Create scraper factory
        factory = ScraperFactory()
        
        # Test Resort Innovation scraper specifically
        logger.info("Testing Resort Innovation scraper...")
        properties = factory.scrape_single_site('resort_innovation')
        
        logger.info(f"[SUCCESS] Resort Innovation: Found {len(properties)} properties")
        
        # Display results
        for i, prop in enumerate(properties, 1):
            logger.info(f"Property {i}:")
            logger.info(f"  Title: {prop.title}")
            logger.info(f"  Price: {prop.price}")
            logger.info(f"  Location: {prop.location}")
            logger.info(f"  Type: {prop.property_type}")
            logger.info(f"  Source: {prop.source_url}")
            logger.info(f"  Images: {len(prop.image_urls)} images")
            logger.info("")
        
        # Get scraping stats
        stats = factory.get_scraping_stats()
        if 'resort_innovation' in stats:
            stat = stats['resort_innovation']
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
    test_resort_innovation_scraper()