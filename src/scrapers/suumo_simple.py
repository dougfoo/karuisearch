"""
SUUMO simplified scraper for Karuizawa properties
Based on actual site structure analysis
"""
import time
import re
from typing import List, Optional
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import logging

from .browser_scraper import BrowserScraper
from .base_scraper import PropertyData

logger = logging.getLogger(__name__)

class SUUMOSimpleScraper(BrowserScraper):
    """Simplified SUUMO scraper based on actual site structure"""
    
    def __init__(self, config: dict = None):
        default_config = {
            'base_url': 'https://suumo.jp',
            'headless': True,
            'wait_timeout': 20,
            'page_load_timeout': 40
        }
        
        if config:
            default_config.update(config)
            
        super().__init__(default_config)
        
    def scrape_listings(self) -> List[PropertyData]:
        """Main scraping method"""
        logger.info("Starting SUUMO simple property scraping")
        
        if not self.setup_browser():
            logger.error("Failed to setup browser")
            return []
        
        try:
            # Navigate to vacation home section
            vacation_url = 'https://suumo.jp/edit/kr/nj_ijyuubessou/'
            if not self.navigate_to_page(vacation_url):
                return []
            
            self.simulate_human_delay(3.0, 5.0)
            
            # Get all select elements (we know there are exactly 2)
            select_elements = self.driver.find_elements(By.TAG_NAME, 'select')
            
            if len(select_elements) < 2:
                logger.error("Expected 2 select elements, but found {len(select_elements)}")
                return []
            
            property_type_select = Select(select_elements[0])  # First select: property types
            prefecture_select = Select(select_elements[1])     # Second select: prefectures
            
            # Select property type: 中古一戸建て (Used House) - most common for vacation homes
            try:
                property_type_select.select_by_visible_text('中古一戸建て')
                logger.info("Selected property type: 中古一戸建て")
                self.simulate_human_delay(1.0, 2.0)
            except Exception as e:
                logger.error(f"Could not select property type: {e}")
                return []
            
            # Select Nagano prefecture
            try:
                # Try to find Nagano in the options
                nagano_selected = False
                for option in prefecture_select.options:
                    if '長野' in option.text:
                        prefecture_select.select_by_visible_text(option.text)
                        logger.info(f"Selected prefecture: {option.text}")
                        nagano_selected = True
                        break
                
                if not nagano_selected:
                    logger.error("Could not find Nagano prefecture in options")
                    return []
                    
                self.simulate_human_delay(1.0, 2.0)
                
            except Exception as e:
                logger.error(f"Could not select Nagano prefecture: {e}")
                return []
            
            # Look for and click search button/link
            search_executed = self.execute_search()
            if not search_executed:
                logger.error("Could not execute search")
                return []
                
            # Wait for results to load
            self.simulate_human_delay(5.0, 8.0)
            
            # Extract properties from results page
            properties = self.extract_properties_from_results()
            
            # Filter for Karuizawa-specific properties
            karuizawa_properties = []
            for prop in properties:
                if self.is_karuizawa_property(prop):
                    karuizawa_properties.append(prop)
            
            logger.info(f"SUUMO: Found {len(karuizawa_properties)} Karuizawa properties")
            return karuizawa_properties
            
        except Exception as e:
            logger.error(f"Error in SUUMO scraping: {e}")
            return []
        finally:
            self.close_browser()
    
    def execute_search(self) -> bool:
        """Find and click the search button"""
        # Look for various search button patterns
        search_selectors = [
            "a:contains('検索')",           # Link containing "検索"
            ".search-btn",
            ".btn-search",
            "[href*='search']",
            "input[value*='検索']",
            "button:contains('検索')"
        ]
        
        # Try XPath approach for Japanese text
        try:
            search_link = self.wait_for_element(By.XPATH, "//a[contains(text(), '検索')]", timeout=10)
            if search_link:
                search_link.click()
                logger.info("Clicked search link via XPath")
                return True
        except:
            pass
            
        # Try other methods
        for selector in search_selectors:
            try:
                if selector.startswith("a:contains") or selector.startswith("button:contains"):
                    # Use XPath for text-based selectors
                    text = selector.split("'")[1]
                    xpath = f"//a[contains(text(), '{text}')] | //button[contains(text(), '{text}')]"
                    element = self.wait_for_element(By.XPATH, xpath, timeout=5)
                else:
                    element = self.wait_for_element(By.CSS_SELECTOR, selector, timeout=5)
                    
                if element and element.is_enabled():
                    element.click()
                    logger.info(f"Clicked search element: {selector}")
                    return True
                    
            except Exception as e:
                logger.debug(f"Failed to click search with {selector}: {e}")
                continue
        
        # Last resort: find any clickable element with '検索' text
        try:
            all_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), '検索') and (@href or @onclick or name()='button' or name()='input')]")
            for element in all_elements:
                if element.is_displayed() and element.is_enabled():
                    element.click()
                    logger.info("Clicked search element (last resort)")
                    return True
        except:
            pass
            
        logger.warning("Could not find search button/link")
        return False
    
    def extract_properties_from_results(self) -> List[PropertyData]:
        """Extract properties from search results page"""
        properties = []
        
        try:
            # Check if we're on a results page
            if '検索結果' not in self.driver.page_source and 'search' not in self.driver.current_url.lower():
                logger.warning("May not be on search results page")
            
            # Look for property listings with SUUMO-specific patterns
            listing_selectors = [
                '.cassetteitem',           # Common SUUMO class
                '.property-unit',
                '.bukken-cassette',
                '.listing-item',
                '[class*="cassette"]',
                '[class*="property"]',
                '[class*="bukken"]'
            ]
            
            property_elements = []
            for selector in listing_selectors:
                elements = self.wait_for_elements(By.CSS_SELECTOR, selector, timeout=10)
                if elements:
                    logger.info(f"Found {len(elements)} property elements with: {selector}")
                    property_elements = elements
                    break
            
            # If no specific containers, look for links with property-like URLs
            if not property_elements:
                property_links = self.driver.find_elements(By.XPATH, "//a[contains(@href, 'bukken') or contains(@href, 'detail')]")
                if property_links:
                    logger.info(f"Found {len(property_links)} property links as fallback")
                    # Get parent containers
                    for link in property_links[:15]:  # Limit processing
                        parent = link.find_element(By.XPATH, "./ancestor::div[contains(@class, 'item') or contains(@class, 'unit') or contains(@class, 'cassette')][1]")
                        if parent and parent not in property_elements:
                            property_elements.append(parent)
            
            # Extract data from elements
            for i, element in enumerate(property_elements[:10], 1):  # Limit to 10
                try:
                    property_data = self.extract_property_from_element(element)
                    if property_data:
                        properties.append(property_data)
                        logger.debug(f"Extracted SUUMO property {i}: {property_data.title}")
                        
                except Exception as e:
                    logger.debug(f"Error extracting property {i}: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"Error extracting properties from results: {e}")
        
        return properties
    
    def extract_property_from_element(self, element) -> Optional[PropertyData]:
        """Extract property data from element"""
        try:
            property_data = PropertyData()
            
            # Get text content
            element_text = element.get_attribute('textContent') or ""
            
            # Extract title - look for property names or addresses
            title_lines = [line.strip() for line in element_text.split('\n') if line.strip()]
            for line in title_lines[:5]:
                if (len(line) > 8 and len(line) < 100 and 
                    not any(skip in line for skip in ['万円', '¥', '築年', '駅', 'DK', '㎡'])):
                    property_data.title = line
                    break
            
            if not property_data.title:
                property_data.title = "SUUMO Karuizawa Property"
            
            # Extract price
            price_patterns = [
                r'([0-9,]+)億([0-9,]+)万円',
                r'([0-9,]+)億円', 
                r'([0-9,]+)万円',
                r'¥([0-9,]+)',
                r'([0-9,]+)円'
            ]
            
            for pattern in price_patterns:
                price_match = re.search(pattern, element_text)
                if price_match:
                    property_data.price = price_match.group(0)
                    break
                    
            if not property_data.price:
                property_data.price = "お問い合わせください"
            
            # Extract location
            if '軽井沢' in element_text:
                for line in element_text.split('\n'):
                    if '軽井沢' in line and len(line.strip()) < 100:
                        property_data.location = line.strip()
                        break
            else:
                property_data.location = "長野県軽井沢"
            
            # Set property type
            property_data.property_type = "House"  # We searched for houses
            
            # Extract source URL
            try:
                link = element.find_element(By.TAG_NAME, 'a')
                href = self.extract_attribute_safely(link, 'href')
                if href:
                    if href.startswith('/'):
                        property_data.source_url = self.base_url + href
                    else:
                        property_data.source_url = href
                else:
                    property_data.source_url = self.driver.current_url
            except:
                property_data.source_url = self.driver.current_url
            
            # Extract room layout
            room_match = re.search(r'([0-9]+[SLDK]+)', element_text)
            if room_match:
                property_data.rooms = room_match.group(0)
            
            # Extract building age
            age_match = re.search(r'築([0-9]+)年', element_text)
            if age_match:
                property_data.building_age = age_match.group(0)
            
            property_data.scraped_at = time.time()
            
            return property_data
            
        except Exception as e:
            logger.error(f"Error extracting SUUMO property: {e}")
            return None
    
    def is_karuizawa_property(self, property_data: PropertyData) -> bool:
        """Check if property is in Karuizawa"""
        if not property_data:
            return False
            
        text_to_check = f"{property_data.title} {property_data.location}".lower()
        karuizawa_keywords = ['軽井沢', 'karuizawa']
        
        return any(keyword in text_to_check for keyword in karuizawa_keywords)