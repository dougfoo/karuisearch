"""
Royal Resort Karuizawa scraper - JavaScript-heavy luxury property site
"""
import time
import re
from typing import List, Optional
from urllib.parse import urljoin, urlparse
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging

from .browser_scraper import BrowserScraper
from .base_scraper import PropertyData

logger = logging.getLogger(__name__)

class RoyalResortScraper(BrowserScraper):
    """Scraper for Royal Resort Karuizawa - luxury property site with dynamic content"""
    
    def __init__(self, config: dict = None):
        default_config = {
            'base_url': 'https://www.royal-resort.co.jp',
            'headless': True,
            'wait_timeout': 30,      # Increased from 15s to 30s
            'page_load_timeout': 60  # Increased from 30s to 60s
        }
        
        if config:
            default_config.update(config)
            
        super().__init__(default_config)
        self.karuizawa_url = self.base_url + '/karuizawa/'
        
    def scrape_listings(self) -> List[PropertyData]:
        """Main scraping method for Royal Resort Karuizawa properties"""
        logger.info("Starting Royal Resort Karuizawa property scraping")
        
        # Setup browser first
        if not self.setup_browser():
            logger.error("Failed to setup browser")
            return []
        
        # Navigate with retry logic
        max_retries = 2
        navigation_success = False
        
        for attempt in range(max_retries + 1):
            if attempt > 0:
                logger.info(f"Retrying navigation (attempt {attempt + 1}/{max_retries + 1})")
                time.sleep(5)  # Wait before retry
                
            if self.navigate_to_page(self.karuizawa_url):
                navigation_success = True
                break
            else:
                logger.warning(f"Navigation attempt {attempt + 1} failed")
        
        if not navigation_success:
            logger.error(f"Failed to navigate to Karuizawa page after {max_retries + 1} attempts")
            self.close_browser()
            return []
            
        # Handle any initial popups
        self.handle_popup_if_present()
        
        # Wait for page to fully load with extended timeout
        logger.info("Waiting for page to fully load...")
        self.simulate_human_delay(5.0, 8.0)  # Increased from 3-5s to 5-8s
        
        # Try to wait for specific content to load
        try:
            # Wait for main content area to be present
            self.wait_for_element(By.TAG_NAME, "main", timeout=20)
            logger.info("Main content area loaded successfully")
        except Exception as e:
            logger.warning(f"Main content area not found: {e}")
        
        # Find property containers with retry logic
        properties = self.find_property_listings_with_retry()
        
        logger.info(f"Found {len(properties)} properties on Royal Resort")
        
        extracted_properties = []
        
        # Limit processing for testing - process only first 3 properties to avoid timeouts
        max_properties_to_process = min(len(properties), 3)
        logger.info(f"Processing first {max_properties_to_process} properties (limited for stability)")
        
        for i, property_element in enumerate(properties[:max_properties_to_process], 1):
            logger.info(f"Processing property {i}/{max_properties_to_process}")
            
            try:
                # PHASE 1.2: Extract with crash recovery
                property_data = self.safe_execute_with_recovery(
                    self.extract_property_from_listing, 
                    property_element,
                    max_retries=1
                )
                
                if property_data:
                    # Generate proper title using title generator
                    if hasattr(property_data, 'price') and (property_data.price or property_data.location or property_data.property_type):
                        from utils.titleGenerator import generate_property_title
                        property_dict = {
                            'source_url': property_data.source_url,
                            'property_type': property_data.property_type,
                            'building_age': property_data.building_age,
                            'price': property_data.price,
                            'location': property_data.location
                        }
                        property_data.title = generate_property_title(property_dict)
                    
                    # Validate the property data
                    if self.validate_property_data(property_data):
                        extracted_properties.append(property_data)
                        logger.info(f"Successfully extracted property {i}: {property_data.title}")
                    else:
                        logger.warning(f"Property {i} failed validation")
                else:
                    logger.warning(f"No data extracted for property {i}")
                    
                # Rate limiting between properties - reduced delay for testing
                self.simulate_human_delay(1.0, 2.0)  # Reduced for faster testing
                
            except Exception as e:
                logger.error(f"Error processing property {i}: {e}")
                continue
                
        logger.info(f"Successfully extracted {len(extracted_properties)} valid properties")
        
        # Clean up browser
        self.close_browser()
        
        return extracted_properties
    
    def find_property_listings_with_retry(self) -> List:
        """Find property listings with retry logic and better error handling"""
        max_attempts = 3
        
        for attempt in range(max_attempts):
            if attempt > 0:
                logger.info(f"Retrying property search (attempt {attempt + 1}/{max_attempts})")
                self.simulate_human_delay(2.0, 3.0)  # Wait between attempts
            
            try:
                properties = self.find_property_listings()
                if properties:
                    logger.info(f"Successfully found {len(properties)} properties on attempt {attempt + 1}")
                    return properties
                else:
                    logger.warning(f"No properties found on attempt {attempt + 1}")
            except Exception as e:
                logger.error(f"Error finding properties on attempt {attempt + 1}: {e}")
        
        logger.error(f"Failed to find properties after {max_attempts} attempts")
        return []
        
    def find_property_listings(self) -> List:
        """Find property listing elements on the page"""
        # Try various selectors for property listings
        selectors_to_try = [
            ".property-list .property-item",
            ".p-card",
            ".property-card", 
            ".listing-item",
            ".bukken-item",
            "[class*='property']",
            "[class*='listing']",
            ".card",
            ".item"
        ]
        
        for selector in selectors_to_try:
            logger.debug(f"Trying selector: {selector}")
            elements = self.wait_for_elements(By.CSS_SELECTOR, selector, timeout=10)  # Increased from 5s to 10s
            if elements:
                logger.info(f"Found {len(elements)} property elements with selector: {selector}")
                # Additional validation - ensure elements are actually visible/loaded
                valid_elements = []
                for elem in elements:
                    try:
                        if elem.is_displayed() and elem.size['height'] > 0:
                            valid_elements.append(elem)
                    except:
                        continue
                
                if valid_elements:
                    logger.info(f"Validated {len(valid_elements)}/{len(elements)} elements as visible")
                    return valid_elements
                else:
                    logger.warning(f"No valid/visible elements found with selector: {selector}")
                    continue
                
        # If no specific selectors work, try to find any clickable elements with property-like content
        logger.warning("No property elements found with standard selectors, trying broader search")
        
        # Look for elements containing price indicators
        price_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), '万円') or contains(text(), 'yen') or contains(text(), '¥')]")
        
        if price_elements:
            # Get parent containers that might be property cards
            property_containers = []
            for price_elem in price_elements:
                # Look for the closest parent that looks like a property container
                parent = price_elem.find_element(By.XPATH, "./ancestor::*[contains(@class, 'item') or contains(@class, 'card') or contains(@class, 'property')][1]")
                if parent and parent not in property_containers:
                    property_containers.append(parent)
                    
            logger.info(f"Found {len(property_containers)} potential property containers from price search")
            return property_containers[:20]  # Limit to prevent too many
            
        logger.warning("No property listings found")
        return []
        
    def extract_property_from_listing(self, element) -> Optional[PropertyData]:
        """Extract property data from a listing element - OPTIMIZED for crash prevention"""
        try:
            # PHASE 1.3: Pre-validate element before extraction
            if not element or not element.is_displayed():
                logger.warning("Element not valid or not displayed")
                return None
                
            property_data = PropertyData()
            
            # PHASE 1.3: Single-pass extraction to minimize DOM queries
            try:
                # Get all text content at once to reduce queries
                element_text = element.get_attribute('textContent') or element.text or ""
                element_html = element.get_attribute('outerHTML') or ""
                
                # Extract all data from cached content
                property_data.title = self.extract_title_optimized(element, element_text, element_html)
                property_data.price = self.extract_price_optimized(element, element_text, element_html)
                property_data.location = self.extract_location_optimized(element, element_text, element_html)
                property_data.property_type = self.extract_property_type_optimized(element, element_text, element_html)
                property_data.size_info = self.extract_size_info_optimized(element, element_text, element_html)
                
            except Exception as e:
                logger.warning(f"Error during optimized extraction, falling back to original: {e}")
                # Fallback to original methods if optimized fails
                property_data.title = self.extract_title(element)
                property_data.price = self.extract_price(element)
                property_data.location = self.extract_location(element)
                property_data.property_type = self.extract_property_type(element)
                property_data.size_info = self.extract_size_info(element)
                
            # Extract room information
            rooms = self.extract_rooms(element)
            if rooms:
                property_data.rooms = rooms
                
            # Extract images
            images = self.extract_images(element)
            if images:
                property_data.image_urls = images
                
            # Try to get detailed information by following link
            detail_url = self.extract_detail_url(element)
            if detail_url:
                property_data.source_url = detail_url
                
                # Optionally get more details from the detail page
                detailed_data = self.get_property_details(detail_url)
                if detailed_data:
                    # Update fields from detailed data
                    if 'building_age' in detailed_data:
                        property_data.building_age = detailed_data['building_age']
                    if 'description' in detailed_data:
                        property_data.description = detailed_data['description']
            else:
                # Use current page as source
                property_data.source_url = self.driver.current_url
                
            # Add timestamp
            property_data.scraped_at = time.time()
            
            return property_data
            
        except Exception as e:
            logger.error(f"Error extracting property data: {e}")
            return None
            
    def extract_title(self, element) -> str:
        """Extract property title"""
        title_selectors = [
            "h1", "h2", "h3", "h4",
            ".title", ".name", ".property-name",
            "[class*='title']", "[class*='name']",
            ".heading", ".property-title"
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
        
    def extract_price(self, element) -> str:
        """Extract property price"""
        price_selectors = [
            ".price", ".amount", ".cost", ".kakaku",
            "[class*='price']", "[class*='amount']", "[class*='cost']"
        ]
        
        # First try specific price selectors
        for selector in price_selectors:
            try:
                price_elem = element.find_element(By.CSS_SELECTOR, selector)
                price = self.extract_text_safely(price_elem)
                if price and ('万円' in price or 'yen' in price.lower() or '¥' in price):
                    return price.strip()
            except:
                continue
                
        # If no specific selectors work, search for text containing price indicators
        try:
            price_xpath = ".//text()[contains(., '万円') or contains(., 'yen') or contains(., '¥')]"
            price_elements = element.find_elements(By.XPATH, price_xpath)
            for price_elem in price_elements:
                price_text = self.extract_text_safely(price_elem)
                if price_text:
                    return price_text.strip()
        except:
            pass
            
        return ""
        
    def extract_location(self, element) -> str:
        """Extract property location"""
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
                
        # Look for Karuizawa-related text
        try:
            karuizawa_xpath = ".//text()[contains(., '軽井沢') or contains(., 'karuizawa') or contains(., 'Karuizawa')]"
            location_elements = element.find_elements(By.XPATH, karuizawa_xpath)
            for loc_elem in location_elements:
                location_text = self.extract_text_safely(loc_elem)
                if location_text:
                    return location_text.strip()
        except:
            pass
            
        return "軽井沢"  # Default to Karuizawa since this is the Karuizawa page
        
    def extract_property_type(self, element) -> str:
        """Extract property type"""
        type_selectors = [
            ".type", ".category", ".property-type",
            "[class*='type']", "[class*='category']"
        ]
        
        for selector in type_selectors:
            try:
                type_elem = element.find_element(By.CSS_SELECTOR, selector)
                prop_type = self.extract_text_safely(type_elem)
                if prop_type:
                    return prop_type.strip()
            except:
                continue
                
        # Look for common property type indicators
        text_content = self.extract_text_safely(element).lower()
        
        if '一戸建て' in text_content or 'house' in text_content:
            return '一戸建て'
        elif '土地' in text_content or 'land' in text_content:
            return '土地'
        elif 'マンション' in text_content or 'apartment' in text_content:
            return 'マンション'
        elif 'ヴィラ' in text_content or 'villa' in text_content:
            return 'ヴィラ'
            
        return "一戸建て"  # Default for luxury resort properties
        
    def extract_size_info(self, element) -> str:
        """Extract size information"""
        size_selectors = [
            ".size", ".area", ".menseki", ".tsubo",
            "[class*='size']", "[class*='area']", "[class*='menseki']"
        ]
        
        for selector in size_selectors:
            try:
                size_elem = element.find_element(By.CSS_SELECTOR, selector)
                size = self.extract_text_safely(size_elem)
                if size and ('㎡' in size or 'm²' in size or '坪' in size or 'sqm' in size.lower()):
                    return size.strip()
            except:
                continue
                
        # Look for size indicators in text
        text_content = self.extract_text_safely(element)
        size_patterns = [
            r'\d+[,.]?\d*\s*㎡',
            r'\d+[,.]?\d*\s*m²',
            r'\d+[,.]?\d*\s*坪',
            r'\d+[,.]?\d*\s*sqm'
        ]
        
        for pattern in size_patterns:
            matches = re.findall(pattern, text_content, re.IGNORECASE)
            if matches:
                return matches[0].strip()
                
        return ""
        
    def extract_rooms(self, element) -> str:
        """Extract room layout information"""
        room_selectors = [
            ".rooms", ".layout", ".madori",
            "[class*='room']", "[class*='layout']", "[class*='madori']"
        ]
        
        for selector in room_selectors:
            try:
                room_elem = element.find_element(By.CSS_SELECTOR, selector)
                rooms = self.extract_text_safely(room_elem)
                if rooms and ('LDK' in rooms or 'DK' in rooms or '部屋' in rooms):
                    return rooms.strip()
            except:
                continue
                
        # Look for room layout patterns
        text_content = self.extract_text_safely(element)
        room_patterns = [
            r'\d+[LS]?LDK',
            r'\d+[LS]?DK',
            r'\d+部屋',
            r'\d+bedroom'
        ]
        
        for pattern in room_patterns:
            matches = re.findall(pattern, text_content, re.IGNORECASE)
            if matches:
                return matches[0].strip()
                
        return ""
        
    def extract_images(self, element) -> List[str]:
        """Extract image URLs"""
        images = []
        
        try:
            img_elements = element.find_elements(By.TAG_NAME, "img")
            
            raw_images = []
            for img in img_elements:
                # Get src or data-src (for lazy loading)
                img_url = self.extract_attribute_safely(img, 'src')
                if not img_url:
                    img_url = self.extract_attribute_safely(img, 'data-src')
                    
                if img_url and img_url.startswith(('http', '//')):
                    # Convert relative URLs to absolute
                    if img_url.startswith('//'):
                        img_url = 'https:' + img_url
                    elif img_url.startswith('/'):
                        img_url = urljoin(self.base_url, img_url)
                        
                    raw_images.append(img_url)
            
            # Filter images using the helper method
            images = self.filter_property_images(raw_images)
                        
        except Exception as e:
            logger.debug(f"Error extracting images: {e}")
            
        return images[:5]  # Limit to 5 images
        
    def filter_property_images(self, img_urls: List[str]) -> List[str]:
        """Filter image URLs to exclude navigation and generic assets"""
        filtered_images = []
        
        exclude_keywords = ['btn_', 'nav_', 'menu_', 'common/', 'header', 'logo', 'icon', 'arrow', 'bullet']
        include_keywords = ['property', 'bukken', 'photo', 'image', 'gallery', 'main', 'villa', 'resort']
        
        for img_url in img_urls:
            # Skip if contains exclude keywords
            if any(keyword in img_url.lower() for keyword in exclude_keywords):
                continue
                
            # Prioritize if contains include keywords
            if any(keyword in img_url.lower() for keyword in include_keywords):
                filtered_images.insert(0, img_url)  # Add to front
            else:
                filtered_images.append(img_url)
        
        return filtered_images[:5]  # Limit to 5 images
        
    def extract_detail_url(self, element) -> str:
        """Extract link to property detail page"""
        try:
            # Look for multiple types of links with different selectors
            link_selectors = [
                'a[href*="property"]', 
                'a[href*="detail"]', 
                'a[href*="bukken"]',
                'a[href*="villa"]',
                'a[href*="estate"]',
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
        
        # Fallback to current page URL
        logger.debug("No valid detail URL found, using current page")
        return self.driver.current_url
        
    def get_property_details(self, detail_url: str) -> Optional[dict]:
        """Get additional details from property detail page"""
        try:
            logger.info(f"Fetching details from: {detail_url}")
            
            # Navigate to detail page
            if not self.navigate_to_page(detail_url):
                logger.warning(f"Could not navigate to detail page: {detail_url}")
                return None
                
            # Wait for page to load
            self.simulate_human_delay(2.0, 4.0)
            
            # Extract additional details
            details = {}
            
            # Look for building age
            building_age = self.extract_building_age_from_detail()
            if building_age:
                details['building_age'] = building_age
                
            # Look for more detailed description
            description = self.extract_description_from_detail()
            if description:
                details['description'] = description
                
            # Look for more detailed room information
            detailed_rooms = self.extract_detailed_rooms()
            if detailed_rooms:
                details['rooms'] = detailed_rooms
                
            return details
            
        except Exception as e:
            logger.warning(f"Error getting property details from {detail_url}: {e}")
            return None
            
    def extract_building_age_from_detail(self) -> str:
        """Extract building age from detail page"""
        age_keywords = ['築年', '建築年', '竣工', '完成', '新築', '年数']
        
        for keyword in age_keywords:
            try:
                xpath = f"//text()[contains(., '{keyword}')]"
                elements = self.driver.find_elements(By.XPATH, xpath)
                for elem in elements:
                    text = self.extract_text_safely(elem)
                    if text and keyword in text:
                        return text.strip()
            except:
                continue
                
        return ""
        
    def extract_description_from_detail(self) -> str:
        """Extract property description from detail page"""
        description_selectors = [
            ".description", ".detail", ".content", ".summary",
            "[class*='description']", "[class*='detail']", "[class*='content']"
        ]
        
        for selector in description_selectors:
            try:
                desc_elem = self.wait_for_element(By.CSS_SELECTOR, selector, timeout=3)
                if desc_elem:
                    description = self.extract_text_safely(desc_elem)
                    if description and len(description) > 50:
                        return description.strip()
            except:
                continue
                
        return ""
        
    def extract_detailed_rooms(self) -> str:
        """Extract detailed room information from detail page"""
        # Look for more specific room layouts on detail pages
        text_content = self.driver.page_source
        
        # Enhanced room pattern matching
        room_patterns = [
            r'\d+[LS]?LDK[\+\w]*',
            r'\d+[LS]?DK[\+\w]*',
            r'\d+階建て',
            r'\d+部屋[\d\w]*'
        ]
        
        for pattern in room_patterns:
            matches = re.findall(pattern, text_content, re.IGNORECASE)
            if matches:
                return matches[0].strip()
                
        return ""

    def is_valid_property_url(self, url: str) -> bool:
        """Validate if URL appears to be a property detail page"""
        if not url:
            return False
        
        # Skip javascript and anchor links
        if url.startswith(('javascript:', '#', 'mailto:')):
            return False
            
        # Check for property-related keywords in URL
        property_keywords = ['property', 'detail', 'bukken', 'listing', 'villa', 'estate', 'karuizawa']
        url_lower = url.lower()
        
        # Must contain at least one property keyword
        has_property_keyword = any(keyword in url_lower for keyword in property_keywords)
        
        # Should not be just the base domain
        is_not_base_url = url != self.base_url and not url.endswith('/')
        
        return has_property_keyword or is_not_base_url

    def validate_property_data(self, property_data: PropertyData) -> bool:
        """Validate Royal Resort property data"""
        try:
            # Basic validation from parent class
            if not super().validate_property_data(property_data):
                return False
                
            # Royal Resort specific validation
            # Must have minimum required fields
            if not all([property_data.title, property_data.price, property_data.location]):
                logger.debug("Missing required fields")
                return False
                
            # Price should be in reasonable range for luxury properties
            if property_data.price:
                # Extract numbers from price
                price_numbers = re.findall(r'[\d,]+', property_data.price)
                if price_numbers:
                    try:
                        # Handle Japanese 万円 format
                        price_value = float(price_numbers[0].replace(',', ''))
                        if '万円' in property_data.price:
                            price_value = price_value * 10000
                            
                        # Royal Resort should have luxury pricing (50M+ yen)
                        if price_value < 50000000:  # 50M yen minimum for luxury resort
                            logger.debug(f"Price too low for luxury resort: {price_value}")
                            return False
                            
                    except ValueError:
                        logger.debug("Could not parse price value")
                        return False
                        
            # Should be related to Karuizawa
            if not property_data.contains_karuizawa():
                logger.debug("Property not related to Karuizawa")
                return False
                
            logger.debug("Royal Resort property validation passed")
            return True
            
        except Exception as e:
            logger.error(f"Validation error: {e}")
            return False
    
    # PHASE 1.3: Optimized extraction methods to reduce DOM queries
    def extract_title_optimized(self, element, element_text: str, element_html: str) -> str:
        """Extract title using cached text content"""
        # Try to find title in text content first
        lines = element_text.split('\n')
        for line in lines[:3]:  # Check first 3 lines
            line = line.strip()
            if len(line) > 10 and len(line) < 100:  # Reasonable title length
                return line
        
        # Fallback to original method
        return self.extract_title(element)
    
    def extract_price_optimized(self, element, element_text: str, element_html: str) -> str:
        """Extract price using cached text content"""
        # Look for price patterns in text
        price_patterns = [
            r'\d+億[\d,]*万円',
            r'\d+億円',
            r'[\d,]+\s*万円',
            r'¥[\d,]+',
        ]
        
        for pattern in price_patterns:
            import re
            match = re.search(pattern, element_text)
            if match:
                return match.group().strip()
        
        # Fallback to original method
        return self.extract_price(element)
    
    def extract_location_optimized(self, element, element_text: str, element_html: str) -> str:
        """Extract location using cached text content"""
        # Look for Karuizawa-related text
        if '軽井沢' in element_text:
            lines = element_text.split('\n')
            for line in lines:
                if '軽井沢' in line and len(line.strip()) > 3:
                    return line.strip()[:100]  # Truncate if too long
        
        # Fallback to original method
        return self.extract_location(element)
    
    def extract_property_type_optimized(self, element, element_text: str, element_html: str) -> str:
        """Extract property type using cached text content"""
        property_types = ['別荘', 'ヴィラ', 'villa', '一戸建て', 'マンション', '土地']
        
        element_text_lower = element_text.lower()
        for prop_type in property_types:
            if prop_type in element_text or prop_type.lower() in element_text_lower:
                return prop_type
        
        # Fallback to original method
        return self.extract_property_type(element)
    
    def extract_size_info_optimized(self, element, element_text: str, element_html: str) -> str:
        """Extract size info using cached text content"""
        # Look for size patterns
        size_patterns = [
            r'\d+[\.\d]*\s*㎡',
            r'\d+[\.\d]*\s*平米',
            r'\d+[\.\d]*\s*坪',
        ]
        
        for pattern in size_patterns:
            import re
            match = re.search(pattern, element_text)
            if match:
                return match.group().strip()
        
        # Fallback to original method
        return self.extract_size_info(element)