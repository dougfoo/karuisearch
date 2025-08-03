# Karui-Search Scraper Architecture Design

## Overview

The scraper architecture follows a modular, extensible design that can handle different types of real estate websites with varying complexity levels - from simple static HTML to complex JavaScript-heavy SPAs.

## Core Architecture Principles

### 1. **Modularity**
- Each scraper is independent and configurable
- Common functionality abstracted into base classes
- Site-specific logic encapsulated in individual scrapers

### 2. **Scalability** 
- Support for multiple concurrent scrapers
- Configurable rate limiting per site
- Easy addition of new target sites

### 3. **Resilience**
- Robust error handling and retry mechanisms
- Circuit breaker pattern for failing sites
- Graceful degradation when sites are unavailable

### 4. **Ethical Compliance**
- Built-in rate limiting and politeness policies
- robots.txt compliance checking
- Human-like browsing patterns

## Class Hierarchy Design

```
AbstractPropertyScraper (ABC)
├── BaseHttpScraper
│   ├── SimpleScraper (requests + BeautifulSoup)
│   └── AjaxScraper (requests + API endpoints)
└── BrowserScraper (Selenium/Playwright)
    ├── SeleniumScraper
    └── PlaywrightScraper
```

## Core Components

### 1. Abstract Base Class

```python
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class PropertyData:
    """Simplified V1 property data structure"""
    title: str
    price: str
    location: str
    property_type: Optional[str] = None
    size_info: Optional[str] = None
    building_age: Optional[str] = None
    description: Optional[str] = None
    image_urls: List[str] = None
    rooms: Optional[str] = None
    source_url: str = ""
    scraped_date: datetime = None

class AbstractPropertyScraper(ABC):
    """Base class for all property scrapers"""
    
    def __init__(self, config: Dict, rate_limiter: RateLimiter):
        self.config = config
        self.rate_limiter = rate_limiter
        self.session_manager = SessionManager()
        self.error_handler = ErrorHandler()
        
    @abstractmethod
    def scrape_listings(self) -> List[PropertyData]:
        """Main method to scrape property listings"""
        pass
        
    @abstractmethod
    def get_property_details(self, url: str) -> Optional[PropertyData]:
        """Get detailed information for a single property"""
        pass
        
    @abstractmethod
    def validate_robots_txt(self) -> bool:
        """Check if scraping is allowed by robots.txt"""
        pass
```

### 2. HTTP-Based Scrapers

#### SimpleScraper (Static HTML)
```python
class SimpleScraper(AbstractPropertyScraper):
    """For simple HTML sites with minimal JavaScript"""
    
    def __init__(self, config: Dict, rate_limiter: RateLimiter):
        super().__init__(config, rate_limiter)
        self.session = requests.Session()
        self.setup_headers()
        
    def scrape_listings(self) -> List[PropertyData]:
        """
        1. Start from homepage
        2. Navigate to property listings
        3. Parse property cards
        4. Extract data using CSS selectors
        5. Follow pagination links
        """
        pass
        
    def parse_property_card(self, element) -> PropertyData:
        """Extract data from a property listing card"""
        pass
```

#### AjaxScraper (API Endpoints)
```python
class AjaxScraper(AbstractPropertyScraper):
    """For sites with AJAX APIs and JSON responses"""
    
    def scrape_listings(self) -> List[PropertyData]:
        """
        1. Discover API endpoints
        2. Replicate search requests
        3. Parse JSON responses
        4. Handle pagination via API
        """
        pass
        
    def discover_api_endpoints(self) -> Dict[str, str]:
        """Analyze network requests to find API URLs"""
        pass
```

### 3. Browser-Based Scrapers

#### BrowserScraper (JavaScript Sites)
```python
class BrowserScraper(AbstractPropertyScraper):
    """For complex JavaScript-heavy sites"""
    
    def __init__(self, config: Dict, rate_limiter: RateLimiter):
        super().__init__(config, rate_limiter)
        self.driver = None
        self.setup_browser()
        
    def scrape_listings(self) -> List[PropertyData]:
        """
        1. Launch browser in stealth mode
        2. Navigate naturally through site
        3. Handle dynamic content loading
        4. Simulate human interactions
        5. Extract data after JS execution
        """
        pass
        
    def simulate_human_behavior(self):
        """Add realistic delays, scrolling, mouse movements"""
        pass
```

## Supporting Components

### 1. Rate Limiter
```python
class RateLimiter:
    """Enforce ethical rate limiting per site"""
    
    def __init__(self, requests_per_second: float, burst_limit: int = 5):
        self.rps = requests_per_second
        self.burst_limit = burst_limit
        self.last_request_time = {}
        
    def wait_if_needed(self, site_id: str):
        """Block until it's safe to make another request"""
        pass
        
    def add_random_delay(self, min_delay: float, max_delay: float):
        """Add human-like random delays"""
        pass
```

