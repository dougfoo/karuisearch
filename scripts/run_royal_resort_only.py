#!/usr/bin/env python3
"""
Royal Resort Only Scraper - Test Phase 1 fixes
Extracts properties from Royal Resort only and saves to mock data
"""
import sys
import os
import json
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from scrapers.royal_resort_scraper import RoyalResortScraper

def create_mock_weekly_data(properties):
    """Create weekly summary data"""
    total_properties = len(properties)
    
    if total_properties > 0:
        prices = []
        for prop in properties:
            price_str = prop.get('price', '0')
            # Extract numeric value from price string
            import re
            price_match = re.search(r'[\d,]+', price_str.replace('万円', '').replace('億', '0000').replace(',', ''))
            if price_match:
                try:
                    price_value = int(price_match.group().replace(',', ''))
                    prices.append(price_value)
                except:
                    pass
        
        avg_price = sum(prices) / len(prices) if prices else 0
        min_price = min(prices) if prices else 0
        max_price = max(prices) if prices else 0
    else:
        avg_price = min_price = max_price = 0
    
    return {
        "week": datetime.now().strftime("%Y-W%U"),
        "totalProperties": total_properties,
        "newProperties": total_properties,  # All are "new" for this test
        "averagePrice": f"{avg_price:,.0f}万円" if avg_price else "0円",
        "priceRange": {
            "min": f"{min_price:,.0f}万円" if min_price else "0円",
            "max": f"{max_price:,.0f}万円" if max_price else "0円"
        },
        "sourceBreakdown": {
            "Royal Resort": total_properties,
            "Mitsui no Mori": 0,
            "Besso Navi": 0
        },
        "generatedAt": datetime.now().isoformat(),
        "note": "Royal Resort only extraction test with Phase 1 fixes"
    }

def save_mock_data(properties, output_dir):
    """Save properties and weekly data to mock files"""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Convert PropertyData objects to dictionaries
    properties_data = []
    for i, prop in enumerate(properties):
        prop_dict = {
            "id": f"royal_resort_{i+1:03d}",
            "title": getattr(prop, 'title', 'Royal Resort Property'),
            "price": getattr(prop, 'price', 'お問い合わせください'),
            "location": getattr(prop, 'location', '軽井沢'),
            "property_type": getattr(prop, 'property_type', '別荘'),
            "building_age": getattr(prop, 'building_age', '不明'),
            "size_info": getattr(prop, 'size_info', '詳細はお問い合わせください'),
            "rooms": getattr(prop, 'rooms', ''),
            "description": getattr(prop, 'description', ''),
            "image_urls": getattr(prop, 'image_urls', []),
            "source_url": getattr(prop, 'source_url', 'https://www.royal-resort.co.jp/karuizawa/'),
            "scraped_at": datetime.now().isoformat()
        }
        properties_data.append(prop_dict)
    
    # Save properties
    properties_file = output_path / "mockProperties.json"
    with open(properties_file, 'w', encoding='utf-8') as f:
        json.dump(properties_data, f, ensure_ascii=False, indent=2)
    
    # Save weekly data
    weekly_data = create_mock_weekly_data(properties_data)
    weekly_file = output_path / "mockWeeklyData.json"
    with open(weekly_file, 'w', encoding='utf-8') as f:
        json.dump(weekly_data, f, ensure_ascii=False, indent=2)
    
    return len(properties_data), str(properties_file), str(weekly_file)

def run_royal_resort_extraction():
    """Run Royal Resort extraction with Phase 1 fixes"""
    print("ROYAL RESORT EXTRACTION - PHASE 1 TEST")
    print("=" * 60)
    print("Testing browser crash fixes and extraction optimization")
    print()
    
    # Configure for stability
    config = {
        'headless': True,
        'wait_timeout': 30,
        'page_load_timeout': 60
    }
    
    scraper = RoyalResortScraper(config)
    properties = []
    
    try:
        print("Starting Royal Resort scraping with Phase 1 improvements...")
        print("   - Browser stability enhancements")
        print("   - Crash recovery system")  
        print("   - Optimized extraction methods")
        print()
        
        # Run the scraper
        start_time = datetime.now()
        properties = scraper.scrape_listings()
        end_time = datetime.now()
        
        duration = (end_time - start_time).total_seconds()
        
        print(f"Extraction completed in {duration:.1f} seconds")
        print(f"Properties extracted: {len(properties)}")
        print()
        
        if properties:
            print("[SUCCESS] Royal Resort properties extracted!")
            print()
            print("Sample extracted properties:")
            print("-" * 40)
            
            for i, prop in enumerate(properties[:3], 1):
                print(f"\n{i}. {getattr(prop, 'title', 'No title')}")
                print(f"   Price: {getattr(prop, 'price', 'No price')}")
                print(f"   Location: {getattr(prop, 'location', 'No location')}")
                print(f"   Type: {getattr(prop, 'property_type', 'No type')}")
            
            # Save to mock data
            output_dir = os.path.join("..", "src", "frontend", "src", "data")
            count, props_file, weekly_file = save_mock_data(properties, output_dir)
            
            print(f"\nMock data saved:")
            print(f"   Properties: {props_file} ({count} properties)")
            print(f"   Weekly data: {weekly_file}")
            print()
            print("Ready for frontend at http://localhost:3001")
            print()
            print("[SUCCESS] ROYAL RESORT PHASE 1 FIXES WORKING!")
            
        else:
            print("[FAILED] No properties extracted - investigation needed")
            print("   Check logs above for error details")
            
    except Exception as e:
        print(f"[ERROR] during extraction: {e}")
        import traceback
        traceback.print_exc()
    
    return properties

if __name__ == "__main__":
    properties = run_royal_resort_extraction()
    
    print(f"\n{'='*60}")
    if properties:
        print(f"[FINAL RESULT] {len(properties)} Royal Resort properties extracted!")
        print("   Phase 1 browser crash fixes are working!")
    else:
        print("[FINAL RESULT] No properties extracted")
        print("   Phase 1 fixes may need additional work")
    print(f"{'='*60}")