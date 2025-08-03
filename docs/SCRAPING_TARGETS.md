# Scraping Targets for Karuizawa Real Estate

## Target Websites

### Top Priority Targets (Batch 1)

#### 1. Royal Resort Karuizawa (Priority: 1)
- **URL**: https://www.royal-resort.co.jp/karuizawa/
- **Focus Area**: Luxury vacation homes and resort properties in Karuizawa
- **Data Available**:
  - High-end vacation home listings
  - Detailed property specifications
  - Professional property photos
  - Resort amenities and features
- **Scraping Complexity**: Low to Medium
- **Rate Limiting**: Conservative (1-2 requests per second)
- **Notes**: Specialized in luxury Karuizawa resort properties

#### 2. Besso Navi (別荘ナビ) (Priority: 2)
- **URL**: https://www.besso-navi.com/b-search
- **Focus Area**: Vacation homes and resort properties
- **Data Available**:
  - Vacation home listings across Japan
  - Property details and amenities
  - Location and access information
  - Property management services
- **Scraping Complexity**: Medium
- **Rate Limiting**: Moderate (1-2 requests per second)
- **Notes**: Specialized vacation home portal

#### 3. Mitsui no Mori Karuizawa (Priority: 3)
- **URL**: https://www.mitsuinomori.co.jp/karuizawa/#searchBox
- **Focus Area**: Mitsui-developed properties in Karuizawa
- **Data Available**:
  - Premium resort properties
  - Land plots and custom homes
  - Community amenities
  - Development information
- **Scraping Complexity**: Medium
- **Rate Limiting**: Conservative (1 request per second)
- **Notes**: Major developer with exclusive Karuizawa properties

### Secondary Targets (Batch 2)

#### 4. Resort Innovation (Priority: 4)
- **URL**: https://www.resortinnovation.com/for-sale.html
- **Focus Area**: Resort properties for sale
- **Data Available**:
  - Resort property listings
  - Investment properties
  - Property specifications
  - Market analysis
- **Scraping Complexity**: Low to Medium
- **Rate Limiting**: Conservative (1 request per second)
- **Notes**: Focus on resort real estate investment

#### 5. Tokyu Resort Karuizawa (Priority: 5)
- **URL**: https://www.tokyu-resort.co.jp/karuizawa/
- **Focus Area**: Tokyu-developed resort properties
- **Data Available**:
  - Resort community properties
  - Vacation home rentals and sales
  - Community amenities
  - Property management services
- **Scraping Complexity**: Medium
- **Rate Limiting**: Conservative (1 request per second)
- **Notes**: Established resort developer with premium properties

#### 6. Resort Home (Priority: 6)
- **URL**: https://www.resort-home.jp/
- **Focus Area**: Resort and vacation homes nationwide
- **Data Available**:
  - Vacation home listings
  - Resort property sales
  - Property management services
  - Market information
- **Scraping Complexity**: Medium
- **Rate Limiting**: Moderate (1-2 requests per second)
- **Notes**: National resort property platform

### Lower Priority Targets (Batch 3)

#### 7. Seibu Real Estate Karuizawa (Priority: 7)
- **URL**: https://resort.seiburealestate-pm.co.jp/karuizawa/property/list/
- **Focus Area**: Seibu resort properties in Karuizawa
- **Data Available**:
  - Resort property listings
  - Property management services
  - Rental and purchase options
  - Community facilities
- **Scraping Complexity**: Medium
- **Rate Limiting**: Moderate (1-2 requests per second)
- **Notes**: Major resort developer and property manager

#### 8. SUUMO (スーモ) (Priority: 8)
- **URL**: https://suumo.jp/
- **Focus Area**: Karuizawa properties
- **Data Available**: 
  - Rental and purchase properties
  - Detailed specifications (size, age, amenities)
  - Multiple property images
  - Location maps and nearby facilities
  - Price history information
