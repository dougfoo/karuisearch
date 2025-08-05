#!/usr/bin/env python3
"""
Karui-Search Demo - Complete Karuizawa Property Scraping System
Demonstrates the full functionality of all 3 scrapers working together
"""
import sys
import os
from datetime import datetime
import json

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from scrapers.scraper_factory import ScraperFactory

def safe_print(text):
    """Print text safely, converting Unicode to ASCII if needed"""
    if isinstance(text, str):
        return text.encode('ascii', 'ignore').decode('ascii')
    return str(text)

def print_banner():
    """Print the Karui-Search banner"""
    print("=" * 80)
    print("                          KARUI-SEARCH (軽井サーチ)")
    print("                   Karuizawa Real Estate Data Aggregator")
    print("=" * 80)
    print()

def print_scraper_overview():
    """Print overview of available scrapers"""
    print("🏠 AVAILABLE SCRAPERS:")
    print("-" * 40)
    
    factory = ScraperFactory()
    scrapers = factory.get_available_scrapers()
    
    for key, info in scrapers.items():
        priority_stars = "⭐" * info['priority']
        print(f"  {priority_stars} {info['name']}")
        print(f"      Type: {info['type'].title()} scraper")
        print(f"      Description: {info['description']}")
        print()

def demo_individual_scrapers():
    """Demonstrate each scraper individually"""
    print("🔍 INDIVIDUAL SCRAPER DEMONSTRATION:")
    print("-" * 50)
    
    factory = ScraperFactory({
        'browser_config': {
            'headless': True,
            'wait_timeout': 15
        }
    })
    
    scrapers = factory.get_available_scrapers()
    individual_results = {}
    
    for i, (key, info) in enumerate(scrapers.items(), 1):
        print(f"\n{i}. Testing {info['name']}...")
        print(f"   URL: {factory.create_scraper(key).base_url if factory.create_scraper(key) else 'N/A'}")
        
        try:
            properties = factory.scrape_single_site(key)
            individual_results[key] = properties
            
            print(f"   ✅ SUCCESS: Found {len(properties)} properties")
            
            if properties:
                sample = properties[0]
                print(f"   Sample: {safe_print(sample.title)[:50]}...")
                print(f"   Price: {safe_print(sample.price)}")
                
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            individual_results[key] = []
            
    return individual_results

def demo_integrated_scraping():
    """Demonstrate integrated multi-site scraping"""
    print("\n🌐 INTEGRATED MULTI-SITE SCRAPING:")
    print("-" * 50)
    
    factory = ScraperFactory({
        'browser_config': {
            'headless': True,
            'wait_timeout': 12
        },
        'rate_limit': {
            'requests_per_second': 0.5  # Slightly faster for demo
        }
    })
    
    print("Starting comprehensive scrape of all Karuizawa property sites...")
    
    try:
        # Scrape all sites
        all_results = factory.scrape_all_sites()
        
        print(f"\n📊 SCRAPING RESULTS:")
        print("-" * 30)
        
        total_properties = 0
        for site_key, properties in all_results.items():
            site_info = factory.SCRAPERS[site_key]
            print(f"  {site_info['name']}: {len(properties)} properties")
            total_properties += len(properties)
            
        print(f"  TOTAL: {total_properties} properties found")
        
        # Generate comprehensive report
        report = factory.generate_summary_report(all_results)
        
        return all_results, report
        
    except Exception as e:
        print(f"❌ ERROR in integrated scraping: {e}")
        return {}, {}

def display_comprehensive_report(report):
    """Display the comprehensive scraping report"""
    if not report:
        print("No report data available")
        return
        
    print(f"\n📈 COMPREHENSIVE ANALYSIS REPORT:")
    print("-" * 50)
    
    summary = report['summary']
    print(f"Scraping completed: {summary['scraping_timestamp']}")
    print(f"Sites processed: {summary['total_sites_scraped']}")
    print(f"Properties found: {summary['total_properties_found']}")
    print(f"Valid properties: {summary['total_valid_properties']}")
    print(f"Success rate: {summary['overall_success_rate']:.1f}%")
    
    print(f"\n📍 SITE-BY-SITE BREAKDOWN:")
    print("-" * 30)
    
    for site_key, site_report in report['site_breakdown'].items():
        success_icon = "✅" if site_report['meets_minimum'] else "⚠️"
        karuizawa_icon = "🏔️" if site_report['has_karuizawa_properties'] else "❓"
        
        print(f"  {success_icon} {karuizawa_icon} {site_report['site_name']}")
        print(f"      Properties: {site_report['valid_properties']}/{site_report['total_properties']} valid ({site_report['success_rate']:.1f}%)")
        
    if 'price_analysis' in report and report['price_analysis']:
        price_stats = report['price_analysis']
        print(f"\n💰 PRICE ANALYSIS:")
        print("-" * 20)
        print(f"Properties with prices: {price_stats['count']}")
        print(f"Price range: ¥{price_stats['min_price']:,.0f} - ¥{price_stats['max_price']:,.0f}")
        print(f"Average price: ¥{price_stats['avg_price']:,.0f}")
        
    if 'property_types' in report and report['property_types']:
        print(f"\n🏘️ PROPERTY TYPES:")
        print("-" * 20)
        for prop_type, count in report['property_types'].items():
            print(f"  {safe_print(prop_type)}: {count} properties")

