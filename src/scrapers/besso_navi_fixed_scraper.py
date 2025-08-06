"""
Fixed Besso Navi scraper using proper search form flow
Based on analysis of https://www.besso-navi.com/b-search
"""
import requests
import re
import time
from typing import List, Optional, Dict
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import logging

from .base_scraper import SimpleScraper, PropertyData
from utils.titleGenerator import generate_property_title

logger = logging.getLogger(__name__)

class BessoNaviFixedScraper(SimpleScraper):
    """Fixed Besso Navi scraper using proper search form flow"""
    
    def __init__(self, config: dict = None):
        default_config = {
            'base_url': 'https://www.besso-navi.com',
            'timeout': 30,
            'headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'ja,en-US;q=0.7,en;q=0.3',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
        }
        
        if config:
            default_config.update(config)
            
        super().__init__(default_config)
        self.session = requests.Session()
        self.session.headers.update(self.config.get('headers', {}))
        
        # Property type mapping
        self.property_types = {
            'villa': 'ヴィラ',
            'land': '土地', 
            'apartment': 'マンション'
        }
        
    def scrape_listings(self) -> List[PropertyData]:
        """Main scraping method using proper search flow"""
        logger.info("Starting Besso Navi Fixed scraper")
        
        all_properties = []
        
        # Search for each property type
        for search_type, japanese_type in self.property_types.items():
            logger.info(f"Searching for {search_type} ({japanese_type}) properties")
            
            try:
                properties = self._search_property_type(search_type)
                if properties:
                    logger.info(f"Found {len(properties)} {search_type} properties")
                    all_properties.extend(properties)
                else:
                    logger.info(f"No {search_type} properties found")
                    
                # Rate limiting between searches
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"Error searching {search_type}: {e}")
                continue
        
        logger.info(f"Total properties found: {len(all_properties)}")
        return all_properties
    
    def _search_property_type(self, property_type: str) -> List[PropertyData]:
        """Search for specific property type"""
        
        # Step 1: Get the search form
        search_url = f"{self.base_url}/b-search"
        
        try:
            response = self.session.get(search_url, timeout=self.config.get('timeout', 30))
            response.raise_for_status()
            
            # Step 2: Submit search form
            search_data = self._build_search_data(property_type)
            result_url = f"{self.base_url}/b-search/result"
            
            # Set referer for proper form submission
            headers = self.session.headers.copy()
            headers['Referer'] = search_url
            
            logger.info(f"Submitting search for {property_type}")
            logger.debug(f"Search data: {search_data}")
            
            response = self.session.post(result_url, data=search_data, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Step 3: Parse results
            return self._parse_search_results(response.content, property_type)
            
        except Exception as e:
            logger.error(f"Search failed for {property_type}: {e}")
            return []
    
    def _build_search_data(self, property_type: str) -> Dict[str, str]:
        """Build search form data for specific property type"""
        
        # Base search data (form structure discovered from testing)
        search_data = {
            'FromPage': 'b_search',
            'price_start': '',           # No price limits for now
            'price_end': '',
            'tochi_start': '',          # Land size limits
            'tochi_end': '',
        }
        
        # Area selection (Karuizawa region) - select multiple relevant areas
        # Based on form analysis: 2,3,4 seem to be Karuizawa-related areas
        karuizawa_areas = ['2', '3', '4']
        search_data['areaid[]'] = karuizawa_areas
        
        # Property type selection using kind_check radio button
        # Based on form analysis: kind_check values 1,2,3 represent different property types
        if property_type == 'villa':
            search_data['kind_check'] = '1'  # Assuming 1 = villa/vacation home
        elif property_type == 'land':
            search_data['kind_check'] = '2'  # Assuming 2 = land
        elif property_type == 'apartment':
            search_data['kind_check'] = '3'  # Assuming 3 = apartment/mansion
        
        return search_data
    
    def _parse_search_results(self, html_content: bytes, property_type: str) -> List[PropertyData]:
        """Parse search results page to extract property links and data"""
        
        soup = BeautifulSoup(html_content, 'html.parser')
        properties = []
        
        # Look for property links using multiple strategies
        property_links = []
        
        # Look for property links with b_id and deduplicate
        seen_ids = set()
        
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            if 'b_id=' in href:
                # Extract the property ID to avoid duplicates
                import re
                id_match = re.search(r'b_id=(\d+)', href)
                if id_match:
                    prop_id = id_match.group(1)
                    if prop_id not in seen_ids:
                        seen_ids.add(prop_id)
                        full_url = urljoin(self.base_url, href)
                        property_links.append(full_url)
        
        # Strategy 3: Debug - show all links if still no results
        if not property_links:
            logger.debug("No property links found, showing all links for debugging:")
            all_links = soup.find_all('a', href=True)
            for i, link in enumerate(all_links[:10]):  # Show first 10
                href = link.get('href', '')
                text = link.get_text(strip=True)
                logger.debug(f"  Link {i+1}: {href} -> '{text[:50]}'")
                
            # Also check if there's any property-related content
            text_content = soup.get_text()
            if '件' in text_content or '物件' in text_content or 'properties' in text_content:
                logger.debug("Page contains property-related text, but no links found")
            else:
                logger.debug("Page doesn't seem to contain property results")
        
        logger.info(f"Found {len(property_links)} property detail links")
        
        # Extract basic info from each property link
        for i, property_url in enumerate(property_links):
            logger.info(f"Processing property {i+1}/{len(property_links)}: {property_url}")
            
            try:
                property_data = self._extract_property_details(property_url, property_type)
                if property_data:
                    properties.append(property_data)
                
                # Rate limiting between property requests
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Error extracting property from {property_url}: {e}")
                continue
        
        return properties
    
    def _extract_property_details(self, property_url: str, property_type: str) -> Optional[PropertyData]:
        """Extract detailed property information from individual property page"""
        
        try:
            response = self.session.get(property_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Create property data object
            data = PropertyData()
            data.source_url = property_url
            data.property_type = self.property_types.get(property_type, property_type)
            
            # Extract title
            title_selectors = ['h1', '.property-title', '.title', 'title']
            for selector in title_selectors:
                title_elem = soup.select_one(selector)
                if title_elem:
                    data.title = title_elem.get_text(strip=True)
                    break
            
            # Extract price
            price_patterns = [
                r'(\d{1,3}(?:,\d{3})*)\s*万円',
                r'(\d{1,3}(?:,\d{3})*)\s*円',
                r'価格[:\s]*(\d{1,3}(?:,\d{3})*)\s*万円'
            ]
            
            text_content = soup.get_text()
            for pattern in price_patterns:
                match = re.search(pattern, text_content)
                if match:
                    data.price = match.group(0)
                    break
            
            # Extract location
            location_keywords = ['所在地', '住所', '地域', 'エリア']
            for keyword in location_keywords:
                location_elem = soup.find(text=re.compile(keyword))
                if location_elem:
                    parent = location_elem.parent
                    if parent:
                        location_text = parent.get_text(strip=True)
                        # Clean up location text
                        data.location = re.sub(f'^{keyword}[:\\s]*', '', location_text)
                        break
            
            # Extract images
            raw_images = []
            img_elements = soup.select('img')
            for img in img_elements:
                src = img.get('src') or img.get('data-src')
                if src and not src.startswith('data:'):
                    img_url = urljoin(property_url, src)
                    if img_url not in raw_images:
                        raw_images.append(img_url)
            
            # Filter images
            data.image_urls = self.filter_property_images(raw_images)
            
            # Set default values if missing
            if not data.title:
                data.title = f"Besso Navi {property_type.title()} Property"
            
            if not data.location:
                data.location = "軽井沢"
            
            if not data.price:
                data.price = "お問い合わせください"
            
            # Set building age and size info
            data.building_age = "不明"
            data.size_info = "詳細はお問い合わせください"
            data.rooms = ""
            
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
            
            logger.info(f"Extracted: {data.title} - {data.price}")
            return data
            
        except Exception as e:
            logger.error(f"Error extracting details from {property_url}: {e}")
            return None