"""
SUUMO vacation home scraper for Karuizawa properties
Handles JavaScript-heavy site with anti-bot protection
"""
import time
import re
from typing import List, Optional
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import logging

from .browser_scraper import BrowserScraper
from .base_scraper import PropertyData

logger = logging.getLogger(__name__)

class SUUMOScraper(BrowserScraper):
    """Scraper for SUUMO vacation home properties in Karuizawa"""
    
    def __init__(self, config: dict = None):
        default_config = {
            'base_url': 'https://suumo.jp',
            'headless': True,
            'wait_timeout': 30,
            'page_load_timeout': 60,
            'name': 'SUUMO Karuizawa'
        }
        
        if config:
            default_config.update(config)
            
        super().__init__(default_config)
        self.vacation_home_url = 'https://suumo.jp/edit/kr/nj_ijyuubessou/'
        
    def scrape_listings(self) -> List[PropertyData]:
        """Main scraping method for SUUMO vacation home properties"""
        logger.info("Starting SUUMO vacation home property scraping")
        
        if not self.setup_browser():
            logger.error("Failed to setup browser")
            return []
        
        try:
            # Navigate to vacation home section
            if not self.navigate_to_page(self.vacation_home_url):
                logger.error("Failed to navigate to SUUMO vacation home page")
                return []
            
            # Handle any popups or cookie consent
            self.handle_popup_if_present()
            
            # Search for Karuizawa properties
            properties = self.search_karuizawa_properties()
            
            logger.info(f"SUUMO: Found {len(properties)} Karuizawa vacation home properties")
            return properties
            
        except Exception as e:
            logger.error(f"Error in SUUMO scraping: {e}")
            return []
        finally:
            self.close_browser()
    
    def search_karuizawa_properties(self) -> List[PropertyData]:
        """Search for Karuizawa vacation home properties"""
        all_properties = []
        
        # First, let's debug what's on the page
        self.debug_page_structure()
        
        # Property types to search
        property_types = [
            ('新築一戸建て', 'New House'),
            ('中古一戸建て', 'Used House'), 
            ('中古マンション', 'Used Apartment'),
            ('土地', 'Land')
        ]
        
        for prop_type_jp, prop_type_en in property_types:
            try:
                logger.info(f"Searching SUUMO for {prop_type_en} properties in Karuizawa")
                
                # Navigate to search form
                if not self.navigate_to_page(self.vacation_home_url):
                    continue
                    
                self.simulate_human_delay(2.0, 4.0)
                
                # Select property type
                if self.select_property_type(prop_type_jp):
                    # Select Nagano prefecture (where Karuizawa is located)
                    if self.select_nagano_prefecture():
                        # Submit search and extract results
                        properties = self.submit_search_and_extract()
                        if properties:
                            # Filter for Karuizawa-specific properties
                            karuizawa_properties = [p for p in properties if self.is_karuizawa_property(p)]
                            logger.info(f"Found {len(karuizawa_properties)} Karuizawa {prop_type_en} properties")
                            all_properties.extend(karuizawa_properties)
                
                # Rate limiting between searches
                self.simulate_human_delay(3.0, 5.0)
                
            except Exception as e:
                logger.warning(f"Error searching for {prop_type_en}: {e}")
                continue
        
        # Deduplicate properties
        return self.deduplicate_properties(all_properties)
    
    def select_property_type(self, property_type: str) -> bool:
        """Select property type from dropdown"""
        try:
            # First, try to find the property type select dropdown
            select_selectors = [
                "select",
                "select[name*='type']",
                "#property_type",
                ".property-type-select"
            ]
            
            for selector in select_selectors:
                try:
                    select_element = self.wait_for_element(By.CSS_SELECTOR, selector, timeout=10)
                    if select_element:
                        select_obj = Select(select_element)
                        
                        # Try to select by visible text
                        try:
                            select_obj.select_by_visible_text(property_type)
                            logger.debug(f"Selected property type by text: {property_type}")
                            return True
                        except:
                            # Try to find option with partial match
                            options = select_obj.options
                            for option in options:
                                if property_type in option.text:
                                    select_obj.select_by_visible_text(option.text)
                                    logger.debug(f"Selected property type by partial match: {option.text}")
                                    return True
                except Exception as e:
                    logger.debug(f"Failed to use selector {selector}: {e}")
                    continue
            
            # Alternative approach: look for radio buttons or checkboxes
            radio_selectors = [
                f"input[type='radio'][value*='{property_type}']",
                f"input[type='checkbox'][value*='{property_type}']"
            ]
            
            for selector in radio_selectors:
                try:
                    element = self.wait_for_element(By.CSS_SELECTOR, selector, timeout=5)
                    if element:
                        element.click()
                        logger.debug(f"Selected property type radio/checkbox: {property_type}")
                        return True
                except:
                    continue
            
            # Last resort: try XPath with text content
            try:
                xpath = f"//option[contains(text(), '{property_type}')]"
                option_element = self.wait_for_element(By.XPATH, xpath, timeout=5)
                if option_element:
                    option_element.click()
                    logger.debug(f"Selected property type by XPath: {property_type}")
                    return True
            except:
                pass
            
            logger.warning(f"Could not select property type: {property_type}")
            return False
            
        except Exception as e:
            logger.error(f"Error selecting property type {property_type}: {e}")
            return False
    
    def select_nagano_prefecture(self) -> bool:
        """Select Nagano prefecture from dropdown"""
        try:
            # Look for prefecture selector - try broader selectors
            prefecture_selectors = [
                "select",  # Try all select elements
                "select[name*='pref']",
                "select[name*='ken']", 
                "#prefecture_select",
                ".prefecture-select"
            ]
            
            for selector in prefecture_selectors:
                try:
                    select_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for select_element in select_elements:
                        if select_element.is_displayed():
                            select_obj = Select(select_element)
                            
                            # Try different ways to select Nagano
                            nagano_options = ['長野県', '長野', 'nagano', '20', 'NAGANO']
                            
                            for option_value in nagano_options:
                                try:
                                    # First try by visible text
                                    select_obj.select_by_visible_text(option_value)
                                    logger.debug(f"Selected Nagano prefecture by text: {option_value}")
                                    return True
                                except:
                                    try:
                                        # Then try by value
                                        select_obj.select_by_value(option_value)
                                        logger.debug(f"Selected Nagano prefecture by value: {option_value}")
                                        return True
                                    except:
                                        continue
                                        
                            # Try partial text match
                            options = select_obj.options
                            for option in options:
                                if '長野' in option.text or 'nagano' in option.text.lower():
                                    select_obj.select_by_visible_text(option.text)
                                    logger.debug(f"Selected Nagano by partial match: {option.text}")
                                    return True
                                    
                except Exception as e:
                    logger.debug(f"Failed with selector {selector}: {e}")
                    continue
            
            logger.warning("Could not select Nagano prefecture")
            return False
            
        except Exception as e:
            logger.error(f"Error selecting Nagano prefecture: {e}")
            return False
    
    def submit_search_and_extract(self) -> List[PropertyData]:
        """Submit search form and extract property results"""
        properties = []
        
        try:
            # Look for search/submit button
            submit_selectors = [
                "input[type='submit']",
                "button[type='submit']", 
                ".search-button",
                ".submit-button",
                "button:contains('検索')",
                "input[value*='検索']"
            ]
            
            search_submitted = False
            for selector in submit_selectors:
                try:
                    submit_button = self.wait_for_element(By.CSS_SELECTOR, selector, timeout=5)
                    if submit_button and submit_button.is_enabled():
                        submit_button.click()
                        logger.debug("Search submitted")
                        search_submitted = True
                        break
                except:
                    continue
            
            if not search_submitted:
                logger.warning("Could not submit search form")
                return properties
            
            # Wait for results page to load
            self.simulate_human_delay(3.0, 6.0)
            
            # Extract properties from results
            properties = self.extract_properties_from_results_page()
            
        except Exception as e:
            logger.error(f"Error submitting search and extracting: {e}")
        
        return properties
    
    def extract_properties_from_results_page(self) -> List[PropertyData]:
        """Extract property data from search results page"""
        properties = []
        
        try:
            # Look for property result containers
            result_selectors = [
                ".property-item",
                ".listing-item",
                ".result-item", 
                ".bukken-item",
                "[class*='property']",
                "[class*='listing']",
                ".cassetteitem"  # SUUMO specific class
            ]
            
            property_elements = []
            for selector in result_selectors:
                elements = self.wait_for_elements(By.CSS_SELECTOR, selector, timeout=10)
                if elements:
                    logger.info(f"Found {len(elements)} property elements with selector: {selector}")
                    property_elements = elements
                    break
            
            if not property_elements:
                logger.warning("No property result elements found")
                return properties
            
            # Extract data from each property element
            for i, element in enumerate(property_elements[:20], 1):  # Limit to prevent timeouts
                try:
                    logger.debug(f"Processing SUUMO property {i}")
                    property_data = self.extract_property_from_element(element)
                    if property_data and self.validate_property_data(property_data):
                        properties.append(property_data)
                        
                    # Rate limiting between extractions
                    if i % 5 == 0:  # Every 5 properties
                        self.simulate_human_delay(1.0, 2.0)
                        
                except Exception as e:
                    logger.debug(f"Error extracting SUUMO property {i}: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"Error extracting from results page: {e}")
        
        return properties
    
    def extract_property_from_element(self, element) -> Optional[PropertyData]:
        """Extract property data from a result element"""
        try:
            property_data = PropertyData()
            
            # Get all text content at once to minimize DOM queries
            element_text = element.get_attribute('textContent') or ""
            element_html = element.get_attribute('outerHTML') or ""
            
            # Extract title
            title_selectors = ['h2', 'h3', '.title', '.name', 'a']
            for selector in title_selectors:
                try:
                    title_elem = element.find_element(By.CSS_SELECTOR, selector)
                    title_text = self.extract_text_safely(title_elem)
                    if title_text and len(title_text.strip()) > 5:
                        property_data.title = title_text.strip()[:150]
                        break
                except:
                    continue
            
            if not property_data.title:
                # Extract from text content
                lines = [line.strip() for line in element_text.split('\n') if line.strip()]
                for line in lines[:3]:
                    if len(line) > 10 and not any(skip in line.lower() for skip in ['price', '円', '¥']):
                        property_data.title = line[:100]
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
            location_keywords = ['軽井沢', 'karuizawa', '中軽井沢', '南軽井沢', '旧軽井沢', '北軽井沢']
            for line in element_text.split('\n'):
                line_clean = line.strip()
                if any(keyword in line_clean.lower() for keyword in location_keywords):
                    property_data.location = line_clean[:100]
                    break
                    
            if not property_data.location:
                property_data.location = "軽井沢"
            
            # Extract property type from SUUMO structure
            if '一戸建て' in element_text or 'house' in element_text.lower():
                property_data.property_type = 'House'
            elif 'マンション' in element_text or 'apartment' in element_text.lower():
                property_data.property_type = 'Apartment'
            elif '土地' in element_text or 'land' in element_text.lower():
                property_data.property_type = 'Land'
            elif '別荘' in element_text or 'villa' in element_text.lower():
                property_data.property_type = 'Villa'
            else:
                property_data.property_type = 'Vacation Home'
            
            # Extract source URL from links
            try:
                link_elem = element.find_element(By.TAG_NAME, 'a')
                href = self.extract_attribute_safely(link_elem, 'href')
                if href:
                    if href.startswith('/'):
                        property_data.source_url = self.base_url + href
                    elif href.startswith('http'):
                        property_data.source_url = href
            except:
                property_data.source_url = self.driver.current_url
            
            # Extract room layout
            room_match = re.search(r'([0-9]+[SLDK]+)', element_text)
            if room_match:
                property_data.rooms = room_match.group(0)
            
            # Extract size
            size_match = re.search(r'([0-9,]+\.?[0-9]*)(?:㎡|m²|平米|坪)', element_text)
            if size_match:
                property_data.size_info = size_match.group(0)
            
            property_data.scraped_at = time.time()
            
            return property_data
            
        except Exception as e:
            logger.error(f"Error extracting SUUMO property data: {e}")
            return None
    
    def is_karuizawa_property(self, property_data: PropertyData) -> bool:
        """Check if property is specifically in Karuizawa area"""
        if not property_data:
            return False
            
        # Check title and location for Karuizawa references
        karuizawa_keywords = ['軽井沢', 'karuizawa', '中軽井沢', '南軽井沢', '旧軽井沢', '北軽井沢']
        
        text_to_check = f"{property_data.title} {property_data.location} {property_data.description or ''}".lower()
        
        return any(keyword in text_to_check for keyword in karuizawa_keywords)
    
    def validate_property_data(self, property_data: PropertyData) -> bool:
        """Validate SUUMO property data"""
        try:
            if not property_data.is_valid():
                return False
            
            # Must be Karuizawa-related
            if not self.is_karuizawa_property(property_data):
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating SUUMO property: {e}")
            return False
    
    def deduplicate_properties(self, properties: List[PropertyData]) -> List[PropertyData]:
        """Remove duplicate properties"""
        seen = set()
        unique_properties = []
        
        for prop in properties:
            # Create deduplication key
            key = f"{prop.title.lower()}-{prop.price}-{prop.location.lower()}"
            if key not in seen:
                seen.add(key)
                unique_properties.append(prop)
            else:
                logger.debug(f"Duplicate SUUMO property filtered: {prop.title}")
        
        return unique_properties
    
    def debug_page_structure(self):
        """Debug method to understand page structure"""
        try:
            logger.info("=== DEBUGGING SUUMO PAGE STRUCTURE ===")
            
            # Check for all select elements
            select_elements = self.driver.find_elements(By.TAG_NAME, 'select')
            logger.info(f"Found {len(select_elements)} select elements")
            
            for i, select_elem in enumerate(select_elements):
                if select_elem.is_displayed():
                    select_obj = Select(select_elem)
                    options_text = [opt.text for opt in select_obj.options[:5]]  # First 5 options
                    logger.info(f"Select {i+1}: {options_text}")
            
            # Check for forms
            forms = self.driver.find_elements(By.TAG_NAME, 'form')
            logger.info(f"Found {len(forms)} form elements")
            
            # Check for buttons/inputs
            buttons = self.driver.find_elements(By.CSS_SELECTOR, 'button, input[type="submit"], input[type="button"]')
            logger.info(f"Found {len(buttons)} button elements")
            
            # Check page title and current URL
            logger.info(f"Page title: {self.driver.title}")
            logger.info(f"Current URL: {self.driver.current_url}")
            
            logger.info("=== END DEBUG INFO ===")
            
        except Exception as e:
            logger.error(f"Error in debug: {e}")