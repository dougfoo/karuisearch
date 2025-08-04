"""
Besso Navi scraper - Form-based vacation home search site
"""
import time
import re
from typing import List, Optional, Dict
from urllib.parse import urljoin
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import logging

from .browser_scraper import BrowserScraper
from .base_scraper import PropertyData

logger = logging.getLogger(__name__)

class BessoNaviScraper(BrowserScraper):
    """Scraper for Besso Navi - vacation home search site with form-based search"""
    
    def __init__(self, config: dict = None):
        default_config = {
            'base_url': 'https://www.besso-navi.com',
            'headless': True,
            'wait_timeout': 15,
            'page_load_timeout': 30
        }
        
        if config:
            default_config.update(config)
            
        super().__init__(default_config)
        self.search_url = self.base_url + '/b-search'
        
        # Search parameters for Karuizawa properties
        self.search_params = {
            'areas': ['軽井沢', '中軽井沢', '南軽井沢', 'karuizawa'],
            'property_types': ['土地', '一戸建て', 'マンション', 'ヴィラ'],
            'price_min': 1000000,    # 1M yen
            'price_max': 500000000,  # 500M yen
            'land_area_min': 100     # 100 sqm
        }
        
    def scrape_listings(self) -> List[PropertyData]:
        """Main scraping method for Besso Navi properties"""
        logger.info("Starting Besso Navi property scraping")
        
        if not self.navigate_to_page(self.search_url):
            logger.error("Failed to navigate to search page")
            return []
            
        # Handle any initial popups
        self.handle_popup_if_present()
        
        # Set up search parameters
        if not self.setup_search_form():
            logger.error("Failed to setup search form")
            return []
            
        # Submit search
        if not self.submit_search():
            logger.error("Failed to submit search")
            return []
            
        # Wait for results to load
        self.simulate_human_delay(3.0, 5.0)
        
        # Extract properties from search results
        all_properties = []
        page_num = 1
        
        while page_num <= 5:  # Limit to 5 pages to prevent infinite loops
            logger.info(f"Processing results page {page_num}")
            
            properties = self.extract_properties_from_current_page()
            
            if not properties:
                logger.info("No more properties found, stopping pagination")
                break
                
            all_properties.extend(properties)
            logger.info(f"Extracted {len(properties)} properties from page {page_num}")
            
            # Try to go to next page
            if not self.navigate_to_next_page():
                logger.info("No more pages available")
                break
                
            page_num += 1
            self.simulate_human_delay(2.0, 4.0)
            
        logger.info(f"Total properties extracted from Besso Navi: {len(all_properties)}")
        return all_properties
        
    def setup_search_form(self) -> bool:
        """Setup the search form with Karuizawa-specific parameters"""
        logger.info("Setting up search form for Karuizawa properties")
        
        try:
            # Wait for form to be present
            form_wait = WebDriverWait(self.driver, 10)
            form_wait.until(EC.presence_of_element_located((By.TAG_NAME, "form")))
            
            # Set area/location to Karuizawa
            if not self.set_search_area():
                logger.warning("Could not set search area")
                
            # Set property types
            if not self.set_property_types():
                logger.warning("Could not set property types")
                
            # Set price range
            if not self.set_price_range():
                logger.warning("Could not set price range")
                
            # Set land area if available
            if not self.set_land_area():
                logger.warning("Could not set land area")
                
            logger.info("Search form setup completed")
            return True
            
        except Exception as e:
            logger.error(f"Error setting up search form: {e}")
            return False
            
    def set_search_area(self) -> bool:
        """Set the search area to Karuizawa"""
        # Try various approaches to set the area
        
        # Approach 1: Look for area select dropdown
        try:
            area_selectors = [
                "select[name*='area']", "select[name*='prefecture']", 
                "select[name*='region']", "select[name*='location']"
            ]
            
            for selector in area_selectors:
                try:
                    select_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    select = Select(select_element)
                    
                    # Try to find Karuizawa-related options
                    for option in select.options:
                        option_text = option.text.lower()
                        if any(area in option_text for area in ['karuizawa', '軽井沢', '長野']):
                            select.select_by_visible_text(option.text)
                            logger.info(f"Selected area: {option.text}")
                            return True
                            
                except Exception:
                    continue
                    
        except Exception as e:
            logger.debug(f"Select dropdown approach failed: {e}")
            
        # Approach 2: Look for checkboxes
        try:
            checkbox_selectors = [
                "input[type='checkbox'][name*='area']",
                "input[type='checkbox'][value*='karuizawa']",
                "input[type='checkbox'][value*='軽井沢']"
            ]
            
            for selector in checkbox_selectors:
                try:
                    checkboxes = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for checkbox in checkboxes:
                        # Check the value or nearby text
                        checkbox_value = checkbox.get_attribute('value') or ''
                        parent_text = checkbox.find_element(By.XPATH, '..').text or ''
                        
                        if any(area in (checkbox_value + parent_text).lower() 
                               for area in ['karuizawa', '軽井沢']):
                            if not checkbox.is_selected():
                                self.safe_click(checkbox)
                                logger.info("Selected Karuizawa area checkbox")
                                return True
                                
                except Exception:
                    continue
                    
        except Exception as e:
            logger.debug(f"Checkbox approach failed: {e}")
            
        # Approach 3: Look for text input
        try:
            text_selectors = [
                "input[type='text'][name*='area']",
                "input[type='text'][name*='location']",
                "input[type='text'][name*='keyword']"
            ]
            
            for selector in text_selectors:
                try:
                    text_input = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if self.safe_send_keys(text_input, "軽井沢"):
                        logger.info("Entered Karuizawa in text field")
                        return True
                        
                except Exception:
                    continue
                    
        except Exception as e:
            logger.debug(f"Text input approach failed: {e}")
            
        logger.warning("Could not set search area to Karuizawa")
        return False
        
    def set_property_types(self) -> bool:
        """Set property types to include all types"""
        try:
            # Look for property type checkboxes or select
            type_selectors = [
                "input[type='checkbox'][name*='type']",
                "input[type='checkbox'][value*='一戸建て']",
                "input[type='checkbox'][value*='土地']",
                "input[type='checkbox'][value*='マンション']",
                "select[name*='type']"
            ]
            
            types_set = False
            
            # Try checkboxes first
            for selector in type_selectors[:4]:  # Checkbox selectors
                try:
                    checkboxes = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for checkbox in checkboxes:
                        checkbox_value = checkbox.get_attribute('value') or ''
                        parent_text = checkbox.find_element(By.XPATH, '..').text or ''
                        combined_text = (checkbox_value + parent_text).lower()
                        
                        # Check if it's a property type we want
                        if any(prop_type in combined_text 
                               for prop_type in ['一戸建て', '土地', 'マンション', 'house', 'land', 'apartment']):
                            if not checkbox.is_selected():
                                self.safe_click(checkbox)
                                types_set = True
                                
                except Exception:
                    continue
                    
            if types_set:
                logger.info("Selected property types via checkboxes")
                return True
                
            # Try select dropdown
            try:
                select_element = self.driver.find_element(By.CSS_SELECTOR, "select[name*='type']")
                select = Select(select_element)
                
                # Select "All" or first option if available
                if len(select.options) > 1:
                    select.select_by_index(0)  # Usually "All" or default
                    logger.info("Selected property type via dropdown")
                    return True
                    
            except Exception as e:
                logger.debug(f"Select dropdown for types failed: {e}")
                
        except Exception as e:
            logger.warning(f"Could not set property types: {e}")
            
        return False
        
    def set_price_range(self) -> bool:
        """Set price range for search"""
        try:
            # Look for price range inputs
            price_selectors = [
                "select[name*='price']", "input[name*='price']",
                "select[name*='amount']", "input[name*='amount']"
            ]
            
            # Try to set minimum price
            min_set = False
            max_set = False
            
            for selector in price_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        element_name = element.get_attribute('name') or ''
                        
                        if 'min' in element_name.lower() or 'from' in element_name.lower():
                            if element.tag_name == 'select':
                                select = Select(element)
                                # Try to find appropriate minimum price option
                                for option in select.options:
                                    if '1000000' in option.get_attribute('value') or '100万' in option.text:
                                        select.select_by_value(option.get_attribute('value'))
                                        min_set = True
                                        break
                            else:
                                self.safe_send_keys(element, "1000000")
                                min_set = True
                                
                        elif 'max' in element_name.lower() or 'to' in element_name.lower():
                            if element.tag_name == 'select':
                                select = Select(element)
                                # Try to find appropriate maximum price option
                                for option in select.options:
                                    if '500000000' in option.get_attribute('value') or '5億' in option.text:
                                        select.select_by_value(option.get_attribute('value'))
                                        max_set = True
                                        break
                            else:
                                self.safe_send_keys(element, "500000000")
                                max_set = True
                                
                except Exception:
                    continue
                    
            if min_set or max_set:
                logger.info(f"Set price range (min: {min_set}, max: {max_set})")
                return True
                
        except Exception as e:
            logger.warning(f"Could not set price range: {e}")
            
        return False
        
    def set_land_area(self) -> bool:
        """Set minimum land area"""
        try:
            area_selectors = [
                "select[name*='area'][name*='land']", "input[name*='area'][name*='land']",
                "select[name*='size']", "input[name*='size']"
            ]
            
            for selector in area_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        element_name = element.get_attribute('name') or ''
                        
                        if 'min' in element_name.lower():
                            if element.tag_name == 'select':
                                select = Select(element)
                                # Try to select 100 sqm or similar
                                for option in select.options:
                                    if '100' in option.get_attribute('value'):
                                        select.select_by_value(option.get_attribute('value'))
                                        logger.info("Set minimum land area")
                                        return True
                            else:
                                self.safe_send_keys(element, "100")
                                logger.info("Set minimum land area")
                                return True
                                
                except Exception:
                    continue
                    
        except Exception as e:
            logger.debug(f"Could not set land area: {e}")
            
        return False
        
    def submit_search(self) -> bool:
        """Submit the search form"""
        try:
            # Look for search/submit button
            button_selectors = [
                "input[type='submit']", "button[type='submit']",
                "input[value*='検索']", "button[value*='検索']",
                "input[value*='search']", "button[value*='search']",
                ".search-button", ".submit-button", "#search-btn"
            ]
            
            for selector in button_selectors:
                try:
                    submit_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if submit_button.is_displayed() and submit_button.is_enabled():
                        self.safe_click(submit_button)
                        logger.info("Submitted search form")
                        return True
                        
                except Exception:
                    continue
                    
            # If no button found, try submitting the form directly
            try:
                form = self.driver.find_element(By.TAG_NAME, "form")
                form.submit()
                logger.info("Submitted form directly")
                return True
                
            except Exception as e:
                logger.debug(f"Direct form submit failed: {e}")
                
        except Exception as e:
            logger.error(f"Could not submit search form: {e}")
            
        return False
        
    def extract_properties_from_current_page(self) -> List[PropertyData]:
        """Extract properties from current search results page"""
        properties = []
        
        try:
            # Wait for search results to load
            result_wait = WebDriverWait(self.driver, 10)
            result_wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            
            # Look for property result containers
            result_selectors = [
                ".search-result", ".result-item", ".property-item",
                ".bukken-item", ".listing-item", ".property-card",
                "[class*='result']", "[class*='property']", "[class*='bukken']"
            ]
            
            property_elements = []
            for selector in result_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        property_elements = elements
                        logger.info(f"Found {len(elements)} property elements with selector: {selector}")
                        break
                        
                except Exception:
                    continue
                    
            if not property_elements:
                # Try broader search for elements containing price indicators
                logger.warning("No property elements found with standard selectors, trying broader search")
                price_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), '万円') or contains(text(), 'yen')]")
                
                property_containers = []
                for price_elem in price_elements:
                    try:
                        # Get parent container
                        parent = price_elem.find_element(By.XPATH, "./ancestor::*[contains(@class, 'item') or contains(@class, 'result') or contains(@class, 'property')][1]")
                        if parent not in property_containers:
                            property_containers.append(parent)
                    except:
                        continue
                        
                property_elements = property_containers[:10]  # Limit to prevent too many
                
            # Extract data from each property element
            for i, element in enumerate(property_elements, 1):
                try:
                    logger.debug(f"Extracting property {i}/{len(property_elements)}")
                    
                    property_data = self.extract_property_from_element(element)
                    
                    if property_data and self.validate_property_data(property_data):
                        properties.append(property_data)
                        logger.debug(f"Successfully extracted property {i}")
                    else:
                        logger.debug(f"Property {i} failed validation or extraction")
                        
                except Exception as e:
                    logger.warning(f"Error extracting property {i}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error extracting properties from page: {e}")
            
        return properties
        
    def extract_property_from_element(self, element) -> Optional[PropertyData]:
        """Extract property data from a search result element"""
        try:
            property_data = PropertyData()
            
            # Extract title/name
            title = self.extract_element_title(element)
            if title:
                property_data.title = title
                
            # Extract price
            price = self.extract_element_price(element)
            if price:
                property_data.price = price
                
            # Extract location
            location = self.extract_element_location(element)
            if location:
                property_data.location = location
            else:
                property_data.location = "軽井沢"  # Default since we searched for Karuizawa
                
            # Extract property type
            prop_type = self.extract_element_property_type(element)
            if prop_type:
                property_data.property_type = prop_type
                
            # Extract size information
            size_info = self.extract_element_size(element)
            if size_info:
                property_data.size_info = size_info
                
            # Extract images
            images = self.extract_element_images(element)
            if images:
                property_data.image_urls = images
                
            # Extract detail URL
            detail_url = self.extract_element_detail_url(element)
            if detail_url:
                property_data.source_url = detail_url
            else:
                property_data.source_url = self.driver.current_url
                
            # Set scraping timestamp
            property_data.scraped_at = time.time()
            
            return property_data
            
        except Exception as e:
            logger.error(f"Error extracting property data from element: {e}")
            return None
            
    def extract_element_title(self, element) -> str:
        """Extract title from property element"""
        title_selectors = [
            "h1", "h2", "h3", "h4", "h5",
            ".title", ".name", ".property-name", ".bukken-name",
            "[class*='title']", "[class*='name']"
        ]
        
        for selector in title_selectors:
            try:
                title_elem = element.find_element(By.CSS_SELECTOR, selector)
                title = self.extract_text_safely(title_elem)
                if title and len(title.strip()) > 3:
                    return title.strip()
            except:
                continue
                
        return ""
        
    def extract_element_price(self, element) -> str:
        """Extract price from property element"""
        price_selectors = [
            ".price", ".amount", ".cost", ".kakaku",
            "[class*='price']", "[class*='amount']", "[class*='cost']"
        ]
        
        for selector in price_selectors:
            try:
                price_elem = element.find_element(By.CSS_SELECTOR, selector)
                price = self.extract_text_safely(price_elem)
                if price and ('万円' in price or 'yen' in price.lower() or '¥' in price):
                    return price.strip()
            except:
                continue
                
        # Search for price in element text
        element_text = self.extract_text_safely(element)
        price_patterns = [
            r'\d+[,]?\d*万円',
            r'¥\d+[,]?\d*',
            r'\d+[,]?\d*\s*yen'
        ]
        
        for pattern in price_patterns:
            matches = re.findall(pattern, element_text, re.IGNORECASE)
            if matches:
                return matches[0].strip()
                
        return ""
        
    def extract_element_location(self, element) -> str:
        """Extract location from property element"""
        location_selectors = [
            ".location", ".area", ".address", ".basho",
            "[class*='location']", "[class*='area']", "[class*='address']"
        ]
        
        for selector in location_selectors:
            try:
                location_elem = element.find_element(By.CSS_SELECTOR, selector)
                location = self.extract_text_safely(location_elem)
                if location and len(location.strip()) > 2:
                    return location.strip()
            except:
                continue
                
        return ""
        
    def extract_element_property_type(self, element) -> str:
        """Extract property type from element"""
        element_text = self.extract_text_safely(element)
        
        if '一戸建て' in element_text:
            return '一戸建て'
        elif '土地' in element_text:
            return '土地'
        elif 'マンション' in element_text:
            return 'マンション'
        elif 'ヴィラ' in element_text or 'villa' in element_text.lower():
            return 'ヴィラ'
            
        return ""
        
    def extract_element_size(self, element) -> str:
        """Extract size information from element"""
        element_text = self.extract_text_safely(element)
        
        size_patterns = [
            r'\d+[,.]?\d*\s*㎡',
            r'\d+[,.]?\d*\s*m²',
            r'\d+[,.]?\d*\s*坪',
            r'\d+[,.]?\d*\s*sqm'
        ]
        
        for pattern in size_patterns:
            matches = re.findall(pattern, element_text, re.IGNORECASE)
            if matches:
                return matches[0].strip()
                
        return ""
        
    def extract_element_images(self, element) -> List[str]:
        """Extract image URLs from element"""
        images = []
        
        try:
            img_elements = element.find_elements(By.TAG_NAME, "img")
            
            for img in img_elements:
                img_url = self.extract_attribute_safely(img, 'src')
                if not img_url:
                    img_url = self.extract_attribute_safely(img, 'data-src')
                    
                if img_url and img_url.startswith(('http', '//')):
                    if img_url.startswith('//'):
                        img_url = 'https:' + img_url
                    elif img_url.startswith('/'):
                        img_url = urljoin(self.base_url, img_url)
                        
                    images.append(img_url)
                    
        except Exception as e:
            logger.debug(f"Error extracting images: {e}")
            
        return images[:3]  # Limit to 3 images
        
    def extract_element_detail_url(self, element) -> str:
        """Extract detail page URL from element"""
        try:
            # Look for multiple types of links with different selectors
            link_selectors = [
                'a[href*="property"]',
                'a[href*="detail"]',
                'a[href*="bukken"]',
                'a[href*="listing"]',
                'a[href*="item"]',
                'a'  # Fallback to any link
            ]
            
            for selector in link_selectors:
                try:
                    link_element = element.find_element(By.CSS_SELECTOR, selector)
                    detail_url = self.extract_attribute_safely(link_element, 'href')
                    
                    if detail_url and self.is_valid_property_url(detail_url):
                        # Convert relative URL to absolute
                        if detail_url.startswith('/'):
                            detail_url = urljoin(self.base_url, detail_url)
                        elif detail_url.startswith('//'):
                            detail_url = 'https:' + detail_url
                        
                        logger.debug(f"Found valid property URL: {detail_url}")
                        return detail_url
                        
                except Exception:
                    continue
                    
        except Exception as e:
            logger.debug(f"Error extracting detail URL: {e}")
        
        # Fallback to current page URL if no detail URL found
        logger.debug("No valid detail URL found, using current search page")
        return self.driver.current_url
        
    def navigate_to_next_page(self) -> bool:
        """Navigate to next page of search results"""
        try:
            # Look for next page button
            next_selectors = [
                ".next", ".page-next", ".pager-next",
                "a[href*='page']", "a[href*='次']",
                "[class*='next']", "[class*='forward']"
            ]
            
            for selector in next_selectors:
                try:
                    next_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if next_button.is_displayed() and next_button.is_enabled():
                        button_text = self.extract_text_safely(next_button).lower()
                        if any(word in button_text for word in ['next', '次', '→', '>']):
                            self.safe_click(next_button)
                            logger.info("Navigated to next page")
                            return True
                            
                except Exception:
                    continue
                    
            logger.info("No next page button found")
            return False
            
        except Exception as e:
            logger.warning(f"Error navigating to next page: {e}")
            return False

    def is_valid_property_url(self, url: str) -> bool:
        """Validate if URL appears to be a property detail page"""
        if not url:
            return False
        
        # Skip javascript and anchor links
        if url.startswith(('javascript:', '#', 'mailto:')):
            return False
            
        # Check for property-related keywords in URL
        property_keywords = ['property', 'detail', 'bukken', 'listing', 'item', 'besso', 'search']
        url_lower = url.lower()
        
        # Must contain at least one property keyword or be a different page than base
        has_property_keyword = any(keyword in url_lower for keyword in property_keywords)
        
        # Should not be just the base domain
        is_not_base_url = url != self.base_url and not url.endswith('/')
        
        return has_property_keyword or is_not_base_url

    def validate_property_data(self, property_data: PropertyData) -> bool:
        """Validate Besso Navi property data"""
        try:
            # Basic validation from parent class
            if not super().validate_property_data(property_data):
                return False
                
            # Besso Navi specific validation
            if not all([property_data.title, property_data.price]):
                logger.debug("Missing required fields for Besso Navi")
                return False
                
            # Should be related to Karuizawa (since we searched for it)
            if not property_data.contains_karuizawa():
                # For Besso Navi, we accept if location is not explicitly set 
                # since we searched specifically for Karuizawa
                if not property_data.location:
                    property_data.location = "軽井沢"
                    
            logger.debug("Besso Navi property validation passed")
            return True
            
        except Exception as e:
            logger.error(f"Validation error: {e}")
            return False