- **Scraping Complexity**: Medium (requires pagination handling)
- **Rate Limiting**: Moderate (2-3 requests per second)
- **Notes**: Japan's largest real estate portal

## Scraping Strategy

### Data Fields to Extract

#### Essential Fields (V1 - Simplified)
```
- title: String (property title/name)
- price: String (keep original format: "5,800万円", "¥58,000,000", etc.)
- location: String (address/area as displayed on site)
- property_type: String (house/apartment/land - as shown on site)
- size_info: String (land/building sizes as displayed: "土地:200㎡ 建物:150㎡")
- building_age: String (age as displayed: "築15年", "新築", "平成20年建築")
- source_url: String (original listing URL)
- scraped_date: Date (when data was collected)
```

#### Optional Fields (V1)
```
- description: String (property description text)
- image_urls: Array[String] (up to 5 main images)
- rooms: String (layout like "3LDK", "4SLDK")
```

### Technical Implementation

#### Enhanced Ethical Scraping Configuration
```yaml
site_name: "royal_resort"
base_url: "https://www.royal-resort.co.jp"
search_endpoints:
  - "/karuizawa/"
selectors:
  property_list: ".property-item"
  title: ".property-title"
  price: ".price-display"
  location: ".location-info"
  images: ".property-images img"

# Conservative rate limiting
rate_limit:
  requests_per_second: 0.33  # 1 request every 3 seconds
  random_delay_range: [1, 2]  # ±1-2 seconds jitter
  max_requests_per_hour: 80   # Conservative hourly limit
  respect_server_delay: true  # Back off if responses slow

# Browser-like headers (rotated)
headers:
  base_headers:
    Accept: "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
    Accept-Language: "ja,en-US;q=0.7,en;q=0.3"
    Accept-Encoding: "gzip, deflate, br"
    DNT: "1"
    Connection: "keep-alive"
    Upgrade-Insecure-Requests: "1"
    Sec-Fetch-Dest: "document"
    Sec-Fetch-Mode: "navigate"
    Sec-Fetch-Site: "none"
  
  # Rotating user agent pool (modern browsers only)
  user_agents:
    - "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    - "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    - "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0"
    - "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15"
    - "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# Human-like browsing patterns
browsing_behavior:
  start_from_homepage: true
  follow_natural_navigation: true
  session_duration: [300, 900]  # 5-15 minutes per session
  pages_per_session: [5, 20]    # Realistic page views
  scroll_simulation: true       # For JS-heavy sites
  active_hours: [9, 18]         # Business hours JST only
```

#### Enhanced Anti-Detection Measures

**Request Patterns:**
- **Natural Navigation**: Always start from homepage, follow site structure naturally
- **Realistic Timing**: Random delays between 2-5 seconds, longer pauses between sections
- **Session Management**: Maintain cookies and sessions like real browsers
- **Time-Aware Scraping**: Only scrape during business hours (9 AM - 6 PM JST)

**Browser Simulation:**
- **Complete Headers**: Include all standard browser headers (Accept, DNT, Sec-Fetch, etc.)
- **User Agent Rotation**: Pool of 5+ modern browser signatures, rotated per session
- **Referrer Handling**: Set appropriate referrer headers when following links
- **Viewport Simulation**: Include realistic screen resolution and viewport headers

**Infrastructure Protection:**
- **Progressive Backoff**: Increase delays if servers respond slowly
- **Circuit Breaker**: Stop scraping if error rate exceeds 10%
- **Health Monitoring**: Track response times and adjust behavior
- **Proxy Rotation**: Optional residential proxy rotation for high-value sites

**Advanced Techniques:**
- **JavaScript Execution**: Use Selenium for SPA sites that require JS
- **Form Interaction**: Simulate search form usage where appropriate
- **Cookie Management**: Accept and manage cookies like real browsers
- **Cache Behavior**: Respect cache headers and ETags

