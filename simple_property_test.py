#!/usr/bin/env python3
"""
Simple property extraction test - focuses on Property 2 validation
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from scrapers.mitsui_scraper import MitsuiNoMoriScraper

def test_property_2_extraction():
    """Test the specific property that we know as Property 2"""
    print("Property 2 Extraction Test")
    print("=" * 40)
    
    scraper = MitsuiNoMoriScraper()
    
    # Property 2 URL
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
        
    # Test results (avoiding Unicode display issues)
    print("\nExtracted Data:")
    print("-" * 20)
    
    # Basic info (convert to ASCII for safe display)
    title_safe = prop.title.encode('ascii', 'ignore').decode('ascii') if prop.title else "No title"
    print(f"Title: {title_safe[:50]}...")
    
    price_safe = prop.price.encode('ascii', 'ignore').decode('ascii') if prop.price else "No price"
    print(f"Price: {price_safe}")
    
    location_safe = prop.location.encode('ascii', 'ignore').decode('ascii') if prop.location else "No location"
    print(f"Location: {location_safe}")
    
    print(f"Property Type: {prop.property_type}")
    print(f"Size Info: {prop.size_info}")
    print(f"Building Age: {prop.building_age}")
    print(f"Images: {len(prop.image_urls)}")
    print(f"Source: {prop.source_url}")
    
    # Validation tests
    print(f"\nValidation Tests:")
    print("-" * 20)
    
    tests = []
    
    # Test 1: Has title
    has_title = bool(prop.title and prop.title.strip())
    tests.append(("Has title", has_title))
    
    # Test 2: Has price
    has_price = bool(prop.price and prop.price.strip())
    tests.append(("Has price", has_price))
    
    # Test 3: Price format (Japanese real estate format)
    price_format_ok = bool(prop.price and ("万円" in prop.price or "yen" in prop.price.lower()))
    tests.append(("Price format OK", price_format_ok))
    
    # Test 4: Has location
    has_location = bool(prop.location and prop.location.strip())
    tests.append(("Has location", has_location))
    
    # Test 5: Karuizawa related
    is_karuizawa = prop.contains_karuizawa()
    tests.append(("Contains Karuizawa", is_karuizawa))
    
    # Test 6: Has property type
    has_prop_type = bool(prop.property_type and prop.property_type.strip())
    tests.append(("Has property type", has_prop_type))
    
    # Test 7: Has size info
    has_size = bool(prop.size_info and prop.size_info.strip())
    tests.append(("Has size info", has_size))
    
    # Test 8: Has images
    has_images = len(prop.image_urls) > 0
    tests.append(("Has images", has_images))
    
    # Test 9: Overall valid
    is_valid = prop.is_valid()
    tests.append(("Overall valid", is_valid))
    
    # Test 10: Proper URL
    correct_url = prop.source_url == test_url
    tests.append(("Correct source URL", correct_url))
    
    # Display results
    passed = 0
    for test_name, result in tests:
        status = "PASS" if result else "FAIL"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1
            
    # Summary
    total = len(tests)
    success_rate = (passed / total) * 100
    
    print(f"\nResults: {passed}/{total} tests passed ({success_rate:.1f}%)")
    
    # Expected values for Property 2
    print(f"\nExpected vs Actual:")
    print("-" * 20)
    
    # We know Property 2 should have these characteristics
    expected_checks = [
        ("Price should be 9,600万円", "9,600" in (prop.price or "")),
        ("Should be detached house", prop.property_type == "一戸建て"),
        ("Should have large land size", "319" in (prop.size_info or "")),
        ("Should be new construction", "新築" in (prop.building_age or "")),
        ("Should have 5 images", len(prop.image_urls) == 5),
        ("Should contain Naka-Karuizawa", "中軽井沢" in (prop.location or ""))
    ]
    
    expected_passed = 0
    for check_name, result in expected_checks:
        status = "MATCH" if result else "DIFFERENT"
        print(f"  {check_name}: {status}")
        if result:
            expected_passed += 1
            
    expected_total = len(expected_checks)
    expected_success = (expected_passed / expected_total) * 100
    
    print(f"\nExpected match: {expected_passed}/{expected_total} ({expected_success:.1f}%)")
    
    # Final evaluation
    if success_rate >= 90 and expected_success >= 70:
        print("\nSUCCESS: Property extraction working excellently!")
        return True
    elif success_rate >= 80:
        print("\nGOOD: Property extraction working well")
        return True
    else:
        print("\nNEEDS WORK: Property extraction needs improvement")
        return False

def test_validation_logic():
    """Test the validation logic specifically"""
    print("\nValidation Logic Test")
    print("=" * 30)
    
    scraper = MitsuiNoMoriScraper()
    
    # Test with Property 2 URL
    soup = scraper.get_soup("https://www.mitsuinomori.co.jp/karuizawa/realestate/025c014hr/")
    if soup:
        prop = scraper.extract_single_property_from_detail_page(
            soup, "https://www.mitsuinomori.co.jp/karuizawa/realestate/025c014hr/"
        )
        
        if prop:
            # Test our validation method
            is_valid = scraper.validate_property_data(prop)
            print(f"Property validation result: {'VALID' if is_valid else 'INVALID'}")
            
            # Test individual validation steps
            print("Individual validation checks:")
            print(f"  Has required fields: {prop.is_valid()}")
            print(f"  Contains Karuizawa: {prop.contains_karuizawa()}")
            
            return is_valid
        else:
            print("No property data to validate")
            return False
    else:
        print("Could not load page for validation test")
        return False

if __name__ == "__main__":
    print("PROPERTY 2 DETAILED TEST CASE")
    print("=" * 50)
    
    # Run the main test
    main_result = test_property_2_extraction()
    
    # Run validation test
    validation_result = test_validation_logic()
    
    print(f"\n" + "=" * 50)
    print("FINAL RESULTS:")
    print(f"Property extraction: {'PASS' if main_result else 'FAIL'}")
    print(f"Validation logic: {'PASS' if validation_result else 'FAIL'}")
    
    overall_success = main_result and validation_result
    print(f"Overall test: {'SUCCESS' if overall_success else 'NEEDS WORK'}")