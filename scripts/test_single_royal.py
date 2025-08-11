#!/usr/bin/env python3
"""
Simple test to extract single Royal Resort property with debugging
"""

import sys
import json
import os
from pathlib import Path
from datetime import datetime

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from scrapers.royal_resort_scraper import RoyalResortScraper

def test_single_extraction():
    print("SINGLE ROYAL RESORT EXTRACTION TEST")
    print("=" * 50)
    
    config = {
        'headless': True,
        'wait_timeout': 30,
        'page_load_timeout': 60
    }
    
    scraper = RoyalResortScraper(config)
    
    try:
        print("Setting up browser...")
        if not scraper.setup_browser():
            print("[ERROR] Browser setup failed")
            return
        
        print("Navigating to Royal Resort...")    
        if not scraper.navigate_to_page(scraper.karuizawa_url):
            print("[ERROR] Navigation failed")
            return
            
        print("Waiting for page load...")
        import time
        time.sleep(8)
        
        print("Finding properties...")
        properties = scraper.find_property_listings_with_retry()
        
        if not properties:
            print("[ERROR] No properties found")
            return
            
        print(f"Found {len(properties)} properties, extracting first one...")
        
        # Extract just the first property
        first_property = properties[0]
        property_data = scraper.safe_execute_with_recovery(
            scraper.extract_property_from_listing, 
            first_property,
            max_retries=1
        )
        
        if property_data:
            print("[SUCCESS] Property extracted successfully!")
            print(f"Title: {property_data.title}")
            print(f"Price: {property_data.price}")
            print(f"Location: {property_data.location}")
            print(f"Source: {property_data.source_url}")
            
            # Save to frontend data
            save_to_frontend(property_data)
            
        else:
            print("[ERROR] Property extraction failed")
        
    except Exception as e:
        print(f"[ERROR] Exception during extraction: {e}")
    finally:
        try:
            scraper.cleanup()
        except:
            pass

def save_to_frontend(property_data):
    """Save single property to frontend mock data"""
    try:
        output_dir = Path("../src/frontend/src/data")
        mock_file = output_dir / "mockProperties.json"
        
        # Load existing properties
        existing_props = []
        if mock_file.exists():
            with open(mock_file, 'r', encoding='utf-8') as f:
                all_props = json.load(f)
            # Remove any existing Royal Resort properties
            existing_props = [p for p in all_props if 'royal-resort' not in p.get('source_url', '').lower()]
        
        # Create Royal Resort property dict
        royal_prop = {
            "id": "royal_resort_001",
            "title": getattr(property_data, 'title', 'Royal Resort Property'),
            "price": getattr(property_data, 'price', 'Ask for price'),
            "location": getattr(property_data, 'location', 'Karuizawa'),
            "property_type": getattr(property_data, 'property_type', 'Villa'),
            "building_age": getattr(property_data, 'building_age', 'Unknown'),
            "size_info": getattr(property_data, 'size_info', 'Contact for details'),
            "rooms": getattr(property_data, 'rooms', ''),
            "description": getattr(property_data, 'description', ''),
            "image_urls": getattr(property_data, 'image_urls', []),
            "source_url": getattr(property_data, 'source_url', 'https://www.royal-resort.co.jp/karuizawa/'),
            "scraped_date": datetime.now().strftime('%Y-%m-%d'),
            "date_first_seen": datetime.now().isoformat(),
            "is_new": True,
            "is_featured": False
        }
        
        # Combine and save
        all_properties = existing_props + [royal_prop]
        
        with open(mock_file, 'w', encoding='utf-8') as f:
            json.dump(all_properties, f, ensure_ascii=False, indent=2)
        
        print(f"[SAVED] Royal Resort property saved to {mock_file}")
        print("Frontend should now show the Royal Resort property!")
        
    except Exception as e:
        print(f"[ERROR] Failed to save to frontend: {e}")

if __name__ == "__main__":
    test_single_extraction()