"""
Very simple test for Tokyu Resort site accessibility
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from scrapers.tokyu_resort_browser_scraper import TokyuResortBrowserScraper
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_tokyu_simple():
    """Simple connectivity test"""
    logger.info("Testing Tokyu Resort site connectivity...")
    
    try:
        config = {
            'base_url': 'https://www.tokyu-resort.co.jp',
            'wait_timeout': 5,
            'page_load_timeout': 10,
            'headless': True
        }
        
        scraper = TokyuResortBrowserScraper(config)
        
        if not scraper.setup_browser():
            logger.error("Failed to setup browser")
            return False
        
        try:
            # Test homepage first
            logger.info("Testing homepage...")
            scraper.driver.get("https://www.tokyu-resort.co.jp/")
            logger.info("Homepage loaded successfully")
            
            # Check page title
            title = scraper.driver.title
            logger.info(f"Page title: {title}")
            
            # Check page source length
            source_length = len(scraper.driver.page_source)
            logger.info(f"Page source length: {source_length}")
            
            if source_length > 1000:
                logger.info("Site is accessible")
                return True
            else:
                logger.error("Site returned minimal content")
                return False
                
        finally:
            scraper.close_browser()
            
    except Exception as e:
        logger.error(f"Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_tokyu_simple()
    print(f"Test result: {'SUCCESS' if success else 'FAILED'}")