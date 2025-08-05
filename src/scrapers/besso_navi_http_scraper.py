"""
Besso Navi HTTP scraper - Form-based vacation home search site without browser
"""
import requests
import re
import time
from typing import List, Optional, Dict
from urllib.parse import urljoin, urlparse, parse_qs
from bs4 import BeautifulSoup
import logging

from .base_scraper import AbstractPropertyScraper, SimpleScraper, PropertyData

logger = logging.getLogger(__name__)

class BessoNaviHTTPScraper(SimpleScraper):
    """HTTP-based scraper for Besso Navi - vacation home search site"""
    
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
        
        # Search parameters for Karuizawa properties
        self.search_params = {
            'areas': ['軽井沢', '中軽井沢', '南軽井沢', 'karuizawa'],
            'property_types': ['土地', '一戸建て', 'マンション', 'ヴィラ'],
            'price_min': 1000000,    # 1M yen
            'price_max': 500000000,  # 500M yen
        }
        
    def scrape_listings(self) -> List[PropertyData]:
        """Main scraping method for Besso Navi properties"""
        logger.info("Starting Besso Navi HTTP property scraping")
        
        all_properties = []
        
        # Try multiple approaches to find properties
        approaches = [
            self._scrape_from_search_page,
            self._scrape_from_listing_pages,
            self._scrape_from_sitemap
        ]
        
        for approach in approaches:
            try:
                logger.info(f"Trying approach: {approach.__name__}")
                properties = approach()
                if properties:
                    all_properties.extend(properties)
                    logger.info(f"Found {len(properties)} properties with {approach.__name__}")
                    break  # Stop after first successful approach
                else:
                    logger.info(f"No properties found with {approach.__name__}")
            except Exception as e:
                logger.warning(f"Approach {approach.__name__} failed: {e}")
                continue
        
        if not all_properties:
            # Fallback: try to extract any property-like content from main pages
            logger.info("All approaches failed, trying fallback content extraction")
            all_properties = self._scrape_fallback_content()
        
        logger.info(f"Total properties extracted from Besso Navi: {len(all_properties)}")
        return all_properties
    
    def _scrape_from_search_page(self) -> List[PropertyData]:
        """Try to scrape from search functionality"""
        logger.info("Attempting to scrape from search page")
        
        search_urls = [
            f"{self.base_url}/b-search",
            f"{self.base_url}/search",
            f"{self.base_url}/property-search",
            f"{self.base_url}/bukken-search"
        ]
        
        for search_url in search_urls:
            try:
                response = self.session.get(search_url, timeout=self.config.get('timeout', 30))
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Look for search form and try to submit it
                    form = soup.find('form')
                    if form:
                        properties = self._submit_search_form(form, search_url)
                        if properties:
                            return properties
                            
            except Exception as e:
                logger.debug(f"Search URL {search_url} failed: {e}")
                continue
                
        return []
    
    def _submit_search_form(self, form, base_url: str) -> List[PropertyData]:
        """Submit search form with Karuizawa parameters"""
        try:
            # Extract form action and method
            action = form.get('action', '')
            method = form.get('method', 'get').lower()
            
            if action.startswith('/'):
                action_url = urljoin(base_url, action)
            else:
                action_url = urljoin(base_url, action) if action else base_url
            
            # Build form data
            form_data = {}
            
            # Find all input fields
            inputs = form.find_all(['input', 'select', 'textarea'])
            for input_elem in inputs:
                name = input_elem.get('name')
                if not name:
                    continue
                    
                input_type = input_elem.get('type', 'text').lower()
                
                if input_type == 'hidden':
                    # Include hidden fields as-is
                    form_data[name] = input_elem.get('value', '')
                elif 'area' in name.lower() or 'location' in name.lower():
                    # Set area to Karuizawa
                    form_data[name] = '軽井沢'
                elif 'keyword' in name.lower():
                    form_data[name] = '軽井沢'
                elif input_type in ['text', 'search']:
                    # Default text inputs
                    if not input_elem.get('value'):
                        form_data[name] = ''
                elif input_type == 'checkbox':
                    # Don't check checkboxes by default
                    pass
                elif input_elem.name == 'select':
                    # Select first non-empty option for selects
                    options = input_elem.find_all('option')
                    for option in options:
                        if option.get('value') and option.get('value') != '':
                            form_data[name] = option.get('value')
                            break
            
            logger.info(f"Submitting form to {action_url} with data: {form_data}")
            
            # Submit form
            if method == 'post':
                response = self.session.post(action_url, data=form_data, timeout=30)
            else:
                response = self.session.get(action_url, params=form_data, timeout=30)
            
            if response.status_code == 200:
                return self._extract_properties_from_response(response.text, action_url)
                
        except Exception as e:
            logger.error(f"Error submitting search form: {e}")
            
        return []
    
    def _scrape_from_listing_pages(self) -> List[PropertyData]:
        """Try to scrape from known listing page patterns"""
        logger.info("Attempting to scrape from listing pages")
        
        listing_urls = [
            f"{self.base_url}/properties",
            f"{self.base_url}/bukken",
            f"{self.base_url}/listings",
            f"{self.base_url}/besso",
            f"{self.base_url}/karuizawa",
            f"{self.base_url}/property-list"
        ]
        
        all_properties = []
        
        for listing_url in listing_urls:
            try:
                response = self.session.get(listing_url, timeout=30)
                if response.status_code == 200:
                    properties = self._extract_properties_from_response(response.text, listing_url)
                    if properties:
                        all_properties.extend(properties)
                        logger.info(f"Found {len(properties)} properties from {listing_url}")
                        
            except Exception as e:
                logger.debug(f"Listing URL {listing_url} failed: {e}")
                continue
        
        return all_properties
    
    def _scrape_from_sitemap(self) -> List[PropertyData]:
        """Try to find properties from sitemap"""
        logger.info("Attempting to scrape from sitemap")
        
        sitemap_urls = [
            f"{self.base_url}/sitemap.xml",
            f"{self.base_url}/sitemap",
            f"{self.base_url}/robots.txt"
        ]
        
        property_urls = []
        
        for sitemap_url in sitemap_urls:
            try:
                response = self.session.get(sitemap_url, timeout=30)
                if response.status_code == 200:
                    if sitemap_url.endswith('.xml'):
                        # Parse XML sitemap
                        soup = BeautifulSoup(response.content, 'xml')
                        urls = soup.find_all('loc')
                        for url_elem in urls:
                            url = url_elem.get_text().strip()
                            if self._is_property_url(url):
                                property_urls.append(url)
                    else:
                        # Parse HTML sitemap or robots.txt
                        soup = BeautifulSoup(response.content, 'html.parser')
                        links = soup.find_all('a', href=True)
                        for link in links:
                            href = link['href']
                            if href.startswith('/'):
                                href = urljoin(self.base_url, href)
                            if self._is_property_url(href):
                                property_urls.append(href)
                                
            except Exception as e:
                logger.debug(f"Sitemap URL {sitemap_url} failed: {e}")
                continue
        
        # Scrape individual property pages
        all_properties = []
        for url in property_urls[:20]:  # Limit to prevent too many requests
            try:
                time.sleep(1)  # Rate limit
                response = self.session.get(url, timeout=30)
                if response.status_code == 200:
                    properties = self._extract_properties_from_response(response.text, url)
                    all_properties.extend(properties)
                    
            except Exception as e:
                logger.debug(f"Property URL {url} failed: {e}")
                continue
        
        return all_properties
    
    def _scrape_fallback_content(self) -> List[PropertyData]:
        """Fallback: scrape any property-like content from main pages"""
        logger.info("Using fallback content extraction")
        
        main_urls = [
            self.base_url,
            f"{self.base_url}/index.html",
            f"{self.base_url}/home"
        ]
        
        all_properties = []
        
        for url in main_urls:
            try:
                response = self.session.get(url, timeout=30)
                if response.status_code == 200:
                    properties = self._extract_properties_from_response(response.text, url)
                    all_properties.extend(properties)
                    
            except Exception as e:
                logger.debug(f"Main URL {url} failed: {e}")
                continue
        
        return all_properties
    
    def _extract_properties_from_response(self, html_content: str, source_url: str) -> List[PropertyData]:
        """Extract properties from HTML content"""
        soup = BeautifulSoup(html_content, 'html.parser')
        properties = []
        
        # Look for property containers using various selectors
        property_selectors = [
            '.property-item', '.bukken-item', '.listing-item',
            '.result-item', '.search-result', '.property-card',
            '[class*="property"]', '[class*="bukken"]', '[class*="listing"]',
            '[class*="result"]', '[class*="item"]'
        ]
        
        property_elements = []
        for selector in property_selectors:
            elements = soup.select(selector)
            if elements:
                property_elements = elements
                logger.info(f"Found {len(elements)} property elements with selector: {selector}")
                break
        
        if not property_elements:
            # Fallback: look for elements containing price indicators
            logger.info("No standard property elements found, searching for price indicators")
            price_elements = soup.find_all(string=re.compile(r'[0-9,]+万円'))
            
            property_containers = []
            for price_string in price_elements:
                parent = price_string.parent
                # Go up the DOM tree to find a reasonable container
                for _ in range(3):
                    if parent and parent.name in ['div', 'article', 'section', 'li']:
                        if parent not in property_containers:
                            property_containers.append(parent)
                        break
                    parent = parent.parent if parent else None
            
            property_elements = property_containers[:10]  # Limit to prevent too many
        
        # Extract data from each element
        for i, element in enumerate(property_elements, 1):
            try:
                property_data = self._extract_property_from_element(element, source_url)
                if property_data and self.validate_property_data(property_data):
                    properties.append(property_data)
                    logger.debug(f"Successfully extracted property {i}")
                    
            except Exception as e:
                logger.debug(f"Error extracting property {i}: {e}")
                continue
        
        return properties
    
    def _extract_property_from_element(self, element, source_url: str) -> Optional[PropertyData]:
        """Extract property data from a single element"""
        try:
            property_data = PropertyData()
            
            # Extract title
            title = self._extract_title_from_element(element)
            if title:
                property_data.title = title
            
            # Extract price
            price = self._extract_price_from_element(element)
            if price:
                property_data.price = price
            
            # Extract location
            location = self._extract_location_from_element(element)
            if location:
                property_data.location = location
            else:
                property_data.location = "軽井沢"  # Default since we're searching for Karuizawa
            
            # Extract property type
            prop_type = self._extract_property_type_from_element(element)
            if prop_type:
                property_data.property_type = prop_type
            
            # Extract size info
            size_info = self._extract_size_from_element(element)
            if size_info:
                property_data.size_info = size_info
            
            # Extract images
            images = self._extract_images_from_element(element)
            if images:
                property_data.image_urls = images
            
            # Extract detail URL
            detail_url = self._extract_detail_url_from_element(element, source_url)
            if detail_url:
                property_data.source_url = detail_url
            else:
                property_data.source_url = source_url
            
            # Set scraping timestamp
            property_data.scraped_at = time.time()
            
            return property_data
            
        except Exception as e:
            logger.error(f"Error extracting property data: {e}")
            return None
    
    def _extract_title_from_element(self, element) -> str:
        """Extract title from element"""
        title_selectors = ['h1', 'h2', 'h3', 'h4', '.title', '.name', '[class*="title"]', '[class*="name"]']
        
        for selector in title_selectors:
            title_elem = element.select_one(selector)
            if title_elem:
                title = title_elem.get_text(strip=True)
                if title and len(title) > 3:
                    return title
        
        return ""
    
    def _extract_price_from_element(self, element) -> str:
        """Extract price from element"""
        price_selectors = ['.price', '.amount', '[class*="price"]', '[class*="amount"]']
        
        # First try specific price selectors
        for selector in price_selectors:
            price_elem = element.select_one(selector)
            if price_elem:
                price_text = price_elem.get_text(strip=True)
                if '万円' in price_text or '¥' in price_text:
                    return price_text
        
        # Fallback: search in element text
        element_text = element.get_text()
        price_patterns = [
            r'\d+億[\d,]*万円',
            r'\d+億円',
            r'[\d,]+万円',
            r'¥[\d,]+'
        ]
        
        for pattern in price_patterns:
            matches = re.findall(pattern, element_text)
            if matches:
                return matches[0]
        
        return ""
    
    def _extract_location_from_element(self, element) -> str:
        """Extract location from element"""
        location_selectors = ['.location', '.area', '.address', '[class*="location"]', '[class*="area"]']
        
        for selector in location_selectors:
            location_elem = element.select_one(selector)
            if location_elem:
                location = location_elem.get_text(strip=True)
                if location and len(location) > 2:
                    return location
        
        return ""
    
    def _extract_property_type_from_element(self, element) -> str:
        """Extract property type from element"""
        element_text = element.get_text()
        
        if '一戸建て' in element_text:
            return '一戸建て'
        elif '土地' in element_text:
            return '土地'
        elif 'マンション' in element_text:
            return 'マンション'
        elif 'ヴィラ' in element_text or 'villa' in element_text.lower():
            return 'ヴィラ'
        elif '別荘' in element_text:
            return '別荘'
        
        return ""
    
    def _extract_size_from_element(self, element) -> str:
        """Extract size information from element"""
        element_text = element.get_text()
        
        size_patterns = [
            r'\d+[,.]?\d*\s*㎡',
            r'\d+[,.]?\d*\s*m²',
            r'\d+[,.]?\d*\s*坪'
        ]
        
        for pattern in size_patterns:
            matches = re.findall(pattern, element_text)
            if matches:
                return matches[0]
        
        return ""
    
    def _extract_images_from_element(self, element) -> List[str]:
        """Extract image URLs from element"""
        images = []
        
        img_elements = element.find_all('img')
        raw_images = []
        
        for img in img_elements:
            img_url = img.get('src') or img.get('data-src')
            if img_url:
                if img_url.startswith('//'):
                    img_url = 'https:' + img_url
                elif img_url.startswith('/'):
                    img_url = urljoin(self.base_url, img_url)
                elif not img_url.startswith('http'):
                    img_url = urljoin(self.base_url, img_url)
                
                if img_url not in raw_images:
                    raw_images.append(img_url)
        
        # Use helper method to filter images
        images = self.filter_property_images(raw_images)
        
        return images
    
    def _extract_detail_url_from_element(self, element, base_url: str) -> str:
        """Extract detail page URL from element"""
        link_selectors = ['a[href*="property"]', 'a[href*="bukken"]', 'a[href*="detail"]', 'a']
        
        for selector in link_selectors:
            link_elem = element.select_one(selector)
            if link_elem:
                href = link_elem.get('href')
                if href:
                    if href.startswith('/'):
                        detail_url = urljoin(self.base_url, href)
                    elif href.startswith('http'):
                        detail_url = href
                    else:
                        detail_url = urljoin(base_url, href)
                    
                    if self._is_property_url(detail_url):
                        return detail_url
        
        return base_url
    
    def _is_property_url(self, url: str) -> bool:
        """Check if URL appears to be a property detail page"""
        if not url:
            return False
        
        if url.startswith(('javascript:', '#', 'mailto:')):
            return False
        
        property_keywords = ['property', 'bukken', 'listing', 'detail', 'besso']
        url_lower = url.lower()
        
        return any(keyword in url_lower for keyword in property_keywords)
    
    def validate_property_data(self, property_data: PropertyData) -> bool:
        """Validate Besso Navi property data"""
        try:
            # Basic validation from parent class
            if not super().validate_property_data(property_data):
                return False
            
            # Must have at least title OR price
            if not property_data.title and not property_data.price:
                logger.debug("Missing both title and price")
                return False
            
            # Set default location if missing
            if not property_data.location:
                property_data.location = "軽井沢"
            
            logger.debug("Besso Navi HTTP property validation passed")
            return True
            
        except Exception as e:
            logger.error(f"Validation error: {e}")
            return False