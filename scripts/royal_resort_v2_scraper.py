#!/usr/bin/env python3
"""
Royal Resort V2 Scraper - Focused approach with specific URLs
Targets houses and land separately with newest-first sorting
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

class RoyalResortV2Scraper(BrowserScraper):
    """Enhanced Royal Resort scraper with targeted URLs"""
    
    def __init__(self, config: Dict):
        super().__init__(config)
        
        # V2 specific URLs - sorted by newest first, 30 per page
        self.houses_url = "https://www.royal-resort.co.jp/karuizawa/estate_list_karuizawa/sell/?page_limit=30&kind_code%5B%5D=2&page=1&sort=create_date-desc"
        self.land_url = "https://www.royal-resort.co.jp/karuizawa/estate_list_karuizawa/sell/?page_limit=30&kind_code%5B%5D=3&page=1&sort=create_date-desc"
        
        # Detail page URL patterns
        self.detail_url_pattern = r'estate_detail_(\d+)/'
        
    def scrape_properties(self) -> List[PropertyData]:
        """Main scraping method for V2 approach"""
        all_properties = []
        
        try:
            print("[INFO] Starting Royal Resort V2 scraper...")
            
            if not self.setup_browser():
                print("[ERROR] Browser setup failed")
                return []
            
            # Scrape houses first
            print("[INFO] Scraping houses (newest first)...")
            houses = self.scrape_property_type(self.houses_url, "house")
            all_properties.extend(houses)
            print(f"[INFO] Found {len(houses)} houses")
            
            # Short delay between types
            time.sleep(3)
            
            # Scrape land
            print("[INFO] Scraping land (newest first)...")
            land = self.scrape_property_type(self.land_url, "land")
            all_properties.extend(land)
            print(f"[INFO] Found {len(land)} land properties")
            
            print(f"[SUCCESS] Total properties found: {len(all_properties)}")
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
    
    def scrape_property_type(self, url: str, property_type: str) -> List[PropertyData]:
        """Scrape a specific property type (houses or land)"""
        properties = []
        
        try:
            print(f"[INFO] Navigating to {property_type} listings...")
            if not self.navigate_to_page(url):
                print(f"[ERROR] Failed to navigate to {property_type} page")
                return []
            
            # Wait for page to load
            time.sleep(5)
            
            # Find property listing elements
            property_elements = self.find_property_listings()
            print(f"[INFO] Found {len(property_elements)} {property_type} listings on page")
            
            # Extract from each property (limit to first 10 properties)
            max_properties = 10
            for i, element in enumerate(property_elements[:max_properties]):
                try:
                    print(f"[INFO] Extracting {property_type} {i+1}/{min(len(property_elements), max_properties)}...")
                    
                    # Get the detail URL from listing
                    detail_url = self.extract_detail_url_from_element(element)
                    if not detail_url:
                        print(f"[WARNING] No detail URL found for {property_type} {i+1}")
                        continue
                    
                    # Extract detailed property data
                    property_data = self.extract_from_detail_page(detail_url, property_type)
                    if property_data:
                        properties.append(property_data)
                        print(f"[SUCCESS] Extracted {property_type} property: {property_data.title}")
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
        """Find property listing elements on the page"""
        try:
            # Wait for listings to load
            time.sleep(3)
            
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
                        print(f"[INFO] Found {len(visible_elements)} visible elements with selector: {selector}")
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
                    print(f"[INFO] Found detail URL: {href}")
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
            print(f"[INFO] Navigating to detail page: {detail_url}")
            
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
    
    def extract_title(self, property_data: PropertyData):
        """Extract property title"""
        try:
            # Try various title selectors
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
            
            # Fallback: use page title
            page_title = self.driver.title
            if page_title:
                property_data.title = page_title.replace(' | Royal Resort', '').strip()
            
        except Exception as e:
            print(f"[ERROR] Error extracting title: {e}")
    
    def extract_price(self, property_data: PropertyData):
        """Extract property price"""
        try:
            # Look for price in text content
            page_text = self.driver.find_element("tag name", 'body').text
            
            # Japanese price patterns
            price_patterns = [
                r'(\d{1,3}(?:,\d{3})*)\s*万円',  # 5,000万円
                r'(\d+)\s*億\s*(\d+)\s*万円',     # 1億5000万円  
                r'(\d+)\s*億円',                  # 2億円
                r'(\d{1,3}(?:,\d{3})*)\s*千万円', # 8千万円
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
            
            # Look for Karuizawa location patterns
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
            
            # Look for size patterns (Japanese)
            size_patterns = [
                r'(\d+(?:\.\d+)?)\s*坪',   # 300坪
                r'(\d+(?:\.\d+)?)\s*㎡',   # 500㎡
                r'(\d+(?:\.\d+)?)\s*平米', # 500平米
            ]
            
            sizes = []
            for pattern in size_patterns:
                matches = re.findall(pattern, page_text)
                sizes.extend([m + '坪' if '坪' in pattern else m + '㎡' for m in matches])
            
            if sizes:
                # Take first few unique sizes
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
            
            # Look for age patterns
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
            # Try to find description sections
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
                        property_data.description = element.text.strip()[:500]  # Limit length
                        return
                except:
                    continue
            
            property_data.description = f"Royal Resort {property_data.property_type} in Karuizawa"
            
        except Exception as e:
            print(f"[ERROR] Error extracting description: {e}")
            property_data.description = "Royal Resort property in Karuizawa"
    
    def extract_images(self, property_data: PropertyData):
        """Extract property images"""
        try:
            # Find image elements
            img_elements = self.driver.find_elements("tag name", 'img')
            
            image_urls = []
            for img in img_elements:
                src = img.get_attribute('src')
                if src and ('royal-resort' in src or 'karuizawa' in src.lower()) and src.startswith('http'):
                    # Avoid duplicate images
                    if src not in image_urls:
                        image_urls.append(src)
                        if len(image_urls) >= 5:  # Limit to 5 images
                            break
            
            property_data.image_urls = image_urls
            
        except Exception as e:
            print(f"[ERROR] Error extracting images: {e}")
            property_data.image_urls = []
    
    def generate_title(self, property_data: PropertyData):
        """Generate proper title using title generator"""
        try:
            from utils.titleGenerator import generate_property_title
            
            # Create dict for title generation
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
            # Fallback title
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
                "id": f"royal_resort_v2_{i+1:03d}",
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
                "is_featured": i < 2  # Mark first 2 as featured
            }
            royal_props.append(prop_dict)
        
        # Combine existing + new Royal Resort properties
        all_properties = existing_props + royal_props
        
        # Save updated properties file
        with open(mock_file, 'w', encoding='utf-8') as f:
            json.dump(all_properties, f, ensure_ascii=False, indent=2)
        
        print(f"[SUCCESS] Saved {len(royal_props)} Royal Resort V2 properties to frontend")
        print(f"Frontend now has {len(all_properties)} total properties")
        
    except Exception as e:
        print(f"[ERROR] Failed to save to frontend: {e}")


def main():
    """Main execution function"""
    print("ROYAL RESORT V2 SCRAPER")
    print("=" * 50)
    print("Targeting houses and land with newest-first sorting")
    print("Using detail page extraction for complete data")
    print()
    
    config = {
        'headless': True,
        'wait_timeout': 30,
        'page_load_timeout': 60
    }
    
    scraper = RoyalResortV2Scraper(config)
    
    try:
        # Run the scraper
        properties = scraper.scrape_properties()
        
        if properties:
            print(f"\n[SUCCESS] Extracted {len(properties)} properties")
            
            # Save to frontend
            save_properties_to_frontend(properties)
            
            # Print summary
            print("\nPROPERTY SUMMARY:")
            for i, prop in enumerate(properties, 1):
                print(f"{i}. {prop.title}")
                print(f"   Price: [Japanese characters]")
                print(f"   Location: {prop.location}")
                print(f"   Type: {prop.property_type}")
                print()
                
        else:
            print("[ERROR] No properties extracted")
            
    except Exception as e:
        print(f"[ERROR] Scraper failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()