#!/usr/bin/env python3
"""
Prototype test script for Mitsui no Mori scraper
"""
import sys
import os
import csv
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from scrapers.mitsui_scraper import MitsuiNoMoriScraper

def test_mitsui_scraper():
    """Test the Mitsui no Mori scraper"""
    print("🏠 Testing Mitsui no Mori Karuizawa Scraper")
    print("=" * 50)
    
    # Initialize scraper
    scraper = MitsuiNoMoriScraper()
    
    try:
        # Scrape properties
        print("📡 Starting scrape...")
        properties = scraper.scrape_listings()
        
        print(f"✅ Found {len(properties)} valid properties")
        
        # Display results
        if properties:
            print("\n📋 Property Data Preview:")
            print("-" * 50)
            
            for i, prop in enumerate(properties[:5], 1):  # Show first 5
                print(f"\n{i}. {prop.title}")
                print(f"   💰 Price: {prop.price}")
                print(f"   📍 Location: {prop.location}")
                print(f"   🏠 Type: {prop.property_type}")
                print(f"   📏 Size: {prop.size_info}")
                print(f"   🏗️  Age: {prop.building_age}")
                print(f"   🛏️  Rooms: {prop.rooms}")
                print(f"   🖼️  Images: {len(prop.image_urls)} found")
                print(f"   🔗 URL: {prop.source_url}")
                
        # Save to CSV for analysis
        save_to_csv(properties)
        
        # Generate summary report
        generate_summary_report(properties)
        
    except Exception as e:
        print(f"❌ Error during scraping: {e}")
        import traceback
        traceback.print_exc()

def save_to_csv(properties):
    """Save scraped properties to CSV file"""
    if not properties:
        print("⚠️  No properties to save")
        return
        
    filename = f"mitsui_properties_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            'title', 'price', 'location', 'property_type', 'size_info', 
            'building_age', 'rooms', 'image_count', 'source_url', 'scraped_date'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for prop in properties:
            writer.writerow({
                'title': prop.title,
                'price': prop.price,
                'location': prop.location,
                'property_type': prop.property_type,
                'size_info': prop.size_info,
                'building_age': prop.building_age,
                'rooms': prop.rooms,
                'image_count': len(prop.image_urls),
                'source_url': prop.source_url,
                'scraped_date': prop.scraped_date.isoformat()
            })
            
    print(f"💾 Saved {len(properties)} properties to {filename}")

def generate_summary_report(properties):
    """Generate a summary report of scraped data"""
    if not properties:
        return
        
    print(f"\n📊 Summary Report")
    print("=" * 30)
    
    # Count by property type
    type_counts = {}
    for prop in properties:
        prop_type = prop.property_type or "Unknown"
        type_counts[prop_type] = type_counts.get(prop_type, 0) + 1
        
    print(f"🏠 Property Types:")
    for prop_type, count in type_counts.items():
        print(f"   {prop_type}: {count}")
        
    # Data completeness analysis
    fields = ['title', 'price', 'location', 'property_type', 'size_info', 'building_age', 'rooms']
    completeness = {}
    
    for field in fields:
        filled = sum(1 for prop in properties if getattr(prop, field, "").strip())
        completeness[field] = (filled / len(properties)) * 100
        
    print(f"\n📈 Data Completeness:")
    for field, percentage in completeness.items():
        print(f"   {field}: {percentage:.1f}%")
        
    # Price analysis (if parseable)
    prices = []
    for prop in properties:
        try:
            import re
            price_numbers = re.findall(r'[\d,]+', prop.price.replace(',', ''))
            if price_numbers:
                prices.append(int(price_numbers[0]))
        except:
            continue
            
    if prices:
        print(f"\n💰 Price Analysis:")
        print(f"   Min: ¥{min(prices):,}")
        print(f"   Max: ¥{max(prices):,}")
        print(f"   Avg: ¥{sum(prices)//len(prices):,}")
        
    # Image availability
    with_images = sum(1 for prop in properties if prop.image_urls)
    print(f"\n🖼️  Images: {with_images}/{len(properties)} properties have images")
    
    # Success metrics
    print(f"\n✅ Success Metrics:")
    print(f"   Total properties: {len(properties)}")
    print(f"   Required fields complete: {completeness.get('title', 0):.1f}% title, {completeness.get('price', 0):.1f}% price, {completeness.get('location', 0):.1f}% location")
    
    success_rate = min(completeness.get('title', 0), completeness.get('price', 0), completeness.get('location', 0))
    if success_rate >= 80:
        print(f"   🎉 SUCCESS: {success_rate:.1f}% data completeness (target: >80%)")
    else:
        print(f"   ⚠️  NEEDS IMPROVEMENT: {success_rate:.1f}% data completeness (target: >80%)")

if __name__ == "__main__":
    test_mitsui_scraper()