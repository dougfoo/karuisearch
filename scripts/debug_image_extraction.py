#!/usr/bin/env python3
"""
Debug script to test image extraction logic step by step
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
from typing import List

def debug_image_extraction(url: str):
    """Debug image extraction for a specific property URL"""
    print(f"\n=== DEBUGGING IMAGE EXTRACTION FOR: {url} ===")
    
    try:
        # Step 1: Fetch the page
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        print(f"+ Page fetched successfully (status: {response.status_code})")
        
        # Step 2: Parse HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        print(f"+ HTML parsed successfully")
        
        # Step 3: Find all image elements
        img_elements = soup.select('img')
        print(f"+ Found {len(img_elements)} img elements")
        
        # Step 4: Extract all image URLs
        raw_images = []
        for i, img in enumerate(img_elements):
            src = img.get('src') or img.get('data-src')
            if src:
                print(f"  Image {i+1}: {src}")
                if not src.startswith('data:'):
                    img_url = urljoin(url, src)
                    if img_url not in raw_images:
                        raw_images.append(img_url)
                        print(f"    + Added: {img_url}")
                    else:
                        print(f"    - Duplicate skipped")
                else:
                    print(f"    - Skipped data URL")
            else:
                print(f"  Image {i+1}: No src attribute")
        
        print(f"\n+ Raw images collected: {len(raw_images)}")
        for i, img_url in enumerate(raw_images):
            print(f"  {i+1}. {img_url}")
        
        # Step 5: Apply filtering logic
        filtered_images = filter_property_images(raw_images)
        print(f"\n+ Filtered images: {len(filtered_images)}")
        for i, img_url in enumerate(filtered_images):
            print(f"  {i+1}. {img_url}")
        
        return filtered_images
        
    except Exception as e:
        print(f"X Error: {e}")
        return []

def filter_property_images(image_urls: List[str]) -> List[str]:
    """Apply the same filtering logic as in the scraper"""
    if not image_urls:
        return []
    
    # Filter out common non-property images
    filtered_urls = []
    exclude_patterns = [
        r'logo', r'banner', r'nav', r'menu', r'button', r'icon',
        r'header', r'footer', r'sidebar', r'bg_', r'background',
        r'arrow', r'search', r'contact', r'phone', r'mail',
        r'social', r'facebook', r'twitter', r'instagram',
        r'\.gif$', r'spacer', r'blank', r'transparent'
    ]
    
    for url in image_urls:
        # Skip if matches exclude patterns
        if any(re.search(pattern, url, re.IGNORECASE) for pattern in exclude_patterns):
            print(f"    - Filtered out: {url} (matches exclude pattern)")
            continue
        
        # Skip very small images (likely icons)
        if any(size in url.lower() for size in ['16x16', '32x32', '24x24', 'thumb']):
            print(f"    - Filtered out: {url} (small image)")
            continue
        
        filtered_urls.append(url)
        print(f"    + Kept: {url}")
    
    return filtered_urls

def test_mitsui_properties():
    """Test image extraction on known Mitsui properties"""
    
    # Test URLs from actual scraped data
    test_urls = [
        "https://www.mitsuinomori.co.jp/karuizawa/realestate/nk0405h/",  # prop_02dec0ad - working
        "https://www.mitsuinomori.co.jp/karuizawa/realestate/025c014hr/",  # prop_0014b94e 
        "https://www.mitsuinomori.co.jp/karuizawa/realestate/nk0462lr/",  # prop_0346018e
    ]
    
    print("=== TESTING MITSUI PROPERTY IMAGE EXTRACTION ===")
    
    results = {}
    for url in test_urls:
        images = debug_image_extraction(url)
        results[url] = images
        print(f"\n{'='*60}")
    
    # Summary
    print(f"\n=== SUMMARY ===")
    for url, images in results.items():
        print(f"{url}: {len(images)} images found")
        if images:
            print(f"  First image: {images[0]}")

if __name__ == "__main__":
    test_mitsui_properties()