### 2. Session Manager
```python
class SessionManager:
    """Manage browser sessions and cookies"""
    
    def __init__(self):
        self.sessions = {}
        self.user_agents = UserAgentRotator()
        
    def get_session(self, site_id: str) -> requests.Session:
        """Get or create session for a site"""
        pass
        
    def rotate_user_agent(self, session: requests.Session):
        """Rotate user agent for session"""
        pass
```

### 3. Error Handler
```python
class ErrorHandler:
    """Centralized error handling and circuit breaker"""
    
    def __init__(self):
        self.error_counts = {}
        self.circuit_breakers = {}
        
    def handle_error(self, site_id: str, error: Exception) -> bool:
        """
        Handle errors and decide whether to continue
        Returns True if scraping should continue
        """
        pass
        
    def is_circuit_open(self, site_id: str) -> bool:
        """Check if circuit breaker is open for a site"""
        pass
```

### 4. Scraper Factory
```python
class ScraperFactory:
    """Factory pattern for creating appropriate scrapers"""
    
    SCRAPER_TYPES = {
        'simple': SimpleScraper,
        'ajax': AjaxScraper,
        'browser': BrowserScraper
    }
    
    @classmethod
    def create_scraper(cls, site_config: Dict) -> AbstractPropertyScraper:
        """Create appropriate scraper based on site configuration"""
        scraper_type = site_config.get('scraper_type', 'simple')
        scraper_class = cls.SCRAPER_TYPES[scraper_type]
        
        rate_limiter = RateLimiter(
            requests_per_second=site_config['rate_limit'],
            burst_limit=site_config.get('burst_limit', 5)
        )
        
        return scraper_class(site_config, rate_limiter)
```

## Configuration System

### Site Configuration Format
```yaml
# Example: Royal Resort Karuizawa
royal_resort:
  name: "Royal Resort Karuizawa"
  base_url: "https://www.royal-resort.co.jp"
  scraper_type: "browser"  # simple, ajax, browser
  
  # Rate limiting
  rate_limit: 0.33  # requests per second
  burst_limit: 3
  max_concurrent: 1
  
  # Scraping rules
  selectors:
    property_list: ".property-item"
    title: ".property-title"
    price: ".price-display"
    location: ".location-info" 
    
  # Browser-specific settings
  browser:
    headless: true
    wait_timeout: 10
    page_load_timeout: 30
    
  # Navigation flow
  navigation:
    start_url: "/karuizawa/"
    search_form: "#property-search"
    pagination: ".pagination a"
    
  # Data extraction
  data_mapping:
    title: "text"
    price: "text"
    location: "text"
    images: "src"
```

## Scraping Workflow

### 1. Initialization Phase
```python
def initialize_scraping_session():
    """
    1. Load site configurations
    2. Check robots.txt for all sites
    3. Initialize scrapers via factory
    4. Set up monitoring and logging
    """
    pass
```

### 2. Discovery Phase  
```python
def discover_property_listings():
    """
    1. Start from homepage
    2. Find property listing pages
    3. Identify pagination structure
    4. Map data extraction points
    """
    pass
```

### 3. Extraction Phase
```python
def extract_property_data():
    """
    1. Navigate through property listings
    2. Extract basic property information
    3. Follow links for detailed information
    4. Handle pagination automatically
    """
    pass
```

### 4. Processing Phase
```python
def process_scraped_data():
    """
    1. Validate extracted data
    2. Apply business rules (price range, location)
    3. Detect and handle duplicates
    4. Store in database
    """
    pass
```

## Error Recovery Strategies

### 1. Network Errors
- Exponential backoff with jitter
- Automatic retry with different user agents
- Fallback to alternative endpoints

### 2. Anti-Bot Detection
- Immediate pause and circuit breaker activation
- User agent rotation
- Session reset and IP rotation (if available)

### 3. Site Structure Changes
- Graceful degradation with partial data
- Alerting system for developer intervention
- Automatic fallback to simpler selectors

### 4. Rate Limiting
- Automatic slowdown when rate limits detected
- Dynamic adjustment of request frequency
- Circuit breaker for persistent rate limiting

## Monitoring and Observability

### 1. Metrics Collection
```python
class ScrapingMetrics:
    """Collect scraping performance metrics"""
    
    def track_request(self, site_id: str, duration: float, success: bool):
        pass
        
    def track_data_quality(self, site_id: str, properties_found: int, 
                          validation_failures: int):
        pass
```

### 2. Logging Strategy
- Structured JSON logging
- Different log levels per component
- Correlation IDs for request tracing
- Performance timing logs

### 3. Health Checks
- Per-site success rate monitoring
- Response time tracking
- Data quality score tracking
- Circuit breaker status monitoring

## Security Considerations

### 1. Data Protection
- No storage of personal information
- Respect for copyright content
- Attribution of data sources

### 2. Infrastructure Security
- Secure configuration management
- No hardcoded credentials
- Network security best practices

### 3. Ethical Compliance
- Strict adherence to robots.txt
- Conservative rate limiting
- Transparent user agent identification
- Compliance monitoring and reporting

This architecture provides a solid foundation for ethical, scalable, and maintainable web scraping of Karuizawa real estate properties.