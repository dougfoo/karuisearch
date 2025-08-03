# Karui-Search Scraping Design Overview

## Executive Summary

This document outlines the complete scraping design for the Karui-Search project, covering architecture, site-specific strategies, data pipeline, and error handling. The design prioritizes ethical scraping practices, maintainability, and scalability while focusing on Karuizawa real estate data collection.

---

## A) Overall Scraper Architecture and Class Design

### **Architecture Principles**
- **Modular Design**: Independent scrapers with shared base functionality
- **Ethical First**: Built-in rate limiting, robots.txt compliance, human-like behavior
- **Technology Adaptive**: Support for static HTML, AJAX APIs, and JavaScript-heavy sites
- **Resilient**: Circuit breakers, retry mechanisms, graceful degradation

### **Class Hierarchy**
```
AbstractPropertyScraper (ABC)
├── BaseHttpScraper
│   ├── SimpleScraper (requests + BeautifulSoup)
│   └── AjaxScraper (requests + API endpoints)
└── BrowserScraper (Selenium/Playwright)
    ├── SeleniumScraper
    └── PlaywrightScraper
```

### **Core Components**
1. **AbstractPropertyScraper**: Base interface defining scraping contract
2. **RateLimiter**: Ethical request throttling with random delays
3. **SessionManager**: Browser session and cookie management
4. **ErrorHandler**: Circuit breaker and retry logic
5. **ScraperFactory**: Dynamic scraper creation based on site requirements

### **Configuration-Driven Approach**
- YAML-based site configurations
- Declarative selector mapping
- Runtime behavior modification without code changes

---

## B) Site-Specific Scraping Strategies

### **Site Classification by Complexity**

#### **Tier 1: Simple Static Sites**
- **Sites**: Resort Innovation, some smaller developers
- **Technology**: SimpleScraper (requests + BeautifulSoup)
- **Challenges**: Basic HTML parsing, simple pagination
- **Rate Limit**: 1 request every 3 seconds

#### **Tier 2: Form-Based Dynamic Sites**
- **Sites**: Besso Navi, Resort Home
- **Technology**: AjaxScraper or light BrowserScraper
- **Challenges**: Form submissions, search parameters, AJAX responses
- **Rate Limit**: 1 request every 2-3 seconds

#### **Tier 3: Complex JavaScript Sites**
- **Sites**: Royal Resort, Mitsui no Mori, Tokyu Resort
- **Technology**: BrowserScraper (full browser automation)
- **Challenges**: Dynamic content, AJAX pagination, anti-bot measures
- **Rate Limit**: 1 request every 3-4 seconds

### **Site-Specific Strategies**

#### **Royal Resort Karuizawa** (Priority 1)
```yaml
Complexity: High
Technology: BrowserScraper
Challenges:
  - Heavy JavaScript usage
  - AJAX-based search and pagination
  - Dynamic content loading
  - Premium site with potential anti-bot measures
Strategy:
  - Full browser automation with Selenium
  - Mimic human search patterns
  - Handle dynamic form submissions
  - Monitor for CAPTCHA systems
```

#### **Besso Navi** (Priority 2)
```yaml
Complexity: Medium
Technology: AjaxScraper or SimpleScraper
Challenges:
  - Search form submissions
  - Area-based filtering
  - Curated vs public listings
Strategy:
  - Analyze search form parameters
  - Extract public listings first
  - Handle area-based navigation
  - Respect "contact for more" boundaries
```

#### **Mitsui no Mori** (Priority 3)
```yaml
Complexity: High
Technology: BrowserScraper
Challenges:
  - Premium developer site
  - Sophisticated anti-bot measures
  - Limited public information
Strategy:
  - Stealth browser automation
  - Extra conservative rate limiting
  - Focus on public listing areas
  - Monitor for access restrictions
```

### **Common Navigation Patterns**
1. **Homepage Entry**: Always start from main site homepage
2. **Natural Flow**: Follow intended user navigation paths
3. **Search Simulation**: Use site's own search functionality
4. **Pagination Handling**: Adapt to each site's pagination style

---

## C) Data Pipeline and Processing Workflow

### **Pipeline Architecture**
```
Raw HTML/JSON → Extraction → Validation → Normalization → Storage
```

### **Phase 1: Data Extraction**
```python
Raw Data Collection:
- HTML content or API responses
- Image URLs and metadata
- Source attribution information

Extraction Process:
- CSS selector-based extraction
- Regex patterns for unstructured data
- JSON parsing for API responses
- Image URL collection (max 5 per property)
```

### **Phase 2: Data Validation**
```python
Required Field Validation:
- title: Must not be empty
- price: Must exist and contain numeric data
- location: Must contain Karuizawa keywords
- source_url: Must be valid URL

Business Rule Validation:
- Price range: ¥1,000,000 - ¥500,000,000
- Location: Must match Karuizawa areas
- Description: Truncate at 2000 characters
- Images: Validate URLs, limit to 5 maximum
```

