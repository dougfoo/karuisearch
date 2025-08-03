#!/usr/bin/env python3
"""
Full scraper test for Mitsui no Mori
"""
import sys
import os
import csv
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from scrapers.mitsui_scraper import MitsuiNoMoriScraper

def test_full_scraper():
    """Test the complete scraper functionality"""
    print("Full Mitsui no Mori Scraper Test")
    print("=" * 40)
    
    # Initialize scraper
    scraper = MitsuiNoMoriScraper()
    
    try:
        print("Starting property scraping...")
        properties = scraper.scrape_listings()
        
        print(f"Found {len(properties)} valid properties")
        
        if properties:
            print("\nProperty Summary:")
            print("-" * 30)
            
            for i, prop in enumerate(properties[:5], 1):  # Show first 5
                try:
                    # Safely print property info, handling Unicode
                    title = prop.title.encode('ascii', 'ignore').decode('ascii') if prop.title else "No title"
                    price = prop.price.encode('ascii', 'ignore').decode('ascii') if prop.price else "No price"
                    location = prop.location.encode('ascii', 'ignore').decode('ascii') if prop.location else "No location"
                    
                    print(f"{i}. Title: {title[:50]}...")
                    print(f"   Price: {price}")
                    print(f"   Location: {location}")
                    print(f"   Type: {prop.property_type}")
                    print(f"   Size: {prop.size_info}")
                    print(f"   Images: {len(prop.image_urls)}")
                    print(f"   Valid: {prop.is_valid()}")
                    print()
                except Exception as e:
                    print(f"   Error displaying property {i}: {e}")
                    
        # Save to CSV
        save_results_to_csv(properties)
        
        # Generate summary
        generate_summary(properties)
        
    except Exception as e:
        print(f"Error during scraping: {e}")
        import traceback
        traceback.print_exc()

def save_results_to_csv(properties):
    """Save results to CSV file"""
    if not properties:
        print("No properties to save")
        return
        
    filename = f"mitsui_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            'title', 'price', 'location', 'property_type', 'size_info',
            'building_age', 'rooms', 'image_count', 'source_url', 'valid'
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
                'valid': prop.is_valid()
            })
            
    print(f"Results saved to {filename}")

def generate_summary(properties):
    """Generate summary statistics"""
    print("\nSummary Statistics")
    print("=" * 30)
    
    if not properties:
        print("No properties found")
        return
        
    total = len(properties)
    valid = sum(1 for p in properties if p.is_valid())
    
    print(f"Total properties: {total}")
    print(f"Valid properties: {valid}")
    print(f"Success rate: {(valid/total)*100:.1f}%")
    
    # Field completeness
    fields = ['title', 'price', 'location', 'property_type', 'size_info', 'building_age']
    print(f"\nField Completeness:")
    
    for field in fields:
        filled = sum(1 for p in properties if getattr(p, field, '').strip())
        percentage = (filled / total) * 100 if total > 0 else 0
        print(f"  {field}: {filled}/{total} ({percentage:.1f}%)")
        
    # Images
    with_images = sum(1 for p in properties if p.image_urls)
    print(f"  images: {with_images}/{total} ({(with_images/total)*100:.1f}%)")
    
    # Property types
    types = {}
    for prop in properties:
        prop_type = prop.property_type or "Unknown"
        types[prop_type] = types.get(prop_type, 0) + 1
        
    print(f"\nProperty Types:")
    for prop_type, count in types.items():
        print(f"  {prop_type}: {count}")
        
    # Success evaluation
    print(f"\nSuccess Evaluation:")
    if total >= 10 and (valid/total) >= 0.8:
        print("SUCCESS: Target met (10+ properties, 80%+ valid)")
    elif total >= 5:
        print("PARTIAL: Some properties found, needs improvement")
    else:
        print("NEEDS WORK: Too few properties found")

if __name__ == "__main__":
    test_full_scraper()