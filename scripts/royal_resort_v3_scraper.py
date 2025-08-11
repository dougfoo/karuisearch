#!/usr/bin/env python3
"""
Royal Resort V3 Scraper - Fixed stale element issue
Re-finds elements after each navigation to avoid stale references
"""

import sys
import json
import os
import time
import re
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from scrapers.base_scraper import PropertyData
from scrapers.browser_scraper import BrowserScraper

class RoyalResortV3Scraper(BrowserScraper):
    """Royal Resort scraper V3 - Fixed stale element handling"""
    
    def __init__(self, config: Dict):
        super().__init__(config)
        
        # V3 specific URLs - sorted by newest first, 30 per page
        self.houses_url = "https://www.royal-resort.co.jp/karuizawa/estate_list_karuizawa/sell/?page_limit=30&kind_code%5B%5D=2&page=1&sort=create_date-desc"
        self.land_url = "https://www.royal-resort.co.jp/karuizawa/estate_list_karuizawa/sell/?page_limit=30&kind_code%5B%5D=3&page=1&sort=create_date-desc"
        
    def scrape_properties(self) -> List[PropertyData]:
        """Main scraping method for V3 approach"""
        all_properties = []
        
        try:
            print("[INFO] Starting Royal Resort V3 scraper...")
            
            if not self.setup_browser():
                print("[ERROR] Browser setup failed")
                return []
            
            # Scrape houses first
            print("[INFO] Scraping houses (newest first)...")
            houses = self.scrape_property_type_v3(self.houses_url, "house", 5)
            all_properties.extend(houses)
            print(f"[INFO] Successfully extracted {len(houses)} houses")
            
            # Short delay between types
            time.sleep(3)
            
            # Scrape land
            print("[INFO] Scraping land (newest first)...")
            land = self.scrape_property_type_v3(self.land_url, "land", 5)
            all_properties.extend(land)
            print(f"[INFO] Successfully extracted {len(land)} land properties")
            
            print(f"[SUCCESS] Total properties extracted: {len(all_properties)}")
            return all_properties
            
        except Exception as e:
            print(f"[ERROR] Scraping failed: {e}")
            return []
        finally:
            try:
                if hasattr(self, 'driver') and self.driver:
                    self.driver.quit()
            except:
                pass
    
    def scrape_property_type_v3(self, url: str, property_type: str, max_properties: int) -> List[PropertyData]:
        """V3: Scrape with fresh element finding to avoid stale references"""
        properties = []
        
        try:
            print(f"[INFO] Navigating to {property_type} listings...")
            if not self.navigate_to_page(url):
                print(f"[ERROR] Failed to navigate to {property_type} page")
                return []
            
            # Wait for page to load
            time.sleep(5)
            
            # Extract properties one by one, re-finding elements each time
            for i in range(max_properties):
                try:
                    print(f"[INFO] Processing {property_type} {i+1}/{max_properties}...")
                    
                    # Navigate back to listing page if needed
                    if i > 0:
                        print(f"[INFO] Returning to {property_type} listings page...")
                        if not self.navigate_to_page(url):
                            print(f"[ERROR] Failed to return to {property_type} page")
                            break
                        time.sleep(3)
                    
                    # Fresh find of property elements
                    property_elements = self.find_property_listings()
                    if len(property_elements) <= i:
                        print(f"[INFO] No more {property_type} properties available (found {len(property_elements)})")
                        break
                    
                    # Get the i-th property element
                    element = property_elements[i]
                    
                    # Extract detail URL from this fresh element
                    detail_url = self.extract_detail_url_from_element(element)
                    if not detail_url:
                        print(f"[WARNING] No detail URL found for {property_type} {i+1}")
                        continue
                    
                    # Extract detailed property data
                    property_data = self.extract_from_detail_page(detail_url, property_type)
                    if property_data:
                        properties.append(property_data)
                        print(f"[SUCCESS] Extracted {property_type}: Price [Japanese chars], Location: {property_data.location}")
                    else:
                        print(f"[WARNING] Failed to extract {property_type} {i+1}")
                    
                    # Delay between properties
                    time.sleep(2)
                    
                except Exception as e:
                    print(f"[ERROR] Failed to extract {property_type} {i+1}: {e}")
                    continue
            
        except Exception as e:
            print(f"[ERROR] Failed to scrape {property_type}: {e}")
        
        return properties
    
    def find_property_listings(self) -> List:
        """Find property listing elements on the current page"""
        try:
            # Wait for listings to load
            time.sleep(2)
            
            # Try different selectors for Royal Resort listings
            selectors = [
                ".p-card",
                ".property-item", 
                ".listing-item",
                "[class*='card']",
                ".estate-item"
            ]
            
            for selector in selectors:
                elements = self.driver.find_elements("css selector", selector)
                if elements:
                    # Filter for visible elements
                    visible_elements = [e for e in elements if e.is_displayed() and e.size['height'] > 0]
                    if visible_elements:
                        print(f"[DEBUG] Found {len(visible_elements)} visible elements with selector: {selector}")
                        return visible_elements
            
            print("[WARNING] No property listings found with any selector")
            return []
            
        except Exception as e:
            print(f"[ERROR] Error finding listings: {e}")
            return []
    
    def extract_detail_url_from_element(self, element) -> Optional[str]:
        """Extract the detail page URL from a listing element"""
        try:
            # Look for links within the element
            link_elements = element.find_elements("tag name", 'a')
            
            for link in link_elements:
                href = link.get_attribute('href')
                if href and 'estate_detail_' in href:
                    print(f"[DEBUG] Found detail URL: {href}")
                    return href
            
            # If no direct links, check if element itself is a link
            href = element.get_attribute('href')
            if href and 'estate_detail_' in href:
                return href
            
            return None
            
        except Exception as e:
            print(f"[ERROR] Error extracting detail URL: {e}")
            return None
    
    def extract_from_detail_page(self, detail_url: str, property_type: str) -> Optional[PropertyData]:
        """Extract detailed property information from detail page"""
        try:
            print(f"[DEBUG] Navigating to detail page: {detail_url}")
            
            if not self.navigate_to_page(detail_url):
                print(f"[ERROR] Failed to navigate to detail page")
                return None
            
            # Wait for detail page to load
            time.sleep(4)
            
            # Create property data object
            property_data = PropertyData()
            property_data.source_url = detail_url
            
            # Extract property information from detail page
            self.extract_title(property_data)
            self.extract_price(property_data)
            self.extract_location(property_data)
            self.extract_size_info(property_data)
            self.extract_building_age(property_data)
            self.extract_description(property_data)
            self.extract_images(property_data)
            
            # Set property type based on scraping category
            if property_type == "house":
                property_data.property_type = "一戸建て"
            elif property_type == "land":
                property_data.property_type = "土地"
            else:
                property_data.property_type = "別荘"
            
            # Generate title using title generator
            self.generate_title(property_data)
            
            # Validate the property
            if property_data.is_valid():
                return property_data
            else:
                print(f"[WARNING] Property validation failed for {detail_url}")
                return None
                
        except Exception as e:
            print(f"[ERROR] Error extracting from detail page: {e}")
            return None
    
    # All the extraction methods remain the same as V2
    def extract_title(self, property_data: PropertyData):
        """Extract property title"""
        try:
            title_selectors = [
                "h1.estate-title",
                ".property-title",
                "h1",
                ".title",
                ".estate-name"
            ]
            
            for selector in title_selectors:
                try:
                    element = self.driver.find_element("css selector", selector)
                    if element and element.text.strip():
                        property_data.title = element.text.strip()
                        return
                except:
                    continue
            
            page_title = self.driver.title
            if page_title:
                property_data.title = page_title.replace(' | Royal Resort', '').strip()
            
        except Exception as e:
            print(f"[ERROR] Error extracting title: {e}")
    
    def extract_price(self, property_data: PropertyData):
        """Extract property price"""
        try:
            page_text = self.driver.find_element("tag name", 'body').text
            
            price_patterns = [
                r'(\d{1,3}(?:,\d{3})*)\s*万円',
                r'(\d+)\s*億\s*(\d+)\s*万円',
                r'(\d+)\s*億円',
                r'(\d{1,3}(?:,\d{3})*)\s*千万円',
            ]
            
            for pattern in price_patterns:
                match = re.search(pattern, page_text)
                if match:
                    property_data.price = match.group(0)
                    return
            
            property_data.price = "お問い合わせください"
            
        except Exception as e:
            print(f"[ERROR] Error extracting price: {e}")
            property_data.price = "お問い合わせください"
    
    def extract_location(self, property_data: PropertyData):
        """Extract property location"""
        try:
            page_text = self.driver.find_element("tag name", 'body').text
            
            location_patterns = [
                r'(軽井沢[^,\n]*)',
                r'(中軽井沢[^,\n]*)',
                r'(南軽井沢[^,\n]*)',
                r'(北軽井沢[^,\n]*)'
            ]
            
            for pattern in location_patterns:
                match = re.search(pattern, page_text)
                if match:
                    property_data.location = match.group(1).strip()
                    return
            
            property_data.location = "軽井沢"
            
        except Exception as e:
            print(f"[ERROR] Error extracting location: {e}")
            property_data.location = "軽井沢"
    
    def extract_size_info(self, property_data: PropertyData):
        """Extract size information"""
        try:
            page_text = self.driver.find_element("tag name", 'body').text
            
            size_patterns = [
                r'(\d+(?:\.\d+)?)\s*坪',
                r'(\d+(?:\.\d+)?)\s*㎡',
                r'(\d+(?:\.\d+)?)\s*平米',
            ]
            
            sizes = []
            for pattern in size_patterns:
                matches = re.findall(pattern, page_text)
                sizes.extend([m + '坪' if '坪' in pattern else m + '㎡' for m in matches])
            
            if sizes:
                unique_sizes = list(dict.fromkeys(sizes))[:3]
                property_data.size_info = ' '.join(unique_sizes)
            else:
                property_data.size_info = "詳細はお問い合わせください"
                
        except Exception as e:
            print(f"[ERROR] Error extracting size: {e}")
            property_data.size_info = "詳細はお問い合わせください"
    
    def extract_building_age(self, property_data: PropertyData):
        """Extract building age"""
        try:
            page_text = self.driver.find_element("tag name", 'body').text
            
            age_patterns = [
                r'(新築)',
                r'(築\s*\d+年)',
                r'(\d{4})年\s*建築',
            ]
            
            for pattern in age_patterns:
                match = re.search(pattern, page_text)
                if match:
                    property_data.building_age = match.group(1)
                    return
            
            property_data.building_age = "不明"
            
        except Exception as e:
            print(f"[ERROR] Error extracting building age: {e}")
            property_data.building_age = "不明"
    
    def extract_description(self, property_data: PropertyData):
        """Extract property description"""
        try:
            desc_selectors = [
                ".property-description",
                ".estate-description", 
                ".description",
                ".detail-text"
            ]
            
            for selector in desc_selectors:
                try:
                    element = self.driver.find_element("css selector", selector)
                    if element and element.text.strip():
                        property_data.description = element.text.strip()[:500]
                        return
                except:
                    continue
            
            property_data.description = f"Royal Resort {property_data.property_type} in Karuizawa"
            
        except Exception as e:
            print(f"[ERROR] Error extracting description: {e}")
            property_data.description = "Royal Resort property in Karuizawa"
    
    def extract_images(self, property_data: PropertyData):
        """Extract property images - FIXED for royal-h.es-img.jp domain"""
        try:
            img_elements = self.driver.find_elements("tag name", 'img')
            
            property_images = []
            
            # Define patterns for property images vs UI elements
            property_patterns = [
                'royal-h.es-img.jp',  # Main property image domain
                'sale/img/',          # Property image path pattern
            ]
            
            ui_patterns = [
                'logo',
                'icon', 
                'common',
                'weather',
                'btn',
                'button'
            ]
            
            for img in img_elements:
                src = img.get_attribute('src')
                if not src or not src.startswith('http'):
                    continue
                
                # Check if this is a property image
                is_property_image = any(pattern in src.lower() for pattern in property_patterns)
                is_ui_image = any(pattern in src.lower() for pattern in ui_patterns)
                
                if is_property_image and not is_ui_image:
                    # This looks like a property image
                    if src not in property_images:
                        property_images.append(src)
                        if len(property_images) >= 5:  # Get top 5 property images
                            break
            
            property_data.image_urls = property_images
            print(f"[DEBUG] Found {len(property_images)} property images")
            
        except Exception as e:
            print(f"[ERROR] Error extracting images: {e}")
            property_data.image_urls = []
    
    def generate_title(self, property_data: PropertyData):
        """Generate proper title using title generator"""
        try:
            from utils.titleGenerator import generate_property_title
            
            property_dict = {
                'source_url': property_data.source_url,
                'property_type': property_data.property_type,
                'building_age': property_data.building_age,
                'price': property_data.price,
                'location': property_data.location
            }
            
            generated_title = generate_property_title(property_dict)
            if generated_title and generated_title.strip():
                property_data.title = generated_title
                
        except Exception as e:
            print(f"[ERROR] Error generating title: {e}")
            if not property_data.title:
                property_data.title = f"Royal Resort {property_data.property_type} {property_data.price}"


