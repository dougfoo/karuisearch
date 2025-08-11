#!/usr/bin/env python3
"""
Debug Royal Resort image extraction
Investigate why property images aren't being captured properly
"""

import sys
import os
import time
from pathlib import Path

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from scrapers.browser_scraper import BrowserScraper

class RoyalImageDebugger(BrowserScraper):
    """Debug image extraction for Royal Resort"""
    
    def __init__(self):
        config = {
            'headless': False,  # Show browser for debugging
            'wait_timeout': 30,
            'page_load_timeout': 60
        }
        super().__init__(config)
    
    def debug_images(self, url: str):
        """Debug image extraction for a specific property page"""
        print(f"DEBUGGING IMAGES FOR: {url}")
        print("=" * 70)
        
        try:
            if not self.setup_browser():
                print("[ERROR] Browser setup failed")
                return
            
            print("[INFO] Navigating to property page...")
            if not self.navigate_to_page(url):
                print("[ERROR] Navigation failed")
                return
            
            # Wait for page to load
            print("[INFO] Waiting for page to load...")
            time.sleep(6)
            
            print("[INFO] Analyzing all images on the page...")
            
            # Find all image elements
            img_elements = self.driver.find_elements("tag name", 'img')
            print(f"[INFO] Found {len(img_elements)} total img elements")
            
            # Analyze each image
            for i, img in enumerate(img_elements):
                try:
                    src = img.get_attribute('src')
                    alt = img.get_attribute('alt') or 'No alt text'
                    width = img.size.get('width', 0)
                    height = img.size.get('height', 0)
                    
                    print(f"\n--- Image {i+1} ---")
                    print(f"SRC: {src}")
                    print(f"ALT: {alt}")
                    print(f"SIZE: {width}x{height}")
                    
                    # Check if this looks like a property image
                    if src:
                        if any(pattern in src.lower() for pattern in ['royal-h.es-img.jp', 'estate', 'property', 'sale']):
                            print("[MATCH] This looks like a property image!")
                        elif any(pattern in src.lower() for pattern in ['logo', 'icon', 'common', 'weather']):
                            print("[SKIP] This looks like a UI element")
                        else:
                            print("[UNKNOWN] Unknown image type")
                    
                except Exception as e:
                    print(f"[ERROR] Error analyzing image {i+1}: {e}")
            
            print("\n" + "=" * 70)
            print("CURRENT EXTRACTION LOGIC ANALYSIS:")
            print("=" * 70)
            
            # Test current extraction logic
            current_images = self.extract_images_current_logic()
            print(f"[CURRENT] Current logic found {len(current_images)} images:")
            for img in current_images:
                print(f"  - {img}")
            
            print("\n" + "=" * 70)
            print("IMPROVED EXTRACTION LOGIC:")
            print("=" * 70)
            
            # Test improved extraction logic
            improved_images = self.extract_images_improved_logic()
            print(f"[IMPROVED] Improved logic found {len(improved_images)} images:")
            for img in improved_images:
                print(f"  - {img}")
                
        except Exception as e:
            print(f"[ERROR] Debug failed: {e}")
            import traceback
            traceback.print_exc()
        finally:
            try:
                if hasattr(self, 'driver') and self.driver:
                    self.driver.quit()
            except:
                pass
    
    def extract_images_current_logic(self):
        """Current image extraction logic from V3 scraper"""
        try:
            img_elements = self.driver.find_elements("tag name", 'img')
            
            image_urls = []
            for img in img_elements:
                src = img.get_attribute('src')
                if src and ('royal-resort' in src or 'karuizawa' in src.lower()) and src.startswith('http'):
                    if src not in image_urls:
                        image_urls.append(src)
                        if len(image_urls) >= 5:
                            break
            
            return image_urls
            
        except Exception as e:
            print(f"[ERROR] Current logic failed: {e}")
            return []
    
    def extract_images_improved_logic(self):
        """Improved image extraction logic"""
        try:
            img_elements = self.driver.find_elements("tag name", 'img')
            
            property_images = []
            ui_images = []
            
            # Define patterns for property images vs UI elements
            property_patterns = [
                'royal-h.es-img.jp',
                'estate',
                'property', 
                'sale',
                '_10.jpg',  # Pattern from your example
                'img/2105565966390000020504'  # Property ID pattern
            ]
            
            ui_patterns = [
                'logo',
                'icon', 
                'common',
                'weather',
                'btn',
                'button',
                'nav',
                'header',
                'footer'
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
                        if len(property_images) >= 10:  # Get more property images
                            break
                elif not is_ui_image:
                    # Unknown type, might be property image
                    ui_images.append(src)
            
            # Combine property images first, then unknown images if needed
            all_images = property_images + ui_images[:5-len(property_images)]
            
            return all_images[:5]  # Limit to 5 total
            
        except Exception as e:
            print(f"[ERROR] Improved logic failed: {e}")
            return []

def main():
    """Main debug function"""
    # The property URL from your example
    test_url = "https://www.royal-resort.co.jp/karuizawa/estate_list_karuizawa/sell/estate_detail_2105565966390000020504/"
    
    debugger = RoyalImageDebugger()
    debugger.debug_images(test_url)

if __name__ == "__main__":
    main()