#!/usr/bin/env python3
"""
Clean up duplicate Royal Resort properties from mock data
Keep only Mitsui and Besso Navi properties
"""

import json
import os
from pathlib import Path

def cleanup_mock_data():
    """Remove all Royal Resort properties to prepare for fresh scraping"""
    
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
        
        # Filter out Royal Resort properties (all versions)
        non_royal_props = []
        royal_count = 0
        
        for prop in all_props:
            source_url = prop.get('source_url', '').lower()
            prop_id = prop.get('id', '').lower()
            
            # Check if it's a Royal Resort property
            if ('royal-resort' in source_url or 
                'royal_resort' in prop_id or
                'royal-h.es-img.jp' in str(prop.get('image_urls', []))):
                royal_count += 1
                continue
            else:
                non_royal_props.append(prop)
        
        print(f"[INFO] Removed {royal_count} Royal Resort properties")
        print(f"[INFO] Keeping {len(non_royal_props)} non-Royal Resort properties")
        
        # Save cleaned data
        with open(mock_file, 'w', encoding='utf-8') as f:
            json.dump(non_royal_props, f, ensure_ascii=False, indent=2)
        
        print(f"[SUCCESS] Mock data cleaned! Now has {len(non_royal_props)} properties")
        
        # Show breakdown by source
        mitsui_count = len([p for p in non_royal_props if 'mitsuinomori' in p.get('source_url', '')])
        besso_count = len([p for p in non_royal_props if 'besso-navi' in p.get('source_url', '')])
        
        print(f"[INFO] Breakdown:")
        print(f"  - Mitsui no Mori: {mitsui_count} properties")  
        print(f"  - Besso Navi: {besso_count} properties")
        
    except Exception as e:
        print(f"[ERROR] Failed to cleanup mock data: {e}")

if __name__ == "__main__":
    print("CLEANING UP MOCK DATA")
    print("=" * 40)
    cleanup_mock_data()