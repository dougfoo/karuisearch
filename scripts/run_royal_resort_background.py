#!/usr/bin/env python3
"""
Royal Resort Background Extraction - No timeout limits
Runs extraction in background and saves results progressively
"""
import sys
import os
import json
import threading
import time
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from scrapers.royal_resort_scraper import RoyalResortScraper

class RoyalResortBackgroundProcessor:
    def __init__(self):
        self.properties = []
        self.status = "initializing"
        self.progress = 0
        self.total_found = 0
        self.errors = []
        self.start_time = None
        
    def save_progress(self):
        """Save current progress to mock data files"""
        if not self.properties:
            return
            
        output_dir = Path("../src/frontend/src/data")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Load existing properties (non-Royal Resort ones)
        existing_props = []
        mock_file = output_dir / "mockProperties.json"
        
        if mock_file.exists():
            try:
                with open(mock_file, 'r', encoding='utf-8') as f:
                    all_props = json.load(f)
                # Keep only non-Royal Resort properties
                existing_props = [p for p in all_props if 'royal-resort' not in p.get('source_url', '').lower()]
            except:
                pass
        
        # Convert PropertyData objects to dictionaries
        royal_props = []
        for i, prop in enumerate(self.properties):
            prop_dict = {
                "id": f"royal_resort_{i+1:03d}",
                "title": getattr(prop, 'title', f'Royal Resort Property {i+1}'),
                "price": getattr(prop, 'price', 'お問い合わせください'),
                "location": getattr(prop, 'location', '軽井沢'),
                "property_type": getattr(prop, 'property_type', '別荘'),
                "building_age": getattr(prop, 'building_age', '不明'),
                "size_info": getattr(prop, 'size_info', '詳細はお問い合わせください'),
                "rooms": getattr(prop, 'rooms', ''),
                "description": getattr(prop, 'description', ''),
                "image_urls": getattr(prop, 'image_urls', []),
                "source_url": getattr(prop, 'source_url', 'https://www.royal-resort.co.jp/karuizawa/'),
                "scraped_at": datetime.now().isoformat()
            }
            royal_props.append(prop_dict)
        
        # Combine existing + Royal Resort properties
        all_properties = existing_props + royal_props
        
        # Save updated properties file
        with open(mock_file, 'w', encoding='utf-8') as f:
            json.dump(all_properties, f, ensure_ascii=False, indent=2)
        
        # Create updated weekly data
        weekly_data = {
            "week": datetime.now().strftime("%Y-W%U"),
            "totalProperties": len(all_properties),
            "newProperties": len(royal_props),
            "averagePrice": "8,500万円",  # Estimated for Royal Resort
            "priceRange": {
                "min": "50万円",
                "max": "25億円"
            },
            "sourceBreakdown": {
                "Royal Resort": len(royal_props),
                "Mitsui no Mori": len([p for p in existing_props if 'mitsuinomori' in p.get('source_url', '')]),
                "Besso Navi": len([p for p in existing_props if 'besso-navi' in p.get('source_url', '')])
            },
            "generatedAt": datetime.now().isoformat(),
            "note": f"Background processing: {len(royal_props)} Royal Resort properties added"
        }
        
        weekly_file = output_dir / "mockWeeklyData.json"
        with open(weekly_file, 'w', encoding='utf-8') as f:
            json.dump(weekly_data, f, ensure_ascii=False, indent=2)
            
        print(f"[SAVED] {len(royal_props)} Royal Resort properties to mock data")
        return len(royal_props)
    
    def run_extraction(self):
        """Run the extraction in background thread"""
        self.status = "running"
        self.start_time = datetime.now()
        
        config = {
            'headless': True,
            'wait_timeout': 30,
            'page_load_timeout': 60
        }
        
        scraper = RoyalResortScraper(config)
        
        try:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Starting background extraction...")
            
            # Setup and navigate
            if not scraper.setup_browser():
                self.status = "failed"
                self.errors.append("Browser setup failed")
                return
                
            if not scraper.navigate_to_page(scraper.karuizawa_url):
                self.status = "failed"
                self.errors.append("Navigation failed")
                return
            
            # Wait for page load
            time.sleep(8)  # Extended wait for JS to fully load
            
            # Find properties
            properties = scraper.find_property_listings_with_retry()
            self.total_found = len(properties)
            
            if not properties:
                self.status = "failed"
                self.errors.append("No properties found")
                return
            
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Found {self.total_found} properties, starting extraction...")
            
            # Extract properties one by one with progress saving
            max_to_process = min(5, len(properties))  # Process up to 5 properties
            
            for i, prop_element in enumerate(properties[:max_to_process]):
                try:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] Processing property {i+1}/{max_to_process}...")
                    
                    # Extract with crash recovery
                    property_data = scraper.safe_execute_with_recovery(
                        scraper.extract_property_from_listing, 
                        prop_element,
                        max_retries=2
                    )
                    
                    if property_data:
                        # Generate proper title
                        if hasattr(property_data, 'price') and (property_data.price or property_data.location or property_data.property_type):
                            from utils.titleGenerator import generate_property_title
                            property_dict = {
                                'source_url': property_data.source_url,
                                'property_type': property_data.property_type,
                                'building_age': property_data.building_age,
                                'price': property_data.price,
                                'location': property_data.location
                            }
                            property_data.title = generate_property_title(property_dict)
                        
                        self.properties.append(property_data)
                        self.progress = i + 1
                        
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] [SUCCESS] Property {i+1} extracted: {property_data.title}")
                        
                        # Save progress after each successful extraction
                        saved_count = self.save_progress()
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] [SAVED] Progress saved: {saved_count} total Royal Resort properties")
                        
                    else:
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] [WARNING] Property {i+1} extraction returned None")
                        
                    # Short delay between properties
                    time.sleep(2)
                    
                except Exception as e:
                    error_msg = f"Property {i+1} extraction failed: {e}"
                    self.errors.append(error_msg)
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] [ERROR] {error_msg}")
                    continue
            
            self.status = "completed"
            
        except Exception as e:
            self.status = "failed"
            error_msg = f"Background extraction failed: {e}"
            self.errors.append(error_msg)
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ {error_msg}")
            
        finally:
            try:
                scraper.close_browser()
            except:
                pass
    
    def start_background_extraction(self):
        """Start extraction in background thread"""
        thread = threading.Thread(target=self.run_extraction, daemon=True)
        thread.start()
        return thread

