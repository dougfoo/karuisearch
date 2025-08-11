#!/usr/bin/env python3
"""
Remove Royal Resort duplicates - keep only one instance of each unique property
"""

import json
import os
from pathlib import Path

def deduplicate_royal_properties():
    """Remove duplicate Royal Resort properties based on source_url"""
    
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
        
        # Separate Royal Resort from others
        non_royal_props = []
        royal_props = []
        royal_urls_seen = set()
        
        for prop in all_props:
            source_url = prop.get('source_url', '')
            
            if 'royal-resort' in source_url.lower():
                # Check if we've seen this Royal Resort property URL before
                if source_url not in royal_urls_seen:
                    royal_props.append(prop)
                    royal_urls_seen.add(source_url)
                    print(f"[KEEP] Royal Resort: {prop.get('id')} - Price info")
                else:
                    print(f"[DUPLICATE] Removing Royal Resort duplicate: {prop.get('id')}")
            else:
                non_royal_props.append(prop)
        
        # Combine non-royal + unique royal properties
        final_props = non_royal_props + royal_props
        
        print(f"\n[INFO] Final counts:")
        print(f"  - Non-Royal Resort properties: {len(non_royal_props)}")
        print(f"  - Unique Royal Resort properties: {len(royal_props)}")
        print(f"  - Total properties: {len(final_props)}")
        
        # Save cleaned data
        with open(mock_file, 'w', encoding='utf-8') as f:
            json.dump(final_props, f, ensure_ascii=False, indent=2)
        
        print(f"\n[SUCCESS] Deduplicated! Now has {len(final_props)} properties")
        
        # Show breakdown by source
        mitsui_count = len([p for p in final_props if 'mitsuinomori' in p.get('source_url', '')])
        besso_count = len([p for p in final_props if 'besso-navi' in p.get('source_url', '')])
        royal_count = len([p for p in final_props if 'royal-resort' in p.get('source_url', '')])
        
        print(f"\n[INFO] Final breakdown:")
        print(f"  - Mitsui no Mori: {mitsui_count} properties")  
        print(f"  - Besso Navi: {besso_count} properties")
        print(f"  - Royal Resort: {royal_count} properties")
        
    except Exception as e:
        print(f"[ERROR] Failed to deduplicate: {e}")

if __name__ == "__main__":
    print("DEDUPLICATING ROYAL RESORT PROPERTIES")
    print("=" * 50)
    deduplicate_royal_properties()