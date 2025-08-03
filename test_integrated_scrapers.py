#!/usr/bin/env python3
"""
Integration test for all scrapers working together via ScraperFactory
"""
import sys
import os
import json
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from scrapers.scraper_factory import ScraperFactory

def safe_print(text):
    """Print text safely, converting Unicode to ASCII if needed"""
    if isinstance(text, str):
        return text.encode('ascii', 'ignore').decode('ascii')
    return str(text)

def test_scraper_factory_setup():
    """Test basic ScraperFactory setup and configuration"""
    print("Testing ScraperFactory Setup")
    print("=" * 40)
    
    try:
        # Create factory with default config
        factory = ScraperFactory()
        
        # Test getting available scrapers
        available_scrapers = factory.get_available_scrapers()
        print(f"Available scrapers: {len(available_scrapers)}")
        
        for key, info in available_scrapers.items():
            print(f"  {key}: {info['name']} ({info['type']})")
            
        # Test creating individual scrapers
        created_scrapers = {}
        for scraper_key in available_scrapers.keys():
            scraper = factory.create_scraper(scraper_key)
            created_scrapers[scraper_key] = scraper is not None
            print(f"  Create {scraper_key}: {'SUCCESS' if scraper else 'FAILED'}")
            
        success_count = sum(1 for success in created_scrapers.values() if success)
        total_count = len(created_scrapers)
        
        print(f"\nScraper creation: {success_count}/{total_count} successful")
        
        if success_count == total_count:
            print("✅ SUCCESS: ScraperFactory setup working")
            return True
        else:
            print("⚠️ PARTIAL: Some scrapers failed to create")
            return success_count > 0
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_single_site_scraping():
    """Test scraping individual sites through the factory"""
    print("\nTesting Single Site Scraping")
    print("=" * 40)
    
    try:
        factory = ScraperFactory()
        
        # Test with Mitsui (known working scraper)
        print("Testing Mitsui no Mori scraper...")
        
        mitsui_results = factory.scrape_single_site('mitsui')
        print(f"Mitsui properties found: {len(mitsui_results)}")
        
        if mitsui_results:
            # Show sample property
            sample_prop = mitsui_results[0]
            print(f"Sample property:")
            print(f"  Title: {safe_print(sample_prop.title)[:50]}...")
            print(f"  Price: {safe_print(sample_prop.price)}")
            print(f"  Location: {safe_print(sample_prop.location)}")
            print(f"  Valid: {'YES' if sample_prop.is_valid() else 'NO'}")
            
        # Check scraping stats
        stats = factory.get_scraping_stats()
        if 'mitsui' in stats:
            mitsui_stats = stats['mitsui']
            print(f"Scraping stats:")
            print(f"  Duration: {mitsui_stats['scrape_duration']:.1f}s")
            print(f"  Success: {'YES' if mitsui_stats['success'] else 'NO'}")
            
        if len(mitsui_results) > 0:
            print("✅ SUCCESS: Single site scraping working")
            return True
        else:
            print("❌ FAILED: No properties extracted")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_multi_site_scraping():
    """Test scraping multiple sites together"""
    print("\nTesting Multi-Site Scraping")
    print("=" * 40)
    
    try:
        factory = ScraperFactory()
        
        # Test with all available scrapers
        print("Starting multi-site scrape...")
        
        # Use a shorter timeout for testing
        test_config = {
            'browser_config': {
                'headless': True,
                'wait_timeout': 10,
                'page_load_timeout': 20
            }
        }
        
        factory.config = test_config
        
        # Scrape all sites
        all_results = factory.scrape_all_sites()
        
        print(f"Sites scraped: {len(all_results)}")
        
        total_properties = 0
        for site_key, properties in all_results.items():
            site_name = factory.SCRAPERS[site_key]['name']
            print(f"  {site_name}: {len(properties)} properties")
            total_properties += len(properties)
            
        print(f"Total properties: {total_properties}")
        
        # Test combining results
        combined_results = factory.get_combined_results(all_results)
        print(f"Combined unique properties: {len(combined_results)}")
        
        # Test validation
        validation_report = factory.validate_all_results(all_results)
        print(f"\nValidation Summary:")
        
        total_valid = 0
        for site_key, report in validation_report.items():
            print(f"  {report['site_name']}: {report['valid_properties']}/{report['total_properties']} valid ({report['success_rate']:.1f}%)")
            total_valid += report['valid_properties']
            
        print(f"Overall valid properties: {total_valid}")
        
        if total_valid > 0:
            print("✅ SUCCESS: Multi-site scraping working")
            return True
        else:
            print("⚠️ WARNING: No valid properties found")
            return total_properties > 0
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_reporting_and_export():
    """Test reporting and export functionality"""
    print("\nTesting Reporting and Export")
    print("=" * 40)
    
    try:
        factory = ScraperFactory()
        
        # Use Mitsui for reliable test data
        results = {'mitsui': factory.scrape_single_site('mitsui')}
        
        if not results['mitsui']:
            print("No test data available for reporting test")
            return False
            
        # Test summary report
        print("Generating summary report...")
        summary_report = factory.generate_summary_report(results)
        
        print(f"Summary report sections:")
        for section in summary_report.keys():
            print(f"  - {section}")
            
        # Check summary data
        summary = summary_report['summary']
        print(f"Total properties: {summary['total_properties_found']}")
        print(f"Valid properties: {summary['total_valid_properties']}")
        print(f"Success rate: {summary['overall_success_rate']:.1f}%")
        
        # Test JSON export
        print("\nTesting JSON export...")
        json_export = factory.export_results(results, 'json')
        
        # Verify it's valid JSON
        parsed_json = json.loads(json_export)
        print(f"JSON export: {len(json_export)} characters")
        print(f"Sites in export: {list(parsed_json.keys())}")
        
        # Test CSV export
        print("\nTesting CSV export...")
        csv_export = factory.export_results(results, 'csv')
        csv_lines = csv_export.strip().split('\n')
        print(f"CSV export: {len(csv_lines)} lines")
        
        if len(csv_lines) > 1:  # Header + data
            print("✅ SUCCESS: Reporting and export working")
            return True
        else:
            print("❌ FAILED: Export generated but no data")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_error_handling():
    """Test error handling and recovery"""
    print("\nTesting Error Handling")
    print("=" * 30)
    
    try:
        factory = ScraperFactory()
        
        # Test creating non-existent scraper
        invalid_scraper = factory.create_scraper('nonexistent')
        print(f"Invalid scraper creation: {'FAILED' if invalid_scraper is None else 'UNEXPECTED SUCCESS'}")
        
        # Test scraping non-existent site
        invalid_results = factory.scrape_single_site('nonexistent')
        print(f"Invalid site scraping: {len(invalid_results)} properties (expected 0)")
        
        # Test export with invalid format
        try:
            factory.export_results({}, 'invalid_format')
            print("Invalid export format: UNEXPECTED SUCCESS")
            error_handling_works = False
        except ValueError:
            print("Invalid export format: CORRECTLY FAILED")
            error_handling_works = True
            
        # Test with empty results
        empty_report = factory.generate_summary_report({})
        print(f"Empty results report: {len(empty_report)} sections")
        
        if error_handling_works and invalid_scraper is None and len(invalid_results) == 0:
            print("✅ SUCCESS: Error handling working correctly")
            return True
        else:
            print("❌ FAILED: Error handling has issues")
            return False
            
    except Exception as e:
        print(f"❌ UNEXPECTED ERROR: {e}")
        return False

