"""
Base scraper classes for Karui-Search project
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime
import time
import random
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class PropertyData:
    """Simplified V1 property data structure"""
    title: str = ""
    price: str = ""
    location: str = ""
    property_type: str = ""
    size_info: str = ""
    building_age: str = ""
    description: str = ""
    image_urls: List[str] = field(default_factory=list)
    rooms: str = ""
    source_url: str = ""
    scraped_date: datetime = field(default_factory=datetime.now)
    
    def is_valid(self) -> bool:
        """Check if property has required fields"""
        return bool(self.title and self.price and self.location and self.source_url)
    
    def contains_karuizawa(self) -> bool:
        """Check if property is related to Karuizawa"""
        karuizawa_keywords = ["軽井沢", "karuizawa", "Karuizawa"]
        text_to_check = f"{self.title} {self.location} {self.description}".lower()
        return any(keyword.lower() in text_to_check for keyword in karuizawa_keywords)

class RateLimiter:
    """Simple rate limiter for ethical scraping"""
    
    def __init__(self, requests_per_second: float = 0.33):
        self.min_delay = 1.0 / requests_per_second
        self.last_request_time = 0
        
    def wait_if_needed(self):
        """Wait if necessary to respect rate limit"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_delay:
            sleep_time = self.min_delay - time_since_last
            # Add random jitter
            sleep_time += random.uniform(0.5, 1.5)
            logger.info(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
            time.sleep(sleep_time)
            
        self.last_request_time = time.time()

class AbstractPropertyScraper(ABC):
    """Base class for all property scrapers"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.base_url = config.get('base_url', '')
        
        # Handle rate limit config format
        rate_limit = config.get('rate_limit', 0.33)
        if isinstance(rate_limit, dict):
            rate_limit = rate_limit.get('requests_per_second', 0.33)
        
        self.rate_limiter = RateLimiter(rate_limit)
        self.session = requests.Session()
        self.setup_session()
        
    def setup_session(self):
        """Configure HTTP session with browser-like headers"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ja,en-US;q=0.7,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        self.session.headers.update(headers)
        
    def safe_request(self, url: str) -> Optional[requests.Response]:
        """Make a safe HTTP request with rate limiting and error handling"""
        try:
            self.rate_limiter.wait_if_needed()
            logger.info(f"Requesting: {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed for {url}: {e}")
            return None
            
    @abstractmethod
    def scrape_listings(self) -> List[PropertyData]:
        """Main method to scrape property listings"""
        pass

class SimpleScraper(AbstractPropertyScraper):
    """Scraper for static HTML sites using requests + BeautifulSoup"""
    
    def get_soup(self, url: str) -> Optional[BeautifulSoup]:
        """Get BeautifulSoup object from URL"""
        response = self.safe_request(url)
        if response:
            return BeautifulSoup(response.content, 'html.parser')
        return None
        
    def extract_text_safely(self, element, selector: str) -> str:
        """Safely extract text from element using CSS selector"""
        if not element:
            return ""
        found = element.select_one(selector)
        return found.get_text(strip=True) if found else ""
        
    def extract_attribute_safely(self, element, selector: str, attribute: str) -> str:
        """Safely extract attribute from element using CSS selector"""
        if not element:
            return ""
        found = element.select_one(selector)
        return found.get(attribute, "") if found else ""
        
    def validate_property_data(self, data: PropertyData) -> bool:
        """Validate property data against business rules"""
        if not data.is_valid():
            logger.warning(f"Property missing required fields: {data.title}")
            return False
            
        if not data.contains_karuizawa():
            logger.warning(f"Property not related to Karuizawa: {data.title}")
            return False
            
        # Basic price validation (if parseable)
        try:
            # Parse Japanese price formats properly
            import re
            price_value = self._parse_japanese_price(data.price)
            
            if price_value and (price_value < 1000000 or price_value > 5000000000):  # 1M to 5B yen range
                logger.warning(f"Price out of range: {data.price} (calculated: {price_value:,} yen)")
                return False
        except (ValueError, IndexError):
            # If we can't parse price, that's ok for V1
            pass
            
        return True
    
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
    
    def _parse_japanese_price(self, price_string: str) -> Optional[int]:
        """
        Parse Japanese price formats properly, handling 億円 and 万円 combinations.
        Examples:
        - "3億5,000万円" -> 350000000
        - "1億円" -> 100000000  
        - "5,000万円" -> 50000000
        - "¥350000000" -> 350000000
        """
        if not price_string:
            return None
            
        import re
        
        # Handle complex format: 3億5,000万円
        if '億' in price_string and '万円' in price_string:
            match = re.match(r'(\d+)億([0-9,]+)万円', price_string)
            if match:
                oku_part = int(match.group(1))  # 3
                man_part = int(match.group(2).replace(',', ''))  # 5000
                return oku_part * 100000000 + man_part * 10000  # 3*100M + 5000*10K = 350M
        
        # Handle 億円 only: 1億円
        if '億円' in price_string:
            match = re.search(r'(\d+)億円', price_string)
            if match:
                return int(match.group(1)) * 100000000  # 1*100M = 100M
        
        # Handle 万円 only: 5,000万円
        if '万円' in price_string:
            match = re.search(r'([0-9,]+)万円', price_string)
            if match:
                return int(match.group(1).replace(',', '')) * 10000  # 5000*10K = 50M
        
        # Handle regular numbers: ¥350000000, 350,000,000円
        numbers = re.findall(r'[0-9,]+', price_string)
        if numbers:
            return int(numbers[0].replace(',', ''))
            
        return None