"""
Tokyu Resort Karuizawa property scraper using browser automation
Handles JavaScript-rendered search results
"""
import re
import time
from typing import List, Optional
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import logging

from .browser_scraper import BrowserScraper
from .base_scraper import PropertyData
from utils.titleGenerator import generate_property_title

logger = logging.getLogger(__name__)

class TokyuResortBrowserScraper(BrowserScraper):
    """Browser-based scraper for Tokyu Resort Karuizawa properties"""
    
    def __init__(self, config: dict = None):
        if config is None:
            config = {
                'base_url': 'https://www.tokyu-resort.co.jp',
                'rate_limit': 0.2,  # 1 request every 5 seconds (very conservative for browser)
                'name': 'Tokyu Resort Karuizawa (Browser)',
                'wait_timeout': 10,
                'page_load_timeout': 15,
                'headless': True
            }
        else:
            # Ensure we have the base URL if not provided
            if 'base_url' not in config:
                config['base_url'] = 'https://www.tokyu-resort.co.jp'
                
        super().__init__(config)
        
    def scrape_listings(self) -> List[PropertyData]:
        """Main method to scrape property listings using browser"""
        all_properties = []
        
        # Setup browser
        if not self.setup_browser():
            logger.error("Failed to setup browser")
            return []
        
        try:
            # Target search URLs for Tokyu Resort properties
            search_urls = [
                '/search/result?HPSRC_AREA_ID[57]=1&SHUBETSU_ID[2]=1&area_top_flg=1&link_id=11villa',  # Karuizawa villas
                '/search/result?HPSRC_AREA_ID[57]=1&area_top_flg=1',  # General Karuizawa search
            ]
            
            for url_path in search_urls:
                try:
                    full_url = f"{self.base_url}{url_path}"
                    logger.info(f"Loading Tokyu Resort search: {full_url}")
                    
                    # Navigate to search results page with timeout handling
                    logger.info(f"Navigating to: {full_url}")
                    try:
                        self.driver.get(full_url)
                        logger.info("Page loaded successfully")
                    except Exception as e:
                        logger.error(f"Failed to load page: {e}")
                        continue
                    
                    # Wait for page to load and JavaScript to render results
                    self.wait_for_search_results()
                    
                    # Extract properties from search results
                    properties = self.extract_properties_from_search_page(full_url)
                    logger.info(f"Found {len(properties)} properties from {url_path}")
                    all_properties.extend(properties)
                    
                    # Rate limiting between searches
                    if len(search_urls) > 1:
                        delay = 1.0 / self.config.get('rate_limit', 0.2)
                        logger.info(f"Rate limiting: waiting {delay:.1f}s before next search")
                        time.sleep(delay)
                        
                except Exception as e:
                    logger.error(f"Error scraping search URL {url_path}: {e}")
                    continue
            
            # Remove duplicates and validate
            unique_properties = self.deduplicate_properties(all_properties)
            logger.info(f"Tokyu Resort (Browser): {len(unique_properties)} unique properties found")
            
            return unique_properties
            
        except Exception as e:
            logger.error(f"Error during scraping: {e}")
            return []
        finally:
            self.close_browser()
    
    def wait_for_search_results(self, timeout: int = 15):
        """Wait for search results to load dynamically"""
        try:
            # Wait for search results container to appear
            wait = WebDriverWait(self.driver, timeout)
            
            # Try multiple possible selectors for search results
            selectors_to_try = [
                "div[class*='result']",
                "div[class*='property']",
                "div[class*='listing']",
                "div[class*='item']",
                "div[class*='card']",
                ".search-results",
                ".property-list",
                ".listing-container"
            ]
            
            for selector in selectors_to_try:
                try:
                    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                    logger.info(f"Search results loaded (detected with selector: {selector})")
                    time.sleep(2)  # Additional wait for content to stabilize
                    return True
                except TimeoutException:
                    continue
            
            # Fallback: wait for any content to load
            logger.warning("Specific selectors failed, waiting for general page load")
            time.sleep(5)  # Give page time to render
            return True
            
        except Exception as e:
            logger.error(f"Error waiting for search results: {e}")
            return False
    
    def extract_properties_from_search_page(self, page_url: str) -> List[PropertyData]:
        """Extract property data from search results page"""
        properties = []
        
        try:
            # Debug: Check page content
            page_source_length = len(self.driver.page_source)
            logger.info(f"Page source length: {page_source_length} characters")
            
            # Find all div elements to understand page structure
            all_divs = self.driver.find_elements(By.TAG_NAME, "div")
            logger.info(f"Found {len(all_divs)} div elements on page")
            
            # Try multiple approaches to find property elements
            property_elements = []
            
            # Approach 1: Look for specific property container patterns
            property_selectors = [
                "div[class*='property']",
                "div[class*='item']",
                "div[class*='result']",
                "div[class*='card']",
                "div[class*='listing']",
                ".property-item",
                ".search-item",
                ".result-item"
            ]
            
            for selector in property_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        logger.info(f"Found {len(elements)} elements with selector: {selector}")
                        property_elements = elements
                        break
                except Exception as e:
                    logger.debug(f"Selector {selector} failed: {e}")
            
            # Approach 2: Look for links to property detail pages (PRIORITIZED)
            if not property_elements:
                try:
                    detail_links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/karuizawa/detail/']")
                    if detail_links:
                        logger.info(f"Found {len(detail_links)} property detail links")
                        # Get parent containers of these links - LIMIT TO 10 for performance
                        property_elements = []
                        for link in detail_links[:10]:  # Limited to 10 properties for /runmocks compatibility
                            try:
                                parent = link.find_element(By.XPATH, "./..")
                                if parent not in property_elements:
                                    property_elements.append(parent)
                            except Exception as e:
                                logger.debug(f"Error getting parent for link: {e}")
                                continue
                        logger.info(f"Using {len(property_elements)} property containers from detail links")
                except Exception as e:
                    logger.debug(f"Detail link approach failed: {e}")
            
            # Approach 3: Look for elements containing price information
            if not property_elements:
                try:
                    # Find elements containing Japanese price patterns
                    page_text = self.driver.page_source
                    if '万円' in page_text or '億円' in page_text:
                        logger.info("Found price text on page, searching for containers")
                        # Use JavaScript to find elements containing price text
                        script = """
                        return Array.from(document.querySelectorAll('div')).filter(function(div) {
                            return div.textContent.includes('万円') || div.textContent.includes('億円');
                        });
                        """
                        price_elements = self.driver.execute_script(script)
                        if price_elements:
                            logger.info(f"Found {len(price_elements)} elements containing price text")
                            property_elements = price_elements[:20]  # Limit for processing
                except Exception as e:
                    logger.debug(f"Price text approach failed: {e}")
            
            # Extract data from found elements
            if property_elements:
                for i, element in enumerate(property_elements):
                    try:
                        property_data = self.extract_single_property_from_element(element, page_url, i+1)
                        if property_data and self.validate_property_data(property_data):
                            # Generate proper title using titleGenerator
                            property_dict = {
                                'title': property_data.title,
                                'price': property_data.price,
                                'location': property_data.location,
                                'property_type': property_data.property_type,
                                'building_age': property_data.building_age,
                                'source': 'Tokyu Resort'
                            }
                            property_data.title = generate_property_title(property_dict)
                            properties.append(property_data)
                            logger.info(f"Extracted property: {property_data.title[:60]}...")
                            
                    except Exception as e:
                        logger.error(f"Error extracting property {i+1}: {e}")
                        continue
            else:
                logger.warning("No property elements found on search page")
                
        except Exception as e:
            logger.error(f"Error extracting properties from search page: {e}")
        
        return properties
    
    def extract_single_property_from_element(self, element, page_url: str, index: int) -> Optional[PropertyData]:
        """Extract data from a single property element"""
        try:
            property_data = PropertyData()
            property_data.source_url = page_url
            
            # Get element text content
            try:
                element_text = element.text
                element_html = element.get_attribute('innerHTML')
            except Exception:
                element_text = ""
                element_html = ""
            
            # Extract property detail link
            try:
                detail_link = element.find_element(By.CSS_SELECTOR, "a[href*='/karuizawa/detail/']")
                detail_url = detail_link.get_attribute('href')
                if detail_url:
                    property_data.source_url = detail_url
            except NoSuchElementException:
                pass
            
            # Extract title
            try:
                title_selectors = ["h1", "h2", "h3", "h4", ".title", ".name", "a[href*='/detail/']"]
                for selector in title_selectors:
                    try:
                        title_elem = element.find_element(By.CSS_SELECTOR, selector)
                        if title_elem and title_elem.text.strip():
                            property_data.title = title_elem.text.strip()
                            break
                    except NoSuchElementException:
                        continue
            except Exception:
                pass
            
            # If no title found, create one
            if not property_data.title:
                property_data.title = f"Tokyu Resort Property {index}"
                # Try to extract from text content
                lines = [line.strip() for line in element_text.split('\n') if line.strip()]
                for line in lines[:3]:
                    if len(line) > 10 and not any(skip in line.lower() for skip in ['price', '円', '¥', 'contact']):
                        property_data.title = line[:100]
                        break
            
            # Extract price
            price_patterns = [
                r'([0-9,]+)億([0-9,]+)万円',  # X億Y万円 format
                r'([0-9,]+)億円',             # X億円 format  
                r'([0-9,]+)万円',             # X万円 format
                r'¥([0-9,]+)',                # ¥X format
                r'([0-9,]+)円'                # X円 format
            ]
            
            for pattern in price_patterns:
                price_match = re.search(pattern, element_text)
                if price_match:
                    property_data.price = price_match.group(0)
                    break
            
            if not property_data.price:
                property_data.price = "お問い合わせください"
            
            # Extract location - look for Karuizawa area references
            location_keywords = ['軽井沢', 'karuizawa', '中軽井沢', '南軽井沢', '旧軽井沢', '北軽井沢']
            for line in element_text.split('\n'):
                line_clean = line.strip()
                if line_clean and any(keyword in line_clean.lower() for keyword in location_keywords):
                    property_data.location = line_clean[:100]
                    break
            
            if not property_data.location:
                property_data.location = "Tokyu Resort Karuizawa"
            
            # Extract property type
            if any(keyword in element_text.lower() for keyword in ['villa', 'ヴィラ', 'ビラ']):
                property_data.property_type = 'Villa'
            elif any(keyword in element_text.lower() for keyword in ['house', '一戸建て', 'ハウス']):
                property_data.property_type = 'House'
            elif any(keyword in element_text.lower() for keyword in ['townhouse', 'タウンハウス']):
                property_data.property_type = 'Townhouse'
            else:
                property_data.property_type = 'Resort Property'
            
            # Extract room information
            room_patterns = [
                r'([0-9]+)LDK',
                r'([0-9]+)SDK', 
                r'([0-9]+)DK'
            ]
            
            for pattern in room_patterns:
                room_match = re.search(pattern, element_text)
                if room_match:
                    property_data.rooms = room_match.group(0)
                    break
            
            # Extract size information
            size_match = re.search(r'([0-9,]+\.?[0-9]*)(?:㎡|m²|平米)', element_text)
            if size_match:
                property_data.size_info = size_match.group(0)
            
            # Extract building age
            age_patterns = [
                r'築([0-9]+)年',
                r'新築',
                r'([0-9]{4})年建築',
                r'平成([0-9]+)年',
                r'令和([0-9]+)年'
            ]
            
            for pattern in age_patterns:
                age_match = re.search(pattern, element_text)
                if age_match:
                    property_data.building_age = age_match.group(0)
                    break
            
            # Extract images
            try:
                img_elements = element.find_elements(By.TAG_NAME, "img")
                img_urls = []
                for img in img_elements:
                    src = img.get_attribute('src') or img.get_attribute('data-src')
                    if src and src.startswith('http'):
                        img_urls.append(src)
                
                property_data.image_urls = self.filter_property_images(img_urls)
            except Exception:
                property_data.image_urls = []
            
            # Create description
            meaningful_lines = []
            for line in element_text.split('\n'):
                line_clean = line.strip()
                if (line_clean and len(line_clean) > 20 and len(line_clean) < 200 and
                    not any(skip in line_clean for skip in [property_data.title, property_data.price])):
                    meaningful_lines.append(line_clean)
                if len(meaningful_lines) >= 2:
                    break
            
            if meaningful_lines:
                property_data.description = ' '.join(meaningful_lines)[:500]
            else:
                property_data.description = f"東急リゾートの軽井沢{property_data.property_type}。リゾートコミュニティでの上質な別荘ライフ。"
            
            return property_data
            
        except Exception as e:
            logger.error(f"Error extracting property data from element: {e}")
            return None
    
    def validate_property_data(self, data: PropertyData) -> bool:
        """Validate property data against business rules"""
        try:
            if not data.is_valid():
                logger.warning(f"Property missing required fields: {data.title}")
                return False
            
            if not data.contains_karuizawa():
                logger.warning(f"Property not related to Karuizawa: {data.title}")
                return False
            
            return True
        except Exception as e:
            logger.error(f"Error validating property data: {e}")
            return False
    
    def deduplicate_properties(self, properties: List[PropertyData]) -> List[PropertyData]:
        """Remove duplicate properties based on title and source URL"""
        seen = set()
        unique_properties = []
        
        for prop in properties:
            # Create a key for deduplication
            key = f"{prop.title.lower()}-{prop.source_url}"
            if key not in seen:
                seen.add(key)
                unique_properties.append(prop)
            else:
                logger.debug(f"Duplicate property filtered: {prop.title}")
        
        return unique_properties
    
    def filter_property_images(self, img_urls: List[str]) -> List[str]:
        """Filter image URLs to prioritize property photos over UI elements"""
        if not img_urls:
            return []
        
        property_images = []
        ui_images = []
        
        for img_url in img_urls:
            # Skip obvious UI elements
            if any(skip in img_url.lower() for skip in [
                'logo', 'icon', 'btn_', 'button', 'nav_', 'menu_', 'header', 'footer',
                'arrow', 'bullet', 'spacer', 'line', 'bg_', 'background', 'banner'
            ]):
                continue
            
            # Prioritize property-related images
            if any(priority in img_url.lower() for priority in [
                'property', 'house', 'home', 'villa', 'building', 'exterior', 'interior',
                'photo', 'image', 'gallery', 'main', 'view', 'room'
            ]):
                property_images.append(img_url)
            else:
                ui_images.append(img_url)
        
        # Combine: property photos first, then other images
        final_images = property_images + ui_images
        
        # Limit to 5 images total
        return final_images[:5]