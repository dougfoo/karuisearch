#!/usr/bin/env python3
"""
Fast balanced scraper - optimized for speed
"""

import sys
import os
import json
import argparse
from datetime import datetime
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from scrapers.scraper_factory import ScraperFactory

def run_fast_balanced_scrape(write_mock=False):
    """Fast scraping with minimal delays"""
    print("==================================================")
    print("    KARUI-SEARCH FAST BALANCED SCRAPER")
    print("    Target: Up to 10 properties per site")
    print("==================================================")
    print(f"Started: {datetime.now().strftime('%H:%M:%S')}")
    
    factory = ScraperFactory()
    all_results = []
    
    # 1. MITSUI (always works reliably)
    print(f"\n{'-' * 20} MITSUI {'-' * 20}")
    try:
        mitsui_scraper = factory.create_scraper('mitsui')
        # Speed up by reducing rate limiting
        mitsui_scraper.rate_limiter.min_delay = 1.0
        mitsui_scraper.rate_limiter.max_delay = 2.0
        
        mitsui_props = mitsui_scraper.scrape_listings()
        print(f"Mitsui: {len(mitsui_props)} properties")
        
        for prop in mitsui_props:
            all_results.append({
                "source": "Mitsui no Mori",
                "title": prop.title,
                "price": prop.price,
                "images": len(prop.image_urls),
                "url": prop.source_url
            })
            
        if mitsui_props:
            sample = mitsui_props[0]
            print(f"  Sample: {sample.title[:50]}...")
            print(f"  Images: {len(sample.image_urls)} images")
            
    except Exception as e:
        print(f"Mitsui error: {e}")
    
    # 2. ROYAL RESORT (limit to 3 for speed)
    print(f"\n{'-' * 18} ROYAL RESORT {'-' * 18}")
    try:
        royal_scraper = factory.create_scraper('royal_resort')
        
        # Quick Royal Resort test
        if royal_scraper.setup_browser():
            if royal_scraper.navigate_to_page(royal_scraper.karuizawa_url):
                properties = royal_scraper.find_property_listings()
                print(f"Royal Resort: Found {len(properties)} total properties")
                
                # Process just first 3 for speed demo
                for i, prop_element in enumerate(properties[:3], 1):
                    print(f"  Processing {i}/3...")
                    try:
                        prop_data = royal_scraper.extract_property_from_listing(prop_element)
                        if prop_data:
                            all_results.append({
                                "source": "Royal Resort",
                                "title": prop_data.title or f"Royal Resort Property {i}",
                                "price": prop_data.price or "Price available",
                                "images": len(prop_data.image_urls),
                                "url": prop_data.source_url or royal_scraper.karuizawa_url
                            })
                        royal_scraper.simulate_human_delay(0.5, 1.0)  # Fast
                    except Exception as e:
                        print(f"    Error: {e}")
                        continue
            
            royal_scraper.close_browser()
        else:
            print("Royal Resort: Browser setup failed")
            
    except Exception as e:
        print(f"Royal Resort error: {e}")
    
    # 3. BESSO NAVI (HTTP, should be fast)
    print(f"\n{'-' * 18} BESSO NAVI {'-' * 19}")
    try:
        besso_scraper = factory.create_scraper('besso_navi')
        besso_props = besso_scraper.scrape_listings()
        print(f"Besso Navi: {len(besso_props)} properties")
        
        for prop in besso_props:
            all_results.append({
                "source": "Besso Navi",
                "title": prop.title,
                "price": prop.price,
                "images": len(prop.image_urls),
                "url": prop.source_url
            })
            
    except Exception as e:
        print(f"Besso Navi error: {e}")
    
    # SUMMARY
    print(f"\n{'=' * 50}")
    print("FAST SCRAPE SUMMARY")
    print(f"{'=' * 50}")
    
    by_source = {}
    total_images = 0
    
    for result in all_results:
        source = result["source"]
        if source not in by_source:
            by_source[source] = []
        by_source[source].append(result)
        total_images += result["images"]
    
    for source, results in by_source.items():
        count = len(results)
        images = sum(r["images"] for r in results)
        print(f"{source:<20}: {count:>2} properties, {images:>3} images")
    
    print(f"{'-' * 50}")
    print(f"{'TOTAL':<20}: {len(all_results):>2} properties, {total_images:>3} images")
    
    # Save results
    if write_mock:
        # Convert to frontend format and save to mock data location
        frontend_data = []
        for i, result in enumerate(all_results):
            frontend_data.append({
                "id": f"prop_{hash(result['title']) % 100000:05x}",
                "price": result["price"],
                "location": result["title"].split(" - ")[-1] if " - " in result["title"] else "軽井沢",
                "property_type": "別荘" if "Royal Resort" in result["source"] else "一戸建て",
                "size_info": "情報なし",
                "building_age": "不明",
                "image_urls": [f"https://via.placeholder.com/400x300/CCCCCC/666666?text=No+Image+Available"] * max(1, result["images"]),
                "rooms": "",
                "source_url": result["url"],
                "scraped_date": datetime.now().strftime('%Y-%m-%d'),
                "date_first_seen": datetime.now().isoformat(),
                "is_new": True,
                "is_featured": i < 3,
                "title": result["title"],
                "description": f"{result['source']}の優良物件。軽井沢の豊かな自然に包まれたリゾートライフをお楽しみください。"
            })
        
        # Save to frontend data directory
        frontend_dir = os.path.join("..", "src", "frontend", "src", "data")
        os.makedirs(frontend_dir, exist_ok=True)
        
        mock_properties_path = os.path.join(frontend_dir, "mockProperties.json")
        with open(mock_properties_path, 'w', encoding='utf-8') as f:
            json.dump(frontend_data, f, indent=2, ensure_ascii=False)
        
        # Generate weekly data
        weekly_data = {
            "week_start": datetime.now().strftime('%Y-%m-%d'),
            "week_end": datetime.now().strftime('%Y-%m-%d'),
            "total_new": len(frontend_data),
            "price_changes": {"increases": 0, "decreases": 0},
            "properties": frontend_data[:6],  # First 6 for weekly report
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "property_types": {"一戸建て": len([p for p in frontend_data if p["property_type"] == "一戸建て"]), 
                                 "別荘": len([p for p in frontend_data if p["property_type"] == "別荘"])},
                "price_ranges": {"under_50M": len(frontend_data)},
                "areas": {"軽井沢": len(frontend_data)}
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
        with open("fast_scrape_results.json", 'w', encoding='utf-8') as f:
            json.dump(all_results, f, indent=2, ensure_ascii=False)
        print(f"\nResults saved to: fast_scrape_results.json")
    
    print(f"Completed: {datetime.now().strftime('%H:%M:%S')}")
    return len(all_results), total_images

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Fast balanced scraper')
    parser.add_argument('--writemock', action='store_true', 
                       help='Write output to src/frontend/src/data/ in mock format')
    args = parser.parse_args()
    
    try:
        props, images = run_fast_balanced_scrape(write_mock=args.writemock)
        print(f"\nSUCCESS: {props} properties with {images} images!")
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()