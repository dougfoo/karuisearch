#!/usr/bin/env python3
"""
Test script for Royal Resort Karuizawa scraper
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from scrapers.royal_resort_scraper import RoyalResortScraper

def safe_print(text):
    """Print text safely, converting Unicode to ASCII if needed"""
    if isinstance(text, str):
        return text.encode('ascii', 'ignore').decode('ascii')
    return str(text)

def test_royal_resort_basic_navigation():
    """Test basic navigation to Royal Resort Karuizawa page"""
    print("Testing Royal Resort Basic Navigation")
    print("=" * 50)
    
    config = {
        'headless': False,  # Show browser for debugging
        'wait_timeout': 15
    }
    
    try:
        with RoyalResortScraper(config) as scraper:
            print(f"Navigating to: {scraper.karuizawa_url}")
            
            # Test navigation
            success = scraper.navigate_to_page(scraper.karuizawa_url)
            print(f"Navigation successful: {'YES' if success else 'NO'}")
            
            if success:
                # Check page title
                page_title = scraper.driver.title
                print(f"Page title: {safe_print(page_title)}")
                
                # Check for potential anti-bot measures
                has_captcha = scraper.check_for_captcha()
                print(f"CAPTCHA detected: {'YES' if has_captcha else 'NO'}")
                
                # Look for property-related content
                page_source = scraper.driver.page_source.lower()
                has_properties = 'property' in page_source or '物件' in page_source
                has_karuizawa = 'karuizawa' in page_source or '軽井沢' in page_source
                has_prices = '万円' in page_source or 'yen' in page_source
                
                print(f"Has property content: {'YES' if has_properties else 'NO'}")
                print(f"Has Karuizawa content: {'YES' if has_karuizawa else 'NO'}")
                print(f"Has price content: {'YES' if has_prices else 'NO'}")
                
                # Try to find property elements
                property_elements = scraper.find_property_listings()
                print(f"Property elements found: {len(property_elements)}")
                
                if property_elements:
                    print("✅ SUCCESS: Found property listings on page")
                    return True
                else:
                    print("⚠️ WARNING: No property listings found")
                    return False
                    
            else:
                print("❌ FAILED: Could not navigate to page")
                return False
                
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_royal_resort_property_extraction():
    """Test property data extraction"""
    print("\nTesting Royal Resort Property Extraction")
    print("=" * 50)
    
    config = {
        'headless': True,  # Run headless for extraction test
        'wait_timeout': 20
    }
    
    try:
        with RoyalResortScraper(config) as scraper:
            print("Attempting to extract properties...")
            
            # Extract properties
            properties = scraper.scrape_listings()
            
            print(f"Total properties extracted: {len(properties)}")
            
            if properties:
                print("\nProperty Summary:")
                print("-" * 30)
                
                for i, prop in enumerate(properties[:3], 1):  # Show first 3
                    print(f"\nProperty {i}:")
                    print(f"  Title: {safe_print(prop.title)[:60]}...")
                    print(f"  Price: {safe_print(prop.price)}")
                    print(f"  Location: {safe_print(prop.location)}")
                    print(f"  Type: {safe_print(prop.property_type)}")
                    print(f"  Size: {safe_print(prop.size_info)}")
                    print(f"  Images: {len(prop.image_urls)}")
                    print(f"  Valid: {'YES' if prop.is_valid() else 'NO'}")
                    print(f"  Karuizawa: {'YES' if prop.contains_karuizawa() else 'NO'}")
                    
                # Validation summary
                valid_count = sum(1 for p in properties if scraper.validate_property_data(p))
                print(f"\nValidation Summary:")
                print(f"Valid properties: {valid_count}/{len(properties)}")
                
                if valid_count > 0:
                    print("✅ SUCCESS: Royal Resort scraper working!")
                    return True
                else:
                    print("⚠️ WARNING: Properties extracted but validation failed")
                    return False
                    
            else:
                print("❌ FAILED: No properties extracted")
                return False
                
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_royal_resort_validation_logic():
    """Test Royal Resort specific validation"""
    print("\nTesting Royal Resort Validation Logic")
    print("=" * 40)
    
    from scrapers.base_scraper import PropertyData
    
    # Test case 1: Valid luxury property
    valid_property = PropertyData(
        title="Royal Karuizawa Villa Premium",
        price="8,500万円", 
        location="軽井沢町",
        property_type="ヴィラ",
        size_info="250㎡",
        source_url="https://www.royal-resort.co.jp/karuizawa/property/123"
    )
    
    # Test case 2: Invalid - price too low
    invalid_low_price = PropertyData(
        title="Cheap Karuizawa Property",
        price="1,000万円",  # Too low for luxury resort
        location="軽井沢町",
        source_url="https://www.royal-resort.co.jp/karuizawa/property/456"
    )
    
    # Test case 3: Invalid - not Karuizawa
    invalid_location = PropertyData(
        title="Tokyo Apartment",
        price="7,000万円",
        location="東京都",
        source_url="https://www.royal-resort.co.jp/tokyo/property/789"
    )
    
    config = {'base_url': 'https://www.royal-resort.co.jp'}
    scraper = RoyalResortScraper(config)
    
    test_cases = [
        ("Valid luxury property", valid_property, True),
        ("Invalid low price", invalid_low_price, False),
        ("Invalid location", invalid_location, False)
    ]
    
    results = []
    for test_name, property_data, expected in test_cases:
        result = scraper.validate_property_data(property_data)
        passed = result == expected
        results.append(passed)
        
        status = "PASS" if passed else "FAIL"
        print(f"  {test_name}: {status} (expected {expected}, got {result})")
        
    passed_tests = sum(results)
    total_tests = len(results)
    
    print(f"\nValidation tests: {passed_tests}/{total_tests} passed")
    
    if passed_tests == total_tests:
        print("✅ SUCCESS: All validation tests passed")
        return True
    else:
        print("❌ FAILED: Some validation tests failed")
        return False

def run_royal_resort_tests():
    """Run all Royal Resort scraper tests"""
    print("ROYAL RESORT KARUIZAWA SCRAPER TEST SUITE")
    print("=" * 60)
    
    tests = [
        ("Basic Navigation", test_royal_resort_basic_navigation),
        ("Property Extraction", test_royal_resort_property_extraction),
        ("Validation Logic", test_royal_resort_validation_logic)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results[test_name] = result
        except Exception as e:
            print(f"ERROR in {test_name}: {e}")
            results[test_name] = False
            
    # Final summary
    print(f"\n{'='*60}")
    print("ROYAL RESORT TEST RESULTS:")
    print("=" * 60)
    
    for test_name, result in results.items():
        status = "PASS ✅" if result else "FAIL ❌"
        print(f"{test_name}: {status}")
        
    passed_tests = sum(1 for result in results.values() if result)
    total_tests = len(results)
    success_rate = (passed_tests / total_tests) * 100
    
    print(f"\nOverall Success Rate: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
    
    if success_rate >= 80:
        print("🎉 EXCELLENT: Royal Resort scraper working great!")
    elif success_rate >= 60:
        print("⚠️ GOOD: Royal Resort scraper working but needs improvement")
    else:
        print("❌ NEEDS WORK: Royal Resort scraper needs attention")
        
    return success_rate >= 80

if __name__ == "__main__":
    run_royal_resort_tests()