def save_results(all_results, report):
    """Save results to files"""
    print(f"\n💾 SAVING RESULTS:")
    print("-" * 20)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    try:
        factory = ScraperFactory()
        
        # Save JSON export
        json_filename = f"karuizawa_properties_{timestamp}.json"
        json_export = factory.export_results(all_results, 'json')
        
        with open(json_filename, 'w', encoding='utf-8') as f:
            f.write(json_export)
            
        print(f"  📄 Property data: {json_filename} ({len(json_export)} chars)")
        
        # Save CSV export
        csv_filename = f"karuizawa_properties_{timestamp}.csv"
        csv_export = factory.export_results(all_results, 'csv')
        
        with open(csv_filename, 'w', encoding='utf-8') as f:
            f.write(csv_export)
            
        csv_lines = len(csv_export.strip().split('\n'))
        print(f"  📊 CSV data: {csv_filename} ({csv_lines} lines)")
        
        # Save detailed report
        report_filename = f"scraping_report_{timestamp}.json"
        with open(report_filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
            
        print(f"  📋 Analysis report: {report_filename}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ ERROR saving files: {e}")
        return False

def demo_data_quality():
    """Demonstrate data quality and validation"""
    print(f"\n🔍 DATA QUALITY DEMONSTRATION:")
    print("-" * 40)
    
    factory = ScraperFactory()
    
    # Use Mitsui scraper as it's most reliable
    print("Testing data quality with Mitsui no Mori properties...")
    
    try:
        properties = factory.scrape_single_site('mitsui')
        
        if not properties:
            print("No properties available for quality demo")
            return
            
        print(f"Analyzing {len(properties)} properties...")
        
        validation_metrics = {
            'has_title': 0,
            'has_price': 0,
            'has_location': 0,
            'has_property_type': 0,
            'has_size_info': 0,
            'has_images': 0,
            'karuizawa_related': 0,
            'overall_valid': 0
        }
        
        for prop in properties:
            if prop.title: validation_metrics['has_title'] += 1
            if prop.price: validation_metrics['has_price'] += 1
            if prop.location: validation_metrics['has_location'] += 1
            if prop.property_type: validation_metrics['has_property_type'] += 1
            if prop.size_info: validation_metrics['has_size_info'] += 1
            if prop.image_urls: validation_metrics['has_images'] += 1
            if prop.contains_karuizawa(): validation_metrics['karuizawa_related'] += 1
            if prop.is_valid(): validation_metrics['overall_valid'] += 1
            
        total = len(properties)
        print(f"\nData Completeness Analysis:")
        for metric, count in validation_metrics.items():
            percentage = (count / total * 100) if total > 0 else 0
            status = "✅" if percentage >= 80 else "⚠️" if percentage >= 50 else "❌"
            metric_name = metric.replace('_', ' ').title()
            print(f"  {status} {metric_name}: {count}/{total} ({percentage:.1f}%)")
            
    except Exception as e:
        print(f"❌ ERROR in data quality demo: {e}")

def main():
    """Main demo function"""
    print_banner()
    
    print("Welcome to Karui-Search - your comprehensive Karuizawa property aggregator!")
    print("This demo will showcase the complete scraping system across all target sites.")
    print()
    
    # Show available scrapers
    print_scraper_overview()
    
    # Test individual scrapers
    individual_results = demo_individual_scrapers()
    
    # Test integrated scraping
    all_results, report = demo_integrated_scraping()
    
    # Display comprehensive report
    display_comprehensive_report(report)
    
    # Demonstrate data quality
    demo_data_quality()
    
    # Save results
    if all_results and report:
        saved = save_results(all_results, report)
        
        if saved:
            print(f"\n🎉 DEMO COMPLETE!")
            print("=" * 50)
            print("Karui-Search successfully demonstrated:")
            print("  ✅ Multi-site property scraping")
            print("  ✅ Data validation and quality analysis")
            print("  ✅ Comprehensive reporting")
            print("  ✅ Export to multiple formats")
            print("  ✅ Ethical scraping with rate limiting")
            print()
            print("The system is ready for production use!")
            print("Run individual test files to verify specific components.")
        else:
            print("⚠️ Demo completed but file saving had issues")
    else:
        print("⚠️ Demo completed but no data was extracted")
        print("Check individual scraper tests for debugging")

if __name__ == "__main__":
    main()