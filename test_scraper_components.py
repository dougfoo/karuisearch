#!/usr/bin/env python3
"""
Test cases for each component of the Mitsui no Mori scraper
"""
import sys
import os
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from scrapers.mitsui_scraper import MitsuiNoMoriScraper
from scrapers.base_scraper import PropertyData, RateLimiter

def test_rate_limiter():
    """Test the rate limiter component"""
    print("Testing Rate Limiter")
    print("-" * 30)
    
    # Test with 2 requests per second (0.5 second delay)
    limiter = RateLimiter(requests_per_second=2.0)
    
    start_time = datetime.now()
    
    # Make 3 requests
    for i in range(3):
        print(f"Request {i+1} at {datetime.now().strftime('%H:%M:%S.%f')[:-3]}")
        limiter.wait_if_needed()
        
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print(f"Total time: {duration:.2f} seconds")
    print(f"Expected minimum: ~1.5 seconds (3 requests with delays)")
    print("Rate limiter test completed\n")

def test_property_data_validation():
    """Test PropertyData validation methods"""
    print("Testing PropertyData Validation")
    print("-" * 30)
    
    # Test valid property
    valid_prop = PropertyData(
        title="軽井沢の美しい別荘",
        price="5,800万円",
        location="軽井沢町",
        source_url="https://example.com/property1"
    )
    
    print(f"Valid property check: {valid_prop.is_valid()}")
    print(f"Karuizawa check: {valid_prop.contains_karuizawa()}")
    
    # Test invalid property (missing required fields)
    invalid_prop = PropertyData(
        title="Nice house",
        location="Tokyo"
        # Missing price and source_url
    )
    
    print(f"Invalid property check: {invalid_prop.is_valid()}")
    print(f"Non-Karuizawa check: {invalid_prop.contains_karuizawa()}")
    print("✅ PropertyData validation test completed\n")

def test_http_connection():
    """Test basic HTTP connection to Mitsui no Mori"""
    print("🌐 Testing HTTP Connection")
    print("-" * 30)
    
    scraper = MitsuiNoMoriScraper()
    
    # Test connection to main page
    main_url = "https://www.mitsuinomori.co.jp/karuizawa/"
    print(f"Testing connection to: {main_url}")
    
    response = scraper.safe_request(main_url)
    
    if response:
        print(f"✅ Connection successful!")
        print(f"Status code: {response.status_code}")
        print(f"Content length: {len(response.content)} bytes")
        print(f"Content type: {response.headers.get('content-type', 'Unknown')}")
        
        # Check if page contains Karuizawa content
        content_text = response.text.lower()
        karuizawa_found = any(kw in content_text for kw in ['軽井沢', 'karuizawa'])
        print(f"Contains Karuizawa content: {karuizawa_found}")
        
    else:
        print("❌ Connection failed!")
        
    print("🌐 HTTP connection test completed\n")

def test_html_parsing():
    """Test HTML parsing and soup creation"""
    print("🍲 Testing HTML Parsing")
    print("-" * 30)
    
    scraper = MitsuiNoMoriScraper()
    
    # Get soup from main page
    main_url = "https://www.mitsuinomori.co.jp/karuizawa/"
    soup = scraper.get_soup(main_url)
    
    if soup:
        print("✅ HTML parsing successful!")
        
        # Test basic soup functionality
        title = soup.find('title')
        print(f"Page title: {title.get_text().strip() if title else 'Not found'}")
        
        # Look for common HTML elements
        links = soup.find_all('a', href=True)
        print(f"Links found: {len(links)}")
        
        images = soup.find_all('img')
        print(f"Images found: {len(images)}")
        
        # Look for price-related content
        price_patterns = soup.find_all(text=lambda text: text and ('万円' in text or '円' in text))
        print(f"Price-related text found: {len(price_patterns)}")
        
        # Look for property-related classes
        property_elements = soup.select('[class*="property"], [class*="bukken"], [class*="item"]')
        print(f"Potential property elements: {len(property_elements)}")
        
    else:
        print("❌ HTML parsing failed!")
        
    print("🍲 HTML parsing test completed\n")

def test_selector_patterns():
    """Test different CSS selector patterns"""
    print("🎯 Testing CSS Selector Patterns")
    print("-" * 30)
    
    scraper = MitsuiNoMoriScraper()
    soup = scraper.get_soup("https://www.mitsuinomori.co.jp/karuizawa/")
    
    if not soup:
        print("❌ Could not load page for selector testing")
        return
        
    # Test different selector strategies
    selectors_to_test = [
        ('.property-item', 'Property items'),
        ('.bukken-item', 'Bukken items'),
        ('.item', 'Generic items'),
        ('[class*="property"]', 'Property-related classes'),
        ('[class*="bukken"]', 'Bukken-related classes'),
        ('div:contains("万円")', 'Divs containing price'),
        ('h1, h2, h3, h4', 'Heading elements'),
        ('img[src]', 'Images with src'),
        ('a[href*="detail"]', 'Detail links'),
        ('a[href*="bukken"]', 'Property links')
    ]
    
    for selector, description in selectors_to_test:
        try:
            if ':contains(' in selector:
                # BeautifulSoup doesn't support :contains, skip for now
                print(f"  {description}: Skipped (not supported)")
                continue
                
            elements = soup.select(selector)
            print(f"  {description}: {len(elements)} elements")
            
            # Show sample content for first element
            if elements:
                sample_text = elements[0].get_text(strip=True)[:100]
                print(f"    Sample: {sample_text}...")
                
        except Exception as e:
            print(f"  {description}: Error - {e}")
            
    print("🎯 CSS selector test completed\n")

