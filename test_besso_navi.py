#!/usr/bin/env python3
"""
Test script for Besso Navi scraper
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from scrapers.besso_navi_scraper import BessoNaviScraper

def safe_print(text):
    """Print text safely, converting Unicode to ASCII if needed"""
    if isinstance(text, str):
        return text.encode('ascii', 'ignore').decode('ascii')
    return str(text)

def test_besso_navi_navigation():
    """Test basic navigation to Besso Navi search page"""
    print("Testing Besso Navi Navigation")
    print("=" * 40)
    
    config = {
        'headless': False,  # Show browser for debugging
        'wait_timeout': 15
    }
    
    try:
        with BessoNaviScraper(config) as scraper:
            print(f"Navigating to: {scraper.search_url}")
            
            # Test navigation
            success = scraper.navigate_to_page(scraper.search_url)
            print(f"Navigation successful: {'YES' if success else 'NO'}")
            
            if success:
                # Check page title
                page_title = scraper.driver.title
                print(f"Page title: {safe_print(page_title)}")
                
                # Check for search form
                try:
                    form = scraper.driver.find_element(By.TAG_NAME, "form")
                    print(f"Search form found: YES")
                    
                    # Look for form elements
                    inputs = scraper.driver.find_elements(By.TAG_NAME, "input")
                    selects = scraper.driver.find_elements(By.TAG_NAME, "select")
                    
                    print(f"Form inputs found: {len(inputs)}")
                    print(f"Form selects found: {len(selects)}")
                    
                except Exception as e:
                    print(f"Search form found: NO - {e}")
                    
                # Check for CAPTCHA
                has_captcha = scraper.check_for_captcha()
                print(f"CAPTCHA detected: {'YES' if has_captcha else 'NO'}")
                
                # Check for Karuizawa/property related content
                page_source = scraper.driver.page_source.lower()
                has_properties = 'property' in page_source or '物件' in page_source
                has_search = 'search' in page_source or '検索' in page_source
                
                print(f"Has property content: {'YES' if has_properties else 'NO'}")
                print(f"Has search functionality: {'YES' if has_search else 'NO'}")
                
                if has_search:
                    print("✅ SUCCESS: Found search page")
                    return True
                else:
                    print("⚠️ WARNING: Search functionality unclear")
                    return False
                    
            else:
                print("❌ FAILED: Could not navigate to search page")
                return False
                
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_besso_navi_form_setup():
    """Test search form setup"""
    print("\nTesting Besso Navi Form Setup")
    print("=" * 40)
    
    config = {
        'headless': True,  # Run headless for form test
        'wait_timeout': 15
    }
    
    try:
        with BessoNaviScraper(config) as scraper:
            print("Navigating to search page...")
            
            if not scraper.navigate_to_page(scraper.search_url):
                print("❌ FAILED: Could not navigate to search page")
                return False
                
            print("Setting up search form...")
            
            # Test form setup
            form_setup_success = scraper.setup_search_form()
            print(f"Form setup successful: {'YES' if form_setup_success else 'NO'}")
            
            if form_setup_success:
                print("Attempting to submit search...")
                
                # Test search submission
                submit_success = scraper.submit_search()
                print(f"Search submitted: {'YES' if submit_success else 'NO'}")
                
                if submit_success:
                    # Wait for results
                    scraper.simulate_human_delay(3.0, 5.0)
                    
                    # Check if we got to a results page
                    current_url = scraper.driver.current_url
                    page_source = scraper.driver.page_source.lower()
                    
                    has_results = ('result' in page_source or 
                                 '結果' in page_source or 
                                 '物件' in page_source)
                    
                    print(f"Results page reached: {'YES' if has_results else 'NO'}")
                    print(f"Current URL: {current_url}")
                    
                    if has_results:
                        print("✅ SUCCESS: Form setup and submission working")
                        return True
                    else:
                        print("⚠️ PARTIAL: Form submitted but results unclear")
                        return True
                else:
                    print("❌ FAILED: Could not submit search")
                    return False
            else:
                print("❌ FAILED: Could not setup search form")
                return False
                
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_besso_navi_property_extraction():
    """Test property extraction from search results"""
    print("\nTesting Besso Navi Property Extraction")
    print("=" * 50)
    
    config = {
        'headless': True,
        'wait_timeout': 20
    }
    
    try:
        with BessoNaviScraper(config) as scraper:
            print("Attempting full property extraction...")
            
            # Extract properties using full scraping method
            properties = scraper.scrape_listings()
            
            print(f"Total properties extracted: {len(properties)}")
            
            if properties:
                print("\nProperty Summary:")
                print("-" * 30)
                
                for i, prop in enumerate(properties[:3], 1):  # Show first 3
                    print(f"\nProperty {i}:")
                    print(f"  Title: {safe_print(prop.title)[:50]}...")
                    print(f"  Price: {safe_print(prop.price)}")
                    print(f"  Location: {safe_print(prop.location)}")
                    print(f"  Type: {safe_print(prop.property_type)}")
                    print(f"  Size: {safe_print(prop.size_info)}")
                    print(f"  Images: {len(prop.image_urls)}")
                    print(f"  Valid: {'YES' if prop.is_valid() else 'NO'}")
                    print(f"  Source: {prop.source_url[:50]}...")
                    
                # Validation summary
                valid_count = sum(1 for p in properties if scraper.validate_property_data(p))
                print(f"\nValidation Summary:")
                print(f"Valid properties: {valid_count}/{len(properties)}")
                
                if valid_count > 0:
                    print("✅ SUCCESS: Besso Navi scraper working!")
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

def test_besso_navi_validation():
    """Test Besso Navi specific validation logic"""
    print("\nTesting Besso Navi Validation Logic")
    print("=" * 40)
    
    from scrapers.base_scraper import PropertyData
    
    # Test case 1: Valid vacation home
    valid_property = PropertyData(
        title="Karuizawa Vacation Villa",
        price="3,500万円",
        location="軽井沢町",
        property_type="一戸建て",
        source_url="https://www.besso-navi.com/property/123"
    )
    
    # Test case 2: Valid land property
    valid_land = PropertyData(
        title="Karuizawa Building Plot",
        price="1,200万円",
        location="中軽井沢",
        property_type="土地",
        size_info="200㎡",
        source_url="https://www.besso-navi.com/property/456"
    )
    
    # Test case 3: Missing location (should be accepted for Besso Navi)
    missing_location = PropertyData(
        title="Resort Property",
        price="2,800万円",
        property_type="ヴィラ",
        source_url="https://www.besso-navi.com/property/789"
    )
    
    # Test case 4: Invalid - missing title and price
    invalid_property = PropertyData(
        location="軽井沢",
        source_url="https://www.besso-navi.com/property/999"
    )
    
    config = {'base_url': 'https://www.besso-navi.com'}
    scraper = BessoNaviScraper(config)
    
    test_cases = [
        ("Valid vacation home", valid_property, True),
        ("Valid land property", valid_land, True),
        ("Missing location (should pass)", missing_location, True),
        ("Invalid - missing essentials", invalid_property, False)
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

def run_besso_navi_tests():
    """Run all Besso Navi scraper tests"""
    print("BESSO NAVI SCRAPER TEST SUITE")
    print("=" * 50)
    
    tests = [
        ("Navigation", test_besso_navi_navigation),
        ("Form Setup", test_besso_navi_form_setup),
        ("Property Extraction", test_besso_navi_property_extraction),
        ("Validation Logic", test_besso_navi_validation)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'='*15} {test_name} {'='*15}")
        try:
            result = test_func()
            results[test_name] = result
        except Exception as e:
            print(f"ERROR in {test_name}: {e}")
            results[test_name] = False
            
    # Final summary
    print(f"\n{'='*50}")
    print("BESSO NAVI TEST RESULTS:")
    print("=" * 50)
    
    for test_name, result in results.items():
        status = "PASS ✅" if result else "FAIL ❌"
        print(f"{test_name}: {status}")
        
    passed_tests = sum(1 for result in results.values() if result)
    total_tests = len(results)
    success_rate = (passed_tests / total_tests) * 100
    
    print(f"\nOverall Success Rate: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
    
    if success_rate >= 80:
        print("🎉 EXCELLENT: Besso Navi scraper working great!")
    elif success_rate >= 60:
        print("⚠️ GOOD: Besso Navi scraper working but needs improvement")
    else:
        print("❌ NEEDS WORK: Besso Navi scraper needs attention")
        
    return success_rate >= 80

if __name__ == "__main__":
    # Fix import issue
    from selenium.webdriver.common.by import By
    
    run_besso_navi_tests()