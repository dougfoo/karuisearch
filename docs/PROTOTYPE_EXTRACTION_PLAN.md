# Prototype Data Extraction Plan - First 3 Sites

## Overview

This document outlines a practical prototype plan for extracting property data from the first 3 target sites. Each site requires a different approach based on its technical complexity and data structure.

---

## Site 1: Royal Resort Karuizawa (Priority 1)
**URL**: https://www.royal-resort.co.jp/karuizawa/  
**Complexity**: High (JavaScript-heavy)  
**Recommended Technology**: BrowserScraper (Selenium)

### **Data Available for Extraction**
```yaml
Extractable Fields:
  ✅ title: Property name/description
  ✅ price: Listed price 
  ✅ location: Area/neighborhood in Karuizawa
  ✅ property_type: House/Land/Apartment
  ✅ size_info: Building size, land size
  ✅ rooms: Layout like "2LDK", "3SLDK"
  ✅ image_urls: Property photos (multiple)
  ⚪ building_age: May be available in details
  ⚪ description: Property descriptions
```

### **Technical Implementation Approach**
```python
class RoyalResortScraper(BrowserScraper):
    """Selenium-based scraper for Royal Resort"""
    
    def scrape_listings(self):
        """
        1. Navigate to /karuizawa/ homepage
        2. Handle dynamic content loading
        3. Find property cards (.p-card or similar)
        4. Extract basic data from cards
        5. Follow links for detailed information
        6. Handle pagination if present
        """
        
    def extract_property_card(self, card_element):
        """Extract data from property listing card"""
        data = PropertyData()
        
        # Price - look for price display elements
        data.price = card_element.select('.price, .amount, [class*="price"]')
        
        # Location - area/neighborhood info
        data.location = card_element.select('.area, .location, [class*="area"]')
        
        # Property type and room layout
        data.rooms = card_element.select('.layout, .rooms, [class*="room"]')
        
        # Images
        images = card_element.select('img')
        data.image_urls = [img.get('src') for img in images[:5]]
        
        return data
```

### **Specific CSS Selectors to Try**
```css
/* Property cards */
.p-card, .property-card, .listing-item, .property-item

/* Price elements */
.price, .amount, .cost, [class*="price"], [class*="amount"]

/* Location/area */
.area, .location, .address, [class*="area"], [class*="location"]

/* Room layout */
.layout, .rooms, .madori, [class*="room"], [class*="layout"]

/* Images */
.property-img img, .listing-img img, .thumbnail img
```

### **Expected Data Quality**
- **High completeness**: Premium site likely has complete data
- **Rich descriptions**: Luxury properties typically well-documented
- **Multiple images**: Professional property photography
- **Potential challenges**: Anti-bot measures, dynamic loading

---

## Site 2: Besso Navi (Priority 2)
**URL**: https://www.besso-navi.com/b-search  
**Complexity**: Medium (Form-based with JavaScript)  
**Recommended Technology**: BrowserScraper (for forms) or AjaxScraper

### **Data Available for Extraction**
```yaml
Extractable Fields:
  ✅ title: Villa/property names
  ✅ price: Listed prices
  ✅ location: Karuizawa area selections
  ✅ property_type: Land/House/Apartment (from form)
  ✅ size_info: Land area ranges available
  ⚪ rooms: May be in property details
  ⚪ image_urls: Depends on listing format
  ⚪ building_age: May be available
  ⚪ description: Property descriptions
```

### **Technical Implementation Approach**
```python
class BessoNaviScraper(BrowserScraper):
    """Form-based scraper for Besso Navi"""
    
    def scrape_listings(self):
        """
        1. Navigate to /b-search
        2. Fill search form with Karuizawa parameters
        3. Submit form and wait for results
        4. Extract property data from results
        5. Handle pagination if present
        """
        
    def setup_search_parameters(self):
        """Configure search form for Karuizawa properties"""
        # Area selection - check Karuizawa-related areas
        self.driver.find_elements(By.CSS_SELECTOR, 'input[type="checkbox"]')
        
        # Property type - all types
        self.driver.find_element(By.CSS_SELECTOR, 'select[name*="type"]')
        
        # Price range - broad range
        self.driver.find_element(By.CSS_SELECTOR, 'select[name*="price"]')
        
    def extract_search_results(self):
        """Extract property data from search results page"""
        # Look for result containers
        results = self.driver.find_elements(By.CSS_SELECTOR, 
            '.result-item, .property-result, .search-result')
            
        for result in results:
            yield self.parse_result_item(result)
```

### **Form Parameters to Use**
```javascript
// Search form configuration
search_params = {
    areas: ["軽井沢", "中軽井沢", "南軽井沢"],  // Karuizawa areas
    property_types: ["土地", "一戸建て", "マンション"],  // All types
    price_min: "1000000",   // 1M yen minimum
    price_max: "500000000", // 500M yen maximum
    land_area_min: "100"    // 100 sqm minimum
}
```

