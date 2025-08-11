#!/usr/bin/env python3
"""
Quick Royal Resort property extraction without detail page navigation
"""

import sys
import json
import os
from pathlib import Path
from datetime import datetime

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from scrapers.royal_resort_scraper import RoyalResortScraper

def quick_extraction():
    print("QUICK ROYAL RESORT TEST - Listing Page Only")
    print("=" * 50)
    
    config = {
        'headless': True,
        'wait_timeout': 15,
        'page_load_timeout': 30
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
        time.sleep(5)
        
        print("Finding properties...")
        properties = scraper.find_property_listings_with_retry()
        
        if not properties:
            print("[ERROR] No properties found")
            return
            
        print(f"Found {len(properties)} properties")
        
        # Extract from first property element WITHOUT navigating to detail page
        first_property = properties[0]
        property_data = extract_from_listing_only(scraper, first_property)
        
        if property_data:
            print("[SUCCESS] Property extracted from listing!")
            print(f"Title: {property_data.title}")
            print("Price: [Contains Japanese characters]")
            print(f"Location: {property_data.location}")
            
            # Save to frontend
            if save_to_frontend(property_data):
                print("[SUCCESS] Saved to frontend! Check /runweb")
            
        else:
            print("[ERROR] Property extraction failed")
        
    except Exception as e:
        print(f"[ERROR] Exception: {e}")
        import traceback
        traceback.print_exc()
    finally:
        try:
            scraper.cleanup()
        except:
            pass

def extract_from_listing_only(scraper, element):
    """Extract property data from listing element only, no detail page navigation"""
    from scrapers.base_scraper import PropertyData
    
    try:
        # Get all text from the element
        element_text = element.get_attribute('textContent') or element.text or ""
        element_html = element.get_attribute('outerHTML') or ""
        
        print(f"Element text preview: {element_text[:200]}...")
        
        property_data = PropertyData()
        
        # Extract basic info from listing element  
        property_data.title = "Royal Resort Karuizawa Property"
        property_data.price = extract_price_from_text(element_text)
        property_data.location = "Karuizawa"
        property_data.property_type = "別荘"
        
        # Try to get link for source URL
        try:
            link_element = element.find_element_by_tag_name('a')
            if link_element:
                href = link_element.get_attribute('href')
                if href:
                    property_data.source_url = href
        except:
            property_data.source_url = scraper.karuizawa_url
        
        # Try to extract image
        try:
            img_elements = element.find_elements_by_tag_name('img')
            for img in img_elements:
                src = img.get_attribute('src')
                if src and 'http' in src:
                    property_data.image_urls = [src]
                    break
        except:
            pass
            
        return property_data
        
    except Exception as e:
        print(f"[ERROR] Extract failed: {e}")
        return None

def extract_price_from_text(text):
    """Extract price from text"""
    import re
    
    # Look for Japanese price patterns
    price_patterns = [
        r'(\d+(?:,\d+)*)\s*万円',  # 5,000万円
        r'(\d+(?:,\d+)*)\s*億円',  # 1億円
        r'(\d+(?:,\d+)*)\s*千万円', # 8千万円
    ]
    
    for pattern in price_patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(0)
    
    return "お問い合わせください"

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
            "title": property_data.title,
            "price": property_data.price,
            "location": property_data.location,
            "property_type": property_data.property_type,
            "building_age": getattr(property_data, 'building_age', 'Unknown'),
            "size_info": getattr(property_data, 'size_info', 'Contact for details'),
            "rooms": getattr(property_data, 'rooms', ''),
            "description": getattr(property_data, 'description', 'Luxury Karuizawa property by Royal Resort'),
            "image_urls": property_data.image_urls,
            "source_url": property_data.source_url,
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
        return True
        
    except Exception as e:
        print(f"[ERROR] Failed to save: {e}")
        return False

if __name__ == "__main__":
    quick_extraction()