"""
Resort Home Karuizawa property scraper
Focuses on Karuizawa-specific real estate listings
"""
import re
import time
from typing import List, Optional
from urllib.parse import urljoin, urlparse
import logging

from .base_scraper import SimpleScraper, PropertyData
from utils.titleGenerator import generate_property_title

logger = logging.getLogger(__name__)

class ResortHomeScraper(SimpleScraper):
    """Scraper for Resort Home Karuizawa properties"""
    
    def __init__(self, config: dict = None):
        default_config = {
            'base_url': 'https://www.resort-home.jp',
            'rate_limit': 0.33,  # 1 request every 3 seconds
            'name': 'Resort Home Karuizawa'
        }
        
        if config:
            default_config.update(config)
            
        super().__init__(default_config)
        
    def scrape_listings(self) -> List[PropertyData]:
        """Main method to scrape Resort Home property listings"""
        logger.info("Starting Resort Home Karuizawa property scraping")
        
        all_properties = []
        
        # Try multiple search approaches based on actual site structure
        search_urls = [
            # Area-based searches (6 Karuizawa areas)
            '/bsearch/area01/',  # Old Karuizawa Area
            '/bsearch/area02/',  # Minami-Gaoka/Minamihara Area  
            '/bsearch/area03/',  # Central Karuizawa North
            '/bsearch/area04/',  # Central Karuizawa South
            '/bsearch/area05/',  # South Karuizawa
            '/bsearch/area06/',  # Oiwake Area
            # Price range searches
            '/bsearch/price01/', # Up to ¥20 million
            '/bsearch/price02/', # ¥20-30 million  
            '/bsearch/price03/', # ¥30-40 million
            '/bsearch/price04/', # ¥40-50 million
            '/bsearch/price05/', # ¥50-100 million
            '/bsearch/price06/', # Over ¥100 million
            # Company-owned properties
            '/bsearch/own/',
            # Map search (might have listings)
            '/bsearch/map/'
        ]
        
        for url_path in search_urls:
            full_url = urljoin(self.base_url, url_path)
            try:
                logger.info(f"Scraping Resort Home from: {full_url}")
                properties = self.scrape_properties_from_page(full_url)
                if properties:
                    logger.info(f"Found {len(properties)} properties from {url_path}")
                    all_properties.extend(properties)
                else:
                    logger.debug(f"No properties found on {url_path}")
                    
                # Rate limiting  
                time.sleep(1.0 / self.config.get('rate_limit', 0.33))
                
            except Exception as e:
                logger.warning(f"Error scraping {full_url}: {e}")
                continue
        
        # Remove duplicates and validate
        unique_properties = self.deduplicate_properties(all_properties)
        validated_properties = [prop for prop in unique_properties if self.validate_property_data(prop)]
        
        logger.info(f"Resort Home: {len(validated_properties)} unique properties found")
        return validated_properties
    
    def scrape_properties_from_page(self, url: str) -> List[PropertyData]:
        """Extract properties from a single page"""
        properties = []
        
        try:
            response = self.session.get(url, timeout=30)
            if response.status_code != 200:
                logger.warning(f"Could not load page: {url} (status: {response.status_code})")
                return properties
            
            # Set proper encoding for Japanese content
            response.encoding = response.apparent_encoding or 'utf-8'
            
            soup = self.get_soup(response.text)
            if not soup:
                return properties
            
            # Look for property containers with various selectors
            property_selectors = [
                '.property-item',
                '.listing-item', 
                '.property-card',
                '.property',
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
            
            # If no specific containers found, look for links to property details
            if not property_elements:
                # Look for links with specific Resort Home detail pattern
                detail_links = soup.find_all('a', href=re.compile(r'/bsearch/detail/\d+-\d+\.html'))
                if detail_links:
                    logger.info(f"Found {len(detail_links)} potential property detail links")
                    # Get parent containers of these links
                    for link in detail_links[:20]:  # Limit to prevent overload
                        parent = link.find_parent(['div', 'article', 'section'])
                        if parent and parent not in property_elements:
                            property_elements.append(parent)
            
            # Extract data from found elements
            if property_elements:
                for element in property_elements:
                    try:
                        property_data = self.extract_property_from_element(element, url)
                        if property_data and self.validate_property_data(property_data):
                            properties.append(property_data)
                    except Exception as e:
                        logger.debug(f"Error extracting property: {e}")
                        continue
            else:
                # Fallback: look for any elements containing price information
                price_elements = soup.find_all(string=re.compile(r'[0-9,]+万円'))
                if price_elements:
                    logger.info(f"Found {len(price_elements)} price mentions on page")
                    # Try to extract properties from price context
                    for price_text in price_elements[:10]:  # Limit processing
                        try:
                            parent = price_text.parent.find_parent(['div', 'article', 'section'])
                            if parent:
                                property_data = self.extract_property_from_element(parent, url)
                                if property_data and self.validate_property_data(property_data):
                                    properties.append(property_data)
                        except Exception as e:
                            logger.debug(f"Error extracting from price context: {e}")
                            continue
                            
        except Exception as e:
            logger.error(f"Error scraping page {url}: {e}")
        
        return properties
    
    def extract_property_from_element(self, element, page_url: str) -> Optional[PropertyData]:
        """Extract property data from a single element"""
        try:
            property_data = PropertyData()
            property_data.source_url = page_url
            
            # Get text content for analysis
            element_text = element.get_text() if hasattr(element, 'get_text') else str(element)
            
            # Extract property detail link with Resort Home pattern
            detail_link = element.find('a', href=re.compile(r'/bsearch/detail/\d+-\d+\.html'))
            if detail_link and detail_link.get('href'):
                detail_url = urljoin(self.base_url, detail_link.get('href'))
                property_data.source_url = detail_url
            
            # Extract title
            title_selectors = ['h1', 'h2', 'h3', '.title', '.name', 'a']
            for selector in title_selectors:
                title_elem = element.select_one(selector)
                if title_elem and title_elem.get_text(strip=True):
                    property_data.title = title_elem.get_text(strip=True)[:150]
                    break
            
            # If no title found, create one
            if not property_data.title:
                lines = [line.strip() for line in element_text.split('\n') if line.strip()]
                for line in lines[:3]:
                    if len(line) > 10 and not any(skip in line.lower() for skip in ['price', '円', '¥', 'contact']):
                        property_data.title = line[:100]
                        break
                
                if not property_data.title:
                    property_data.title = "Resort Home Property"
            
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
            location_keywords = [
                '軽井沢', 'karuizawa', '中軽井沢', '南軽井沢', '旧軽井沢', '北軽井沢',
                '南ヶ丘', '追分', '発地', '借宿', '塩沢'
            ]
            
            for line in element_text.split('\n'):
                line_clean = line.strip()
                if line_clean:
                    for keyword in location_keywords:
                        if keyword in line_clean.lower():
                            property_data.location = line_clean[:100]
                            break
                    if property_data.location:
                        break
            
            if not property_data.location:
                property_data.location = "Resort Home Karuizawa"
            
            # Extract property type
            if any(keyword in element_text.lower() for keyword in ['villa', 'ヴィラ', 'ビラ', '別荘']):
                property_data.property_type = 'Villa'
            elif any(keyword in element_text.lower() for keyword in ['house', '一戸建て', 'ハウス']):
                property_data.property_type = 'House'
            elif any(keyword in element_text.lower() for keyword in ['land', '土地', 'lot']):
                property_data.property_type = 'Land'
            elif any(keyword in element_text.lower() for keyword in ['apartment', 'マンション']):
                property_data.property_type = 'Apartment'
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
            size_match = re.search(r'([0-9,]+\.?[0-9]*)(?:㎡|m²|平米|坪)', element_text)
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
            img_elements = element.find_all('img')
            img_urls = []
            for img in img_elements:
                src = img.get('src') or img.get('data-src')
                if src:
                    full_img_url = urljoin(self.base_url, src)
                    if self.is_property_image(full_img_url):
                        img_urls.append(full_img_url)
            
            property_data.image_urls = img_urls[:5]  # Limit to 5 images
            
            # Create description
            meaningful_lines = []
            for line in element_text.split('\n'):
                line_clean = line.strip()
                if (line_clean and len(line_clean) > 15 and len(line_clean) < 200 and
                    not any(skip in line_clean for skip in [property_data.title or '', property_data.price])):
                    meaningful_lines.append(line_clean)
                if len(meaningful_lines) >= 2:
                    break
            
            if meaningful_lines:
                property_data.description = ' '.join(meaningful_lines)[:500]
            else:
                property_data.description = f"Resort Homeの軽井沢{property_data.property_type}。リゾートライフをお楽しみください。"
            
            # Generate consistent title using titleGenerator
            title_data = {
                'source': 'Resort Home',
                'property_type': property_data.property_type,
                'building_age': property_data.building_age or '不明',
                'price': property_data.price,
                'location': property_data.location
            }
            property_data.title = generate_property_title(title_data)
            
            return property_data
            
        except Exception as e:
            logger.error(f"Error extracting property data: {e}")
            return None
    
    def is_property_image(self, img_url: str) -> bool:
        """Check if image URL is likely a property photo"""
        skip_keywords = [
            'logo', 'icon', 'btn_', 'button', 'nav_', 'menu_', 'header', 'footer',
            'arrow', 'bullet', 'spacer', 'line', 'bg_', 'background', 'banner'
        ]
        
        img_url_lower = img_url.lower()
        return not any(keyword in img_url_lower for keyword in skip_keywords)
    
    def validate_property_data(self, property_data: PropertyData) -> bool:
        """Validate Resort Home property data"""
        try:
            # Basic validation
            if not property_data.is_valid():
                return False
            
            # Must be Karuizawa-related
            if not property_data.contains_karuizawa():
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