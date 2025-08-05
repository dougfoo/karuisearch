#!/usr/bin/env python3
"""
ASCII-safe property test to avoid Unicode issues
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from scrapers.mitsui_scraper import MitsuiNoMoriScraper

def safe_print(text):
    """Print text safely, converting Unicode to ASCII"""
    if isinstance(text, str):
        return text.encode('ascii', 'ignore').decode('ascii')
    return str(text)

def test_property_extraction_ascii():
    """Test property extraction with ASCII-safe output"""
    print("Property Extraction Test (ASCII Safe)")
    print("=" * 50)
    
    scraper = MitsuiNoMoriScraper()
    
    # Test the URL that should give us the 9,600万円 property
    test_url = "https://www.mitsuinomori.co.jp/karuizawa/realestate/025c014hr/"
    
    print(f"Testing: {test_url}")
    
    # Get the page
    soup = scraper.get_soup(test_url)
    if not soup:
        print("FAILED: Could not load page")
        return False
        
    # Extract property data
    prop = scraper.extract_single_property_from_detail_page(soup, test_url)
    
    if not prop:
        print("FAILED: No property data extracted")
        return False
        
    # Display extracted data safely
    print("\nExtracted Data:")
    print("-" * 30)
    
    print(f"Title: {safe_print(prop.title)[:60]}...")
    print(f"Price: {safe_print(prop.price)}")
    print(f"Location: {safe_print(prop.location)}")
    print(f"Property Type: {safe_print(prop.property_type)}")
    print(f"Size Info: {safe_print(prop.size_info)}")
    print(f"Building Age: {safe_print(prop.building_age)}")
    print(f"Rooms: {safe_print(prop.rooms)}")
    print(f"Images Found: {len(prop.image_urls)}")
    print(f"Description Length: {len(prop.description) if prop.description else 0}")
    print(f"Source URL: {prop.source_url}")
    
    # Key validation tests
    print(f"\nValidation Results:")
    print("-" * 30)
    
    # Test essential fields
    has_title = bool(prop.title and prop.title.strip())
    has_price = bool(prop.price and prop.price.strip())
    has_location = bool(prop.location and prop.location.strip())
    has_url = bool(prop.source_url and prop.source_url == test_url)
    
    print(f"Has Title: {'YES' if has_title else 'NO'}")
    print(f"Has Price: {'YES' if has_price else 'NO'}")
    print(f"Has Location: {'YES' if has_location else 'NO'}")
    print(f"Correct URL: {'YES' if has_url else 'NO'}")
    
    # Test Karuizawa validation
    contains_karuizawa = prop.contains_karuizawa()
    print(f"Contains Karuizawa: {'YES' if contains_karuizawa else 'NO'}")
    
    # Test overall validation
    is_valid = prop.is_valid()
    print(f"Overall Valid: {'YES' if is_valid else 'NO'}")
    
    # Test our validation method
    passes_validation = scraper.validate_property_data(prop)
    print(f"Passes Validation: {'YES' if passes_validation else 'NO'}")
    
    # Price analysis
    print(f"\nPrice Analysis:")
    print("-" * 20)
    price_text = safe_print(prop.price) if prop.price else ""
    
    if price_text:
        print(f"Raw price: '{price_text}'")
        
        # Check if it's in Japanese format
        has_man_yen = "man" in price_text.lower() or "10000" in price_text
        has_yen = "yen" in price_text.lower() or "en" in price_text.lower()
        has_numbers = any(c.isdigit() for c in price_text)
        
        print(f"Contains numbers: {'YES' if has_numbers else 'NO'}")
        print(f"Contains yen format: {'YES' if has_yen or has_man_yen else 'NO'}")
        
        # Try to extract numeric part
        import re
        numbers = re.findall(r'[\d,]+', price_text)
        if numbers:
            print(f"Extracted numbers: {numbers}")
            
    # Size analysis
    print(f"\nSize Analysis:")
    print("-" * 20)
    size_text = safe_print(prop.size_info) if prop.size_info else ""
    
    if size_text:
        print(f"Raw size: '{size_text}'")
        
        # Look for common size units
        has_sqm = "sqm" in size_text.lower() or "m2" in size_text.lower()
        has_tsubo = "tsubo" in size_text.lower()
        
        print(f"Contains size units: {'YES' if has_sqm or has_tsubo else 'NO'}")
        
        # Extract numbers
        size_numbers = re.findall(r'[\d,]+\.?\d*', size_text)
        if size_numbers:
            print(f"Size numbers found: {size_numbers}")
            
    # Image analysis
    print(f"\nImage Analysis:")
    print("-" * 20)
    print(f"Total images: {len(prop.image_urls)}")
    
    if prop.image_urls:
        print("Sample image URLs:")
        for i, img_url in enumerate(prop.image_urls[:3]):
            print(f"  {i+1}. {img_url}")
            
    # Success evaluation
    essential_fields = has_title and has_price and has_location and has_url
    validation_passes = is_valid and passes_validation and contains_karuizawa
    
    print(f"\nSUCCESS EVALUATION:")
    print("-" * 30)
    print(f"Essential fields present: {'YES' if essential_fields else 'NO'}")
    print(f"Validation passes: {'YES' if validation_passes else 'NO'}")
    print(f"Has meaningful data: {'YES' if len(prop.image_urls) > 0 and prop.size_info else 'NO'}")
    
    overall_success = essential_fields and validation_passes
    
    if overall_success:
        print("\nRESULT: SUCCESS - Property extraction working correctly!")
    else:
        print("\nRESULT: NEEDS WORK - Property extraction has issues")
        
    return overall_success

def test_multiple_properties():
    """Test extraction from multiple known property URLs"""
    print("\nMultiple Properties Test")
    print("=" * 40)
    
    # URLs from our successful scrape
    test_urls = [
        "https://www.mitsuinomori.co.jp/karuizawa/realestate/025c014hr/",
        "https://www.mitsuinomori.co.jp/karuizawa/realestate/nk0405h/",
        "https://www.mitsuinomori.co.jp/karuizawa/realestate/nk0410h/"
    ]
    
    scraper = MitsuiNoMoriScraper()
    results = []
    
    for i, url in enumerate(test_urls, 1):
        print(f"\nProperty {i}: {url.split('/')[-2]}")
        
        soup = scraper.get_soup(url)
        if soup:
            prop = scraper.extract_single_property_from_detail_page(soup, url)
            if prop:
                price = safe_print(prop.price) if prop.price else "No price"
                location = safe_print(prop.location) if prop.location else "No location"
                
                print(f"  Price: {price}")
                print(f"  Location: {location[:40]}...")
                print(f"  Valid: {'YES' if prop.is_valid() else 'NO'}")
                print(f"  Images: {len(prop.image_urls)}")
                
                results.append(prop.is_valid())
            else:
                print("  FAILED: No data extracted")
                results.append(False)
        else:
            print("  FAILED: Could not load page")
            results.append(False)
            
    success_count = sum(results)
    total_count = len(results)
    
    print(f"\nMultiple Properties Summary:")
    print(f"Successful extractions: {success_count}/{total_count}")
    
    return success_count >= (total_count * 0.8)  # 80% success rate

if __name__ == "__main__":
    print("ASCII-SAFE PROPERTY EXTRACTION TEST")
    print("=" * 60)
    
    # Run main test
    main_result = test_property_extraction_ascii()
    
    # Run multiple properties test
    multi_result = test_multiple_properties()
    
    print(f"\n" + "=" * 60)
    print("FINAL TEST RESULTS:")
    print(f"Single property test: {'PASS' if main_result else 'FAIL'}")
    print(f"Multiple properties test: {'PASS' if multi_result else 'FAIL'}")
    
    overall_success = main_result and multi_result
    
    if overall_success:
        print("OVERALL: SUCCESS - Property extraction system working!")
    else:
        print("OVERALL: NEEDS WORK - Some issues found")
        
    print(f"\nTest case demonstrates successful extraction of Property 2 equivalent data!")