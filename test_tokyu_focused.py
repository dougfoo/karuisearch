"""
Focused test for Tokyu Resort search results extraction
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from scrapers.tokyu_resort_browser_scraper import TokyuResortBrowserScraper
import logging
import time
from selenium.webdriver.common.by import By

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_tokyu_focused():
    """Focused test with limited extraction"""
    logger.info("Testing Tokyu Resort search results...")
    
    try:
        config = {
            'base_url': 'https://www.tokyu-resort.co.jp',
            'wait_timeout': 8,
            'page_load_timeout': 12,
            'headless': True
        }
        
        scraper = TokyuResortBrowserScraper(config)
        
        if not scraper.setup_browser():
            logger.error("Failed to setup browser")
            return []
        
        try:
            # Load search page
            search_url = "https://www.tokyu-resort.co.jp/search/result?HPSRC_AREA_ID[57]=1&SHUBETSU_ID[2]=1&area_top_flg=1&link_id=11villa"
            logger.info(f"Loading search: {search_url}")
            
            scraper.driver.get(search_url)
            logger.info("Search page loaded")
            
            # Wait a bit for content to render
            time.sleep(3)
            
            # Quick check for page content
            source_length = len(scraper.driver.page_source)
            logger.info(f"Page content length: {source_length}")
            
            # Look for property links quickly
            try:
                property_links = scraper.driver.find_elements(By.CSS_SELECTOR, "a[href*='/karuizawa/detail/']")
                logger.info(f"Found {len(property_links)} property detail links")
                
                if property_links:
                    # Show first few links
                    for i, link in enumerate(property_links[:3]):
                        href = link.get_attribute('href')
                        text = link.text.strip()
                        logger.info(f"Link {i+1}: {href} - {text[:50]}...")
                    
                    logger.info("SUCCESS: Found property links on search page")
                    return True
                else:
                    logger.warning("No property links found")
                    
                    # Debug: check for any links
                    all_links = scraper.driver.find_elements(By.TAG_NAME, "a")
                    logger.info(f"Total links on page: {len(all_links)}")
                    
                    # Check for price text
                    page_text = scraper.driver.page_source
                    if '万円' in page_text:
                        logger.info("Found price text in page - content is loaded")
                        
                        # Try to find elements containing price
                        script = """
                        return Array.from(document.querySelectorAll('*')).filter(function(el) {
                            return el.textContent.includes('万円') && el.children.length < 5;
                        }).slice(0, 3);
                        """
                        price_elements = scraper.driver.execute_script(script)
                        logger.info(f"Found {len(price_elements)} elements with price text")
                        
                        for i, elem in enumerate(price_elements):
                            text = elem.text.strip()
                            logger.info(f"Price element {i+1}: {text[:100]}...")
                    else:
                        logger.warning("No price text found - page might not be fully loaded")
                    
                    return False
                    
            except Exception as e:
                logger.error(f"Error finding property links: {e}")
                return False
                
        finally:
            scraper.close_browser()
            
    except Exception as e:
        logger.error(f"Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_tokyu_focused()
    print(f"Test result: {'SUCCESS' if success else 'FAILED'}")