### **Expected Data Quality**
- **Medium completeness**: Vacation home specialist, good data
- **Area focus**: Strong Karuizawa coverage
- **Mixed access**: Some properties public, others require contact
- **Potential challenges**: Form validation, session management

---

## Site 3: Mitsui no Mori (Priority 3)
**URL**: https://www.mitsuinomori.co.jp/karuizawa/  
**Complexity**: Medium-High (WordPress with some dynamic content)  
**Recommended Technology**: SimpleScraper + BrowserScraper fallback

### **Data Available for Extraction**
```yaml
Extractable Fields:
  ✅ title: Property names
  ✅ price: Listed prices  
  ✅ location: Karuizawa development areas
  ✅ property_type: 一戸建て (houses), 土地 (land)
  ✅ size_info: Size information
  ✅ image_urls: Thumbnail and detail images
  ⚪ rooms: May be in property details
  ⚪ building_age: For houses
  ⚪ description: Property descriptions available
```

### **Technical Implementation Approach**
```python
class MitsuiNoMoriScraper(SimpleScraper):
    """Static HTML scraper for Mitsui no Mori"""
    
    def scrape_listings(self):
        """
        1. Start from /karuizawa/ homepage
        2. Find property listing sections
        3. Parse property cards directly from HTML
        4. Follow links to detailed pages
        5. Handle category navigation (houses vs land)
        """
        
    def find_property_listings(self):
        """Locate property listing containers"""
        response = self.session.get(self.base_url + "/karuizawa/")
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Look for property containers
        containers = soup.select('.property-list, .bukken-list, .item-list')
        
        for container in containers:
            properties = container.select('.property-item, .bukken-item, .item')
            for prop in properties:
                yield self.extract_property_data(prop)
                
    def extract_property_data(self, element):
        """Extract data from property element"""
        data = PropertyData()
        
        # Title
        title_elem = element.select_one('.title, .name, h3, h4')
        data.title = title_elem.get_text(strip=True) if title_elem else ""
        
        # Price
        price_elem = element.select_one('.price, .amount, [class*="price"]')
        data.price = price_elem.get_text(strip=True) if price_elem else ""
        
        # Link to details
        link_elem = element.select_one('a[href]')
        if link_elem:
            detail_url = urljoin(self.base_url, link_elem['href'])
            # Fetch detailed information
            detailed_data = self.get_property_details(detail_url)
            data.update(detailed_data)
            
        return data
```

### **Specific CSS Selectors to Try**
```css
/* Property containers */
.property-list, .bukken-list, .item-list, .properties

/* Individual properties */
.property-item, .bukken-item, .item, .property

/* Content elements */
.title, .name, .bukken-name
.price, .amount, .kakaku
.area, .location, .basho
.size, .menseki, .tsubo
```

### **Expected Data Quality**
- **High completeness**: Major developer, comprehensive data
- **Premium properties**: High-quality listings
- **Structured data**: Well-organized WordPress site
- **Potential challenges**: Premium access restrictions, limited public data

---

## Prototype Implementation Plan

### **Phase 1: Basic Data Extraction (Week 1)**
```python
# Create minimal working scrapers for each site
class PrototypeScraper:
    def extract_basic_data(self, url):
        """Extract just title, price, location for proof of concept"""
        
    def validate_karuizawa_content(self, data):
        """Ensure data contains Karuizawa-related keywords"""
        
    def save_to_csv(self, data):
        """Save prototype data for analysis"""
```

### **Phase 2: Enhanced Extraction (Week 2)**
```python
# Add complete field extraction and validation
class EnhancedScraper:
    def extract_complete_data(self, url):
        """Extract all available fields"""
        
    def handle_images(self, data):
        """Extract and validate image URLs"""
        
    def apply_business_rules(self, data):
        """Price range, location validation"""
```

### **Success Metrics for Prototype**
```yaml
Site 1 (Royal Resort):
  Target: 20+ properties extracted
  Required: title, price, location
  Success: >80% data completeness

Site 2 (Besso Navi):
  Target: 15+ properties extracted  
  Required: title, price, location
  Success: Form submission works, data extracted

Site 3 (Mitsui no Mori):
  Target: 10+ properties extracted
  Required: title, price, location
  Success: Static scraping successful
```

### **Risk Mitigation**
```yaml
Technical Risks:
  - Anti-bot detection: Start with conservative rate limits
  - Dynamic content: Fallback to simpler extraction methods
  - Site changes: Version control for selectors

Data Risks:
  - Empty results: Validate selectors manually first
  - Invalid data: Implement strict validation
  - Duplicate detection: Hash-based deduplication
```

This prototype plan focuses on proving the core extraction concept works for each site before building the full architecture.