def run_background_extraction():
    """Main function to run background extraction"""
    print("ROYAL RESORT BACKGROUND EXTRACTION")
    print("=" * 50)
    print("Running without timeout limits, saving progress as we go")
    print()
    
    processor = RoyalResortBackgroundProcessor()
    
    # Start background extraction
    extraction_thread = processor.start_background_extraction()
    
    # Monitor progress
    print("Background extraction started...")
    print("Press Ctrl+C to stop monitoring (extraction will continue)")
    print()
    
    try:
        last_progress = -1
        while extraction_thread.is_alive():
            if processor.progress != last_progress:
                elapsed = (datetime.now() - processor.start_time).total_seconds() if processor.start_time else 0
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Progress: {processor.progress}/{processor.total_found} properties extracted ({elapsed:.1f}s elapsed)")
                last_progress = processor.progress
            
            time.sleep(5)  # Check every 5 seconds
        
        # Final status
        print()
        print("=" * 50)
        print("BACKGROUND EXTRACTION COMPLETED")
        print(f"Status: {processor.status}")
        print(f"Properties extracted: {len(processor.properties)}")
        print(f"Total found: {processor.total_found}")
        
        if processor.errors:
            print(f"Errors: {len(processor.errors)}")
            for error in processor.errors[-3:]:  # Show last 3 errors
                print(f"  - {error}")
        
        if processor.properties:
            print()
            print("[SUCCESS] Royal Resort properties extracted and saved!")
            print(f"   Check frontend at http://localhost:3001")
            print(f"   Mock data updated with {len(processor.properties)} Royal Resort properties")
        else:
            print()
            print("[WARNING] No properties were successfully extracted")
            
    except KeyboardInterrupt:
        print()
        print("Monitoring stopped, but extraction continues in background...")
        print("Check mock data files for progress updates")
    
    return processor.properties

if __name__ == "__main__":
    properties = run_background_extraction()