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
            'wait_timeout': 15,
            'page_load_timeout': 30
        }
        
        if config:
            default_config.update(config)
            
        super().__init__(default_config)
        self.karuizawa_url = self.base_url + '/karuizawa/'
        
    def scrape_listings(self) -> List[PropertyData]:
        """Main scraping method for Royal Resort Karuizawa properties"""
        logger.info("Starting Royal Resort Karuizawa property scraping")
        
        if not self.navigate_to_page(self.karuizawa_url):
            logger.error("Failed to navigate to Karuizawa page")
            return []
            
        # Handle any initial popups
        self.handle_popup_if_present()
        
        # Wait for page to fully load
        self.simulate_human_delay(3.0, 5.0)
        
        # Find property containers
        properties = self.find_property_listings()
        
        logger.info(f"Found {len(properties)} properties on Royal Resort")
        
        extracted_properties = []
        
        for i, property_element in enumerate(properties, 1):
            logger.info(f"Processing property {i}/{len(properties)}")
            
            try:
                # Extract basic data from the listing card
                property_data = self.extract_property_from_listing(property_element)
                
                if property_data:
                    # Validate the property data
                    if self.validate_property_data(property_data):
                        extracted_properties.append(property_data)
                        logger.info(f"Successfully extracted property {i}")
                    else:
                        logger.warning(f"Property {i} failed validation")
                else:
                    logger.warning(f"No data extracted for property {i}")
                    
                # Rate limiting between properties
                self.simulate_human_delay(2.0, 4.0)
                
            except Exception as e:
                logger.error(f"Error processing property {i}: {e}")
                continue
                
        logger.info(f"Successfully extracted {len(extracted_properties)} valid properties")
        return extracted_properties
        
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
            elements = self.wait_for_elements(By.CSS_SELECTOR, selector, timeout=5)
            if elements:
                logger.info(f"Found {len(elements)} property elements with selector: {selector}")
                return elements
                
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
        """Extract property data from a listing element"""
        try:
            property_data = PropertyData()
            
            # Extract title
            title = self.extract_title(element)
            if title:
                property_data.title = title
                
            # Extract price
            price = self.extract_price(element)
            if price:
                property_data.price = price
                
            # Extract location/area information
            location = self.extract_location(element)
            if location:
                property_data.location = location
                
            # Extract property type if available
            prop_type = self.extract_property_type(element)
            if prop_type:
                property_data.property_type = prop_type
                
            # Extract size information
            size_info = self.extract_size_info(element)
            if size_info:
                property_data.size_info = size_info
                
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
                    property_data.update_from_dict(detailed_data)
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
                        
                    # Filter out tiny images (likely icons)
                    if not any(skip in img_url.lower() for skip in ['icon', 'logo', 'button', 'arrow']):
                        images.append(img_url)
                        
        except Exception as e:
            logger.debug(f"Error extracting images: {e}")
            
        return images[:5]  # Limit to 5 images
        
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