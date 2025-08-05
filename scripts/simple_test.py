#!/usr/bin/env python3
"""
Simple test for Mitsui no Mori scraper components
"""
import sys
import os
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from scrapers.mitsui_scraper import MitsuiNoMoriScraper
from scrapers.base_scraper import PropertyData, RateLimiter

def test_basic_components():
    """Test basic components"""
    print("Testing Basic Components")
    print("=" * 40)
    
    # Test PropertyData
    print("\n1. Testing PropertyData:")
    prop = PropertyData(
        title="Karuizawa Beautiful Villa",
        price="58,000,000 yen",
        location="Karuizawa-machi",
        source_url="https://example.com/property1"
    )
    
    print(f"   Valid: {prop.is_valid()}")
    print(f"   Contains Karuizawa: {prop.contains_karuizawa()}")
    
    # Test Rate Limiter
    print("\n2. Testing Rate Limiter:")
    limiter = RateLimiter(requests_per_second=1.0)
    
    start = datetime.now()
    for i in range(2):
        print(f"   Request {i+1} at {datetime.now().strftime('%H:%M:%S')}")
        limiter.wait_if_needed()
    end = datetime.now()
    
    print(f"   Duration: {(end-start).total_seconds():.1f} seconds")
    
    print("\nBasic components test completed!")

def test_http_connection():
    """Test HTTP connection"""
    print("\nTesting HTTP Connection")
    print("=" * 40)
    
    scraper = MitsuiNoMoriScraper()
    
    # Test connection
    url = "https://www.mitsuinomori.co.jp/karuizawa/"
    print(f"Connecting to: {url}")
    
    response = scraper.safe_request(url)
    
    if response:
        print(f"SUCCESS: Status {response.status_code}")
        print(f"Content length: {len(response.content)} bytes")
        
        # Check for Karuizawa content
        content = response.text.lower()
        has_karuizawa = 'karuizawa' in content or 'kariuzawa' in content
        print(f"Contains Karuizawa content: {has_karuizawa}")
        
        # Check for price content
        has_price = 'yen' in content or 'price' in content
        print(f"Contains price content: {has_price}")
        
    else:
        print("FAILED: Could not connect")
        
    print("HTTP connection test completed!")

def test_html_parsing():
    """Test HTML parsing"""
    print("\nTesting HTML Parsing")
    print("=" * 40)
    
    scraper = MitsuiNoMoriScraper()
    
    # Get soup
    soup = scraper.get_soup("https://www.mitsuinomori.co.jp/karuizawa/")
    
    if soup:
        print("SUCCESS: HTML parsed")
        
        # Basic analysis
        title = soup.find('title')
        print(f"Page title: {title.get_text().strip() if title else 'Not found'}")
        
        links = soup.find_all('a', href=True)
        print(f"Links found: {len(links)}")
        
        images = soup.find_all('img')
        print(f"Images found: {len(images)}")
        
        # Look for potential property elements
        divs = soup.find_all('div')
        print(f"Div elements: {len(divs)}")
        
        # Show sample div content
        if divs:
            sample_text = divs[0].get_text(strip=True)[:100]
            print(f"Sample content: {sample_text}...")
            
    else:
        print("FAILED: Could not parse HTML")
        
    print("HTML parsing test completed!")

def test_property_extraction():
    """Test property data extraction"""
    print("\nTesting Property Extraction")
    print("=" * 40)
    
    # Create sample HTML for testing
    sample_html = '''
    <div class="property-item">
        <h3>Beautiful Karuizawa Villa</h3>
        <div class="price">58,000,000 yen</div>
        <div class="location">Karuizawa-machi, Nagano</div>
        <div class="details">Land: 300sqm Building: 180sqm Age: 15 years</div>
        <img src="/images/property1.jpg" alt="Property image">
    </div>
    '''
    
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(sample_html, 'html.parser')
    element = soup.find('div', class_='property-item')
    
    scraper = MitsuiNoMoriScraper()
    prop_data = scraper.extract_property_from_element(element, "https://test.com")
    
    print("Extracted data:")
    print(f"   Title: {prop_data.title}")
    print(f"   Price: {prop_data.price}")
    print(f"   Location: {prop_data.location}")
    print(f"   Size Info: {prop_data.size_info}")
    print(f"   Images: {len(prop_data.image_urls)}")
    print(f"   Valid: {prop_data.is_valid()}")
    print(f"   Karuizawa: {prop_data.contains_karuizawa()}")
    
    print("Property extraction test completed!")

def run_all_tests():
    """Run all tests"""
    print("Running Mitsui no Mori Scraper Tests")
    print("=" * 50)
    
    test_functions = [
        test_basic_components,
        test_http_connection,
        test_html_parsing,
        test_property_extraction
    ]
    
    for test_func in test_functions:
        try:
            test_func()
        except Exception as e:
            print(f"ERROR in {test_func.__name__}: {e}")
            import traceback
            traceback.print_exc()
            
    print("\nAll tests completed!")

if __name__ == "__main__":
    run_all_tests()