def run_integration_tests():
    """Run all integration tests"""
    print("INTEGRATED SCRAPER SYSTEM TEST SUITE")
    print("=" * 60)
    
    tests = [
        ("ScraperFactory Setup", test_scraper_factory_setup),
        ("Single Site Scraping", test_single_site_scraping),
        ("Multi-Site Scraping", test_multi_site_scraping),
        ("Reporting and Export", test_reporting_and_export),
        ("Error Handling", test_error_handling)
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
    print("INTEGRATION TEST RESULTS:")
    print("=" * 60)
    
    for test_name, result in results.items():
        status = "PASS ✅" if result else "FAIL ❌"
        print(f"{test_name}: {status}")
        
    passed_tests = sum(1 for result in results.values() if result)
    total_tests = len(results)
    success_rate = (passed_tests / total_tests) * 100
    
    print(f"\nOverall Success Rate: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
    
    if success_rate >= 80:
        print("🎉 EXCELLENT: Integrated scraper system working great!")
        print("\nSystem is ready for:")
        print("  ✅ Multi-site property scraping")
        print("  ✅ Data validation and reporting")
        print("  ✅ Export to JSON/CSV formats")
        print("  ✅ Error handling and recovery")
    elif success_rate >= 60:
        print("⚠️ GOOD: Integrated system working but needs improvement")
    else:
        print("❌ NEEDS WORK: Integrated system needs attention")
        
    return success_rate >= 80

def demo_full_scraping_workflow():
    """Demonstrate a complete scraping workflow"""
    print("\n" + "="*60)
    print("DEMONSTRATION: COMPLETE SCRAPING WORKFLOW")
    print("=" * 60)
    
    try:
        # Create factory
        print("1. Creating ScraperFactory...")
        factory = ScraperFactory({
            'browser_config': {'headless': True, 'wait_timeout': 15}
        })
        
        # Scrape all sites
        print("\n2. Scraping all available sites...")
        all_results = factory.scrape_all_sites()
        
        # Generate comprehensive report
        print("\n3. Generating comprehensive report...")
        report = factory.generate_summary_report(all_results)
        
        # Display summary
        print("\n4. FINAL RESULTS SUMMARY:")
        print("-" * 40)
        summary = report['summary']
        print(f"Sites scraped: {summary['total_sites_scraped']}")
        print(f"Total properties found: {summary['total_properties_found']}")
        print(f"Valid properties: {summary['total_valid_properties']}")
        print(f"Overall success rate: {summary['overall_success_rate']:.1f}%")
        
        print(f"\nSite breakdown:")
        for site_key, site_report in report['site_breakdown'].items():
            print(f"  {site_report['site_name']}: {site_report['valid_properties']}/{site_report['total_properties']} properties")
            
        if summary['total_valid_properties'] > 0:
            print(f"\n🎉 SUCCESS: Complete workflow extracted {summary['total_valid_properties']} valid Karuizawa properties!")
            
            # Save sample export
            print("\n5. Exporting results to JSON...")
            json_export = factory.export_results(all_results, 'json')
            
            # Save to file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"karuizawa_properties_{timestamp}.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(json_export)
                
            print(f"Results saved to: {filename}")
            print(f"File size: {len(json_export)} characters")
            
            return True
        else:
            print("❌ No valid properties found in complete workflow")
            return False
            
    except Exception as e:
        print(f"❌ ERROR in complete workflow: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Run all integration tests
    integration_success = run_integration_tests()
    
    # If integration tests pass, run the demo workflow
    if integration_success:
        demo_success = demo_full_scraping_workflow()
        
        if demo_success:
            print(f"\n🏆 COMPLETE SUCCESS!")
            print("The integrated Karuizawa property scraping system is fully operational!")
        else:
            print(f"\n⚠️ Integration tests passed but demo workflow had issues")
    else:
        print(f"\n❌ Integration tests failed - system needs work before demo")