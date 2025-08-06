#!/usr/bin/env python3
"""
Script to update property titles in mockProperties.json using the title generation utility
"""

import json
import sys
import os
from pathlib import Path

# Set UTF-8 encoding for console output
sys.stdout.reconfigure(encoding='utf-8')

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / ".." / "src"))

from utils.titleGenerator import generate_property_title

def main():
    # Paths
    mock_data_path = Path("src/frontend/src/data/mockProperties.json")
    
    # Load existing mock data
    print(f"Loading mock data from {mock_data_path}")
    with open(mock_data_path, 'r', encoding='utf-8') as f:
        properties = json.load(f)
    
    print(f"Found {len(properties)} properties to update")
    
    # Update titles for each property
    updated_count = 0
    for property_data in properties:
        old_title = property_data.get('title', '')
        new_title = generate_property_title(property_data)
        
        if new_title != old_title:
            property_data['title'] = new_title
            updated_count += 1
            print(f"[OK] Updated {property_data['id']}: {new_title}")
        else:
            print(f"[-] No change for {property_data['id']}: {old_title}")
    
    # Save updated data
    print(f"\nSaving updated data with {updated_count} title changes...")
    with open(mock_data_path, 'w', encoding='utf-8') as f:
        json.dump(properties, f, ensure_ascii=False, indent=2)
    
    print(f"[SUCCESS] Successfully updated {updated_count}/{len(properties)} property titles!")
    
    # Show some examples
    print("\n[EXAMPLES] Sample updated titles:")
    for i, prop in enumerate(properties[:5]):
        print(f"  {i+1}. {prop['title']}")

if __name__ == "__main__":
    main()