"""
Tokyu Resort Karuizawa property scraper
"""
import re
from typing import List, Optional, Dict, Any
from urllib.parse import urljoin
import logging
from .base_scraper import SimpleScraper, PropertyData
from utils.titleGenerator import generate_property_title

logger = logging.getLogger(__name__)

class TokyuResortScraper(SimpleScraper):
    """Scraper for Tokyu Resort Karuizawa properties"""
    
    def __init__(self, config: dict = None):
        if config is None:
            config = {
                'base_url': 'https://www.tokyu-resort.co.jp',
                'rate_limit': 0.25,  # 1 request every 4 seconds (conservative)
                'name': 'Tokyu Resort Karuizawa'
            }
        else:
            # Ensure we have the base URL if not provided
            if 'base_url' not in config:
                config['base_url'] = 'https://www.tokyu-resort.co.jp'
            
            # Handle rate limit config format compatibility
            if 'rate_limit' in config and isinstance(config['rate_limit'], dict):
                # Extract requests_per_second from dict format
                config['rate_limit'] = config['rate_limit']['requests_per_second']
                
        super().__init__(config)
        
    def scrape_listings(self) -> List[PropertyData]:
        """Main method to scrape property listings"""
        all_properties = []
        
        # Target URLs for Tokyu Resort properties
        target_urls = [
            '/search/result?HPSRC_AREA_ID[57]=1&SHUBETSU_ID[2]=1&area_top_flg=1&link_id=11villa',  # Karuizawa villa search results
            '/search/result?HPSRC_AREA_ID[57]=1&area_top_flg=1',  # General Karuizawa search results
            '/search/result?HPSRC_AREA_ID[57]=1',  # Karuizawa area results
        ]
        
        for url_path in target_urls:
            try:
                full_url = urljoin(self.base_url, url_path)
                logger.info(f"Scraping Tokyu Resort from: {full_url}")
                
                soup = self.get_soup(full_url)
                if not soup:
                    logger.warning(f"Could not load page: {full_url}")
                    continue
                    
                # Extract properties from this page
                properties = self.extract_properties_from_page(soup, full_url)
                logger.info(f"Found {len(properties)} properties on {url_path}")
                all_properties.extend(properties)
                
                # Look for additional property detail pages
                detail_links = self.find_property_detail_links(soup, full_url)
                for detail_url in detail_links[:5]:  # Limit to avoid excessive requests
                    detail_soup = self.get_soup(detail_url)
                    if detail_soup:
                        detail_properties = self.extract_properties_from_detail_page(detail_soup, detail_url)
                        logger.info(f"Found {len(detail_properties)} properties on detail page")
                        all_properties.extend(detail_properties)
                        
            except Exception as e:
                logger.error(f"Error scraping {url_path}: {e}")
                continue
        
        # Remove duplicates and validate
        unique_properties = self.deduplicate_properties(all_properties)
        logger.info(f"Tokyu Resort: {len(unique_properties)} unique properties found")
        
        return unique_properties
    
    def extract_properties_from_page(self, soup, page_url: str) -> List[PropertyData]:
        """Extract property data from a listing page"""
        properties = []
        
        # Debug: Log page title and structure
        page_title = soup.find('title')
        if page_title:
            logger.info(f"Page title: {page_title.get_text()}")
        
        # Debug: Log all div elements with classes to understand structure
        all_divs_with_classes = soup.find_all('div', class_=True)
        logger.info(f"Found {len(all_divs_with_classes)} div elements with classes")
        
        # Sample some class names for debugging
        class_samples = []
        for div in all_divs_with_classes[:10]:
            class_list = div.get('class')
            if class_list:
                class_samples.extend(class_list[:2])  # Take first 2 classes per div
        logger.info(f"Sample classes found: {class_samples[:20]}")
        
        # Look for property containers with various possible class names
        property_selectors = [
            '.property-item',
            '.listing-item', 
            '.property-card',
            '.property',
            '.listing',
            '.item',
            '.result-item',
            '.search-result',
            '.property-result',
            '[class*="property"]',
            '[class*="listing"]',
            '[class*="result"]',
            '[class*="item"]'
        ]
        
        property_elements = []
        for selector in property_selectors:
            elements = soup.select(selector)
            if elements:
                logger.info(f"Found {len(elements)} elements with selector: {selector}")
                property_elements = elements
                break
        
        # If no specific property containers found, look for structured content
        if not property_elements:
            # Look for divs or sections that might contain property information
            potential_elements = soup.find_all(['div', 'section', 'article'], 
                                             class_=lambda x: x and any(
                                                 keyword in x.lower() for keyword in 
                                                 ['property', 'listing', 'item', 'card', 'result', 'estate', 'home', 'villa', 'resort', 'bukken', 'recommend', 'new']
                                             ))
            
            if potential_elements:
                logger.info(f"Found {len(potential_elements)} potential property elements")
                property_elements = potential_elements[:15]  # Limit to reasonable number
            
            # Fallback: look for any elements containing price or property-related text
            if not property_elements:
                price_elements = soup.find_all(text=re.compile(r'[0-9,]+万円|億円|¥[0-9,]+'))
                if price_elements:
                    logger.info(f"Found {len(price_elements)} elements with price text")
                    # Get parent elements that contain price information
                    property_elements = []
                    for price_elem in price_elements[:10]:
                        parent = price_elem.parent
                        if parent and parent not in property_elements:
                            property_elements.append(parent)
        
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
                        'source': 'Tokyu Resort'
                    }
                    property_data.title = generate_property_title(property_dict)
                    properties.append(property_data)
                    logger.info(f"Extracted property: {property_data.title[:60]}...")
                    
            except Exception as e:
                logger.error(f"Error extracting property {i+1} from {page_url}: {e}")
                continue
        
        return properties
    
    def extract_properties_from_detail_page(self, soup, page_url: str) -> List[PropertyData]:
        """Extract property data from a detail page"""
        properties = []
        
        try:
            property_data = self.extract_single_property_detail(soup, page_url)
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
                logger.info(f"Extracted detail property: {property_data.title[:60]}...")
                
        except Exception as e:
            logger.error(f"Error extracting detail property from {page_url}: {e}")
        
        return properties
    
    def extract_single_property(self, element, page_url: str, index: int) -> Optional[PropertyData]:
        """Extract data from a single property element"""
        try:
            property_data = PropertyData()
            property_data.source_url = page_url
            
            # Extract title/name
            title_selectors = ['h1', 'h2', 'h3', 'h4', '.title', '.name', '.property-title', '.property-name', '.heading']
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
                    property_data.title = f"Tokyu Resort Property {index}"
                    # Try to find a meaningful first line
                    for line in lines[:3]:
                        if len(line) > 10 and not any(skip in line.lower() for skip in ['price', '円', '¥', 'contact', '価格']):
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
                price_keywords = ['価格', 'price', '円', '¥', 'yen', '販売価格', '物件価格']
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
            location_keywords = ['軽井沢', 'karuizawa', '所在地', 'location', '住所', 'address', '所在', '立地']
            element_text_lower = element_text.lower()
            
            for line in element_text.split('\n'):
                line_clean = line.strip()
                if line_clean and any(keyword in line_clean.lower() for keyword in location_keywords):
                    property_data.location = line_clean[:100]
                    break
            
            # Default location if not found
            if not property_data.location:
                property_data.location = "Karuizawa Resort Community"
            
            # Extract property type
            type_keywords = {
                'villa': 'Villa',
                'house': 'House', 
                'home': 'Home',
                'land': 'Land',
                'plot': 'Land',
                'apartment': 'Apartment',
                'condo': 'Condominium',
                'resort': 'Resort Property',
                'townhouse': 'Townhouse',
                'mansion': 'Mansion',
                'estate': 'Estate'
            }
            
            element_text_lower = element_text.lower()
            for keyword, prop_type in type_keywords.items():
                if keyword in element_text_lower:
                    property_data.property_type = prop_type
                    break
            
            if not property_data.property_type:
                property_data.property_type = "Resort Community Property"
            
            # Extract images
            img_elements = element.find_all('img')
            img_urls = []
            for img in img_elements:
                src = img.get('src') or img.get('data-src') or img.get('data-lazy')
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
            
            # Extract rooms info
            room_patterns = [
                r'([0-9]+)LDK',
                r'([0-9]+)SDK',
                r'([0-9]+)DK',
                r'([0-9]+)R'
            ]
            
            for pattern in room_patterns:
                room_match = re.search(pattern, element_text)
                if room_match:
                    property_data.rooms = room_match.group(0)
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
    
    def extract_single_property_detail(self, soup, page_url: str) -> Optional[PropertyData]:
        """Extract detailed property data from a property detail page"""
        try:
            property_data = PropertyData()
            property_data.source_url = page_url
            
            # Extract title from page title or main heading
            title_selectors = ['h1', '.page-title', '.property-title', '.main-title', 'title']
            for selector in title_selectors:
                title_elem = soup.select_one(selector)
                if title_elem and title_elem.get_text(strip=True):
                    property_data.title = title_elem.get_text(strip=True)[:200]
                    break
            
            if not property_data.title:
                property_data.title = "Tokyu Resort Property Detail"
            
            # Extract comprehensive property information
            page_text = soup.get_text()
            
            # Extract price with more detailed patterns
            price_patterns = [
                r'販売価格[:\s]*([0-9,]+)億([0-9,]+)万円',
                r'価格[:\s]*([0-9,]+)億([0-9,]+)万円',
                r'販売価格[:\s]*([0-9,]+)億円',
                r'価格[:\s]*([0-9,]+)億円',
                r'販売価格[:\s]*([0-9,]+)万円',
                r'価格[:\s]*([0-9,]+)万円',
                r'([0-9,]+)億([0-9,]+)万円',
                r'([0-9,]+)億円',
                r'([0-9,]+)万円'
            ]
            
            for pattern in price_patterns:
                price_match = re.search(pattern, page_text)
                if price_match:
                    property_data.price = price_match.group(0)
                    break
            
            if not property_data.price:
                property_data.price = "お問い合わせください"
            
            # Extract location
            location_patterns = [
                r'所在地[:\s]*([^\\n]+軽井沢[^\\n]+)',
                r'住所[:\s]*([^\\n]+軽井沢[^\\n]+)',
                r'立地[:\s]*([^\\n]+軽井沢[^\\n]+)',
                r'(軽井沢[^\\n]+)',
            ]
            
            for pattern in location_patterns:
                location_match = re.search(pattern, page_text)
                if location_match:
                    property_data.location = location_match.group(1).strip()[:150]
                    break
            
            if not property_data.location:
                property_data.location = "Tokyu Resort Karuizawa"
            
            # Extract property type
            if any(keyword in page_text.lower() for keyword in ['villa', 'ヴィラ', 'ビラ']):
                property_data.property_type = 'Villa'
            elif any(keyword in page_text.lower() for keyword in ['townhouse', 'タウンハウス']):
                property_data.property_type = 'Townhouse'
            elif any(keyword in page_text.lower() for keyword in ['mansion', 'マンション']):
                property_data.property_type = 'Mansion'
            elif any(keyword in page_text.lower() for keyword in ['land', '土地']):
                property_data.property_type = 'Land'
            else:
                property_data.property_type = 'Resort Property'
            
            # Extract comprehensive images
            img_elements = soup.find_all('img')
            img_urls = []
            for img in img_elements:
                src = img.get('src') or img.get('data-src') or img.get('data-lazy')
                if src:
                    if src.startswith('/'):
                        src = urljoin(self.base_url, src)
                    elif src.startswith('http'):
                        pass
                    else:
                        src = urljoin(page_url, src)
                    img_urls.append(src)
            
            property_data.image_urls = self.filter_property_images(img_urls)
            
            # Extract detailed specifications
            size_patterns = [
                r'敷地面積[:\s]*([0-9,]+\.?[0-9]*)(?:㎡|m²|平米)',
                r'建物面積[:\s]*([0-9,]+\.?[0-9]*)(?:㎡|m²|平米)',
                r'専有面積[:\s]*([0-9,]+\.?[0-9]*)(?:㎡|m²|平米)',
                r'([0-9,]+\.?[0-9]*)(?:㎡|m²|平米)'
            ]
            
            size_info_parts = []
            for pattern in size_patterns:
                size_matches = re.findall(pattern, page_text)
                if size_matches:
                    for match in size_matches[:2]:  # Take first 2 matches
                        size_info_parts.append(f"{match}㎡")
            
            if size_info_parts:
                property_data.size_info = ' / '.join(size_info_parts)
            
            # Extract building age
            age_patterns = [
                r'築年数[:\s]*([^\\n]+)',
                r'建築年[:\s]*([^\\n]+)',
                r'築([0-9]+)年',
                r'平成([0-9]+)年',
                r'令和([0-9]+)年',
                r'新築'
            ]
            
            for pattern in age_patterns:
                age_match = re.search(pattern, page_text)
                if age_match:
                    property_data.building_age = age_match.group(0)[:50]
                    break
            
            # Extract room configuration
            room_patterns = [
                r'間取り[:\s]*([0-9]+[LDS]?[DK]+)',
                r'([0-9]+LDK)',
                r'([0-9]+SDK)',
                r'([0-9]+DK)'
            ]
            
            for pattern in room_patterns:
                room_match = re.search(pattern, page_text)
                if room_match:
                    property_data.rooms = room_match.group(1) if pattern.startswith('間取り') else room_match.group(0)
                    break
            
            # Create comprehensive description
            desc_parts = []
            if property_data.location and 'karuizawa' in property_data.location.lower():
                desc_parts.append(f"軽井沢の{property_data.property_type}")
            
            # Add key features from page content
            feature_keywords = ['リゾート', '自然', '別荘', 'ヴィラ', '温泉', 'ゴルフ', '避暑', 'セカンドハウス']
            found_features = []
            for keyword in feature_keywords:
                if keyword in page_text and keyword not in found_features:
                    found_features.append(keyword)
                    if len(found_features) >= 3:
                        break
            
            if found_features:
                desc_parts.append('、'.join(found_features) + 'を楽しめる物件')
            
            if desc_parts:
                property_data.description = '。'.join(desc_parts) + '。'
            
            return property_data
            
        except Exception as e:
            logger.error(f"Error extracting detail property data: {e}")
            return None
    
    def find_property_detail_links(self, soup, base_url: str) -> List[str]:
        """Find links to individual property detail pages"""
        detail_links = []
        
        try:
            # Look for Tokyu Resort specific detail page patterns
            link_patterns = [
                'a[href*="/karuizawa/detail/"]',  # Primary pattern: /karuizawa/detail/XXXXX
                'a[href*="/detail/"]',             # Secondary pattern: /detail/XXXXX
                'a[href*="detail"]',               # General detail links
                'a[href*="property"]',             # Property links
            ]
            
            for pattern in link_patterns:
                links = soup.select(pattern)
                for link in links:
                    href = link.get('href')
                    if href:
                        if href.startswith('/'):
                            url = urljoin(self.base_url, href)
                        elif href.startswith('http'):
                            url = href
                        else:
                            url = urljoin(base_url, href)
                        
                        # Filter for valid Tokyu Resort detail URLs
                        if ('/karuizawa/detail/' in url or '/detail/' in url) and url != base_url and url not in detail_links:
                            detail_links.append(url)
                            logger.info(f"Found detail link: {url}")
                
                if detail_links:  # Found some links with this pattern
                    break
            
            # Also search for any links that contain property IDs (numeric patterns)
            if not detail_links:
                all_links = soup.find_all('a', href=True)
                for link in all_links:
                    href = link.get('href')
                    if href and ('detail' in href or 'property' in href):
                        if href.startswith('/'):
                            url = urljoin(self.base_url, href)
                        elif href.startswith('http'):
                            url = href
                        else:
                            url = urljoin(base_url, href)
                        
                        if url not in detail_links and len(detail_links) < 10:
                            detail_links.append(url)
                            logger.info(f"Found potential detail link: {url}")
        
        except Exception as e:
            logger.error(f"Error finding detail links: {e}")
        
        return detail_links[:10]  # Limit to prevent excessive requests
    
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
                'arrow', 'bullet', 'spacer', 'line', 'bg_', 'background', 'banner'
            ]):
                continue
            
            # Prioritize property-related images
            if any(priority in img_url.lower() for priority in [
                'property', 'house', 'home', 'villa', 'building', 'exterior', 'interior',
                'photo', 'image', 'gallery', 'main', 'view', 'room', 'estate'
            ]):
                property_images.append(img_url)
            else:
                ui_images.append(img_url)
        
        # Combine: property photos first, then other images
        final_images = property_images + ui_images
        
        # Limit to 5 images total
        return final_images[:5]