"""
Test script for Seibu Real Estate scraper
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from scrapers.scraper_factory import ScraperFactory
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_seibu_real_estate_scraper():
    """Test the Seibu Real Estate scraper"""
    logger.info("Starting Seibu Real Estate scraper test...")
    
    try:
        # Create scraper factory
        factory = ScraperFactory()
        
        # Test Seibu Real Estate scraper specifically
        logger.info("Testing Seibu Real Estate scraper...")
        properties = factory.scrape_single_site('seibu_real_estate')
        
        logger.info(f"[SUCCESS] Seibu Real Estate: Found {len(properties)} properties")
        
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
            if prop.building_age:
                logger.info(f"  Age: {prop.building_age}")
            logger.info("")
        
        # Get scraping stats
        stats = factory.get_scraping_stats()
        if 'seibu_real_estate' in stats:
            stat = stats['seibu_real_estate']
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
    test_seibu_real_estate_scraper()