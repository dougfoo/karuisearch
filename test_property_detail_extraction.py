#!/usr/bin/env python3
"""
Test case for detailed property extraction - validates specific property data
"""
import sys
import os
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from scrapers.mitsui_scraper import MitsuiNoMoriScraper
from scrapers.base_scraper import PropertyData

def test_specific_property_extraction():
    """Test extraction of a specific known property (Property 2 equivalent)"""
    print("Testing Specific Property Extraction")
    print("=" * 50)
    
    scraper = MitsuiNoMoriScraper()
    
    # Test the specific property URL that gave us Property 2
    test_url = "https://www.mitsuinomori.co.jp/karuizawa/realestate/025c014hr/"
    
    print(f"Testing property URL: {test_url}")
    print("-" * 50)
    
    # Extract the property
    soup = scraper.get_soup(test_url)
    if not soup:
        print("FAILED: Could not load property page")
        return False
        
    # Extract property data
    property_data = scraper.extract_single_property_from_detail_page(soup, test_url)
    
    if not property_data:
        print("FAILED: No property data extracted")
        return False
        
    # Display extracted data
    print("EXTRACTED PROPERTY DATA:")
    print(f"Title: {property_data.title}")
    print(f"Price: {property_data.price}")
    print(f"Location: {property_data.location}")
    print(f"Property Type: {property_data.property_type}")
    print(f"Size Info: {property_data.size_info}")
    print(f"Building Age: {property_data.building_age}")
    print(f"Rooms: {property_data.rooms}")
    print(f"Images: {len(property_data.image_urls)} found")
    print(f"Description length: {len(property_data.description) if property_data.description else 0} characters")
    print(f"Source URL: {property_data.source_url}")
    
    # Validation tests
    print(f"\nVALIDATION TESTS:")
    print("-" * 30)
    
    test_results = {}
    
    # Test 1: Required fields present
    required_fields = ['title', 'price', 'location', 'source_url']
    for field in required_fields:
        value = getattr(property_data, field, '')
        has_value = bool(value and value.strip())
        test_results[f"Has {field}"] = has_value
        print(f"✅ {field}: {'PASS' if has_value else 'FAIL'}")
        
    # Test 2: Price format validation
    price_valid = bool(property_data.price and ('万円' in property_data.price or 'yen' in property_data.price.lower()))
    test_results["Price format valid"] = price_valid
    print(f"✅ Price format: {'PASS' if price_valid else 'FAIL'}")
    
    # Test 3: Karuizawa location check
    karuizawa_valid = property_data.contains_karuizawa()
    test_results["Contains Karuizawa"] = karuizawa_valid
    print(f"✅ Karuizawa location: {'PASS' if karuizawa_valid else 'FAIL'}")
    
    # Test 4: Property type check
    property_type_valid = bool(property_data.property_type and property_data.property_type.strip())
    test_results["Has property type"] = property_type_valid
    print(f"✅ Property type: {'PASS' if property_type_valid else 'FAIL'}")
    
    # Test 5: Size information check
    size_valid = bool(property_data.size_info and property_data.size_info.strip())
    test_results["Has size info"] = size_valid
    print(f"✅ Size info: {'PASS' if size_valid else 'FAIL'}")
    
    # Test 6: Images check
    images_valid = len(property_data.image_urls) > 0
    test_results["Has images"] = images_valid
    print(f"✅ Images found: {'PASS' if images_valid else 'FAIL'}")
    
    # Test 7: Overall validation
    overall_valid = property_data.is_valid()
    test_results["Overall valid"] = overall_valid
    print(f"✅ Overall validation: {'PASS' if overall_valid else 'FAIL'}")
    
    # Calculate success rate
    passed_tests = sum(1 for result in test_results.values() if result)
    total_tests = len(test_results)
    success_rate = (passed_tests / total_tests) * 100
    
    print(f"\nTEST SUMMARY:")
    print(f"Passed: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
    
    if success_rate >= 85:
        print("🎉 SUCCESS: Property extraction working excellently!")
        return True
    elif success_rate >= 70:
        print("⚠️ PARTIAL: Property extraction working but needs improvement")
        return True
    else:
        print("❌ FAILED: Property extraction needs significant work")
        return False

def test_price_parsing():
    """Test price parsing specifically"""
    print("\nTesting Price Parsing")
    print("=" * 30)
    
    # Test various price formats we might encounter
    test_prices = [
        "9,600万円",
        "5,000万円", 
        "¥96,000,000",
        "96,000,000円",
        "価格: 9,600万円",
        "9600万円",
        "96,000,000 yen"
    ]
    
    for price_text in test_prices:
        # Create a test property
        test_prop = PropertyData(
            title="Test Property",
            price=price_text,
            location="Karuizawa",
            source_url="https://test.com"
        )
        
        # Test validation
        from scrapers.base_scraper import SimpleScraper
        scraper = SimpleScraper({'base_url': 'https://test.com'})
        is_valid = scraper.validate_property_data(test_prop)
        
        print(f"Price '{price_text}': {'VALID' if is_valid else 'INVALID'}")

def test_expected_data_structure():
    """Test that extracted data matches expected structure for Property 2"""
    print("\nTesting Expected Data Structure")
    print("=" * 40)
    
    scraper = MitsuiNoMoriScraper()
    soup = scraper.get_soup("https://www.mitsuinomori.co.jp/karuizawa/realestate/025c014hr/")
    
    if not soup:
        print("Could not load test property")
        return False
        
    property_data = scraper.extract_single_property_from_detail_page(
        soup, "https://www.mitsuinomori.co.jp/karuizawa/realestate/025c014hr/"
    )
    
    # Expected characteristics for Property 2
    expected_checks = {
        "Price contains '万円'": "万円" in (property_data.price or ""),
        "Location contains Karuizawa": "karuizawa" in (property_data.location or "").lower(),
        "Property type is house": property_data.property_type == "一戸建て",
        "Has size information": bool(property_data.size_info and property_data.size_info.strip()),
        "Price is in premium range": "9," in (property_data.price or "") or "8," in (property_data.price or "") or "7," in (property_data.price or ""),
        "Has multiple images": len(property_data.image_urls) >= 3,
        "Building age specified": bool(property_data.building_age and property_data.building_age.strip())
    }
    
    print("Expected data structure checks:")
    for check_name, result in expected_checks.items():
        print(f"  {check_name}: {'✅ PASS' if result else '❌ FAIL'}")
        
    passed = sum(1 for result in expected_checks.values() if result)
    total = len(expected_checks)
    
    print(f"\nStructure validation: {passed}/{total} ({(passed/total)*100:.1f}%)")
    
    return passed >= (total * 0.8)  # 80% pass rate

def run_detailed_property_tests():
    """Run all detailed property extraction tests"""
    print("DETAILED PROPERTY EXTRACTION TEST SUITE")
    print("=" * 60)
    
    test_functions = [
        ("Specific Property Extraction", test_specific_property_extraction),
        ("Price Parsing", test_price_parsing),
        ("Expected Data Structure", test_expected_data_structure)
    ]
    
    results = {}
    
    for test_name, test_func in test_functions:
        try:
            print(f"\n{'='*20} {test_name} {'='*20}")
            result = test_func()
            results[test_name] = result
        except Exception as e:
            print(f"ERROR in {test_name}: {e}")
            results[test_name] = False
            import traceback
            traceback.print_exc()
            
    # Final summary
    print(f"\n{'='*60}")
    print("FINAL TEST RESULTS:")
    print("=" * 60)
    
    for test_name, result in results.items():
        status = "PASS ✅" if result else "FAIL ❌"
        print(f"{test_name}: {status}")
        
    passed_tests = sum(1 for result in results.values() if result)
    total_tests = len(results)
    overall_success = (passed_tests / total_tests) * 100
    
    print(f"\nOverall Success Rate: {passed_tests}/{total_tests} ({overall_success:.1f}%)")
    
    if overall_success >= 80:
        print("🎉 EXCELLENT: Property extraction system is working great!")
    elif overall_success >= 60:
        print("⚠️ GOOD: Property extraction working but has room for improvement")
    else:
        print("❌ NEEDS WORK: Property extraction system needs attention")
        
    return overall_success >= 80

if __name__ == "__main__":
    run_detailed_property_tests()