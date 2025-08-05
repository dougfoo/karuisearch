#!/usr/bin/env python3
"""
Balanced scraper - 10 properties from each of the 3 sites
"""

import sys
import os
import json
import argparse
from datetime import datetime
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from scrapers.scraper_factory import ScraperFactory
from utils.titleGenerator import generate_property_title

def create_limited_scraper(scraper, site_name, limit=10):
    """Create a version of scraper that processes only 'limit' properties"""
    
    if site_name == 'mitsui':
        # Mitsui is already reasonably fast, just return as-is
        return scraper
    
    elif site_name == 'royal_resort':
        # Limit Royal Resort to 10 properties to avoid timeout
        original_scrape = scraper.scrape_listings
        
        def limited_royal_scrape():
            print(f"Starting Royal Resort scraping (limited to {limit} properties)")
            
            if not scraper.setup_browser():
                print("Failed to setup browser")
                return []
            
            if not scraper.navigate_to_page(scraper.karuizawa_url):
                print("Failed to navigate")
                scraper.close_browser()
                return []
            
            # Find properties but limit processing
            properties = scraper.find_property_listings()
            total_found = len(properties)
            properties = properties[:limit]
            print(f"Found {total_found} properties, processing first {len(properties)}")
            
            extracted = []
            for i, prop_element in enumerate(properties, 1):
                print(f"  Processing Royal Resort property {i}/{len(properties)}")
                try:
                    prop_data = scraper.extract_property_from_listing(prop_element)
                    if prop_data and scraper.validate_property_data(prop_data):
                        # Generate consistent title
                        prop_data.title = generate_property_title(
                            source="Royal Resort",
                            property_type=prop_data.property_type or "別荘",
                            building_age=prop_data.building_age or "不明",
                            price=prop_data.price,
                            location=prop_data.location
                        )
                        extracted.append(prop_data)
                        print(f"    + Extracted: {prop_data.title[:60]}...")
                    scraper.simulate_human_delay(1.0, 2.0)  # Faster for balanced run
                except Exception as e:
                    print(f"    - Error: {e}")
                    continue
            
            scraper.close_browser()
            return extracted
        
        scraper.scrape_listings = limited_royal_scrape
        return scraper
    
    elif site_name == 'besso_navi':
        # Besso Navi is already reasonably fast with HTTP
        return scraper
    
    return scraper

def run_balanced_scrape(write_mock=False):
    """Run balanced scraping - 10 properties from each site"""
    print("=" * 50)
    print("    KARUI-SEARCH BALANCED SCRAPER")
    print("    Target: 10 properties per site")
    print("=" * 50)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    factory = ScraperFactory()
    all_properties = []
    results_summary = {}
    
    sites = ['mitsui', 'royal_resort', 'besso_navi']
    site_names = {
        'mitsui': 'Mitsui no Mori',
        'royal_resort': 'Royal Resort Karuizawa', 
        'besso_navi': 'Besso Navi'
    }
    
    for site in sites:
        print(f"\n{'-' * 30}")
        print(f"SCRAPING: {site_names[site]}")
        print(f"{'-' * 30}")
        
        try:
            # Create and configure scraper
            scraper = factory.create_scraper(site)
            limited_scraper = create_limited_scraper(scraper, site, limit=10)
            
            # Scrape properties
            properties = limited_scraper.scrape_listings()
            
            # Add to results
            all_properties.extend(properties)
            results_summary[site] = {
                'count': len(properties),
                'site_name': site_names[site],
                'properties': properties
            }
            
            print(f"Result: {len(properties)} properties extracted")
            
            # Show sample
            if properties:
                sample = properties[0]
                print(f"Sample: {sample.title[:70]}...")
                print(f"        Price: {sample.price}, Images: {len(sample.image_urls)}")
            
        except Exception as e:
            print(f"Error scraping {site}: {e}")
            results_summary[site] = {
                'count': 0,
                'site_name': site_names[site],
                'error': str(e),
                'properties': []
            }
    
    # Generate summary
    print(f"\n{'=' * 50}")
    print("SCRAPING SUMMARY")
    print(f"{'=' * 50}")
    
    total_properties = 0
    total_images = 0
    
    for site, data in results_summary.items():
        count = data['count']
        total_properties += count
        site_images = sum(len(p.image_urls) for p in data['properties'])
        total_images += site_images
        
        status = "SUCCESS" if count > 0 else "FAILED"
        print(f"{data['site_name']:<25}: {count:>2} properties, {site_images:>3} images - {status}")
    
    print(f"{'-' * 50}")
    print(f"{'TOTAL':<25}: {total_properties:>2} properties, {total_images:>3} images")
    
    # Save results
    export_data = []
    
    for prop in all_properties:
        export_data.append({
            "id": getattr(prop, 'id', f"prop_{hash(prop.title) % 10000:04x}"),
            "title": prop.title,
            "price": prop.price,
            "location": prop.location,
            "property_type": prop.property_type,
            "size_info": prop.size_info,
            "building_age": prop.building_age,
            "image_urls": prop.image_urls,
            "rooms": prop.rooms,
            "source_url": prop.source_url,
            "scraped_date": datetime.now().strftime('%Y-%m-%d'),
            "date_first_seen": datetime.now().isoformat(),
            "is_new": True,
            "is_featured": len(export_data) < 6,
            "description": f"軽井沢の優良物件。豊かな自然に包まれたリゾートライフをお楽しみください。"
        })
    
    if write_mock:
        # Save to frontend data directory
        frontend_dir = os.path.join("..", "src", "frontend", "src", "data")
        os.makedirs(frontend_dir, exist_ok=True)
        
        mock_properties_path = os.path.join(frontend_dir, "mockProperties.json")
        with open(mock_properties_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        # Generate weekly data
        weekly_data = {
            "week_start": datetime.now().strftime('%Y-%m-%d'),
            "week_end": datetime.now().strftime('%Y-%m-%d'),
            "total_new": len(export_data),
            "price_changes": {"increases": 1, "decreases": 0},
            "properties": export_data[:6],  # First 6 for weekly report
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "property_types": {
                    "一戸建て": len([p for p in export_data if p["property_type"] == "一戸建て"]), 
                    "別荘": len([p for p in export_data if p["property_type"] == "別荘"])
                },
                "price_ranges": {"under_50M": len([p for p in export_data if "万円" in str(p["price"])])},
                "areas": {"軽井沢": len(export_data)}
            }
        }
        
        weekly_data_path = os.path.join(frontend_dir, "mockWeeklyData.json")
        with open(weekly_data_path, 'w', encoding='utf-8') as f:
            json.dump(weekly_data, f, indent=2, ensure_ascii=False)
        
        print(f"\nMock data saved to:")
        print(f"  {mock_properties_path}")
        print(f"  {weekly_data_path}")
    else:
        # Save to regular results file
        output_file = "balanced_scrape_results.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        print(f"\nResults saved to: {output_file}")
    
    print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    return total_properties, total_images

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Balanced scraper - 10 properties per site')
    parser.add_argument('--writemock', action='store_true', 
                       help='Write output to src/frontend/src/data/ in mock format')
    args = parser.parse_args()
    
    try:
        props, images = run_balanced_scrape(write_mock=args.writemock)
        print(f"\nSUCCESS: {props} properties with {images} images extracted!")
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()