def test_data_extraction_patterns():
    """Test regex patterns for data extraction"""
    print("🔍 Testing Data Extraction Patterns")
    print("-" * 30)
    
    # Sample text that might be found on property pages
    sample_texts = [
        "軽井沢の豪華別荘 5,800万円 土地:300㎡ 建物:180㎡ 築15年 3LDK",
        "Karuizawa Premium House ¥58,000,000 Land: 300sqm Building: 180sqm",
        "中軽井沢エリア 土地売り 2,200万円 500坪",
        "新築一戸建て 軽井沢町 平成30年建築 4SLDK",
        "価格：3,500万円　所在地：長野県北佐久郡軽井沢町",
    ]
    
    import re
    
    # Test price patterns
    price_patterns = [
        r'[\d,]+\s*万円',
        r'¥[\d,]+',
        r'[\d,]+\s*円',
        r'価格[:\s]*[\d,]+[万円]+'
    ]
    
    print("Price pattern testing:")
    for text in sample_texts:
        print(f"  Text: {text}")
        for pattern in price_patterns:
            matches = re.findall(pattern, text)
            if matches:
                print(f"    Pattern '{pattern}': {matches}")
                
    print("\nLocation pattern testing:")
    location_patterns = [
        r'軽井沢[^。\n]*',
        r'[東西南北中旧新][軽井沢]+',
        r'karuizawa[^。\n]*'
    ]
    
    for text in sample_texts:
        for pattern in location_patterns:
            matches = re.findall(pattern, text, re.I)
            if matches:
                print(f"  '{pattern}' found: {matches}")
                
    print("\nSize pattern testing:")
    size_patterns = [
        r'[\d,]+\.?\d*\s*㎡',
        r'[\d,]+\.?\d*\s*坪',
        r'土地[:\s]*[\d,]+\.?\d*\s*[㎡坪]',
        r'建物[:\s]*[\d,]+\.?\d*\s*[㎡坪]'
    ]
    
    for text in sample_texts:
        for pattern in size_patterns:
            matches = re.findall(pattern, text)
            if matches:
                print(f"  '{pattern}' found: {matches}")
                
    print("🔍 Data extraction pattern test completed\n")

def test_single_property_extraction():
    """Test extraction from a single property element"""
    print("🏠 Testing Single Property Extraction")
    print("-" * 30)
    
    # Create mock HTML for testing
    mock_html = """
    <div class="property-item">
        <h3>軽井沢の美しい別荘</h3>
        <div class="price">5,800万円</div>
        <div class="location">長野県軽井沢町</div>
        <div class="details">土地:300㎡ 建物:180㎡ 築15年 3LDK</div>
        <img src="/images/property1.jpg" alt="Property image">
        <a href="/property/detail/123">詳細を見る</a>
    </div>
    """
    
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(mock_html, 'html.parser')
    element = soup.find('div', class_='property-item')
    
    scraper = MitsuiNoMoriScraper()
    property_data = scraper.extract_property_from_element(element, "https://test.com")
    
    print("Extracted property data:")
    print(f"  Title: {property_data.title}")
    print(f"  Price: {property_data.price}")
    print(f"  Location: {property_data.location}")
    print(f"  Property Type: {property_data.property_type}")
    print(f"  Size Info: {property_data.size_info}")
    print(f"  Building Age: {property_data.building_age}")
    print(f"  Rooms: {property_data.rooms}")
    print(f"  Images: {len(property_data.image_urls)}")
    print(f"  Valid: {property_data.is_valid()}")
    print(f"  Contains Karuizawa: {property_data.contains_karuizawa()}")
    
    print("🏠 Single property extraction test completed\n")

def run_all_tests():
    """Run all test cases"""
    print("🧪 Running All Scraper Component Tests")
    print("=" * 50)
    
    test_functions = [
        test_property_data_validation,
        test_rate_limiter,
        test_http_connection,
        test_html_parsing,
        test_selector_patterns,
        test_data_extraction_patterns,
        test_single_property_extraction
    ]
    
    for test_func in test_functions:
        try:
            test_func()
        except Exception as e:
            print(f"❌ Test {test_func.__name__} failed: {e}")
            import traceback
            traceback.print_exc()
            print()
            
    print("🧪 All tests completed!")

if __name__ == "__main__":
    run_all_tests()