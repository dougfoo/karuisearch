"""
Quick test for Tokyu Resort BrowserScraper - limited to first few properties
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from scrapers.tokyu_resort_browser_scraper import TokyuResortBrowserScraper
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_tokyu_resort_quick():
    """Quick test of Tokyu Resort scraper with limited results"""
    logger.info("Starting Tokyu Resort BrowserScraper quick test...")
    
    try:
        # Create scraper directly with debug config
        config = {
            'base_url': 'https://www.tokyu-resort.co.jp',
            'rate_limit': 0.1,  # Slower for testing
            'wait_timeout': 10,
            'page_load_timeout': 20,
            'headless': True
        }
        
        scraper = TokyuResortBrowserScraper(config)
        
        # Setup browser
        if not scraper.setup_browser():
            logger.error("Failed to setup browser")
            return []
        
        try:
            # Load just the first search URL
            search_url = "https://www.tokyu-resort.co.jp/search/result?HPSRC_AREA_ID[57]=1&SHUBETSU_ID[2]=1&area_top_flg=1&link_id=11villa"
            logger.info(f"Loading: {search_url}")
            
            scraper.driver.get(search_url)
            scraper.wait_for_search_results()
            
            # Extract first 3 properties only
            properties = scraper.extract_properties_from_search_page(search_url)
            
            logger.info(f"Found {len(properties)} properties")
            
            # Display first few results
            for i, prop in enumerate(properties[:5], 1):
                logger.info(f"Property {i}:")
                logger.info(f"  Title: {prop.title}")
                logger.info(f"  Price: {prop.price}")
                logger.info(f"  Location: {prop.location}")
                logger.info(f"  Type: {prop.property_type}")
                logger.info(f"  Source: {prop.source_url}")
                logger.info("")
                
        finally:
            scraper.close_browser()
            
        return properties
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
        return []

if __name__ == "__main__":
    test_tokyu_resort_quick()