### **Phase 3: Data Normalization**
```python
Simplified V1 Approach:
- Store prices as original strings ("5,800万円")
- Keep size info as displayed ("土地:200㎡ 建物:150㎡")
- Preserve building age format ("築15年", "新築")
- Maintain original Japanese text formatting

Future Enhancement Hooks:
- Price parsing to numeric values
- Size conversion to standard units
- Date standardization
- Location geocoding
```

### **Phase 4: Duplicate Detection**
```python
Duplicate Detection Strategy:
- Hash-based exact duplicate detection
- Fuzzy matching on title + location + price
- Cross-source deduplication
- Update vs new listing identification

Algorithm:
1. Generate content hash (title + price + location)
2. Check exact matches first
3. Apply fuzzy similarity scoring (>80% match)
4. Flag potential duplicates for review
```

### **Phase 5: Data Storage**
```python
Database Operations:
- Insert new properties
- Update existing properties
- Track data changes over time
- Maintain source attribution

Storage Format:
- Simplified property table (V1)
- JSON arrays for images
- String fields for flexible data
- Timestamp tracking for changes
```

### **Data Quality Scoring**
```python
Quality Factors:
- Required fields present: 40%
- Optional fields present: 30%
- Image availability: 20%
- Description quality: 10%

Quality Categories:
- High: 80%+ (complete data)
- Medium: 60-79% (good data)
- Low: <60% (minimal data)
```

---

## D) Error Handling and Resilience Mechanisms

### **Error Classification**

#### **Level 1: Network Errors**
```python
Temporary Issues:
- Connection timeouts
- DNS resolution failures
- Server 5xx errors

Response Strategy:
- Exponential backoff (1s, 2s, 4s)
- Maximum 3 retry attempts
- User agent rotation on retry
- Circuit breaker after consecutive failures
```

#### **Level 2: Anti-Bot Detection**
```python
Detection Indicators:
- HTTP 429 (Too Many Requests)
- CAPTCHA challenges
- Unusual redirects
- JavaScript challenges

Response Strategy:
- Immediate stop for current session
- 24-hour circuit breaker activation
- Alert human operator
- Review and adjust scraping parameters
```

#### **Level 3: Site Structure Changes**
```python
Change Types:
- CSS selector changes
- URL structure modifications
- New authentication requirements
- Layout redesigns

Response Strategy:
- Graceful degradation with partial data
- Alert system for developer intervention
- Fallback to simpler extraction methods
- Version compatibility tracking
```

### **Circuit Breaker Pattern**
```python
Circuit States:
- CLOSED: Normal operation
- OPEN: Failures exceed threshold, stop requests
- HALF_OPEN: Test single request after timeout

Thresholds:
- Failure rate: >20% in 10 requests
- Consecutive failures: >5
- Reset timeout: 1 hour for network, 24 hours for anti-bot
```

### **Monitoring and Alerting**
```python
Key Metrics:
- Success rate per site (target: >90%)
- Average response time (alert: >10s)
- Data quality scores (alert: <70%)
- Error rate trends

Alert Conditions:
- Circuit breaker activation
- Success rate below 80%
- No data collected for 24 hours
- Price validation failures >50%

Notification Channels:
- Console logging for development
- File logging for production
- Future: Email/Slack integration
```

### **Recovery Mechanisms**
```python
Automatic Recovery:
- Retry with exponential backoff
- User agent rotation
- Session reset and cleanup
- Fallback to alternative selectors

Manual Recovery:
- Configuration updates
- Selector rule modifications
- Rate limit adjustments
- Emergency stop mechanisms
```

### **Data Integrity Protection**
```python
Safeguards:
- Transaction-based database operations
- Data validation before storage
- Backup of raw scraped data
- Change tracking and audit logs

Rollback Capabilities:
- Revert problematic data imports
- Restore from backup snapshots
- Manual data correction tools
- Selective re-scraping of specific periods
```

---

## Implementation Roadmap

### **Phase 1: Foundation (Weeks 1-2)**
- Implement base scraper architecture
- Create SimpleScraper for basic sites
- Set up data pipeline and validation
- Implement basic error handling

### **Phase 2: Core Sites (Weeks 3-4)**
- Implement BrowserScraper for complex sites
- Add Royal Resort Karuizawa scraper
- Implement duplicate detection
- Add monitoring and alerting

### **Phase 3: Expansion (Weeks 5-6)**
- Add remaining target sites
- Implement advanced error recovery
- Performance optimization
- Data quality improvements

### **Phase 4: Production (Weeks 7-8)**
- Production deployment
- Monitoring dashboards
- Documentation completion
- User acceptance testing

---

## Success Criteria

### **Technical Metrics**
- **Reliability**: >90% success rate across all sites
- **Performance**: Complete daily scraping within 2 hours
- **Data Quality**: >80% of properties have complete essential data
- **Compliance**: Zero robots.txt violations

### **Business Metrics**
- **Coverage**: Collect from all 8 target sites
- **Freshness**: Daily data updates
- **Completeness**: >100 new properties per week
- **Accuracy**: <5% duplicate rate after processing

This design provides a comprehensive framework for ethical, scalable, and maintainable scraping of Karuizawa real estate data.