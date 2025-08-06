"""
Mitsui no Mori Karuizawa property scraper
"""
import re
from typing import List, Optional
from urllib.parse import urljoin
import logging
from .base_scraper import SimpleScraper, PropertyData
from utils.titleGenerator import generate_property_title

logger = logging.getLogger(__name__)

class MitsuiNoMoriScraper(SimpleScraper):
    """Scraper for Mitsui no Mori Karuizawa properties"""
    
    def __init__(self, config: dict = None):
        if config is None:
            config = {
                'base_url': 'https://www.mitsuinomori.co.jp',
                'rate_limit': 0.25,  # 1 request every 4 seconds (conservative)
                'name': 'Mitsui no Mori Karuizawa'
            }
        else:
            # Ensure we have the base URL if not provided
            if 'base_url' not in config:
                config['base_url'] = 'https://www.mitsuinomori.co.jp'
            
            # Handle rate limit config format compatibility
            if 'rate_limit' in config and isinstance(config['rate_limit'], dict):
                # Extract requests_per_second from dict format
                config['rate_limit'] = config['rate_limit']['requests_per_second']
                
        super().__init__(config)
        
    def scrape_listings(self) -> List[PropertyData]:
        """Main method to scrape property listings"""
        all_properties = []
        
        # Start from the main Karuizawa page
        main_url = urljoin(self.base_url, '/karuizawa/')
        logger.info(f"Starting scrape from: {main_url}")
        
        soup = self.get_soup(main_url)
        if not soup:
            logger.error("Failed to load main page")
            return []
            
        # Find property listings on the main page
        properties = self.extract_properties_from_page(soup, main_url)
        all_properties.extend(properties)
        
        # Look for additional property links or pages
        property_links = self.find_property_detail_links(soup)
        for link_url in property_links[:10]:  # Limit to 10 for prototype
            detail_properties = self.scrape_property_detail_page(link_url)
            all_properties.extend(detail_properties)
            
        # Filter and validate
        valid_properties = []
        for prop in all_properties:
            if self.validate_property_data(prop):
                valid_properties.append(prop)
                
        logger.info(f"Scraped {len(valid_properties)} valid properties from {len(all_properties)} total")
        return valid_properties
        
    def extract_properties_from_page(self, soup, page_url: str) -> List[PropertyData]:
        """Extract property data from a listings page"""
        properties = []
        
        # For Mitsui no Mori, try a broader approach since it might be a more complex site
        logger.info(f"Analyzing page: {page_url}")
        
        # Strategy 1: Look for any div that might contain property information
        all_divs = soup.find_all('div')
        logger.info(f"Found {len(all_divs)} div elements to analyze")
        
        # Strategy 2: Look for content in the page that suggests properties
        page_text = soup.get_text()
        
        # Check if this is a property detail page (single property)
        if '/realestate/' in page_url and len(page_url.split('/')) > 5:
            # This is likely a single property detail page
            single_property = self.extract_single_property_from_detail_page(soup, page_url)
            if single_property:
                properties.append(single_property)
                
        else:
            # This is a listing page, look for multiple properties
            # Try to find content blocks that might contain property info
            content_areas = soup.select('main, .main, .content, #content, #main')
            
            if not content_areas:
                content_areas = [soup]  # Use whole page as fallback
                
            for content_area in content_areas:
                # Look for any structured content
                potential_properties = content_area.find_all(['div', 'section', 'article'])
                
                for element in potential_properties:
                    try:
                        # Check if this element might contain property info
                        element_text = element.get_text()
                        
                        # Skip if element is too small or too large
                        if len(element_text.strip()) < 20 or len(element_text.strip()) > 2000:
                            continue
                            
                        # Try to extract property data
                        property_data = self.extract_property_from_element(element, page_url)
                        if property_data and (property_data.title or property_data.price):
                            properties.append(property_data)
                            
                    except Exception as e:
                        continue
                        
        logger.info(f"Extracted {len(properties)} potential properties from page")
        return properties
        
    def extract_single_property_from_detail_page(self, soup, page_url: str) -> Optional[PropertyData]:
        """Extract property data from a single property detail page"""
        data = PropertyData()
        data.source_url = page_url
        
        # For detail pages, property info is often in the main content area
        page_text = soup.get_text()
        
        # Extract title - often in h1 or main heading
        title_selectors = ['h1', 'h2', '.title', '.property-title', 'title']
        for selector in title_selectors:
            title_elem = soup.select_one(selector)
            if title_elem:
                title_text = title_elem.get_text(strip=True)
                if len(title_text) > 5 and len(title_text) < 200:  # Reasonable title length
                    data.title = title_text
                    break
                    
        # If no title found, create one from URL
        if not data.title:
            data.title = f"Mitsui Property {page_url.split('/')[-2] if page_url.endswith('/') else page_url.split('/')[-1]}"
            
        # Extract other data using the same patterns as before
        # Since this is a detail page, be more generous with extraction
        
        # Price patterns - more flexible for detail pages
        # Order matters: complex formats first, then simpler ones
        price_patterns = [
            r'\d+億[\d,]*万円',      # e.g., "3億5,000万円", "2億万円"
            r'\d+億円',              # e.g., "3億円"
            r'[\d,]+\s*万円',        # e.g., "5,000万円"
            r'¥[\d,]+',              # e.g., "¥350000000"
            r'[\d,]+\s*円',          # e.g., "350,000,000円"
            r'価格[:\s]*[\d,]+',
            r'金額[:\s]*[\d,]+',
            r'\d{1,3}(,\d{3})*\s*(yen|YEN)',
            r'price[:\s]*[\d,]+'
        ]
        
        for pattern in price_patterns:
            price_match = re.search(pattern, page_text, re.I)
            if price_match:
                data.price = price_match.group().strip()
                break
                
        # Location - should definitely contain Karuizawa
        data.location = "Karuizawa"  # Default since this is Mitsui no Mori Karuizawa
        
        # Look for more specific location info
        location_patterns = [
            r'[東西南北中旧新]軽井沢[^。\n]*',
            r'軽井沢[町市区][^。\n]*',
            r'location[:\s]*[^。\n]*karuizawa[^。\n]*'
        ]
        
        for pattern in location_patterns:
            location_match = re.search(pattern, page_text, re.I)
            if location_match:
                data.location = location_match.group().strip()
                break
                
        # Property type - default to house for Mitsui no Mori
        data.property_type = "一戸建て"  # Default for Mitsui development
        
        # Size information
        size_patterns = [
            r'[\d,]+\.?\d*\s*㎡',
            r'[\d,]+\.?\d*\s*平米',
            r'[\d,]+\.?\d*\s*坪',
            r'敷地[:\s]*[\d,]+\.?\d*\s*[㎡平米坪]',
            r'建物[:\s]*[\d,]+\.?\d*\s*[㎡平米坪]',
            r'land[:\s]*[\d,]+\.?\d*\s*[sqm㎡]',
            r'building[:\s]*[\d,]+\.?\d*\s*[sqm㎡]'
        ]
        
        size_info_parts = []
        for pattern in size_patterns:
            size_matches = re.findall(pattern, page_text, re.I)
            size_info_parts.extend(size_matches[:2])  # Limit to avoid too much
            
        if size_info_parts:
            data.size_info = ' '.join(size_info_parts)
            
        # Extract images - collect all valid URLs first, then filter
        raw_images = []
        img_elements = soup.select('img')
        for img in img_elements:
            src = img.get('src') or img.get('data-src')
            if src and not src.startswith('data:'):  # Skip base64 images
                img_url = urljoin(self.base_url, src)
                if img_url not in raw_images:
                    raw_images.append(img_url)
        
        # Use helper method to filter and prioritize images
        data.image_urls = self.filter_property_images(raw_images)
                    
        # Description - try to get meaningful description
        desc_selectors = ['.description', '.detail', '.content', '.summary', 'main']
        for selector in desc_selectors:
            desc_elem = soup.select_one(selector)
            if desc_elem:
                desc_text = desc_elem.get_text(strip=True)
                if len(desc_text) > 50:  # Meaningful description
                    data.description = desc_text[:2000]  # Truncate
                    break
                    
        # Building age
        age_patterns = [
            r'築\d+年',
            r'建築年[:\s]*[平成昭和令和]\d+年',
            r'\d{4}年建築',
            r'新築'
        ]
        
        for pattern in age_patterns:
            age_match = re.search(pattern, page_text)
            if age_match:
                data.building_age = age_match.group()
                break
        
        # Generate proper title using title generator
        if data.price or data.location or data.property_type:
            property_dict = {
                'source_url': data.source_url,
                'property_type': data.property_type,
                'building_age': data.building_age,
                'price': data.price,
                'location': data.location
            }
            data.title = generate_property_title(property_dict)
                
        return data if (data.title or data.price) else None
        
    def extract_property_from_element(self, element, page_url: str) -> Optional[PropertyData]:
        """Extract property data from a single HTML element"""
        data = PropertyData()
        data.source_url = page_url
        
        # Extract title - try multiple selectors
        title_selectors = ['h1', 'h2', 'h3', 'h4', '.title', '.name', '.property-title', '[class*="title"]']
        for selector in title_selectors:
            title = self.extract_text_safely(element, selector)
            if title and len(title) > 5:  # Reasonable title length
                data.title = title[:500]  # Truncate if too long
                break
                
        # Extract price - look for currency indicators
        # Order matters: complex formats first, then simpler ones
        price_patterns = [
            r'\d+億[\d,]*万円',      # e.g., "3億5,000万円", "2億万円"
            r'\d+億円',              # e.g., "3億円"
            r'[\d,]+\s*万円',        # e.g., "5,000万円"
            r'¥[\d,]+',              # e.g., "¥350000000"
            r'[\d,]+\s*円',          # e.g., "350,000,000円"
            r'price[:\s]*[\d,]+',
            r'金額[:\s]*[\d,]+'
        ]
        
        element_text = element.get_text()
        for pattern in price_patterns:
            price_match = re.search(pattern, element_text, re.I)
            if price_match:
                data.price = price_match.group().strip()
                break
                
        # Extract location - look for Karuizawa-related text
        location_patterns = [
            r'軽井沢[^。\n]*',
            r'[東西南北中旧新][軽井沢]{1,10}',
            r'karuizawa[^。\n]*'
        ]
        
        for pattern in location_patterns:
            location_match = re.search(pattern, element_text, re.I)
            if location_match:
                data.location = location_match.group().strip()
                break
                
        # If no specific location found, use generic Karuizawa
        if not data.location and any(kw in element_text.lower() for kw in ['軽井沢', 'karuizawa']):
            data.location = "軽井沢"
            
        # Extract property type
        type_keywords = {
            '一戸建て': '一戸建て',
            '戸建': '一戸建て', 
            '土地': '土地',
            'land': '土地',
            'house': '一戸建て',
            'マンション': 'マンション',
            '別荘': '別荘'
        }
        
        element_text_lower = element_text.lower()
        for keyword, prop_type in type_keywords.items():
            if keyword in element_text_lower:
                data.property_type = prop_type
                break
                
        # Extract size information
        size_patterns = [
            r'[\d,]+\.?\d*\s*㎡',
            r'[\d,]+\.?\d*\s*平米',
            r'[\d,]+\.?\d*\s*坪',
            r'土地[:\s]*[\d,]+\.?\d*\s*[㎡平米坪]',
            r'建物[:\s]*[\d,]+\.?\d*\s*[㎡平米坪]'
        ]
        
        size_info_parts = []
        for pattern in size_patterns:
            size_matches = re.findall(pattern, element_text)
            size_info_parts.extend(size_matches)
            
        if size_info_parts:
            data.size_info = ' '.join(size_info_parts[:3])  # Limit to avoid too much text
            
        # Extract room layout
        room_patterns = [
            r'\d+[SLDK]+',
            r'\d+LDK',
            r'\d+DK',
            r'\d+K'
        ]
        
        for pattern in room_patterns:
            room_match = re.search(pattern, element_text)
            if room_match:
                data.rooms = room_match.group()
                break
                
        # Extract images - collect all valid URLs first, then filter
        raw_images = []
        img_elements = element.select('img')
        for img in img_elements:
            src = img.get('src') or img.get('data-src')
            if src and not src.startswith('data:'):
                # Convert relative URLs to absolute
                img_url = urljoin(self.base_url, src)
                if img_url not in raw_images:
                    raw_images.append(img_url)
        
        # Use helper method to filter and prioritize images
        data.image_urls = self.filter_property_images(raw_images)
                
        # Extract building age if available
        age_patterns = [
            r'築\d+年',
            r'平成\d+年',
            r'昭和\d+年',
            r'令和\d+年',
            r'新築',
            r'\d{4}年建築'
        ]
        
        for pattern in age_patterns:
            age_match = re.search(pattern, element_text)
            if age_match:
                data.building_age = age_match.group()
                break
        
        # Generate proper title using title generator
        if data.price or data.location or data.property_type:
            property_dict = {
                'source_url': data.source_url,
                'property_type': data.property_type,
                'building_age': data.building_age,
                'price': data.price,
                'location': data.location
            }
            data.title = generate_property_title(property_dict)
                
        return data
        
    def filter_property_images(self, img_urls: List[str]) -> List[str]:
        """Filter image URLs to exclude navigation and generic assets"""
        filtered_images = []
        
        exclude_keywords = ['btn_', 'nav_', 'menu_', 'common/', 'header', 'logo', 'icon', 'arrow', 'bullet']
        include_keywords = ['property', 'bukken', 'photo', 'image', 'gallery', 'main']
        
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
        
    def is_valid_property_url(self, url: str) -> bool:
        """Validate if URL appears to be a property detail page"""
        if not url:
            return False
        
        # Skip javascript and anchor links
        if url.startswith(('javascript:', '#', 'mailto:')):
            return False
            
        # Check for property-related keywords in URL
        property_keywords = ['property', 'detail', 'bukken', 'listing', 'realestate']
        url_lower = url.lower()
        
        # Must contain at least one property keyword
        has_property_keyword = any(keyword in url_lower for keyword in property_keywords)
        
        # Should not be just the base domain
        is_not_base_url = url != self.base_url and not url.endswith('/')
        
        return has_property_keyword or is_not_base_url
        
    def find_property_detail_links(self, soup) -> List[str]:
        """Find links to individual property detail pages"""
        links = []
        
        # Look for links that might lead to property details
        link_elements = soup.select('a[href]')
        
        for link in link_elements:
            href = link.get('href', '')
            link_text = link.get_text(strip=True).lower()
            
            # Filter for property-related links
            if any(keyword in href.lower() or keyword in link_text for keyword in 
                   ['property', 'bukken', '物件', 'detail', '詳細', 'house', 'land']):
                full_url = urljoin(self.base_url, href)
                if full_url not in links and full_url != self.base_url:
                    links.append(full_url)
                    
        logger.info(f"Found {len(links)} potential property detail links")
        return links[:10]  # Limit for prototype
        
    def scrape_property_detail_page(self, url: str) -> List[PropertyData]:
        """Scrape a detailed property page"""
        soup = self.get_soup(url)
        if not soup:
            return []
            
        # Extract detailed property information
        properties = self.extract_properties_from_page(soup, url)
        
        # For detail pages, we might get more comprehensive data
        for prop in properties:
            if not prop.description:
                # Try to get description from detail page
                desc_selectors = ['.description', '.detail', '.content', '[class*="desc"]']
                for selector in desc_selectors:
                    desc = self.extract_text_safely(soup, selector)
                    if desc and len(desc) > 20:
                        prop.description = desc[:2000]  # Truncate to limit
                        break
                        
        return properties