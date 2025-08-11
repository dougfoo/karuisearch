#!/usr/bin/env python3
"""
Fix Besso Navi image ordering - put actual property photos first
"""

import json
import os
from pathlib import Path

def fix_besso_images():
    """Fix Besso Navi image ordering to show property photos first"""
    
    # Path to mock data
    mock_file = Path("../src/frontend/src/data/mockProperties.json")
    
    if not mock_file.exists():
        print("[ERROR] Mock properties file not found")
        return
    
    try:
        # Load current properties
        with open(mock_file, 'r', encoding='utf-8') as f:
            all_props = json.load(f)
        
        print(f"[INFO] Found {len(all_props)} total properties")
        
        fixed_count = 0
        
        for prop in all_props:
            source_url = prop.get('source_url', '')
            
            if 'besso-navi' in source_url.lower():
                image_urls = prop.get('image_urls', [])
                if image_urls and len(image_urls) > 1:
                    # Check if first image is pagetop.gif (header/logo)
                    if 'pagetop.gif' in image_urls[0]:
                        # Find the first actual property photo (viewphoto.php)
                        property_photo = None
                        other_images = []
                        
                        for img in image_urls:
                            if 'viewphoto.php' in img and property_photo is None:
                                property_photo = img
                            elif 'viewphoto.php' not in img and 'pagetop.gif' not in img:
                                other_images.append(img)
                        
                        if property_photo:
                            # Reorder: property photo first, then others
                            new_image_order = [property_photo] + other_images
                            prop['image_urls'] = new_image_order[:4]  # Keep max 4 images
                            fixed_count += 1
                            print(f"[FIXED] {prop.get('id')}: Put property photo first")
        
        if fixed_count > 0:
            # Save updated data
            with open(mock_file, 'w', encoding='utf-8') as f:
                json.dump(all_props, f, ensure_ascii=False, indent=2)
            
            print(f"\n[SUCCESS] Fixed {fixed_count} Besso Navi properties")
        else:
            print("\n[INFO] No Besso Navi properties needed fixing")
        
    except Exception as e:
        print(f"[ERROR] Failed to fix Besso images: {e}")

if __name__ == "__main__":
    print("FIXING BESSO NAVI IMAGE ORDERING")
    print("=" * 40)
    fix_besso_images()