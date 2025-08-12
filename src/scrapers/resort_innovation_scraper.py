"""
Resort Innovation property scraper for Karuizawa real estate
"""
import re
from typing import List, Optional, Dict, Any
from urllib.parse import urljoin
import logging
from .base_scraper import SimpleScraper, PropertyData
from utils.titleGenerator import generate_property_title

logger = logging.getLogger(__name__)

class ResortInnovationScraper(SimpleScraper):
    """Scraper for Resort Innovation properties"""
    
    def __init__(self, config: dict = None):
        if config is None:
            config = {
                'base_url': 'https://www.resortinnovation.com',
                'rate_limit': 0.25,  # 1 request every 4 seconds (conservative)
                'name': 'Resort Innovation'
            }
        else:
            # Ensure we have the base URL if not provided
            if 'base_url' not in config:
                config['base_url'] = 'https://www.resortinnovation.com'
            
            # Handle rate limit config format compatibility
            if 'rate_limit' in config and isinstance(config['rate_limit'], dict):
                # Extract requests_per_second from dict format
                config['rate_limit'] = config['rate_limit']['requests_per_second']
                
        super().__init__(config)
        
    def scrape_listings(self) -> List[PropertyData]:
        """Main method to scrape property listings"""
        all_properties = []
        
        # Target URLs for Resort Innovation properties
        target_urls = [
            '/for-sale.html',  # Main for-sale page
            '/properties.html',  # Alternative properties page
            '/listings.html'  # Alternative listings page
        ]
        
        for url_path in target_urls:
            try:
                full_url = urljoin(self.base_url, url_path)
                logger.info(f"Scraping Resort Innovation from: {full_url}")
                
                soup = self.get_soup(full_url)
                if not soup:
                    logger.warning(f"Could not load page: {full_url}")
                    continue
                    
                # Extract properties from this page
                properties = self.extract_properties_from_page(soup, full_url)
                logger.info(f"Found {len(properties)} properties on {url_path}")
                all_properties.extend(properties)
                
                # Look for pagination or additional property pages
                additional_pages = self.find_additional_pages(soup, full_url)
                for page_url in additional_pages:
                    page_soup = self.get_soup(page_url)
                    if page_soup:
                        page_properties = self.extract_properties_from_page(page_soup, page_url)
                        logger.info(f"Found {len(page_properties)} properties on additional page")
                        all_properties.extend(page_properties)
                        
            except Exception as e:
                logger.error(f"Error scraping {url_path}: {e}")
                continue
        
        # Remove duplicates and validate
        unique_properties = self.deduplicate_properties(all_properties)
        logger.info(f"Resort Innovation: {len(unique_properties)} unique properties found")
        
        return unique_properties
    
    def extract_properties_from_page(self, soup, page_url: str) -> List[PropertyData]:
        """Extract property data from a page"""
        properties = []
        
        # Look for property containers with various possible class names
        property_selectors = [
            '.property-item',
            '.listing-item', 
            '.property-card',
            '.property',
            '.listing',
            '.item',
            '[class*="property"]',
            '[class*="listing"]',
            '[class*="item"]'
        ]
        
        property_elements = []
        for selector in property_selectors:
            elements = soup.select(selector)
            if elements:
                logger.info(f"Found {len(elements)} elements with selector: {selector}")
                property_elements = elements
                break
        
        # If no specific property containers found, look for any structured content
        if not property_elements:
            # Look for divs or articles that might contain property information
            potential_elements = soup.find_all(['div', 'article', 'section'], 
                                             class_=lambda x: x and any(
                                                 keyword in x.lower() for keyword in 
                                                 ['property', 'listing', 'item', 'card', 'result', 'estate', 'home']
                                             ))
            
            if potential_elements:
                logger.info(f"Found {len(potential_elements)} potential property elements")
                property_elements = potential_elements[:20]  # Limit to reasonable number
        
        # Extract data from each element
        for i, element in enumerate(property_elements):
            try:
                property_data = self.extract_single_property(element, page_url, i+1)
                if property_data and self.validate_property_data(property_data):
                    # Generate proper title using titleGenerator
                    property_dict = {
                        'title': property_data.title,
                        'price': property_data.price,
                        'location': property_data.location,
                        'property_type': property_data.property_type,
                        'building_age': property_data.building_age,
                        'source': 'Resort Innovation'
                    }
                    property_data.title = generate_property_title(property_dict)
                    properties.append(property_data)
                    logger.info(f"Extracted property: {property_data.title[:60]}...")
                    
            except Exception as e:
                logger.error(f"Error extracting property {i+1} from {page_url}: {e}")
                continue
        
        return properties
    
    def extract_single_property(self, element, page_url: str, index: int) -> Optional[PropertyData]:
        """Extract data from a single property element"""
        try:
            property_data = PropertyData()
            property_data.source_url = page_url
            
            # Extract title/name
            title_selectors = ['h1', 'h2', 'h3', 'h4', '.title', '.name', '.property-title', '.property-name']
            for selector in title_selectors:
                title_elem = element.select_one(selector)
                if title_elem and title_elem.get_text(strip=True):
                    property_data.title = title_elem.get_text(strip=True)
                    break
            
            # If no title found, create one from available text
            if not property_data.title:
                text_content = element.get_text(strip=True)
                lines = [line.strip() for line in text_content.split('\n') if line.strip()]
                if lines:
                    property_data.title = f"Resort Innovation Property {index}"
                    # Try to find a meaningful first line
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
            
            element_text = element.get_text()
            for pattern in price_patterns:
                price_match = re.search(pattern, element_text)
                if price_match:
                    property_data.price = price_match.group(0)
                    break
            
            # If no price pattern found, look for price-related text
            if not property_data.price:
                price_keywords = ['価格', 'price', '円', '¥', 'yen']
                for line in element_text.split('\n'):
                    if any(keyword in line.lower() for keyword in price_keywords):
                        # Clean up the line and use as price
                        clean_line = line.strip()
                        if clean_line and len(clean_line) < 100:
                            property_data.price = clean_line
                            break
                
                # Default price if none found
                if not property_data.price:
                    property_data.price = "お問い合わせください"
            
            # Extract location
            location_keywords = ['軽井沢', 'karuizawa', '所在地', 'location', '住所', 'address']
            element_text_lower = element_text.lower()
            
            for line in element_text.split('\n'):
                line_clean = line.strip()
                if line_clean and any(keyword in line_clean.lower() for keyword in location_keywords):
                    property_data.location = line_clean[:100]
                    break
            
            # Default location if not found
            if not property_data.location:
                property_data.location = "Karuizawa Resort Area"
            
            # Extract property type
            type_keywords = {
                'villa': 'Villa',
                'house': 'House', 
                'home': 'Home',
                'land': 'Land',
                'plot': 'Land',
                'apartment': 'Apartment',
                'condo': 'Condominium',
                'resort': 'Resort Property'
            }
            
            for keyword, prop_type in type_keywords.items():
                if keyword in element_text.lower():
                    property_data.property_type = prop_type
                    break
            
            if not property_data.property_type:
                property_data.property_type = "Resort Property"
            
            # Extract images
            img_elements = element.find_all('img')
            img_urls = []
            for img in img_elements:
                src = img.get('src') or img.get('data-src')
                if src:
                    # Convert relative URLs to absolute
                    if src.startswith('/'):
                        src = urljoin(self.base_url, src)
                    elif src.startswith('http'):
                        pass  # Already absolute
                    else:
                        src = urljoin(page_url, src)
                    img_urls.append(src)
            
            # Filter and clean image URLs
            property_data.image_urls = self.filter_property_images(img_urls)
            
            # Extract additional info
            size_match = re.search(r'([0-9,]+)(?:㎡|m²|平米|坪)', element_text)
            if size_match:
                property_data.size_info = size_match.group(0)
            
            # Look for building age
            age_patterns = [
                r'築([0-9]+)年',  # 築X年
                r'建築.*?([0-9]+)年',  # 建築...X年
                r'新築',  # New construction
                r'平成([0-9]+)年',  # Heisei era
                r'令和([0-9]+)年'   # Reiwa era
            ]
            
            for pattern in age_patterns:
                age_match = re.search(pattern, element_text)
                if age_match:
                    property_data.building_age = age_match.group(0)
                    break
            
            # Extract description (first few meaningful lines)
            meaningful_lines = []
            for line in element_text.split('\n'):
                line_clean = line.strip()
                if (line_clean and len(line_clean) > 20 and len(line_clean) < 200 and
                    not any(skip in line_clean for skip in [property_data.title, property_data.price])):
                    meaningful_lines.append(line_clean)
                if len(meaningful_lines) >= 3:
                    break
            
            if meaningful_lines:
                property_data.description = ' '.join(meaningful_lines)[:500]
            
            return property_data
            
        except Exception as e:
            logger.error(f"Error extracting property data: {e}")
            return None
    
    def find_additional_pages(self, soup, current_url: str) -> List[str]:
        """Find additional pages with property listings"""
        additional_urls = []
        
        try:
            # Look for pagination links
            pagination_selectors = [
                'a[href*="page"]',
                'a[href*="p="]', 
                '.pagination a',
                '.pager a',
                'a[class*="next"]',
                'a[class*="more"]'
            ]
            
            for selector in pagination_selectors:
                links = soup.select(selector)
                for link in links:
                    href = link.get('href')
                    if href:
                        if href.startswith('/'):
                            url = urljoin(self.base_url, href)
                        elif href.startswith('http'):
                            url = href
                        else:
                            url = urljoin(current_url, href)
                        
                        # Avoid infinite loops
                        if url != current_url and url not in additional_urls:
                            additional_urls.append(url)
                
                # Limit to prevent excessive crawling
                if len(additional_urls) >= 5:
                    break
        
        except Exception as e:
            logger.error(f"Error finding additional pages: {e}")
        
        return additional_urls
    
    def deduplicate_properties(self, properties: List[PropertyData]) -> List[PropertyData]:
        """Remove duplicate properties based on title and price"""
        seen = set()
        unique_properties = []
        
        for prop in properties:
            # Create a simple key for deduplication
            key = f"{prop.title.lower()}-{prop.price}-{prop.location.lower()}"
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
                'arrow', 'bullet', 'spacer', 'line', 'bg_', 'background'
            ]):
                continue
            
            # Prioritize property-related images
            if any(priority in img_url.lower() for priority in [
                'property', 'house', 'home', 'villa', 'building', 'exterior', 'interior',
                'photo', 'image', 'gallery', 'main', 'view'
            ]):
                property_images.append(img_url)
            else:
                ui_images.append(img_url)
        
        # Combine: property photos first, then other images
        final_images = property_images + ui_images
        
        # Limit to 5 images total
        return final_images[:5]