def save_properties_to_frontend(properties: List[PropertyData]):
    """Save extracted properties to frontend mock data"""
    if not properties:
        print("[WARNING] No properties to save")
        return
    
    try:
        output_dir = Path("../src/frontend/src/data")
        mock_file = output_dir / "mockProperties.json"
        
        # Load existing properties (non-Royal Resort ones)
        existing_props = []
        if mock_file.exists():
            with open(mock_file, 'r', encoding='utf-8') as f:
                all_props = json.load(f)
            # Keep only non-Royal Resort properties
            existing_props = [p for p in all_props if 'royal-resort' not in p.get('source_url', '').lower()]
        
        # Convert PropertyData objects to dictionaries
        royal_props = []
        for i, prop in enumerate(properties):
            prop_dict = {
                "id": f"royal_resort_v3_{i+1:03d}",
                "title": prop.title,
                "price": prop.price,
                "location": prop.location,
                "property_type": prop.property_type,
                "building_age": prop.building_age,
                "size_info": prop.size_info,
                "rooms": getattr(prop, 'rooms', ''),
                "description": prop.description,
                "image_urls": prop.image_urls,
                "source_url": prop.source_url,
                "scraped_date": datetime.now().strftime('%Y-%m-%d'),
                "date_first_seen": datetime.now().isoformat(),
                "is_new": True,
                "is_featured": i < 3  # Mark first 3 as featured
            }
            royal_props.append(prop_dict)
        
        # Combine existing + new Royal Resort properties
        all_properties = existing_props + royal_props
        
        # Save updated properties file
        with open(mock_file, 'w', encoding='utf-8') as f:
            json.dump(all_properties, f, ensure_ascii=False, indent=2)
        
        print(f"[SUCCESS] Saved {len(royal_props)} Royal Resort V3 properties to frontend")
        print(f"Frontend now has {len(all_properties)} total properties")
        
    except Exception as e:
        print(f"[ERROR] Failed to save to frontend: {e}")


def main():
    """Main execution function"""
    print("ROYAL RESORT V3 SCRAPER")
    print("=" * 50)
    print("Fixed stale element handling - re-finds elements after each navigation")
    print("Targeting 5 houses + 5 land properties (total 10)")
    print()
    
    config = {
        'headless': True,
        'wait_timeout': 30,
        'page_load_timeout': 60
    }
    
    scraper = RoyalResortV3Scraper(config)
    
    try:
        # Run the scraper
        properties = scraper.scrape_properties()
        
        if properties:
            print(f"\n[SUCCESS] Extracted {len(properties)} properties total")
            
            # Save to frontend
            save_properties_to_frontend(properties)
            
            print("\n[SUCCESS] Royal Resort V3 scraping completed!")
            print("Check http://localhost:3000 to see the new properties")
                
        else:
            print("[ERROR] No properties extracted")
            
    except Exception as e:
        print(f"[ERROR] Scraper failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()