#### Error Handling
- Retry failed requests with exponential backoff
- Handle CAPTCHA detection gracefully
- Log failed scraping attempts
- Fallback to alternative data sources

### Data Quality Assurance

#### Validation Rules (V1 - Simplified)
- Required fields: title, price, location, source_url, scraped_date
- Location must contain Karuizawa-related keywords (軽井沢, karuizawa)
- Price range validation: ¥1,000,000 - ¥500,000,000 (when parseable)
- Source URL must be valid and accessible
- Building age optional but recommended for houses/apartments
- Image URLs must be valid if provided (max 5 images)
- Description truncated at 2000 characters

#### Deduplication Strategy
- Hash property details to detect exact duplicates
- Use fuzzy matching for similar properties
- Track properties across multiple sources
- Handle updates vs. new listings

### Compliance and Ethics

#### Legal and Ethical Requirements

**Robots.txt Compliance:**
- Check robots.txt before each scraping session
- Respect crawl-delay directives (minimum 2 seconds even if robots.txt allows faster)
- Honor disallow directives completely
- Re-check robots.txt weekly for updates

**Rate Limiting and Server Respect:**
- Never exceed 1 request per 2 seconds for any site
- Maximum 80 requests per hour per site (conservative limit)
- Progressive backoff if server response times increase
- Complete stop if site returns 429 (Too Many Requests) or 503 (Service Unavailable)
- Monitor for performance impact and adjust accordingly

**Japanese Legal Compliance:**
- Comply with Personal Information Protection Act (PIPA)
- Don't collect personal contact information
- Respect copyright on property descriptions and images
- Provide clear attribution to original sources in all displays

#### Data Collection Ethics

**Public Data Only:**
- Only scrape publicly accessible property listings
- Avoid premium/member-only content
- Don't attempt to bypass login requirements
- Skip any data marked as private or confidential

**Content Respect:**
- Don't store or redistribute copyrighted images
- Store only image URLs, not actual image files
- Include source attribution for all property data
- Respect image copyright and usage rights

**Privacy Protection:**
- Anonymize any accidentally collected personal data
- Don't scrape contact information (phone, email, names)
- Exclude any personally identifiable information from storage
- Implement data retention limits (remove old listings)

#### Best Practices and Monitoring

**Proactive Monitoring:**
- Daily success rate monitoring (alert if <90%)
- Weekly compliance audits and robots.txt checks  
- Monthly review of target site terms of service
- Quarterly assessment of scraping patterns and impacts

**Responsible Implementation:**
- Start with minimal scraping and gradually increase if no issues
- Implement "good citizen" mode during peak hours (slower rates)
- Provide clear identification in User-Agent string
- Maintain detailed logs for compliance documentation

**Error Response Protocols:**
- Immediate stop on CAPTCHA detection
- 24-hour pause on IP blocking detection  
- Exponential backoff on repeated errors (max 3 retries)
- Manual review required before resuming after blocks

## Implementation Priority

### Phase 1: Top Priority Batch (Weeks 1-3)
- Royal Resort Karuizawa scraper implementation
- Besso Navi scraper
- Mitsui no Mori scraper
- Basic data pipeline and database storage
- Deduplication logic for batch 1

### Phase 2: Secondary Batch (Weeks 4-6)
- Resort Innovation scraper
- Tokyu Resort scraper
- Resort Home scraper
- Enhanced data processing
- Cross-batch deduplication

### Phase 3: Final Batch (Weeks 7-8)
- Seibu Real Estate scraper
- SUUMO scraper
- Complete system integration
- Performance optimization and monitoring

## Monitoring and Maintenance

### Health Checks
- Daily scraping success rates
- Data quality metrics
- Website availability monitoring
- Rate limiting compliance

### Maintenance Tasks
- Weekly scraper validation
- Monthly target site review
- Quarterly compliance audit
- Continuous performance optimization

### Alerting
- Failed scraping runs
- Data quality issues
- Rate limit violations
- Target site structure changes