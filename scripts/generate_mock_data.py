#!/usr/bin/env python3
"""
Generate Mock Data Script for Karui-Search

This script scrapes up to 10 listings from each of the 3 sites and generates
mock data files in the correct format for the frontend.

Usage:
    python scripts/generate_mock_data.py

Output:
    - src/frontend/src/data/mockProperties.json
    - src/frontend/src/data/mockWeeklyData.json
"""

import json
import os
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Any
import logging

# Add the src directory to Python path so we can import scrapers
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from scrapers.scraper_factory import ScraperFactory

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('scraping.log')
    ]
)
logger = logging.getLogger(__name__)

def generate_property_id(source_url: str) -> str:
    """Generate a consistent property ID from source URL"""
    return f"prop_{hash(source_url) % 100000000:08x}"

def convert_property_to_dict(prop, site_key: str, index: int) -> Dict[str, Any]:
    """Convert PropertyData object to dictionary format"""
    return {
        "id": generate_property_id(prop.source_url),
        "title": prop.title or f"{site_key.title()} Property {index + 1}",
        "price": prop.price or "価格応談",
        "location": prop.location or "軽井沢",
        "property_type": prop.property_type or "一戸建て",
        "size_info": prop.size_info or "",
        "building_age": prop.building_age or "",
        "description": prop.description or f"{prop.title or 'Property'} - {prop.location or 'Karuizawa'}",
        "image_urls": prop.image_urls[:5],  # Limit to 5 images
        "rooms": prop.rooms or "",
        "source_url": prop.source_url,
        "scraped_date": datetime.now().strftime('%Y-%m-%d'),
        "date_first_seen": datetime.now().isoformat(),
        "is_new": True,
        "is_featured": index < 2  # Mark first 2 from each site as featured
    }

def add_fallback_properties(site_key: str, existing_count: int, target_count: int = 10) -> List[Dict[str, Any]]:
    """Generate fallback properties if scraping didn't get enough results"""
    fallback_properties = []
    
    site_configs = {
        'mitsui': {
            'base_url': 'https://www.mitsuinomori.co.jp',
            'name': '三井の森',
            'type': '一戸建て',
            'location_prefix': '軽井沢町'
        },
        'royal_resort': {
            'base_url': 'https://www.royal-resort.co.jp',
            'name': 'ロイヤルリゾート',
            'type': '別荘',
            'location_prefix': '軽井沢町'
        },
        'besso_navi': {
            'base_url': 'https://www.besso-navi.com',
            'name': '別荘ナビ',
            'type': '別荘',
            'location_prefix': '軽井沢町'
        }
    }
    
    if site_key not in site_configs:
        return fallback_properties
        
    config = site_configs[site_key]
    needed_count = max(0, target_count - existing_count)
    
    locations = ['中軽井沢', '南軽井沢', '旧軽井沢', '軽井沢', '北軽井沢']
    base_prices = [3500, 4800, 6200, 7500, 8900, 12000, 15000, 18500, 22000, 28000]
    
    for i in range(needed_count):
        location = locations[i % len(locations)]
        base_price = base_prices[i % len(base_prices)]
        
        fallback_prop = {
            "id": f"prop_{site_key}_{existing_count + i + 1:03d}",
            "title": f"{config['name']} {location}物件",
            "price": f"¥{base_price:,}万円",
            "location": f"長野県北佐久郡{config['location_prefix']}{location}",
            "property_type": config['type'],
            "size_info": f"{180 + i * 20}㎡ (building) / {400 + i * 50}㎡ (land)",
            "building_age": "築8年" if i % 3 == 0 else "新築",
            "description": f"{location}の{config['type']}。{config['name']}厳選の優良物件。軽井沢の豊かな自然に包まれたリゾートライフをお楽しみください。",
            "image_urls": [
                f"https://via.placeholder.com/400x300/4CAF50/ffffff?text={site_key.title()}+Property+{i+1}",
                f"https://via.placeholder.com/400x300/66BB6A/ffffff?text=Interior+View",
                f"https://via.placeholder.com/400x300/8BC34A/ffffff?text=Exterior+View"
            ],
            "rooms": f"{2 + i % 3}LDK" if config['type'] != '土地' else "",
            "source_url": f"{config['base_url']}/property/{site_key}_{existing_count + i + 1:03d}",
            "scraped_date": datetime.now().strftime('%Y-%m-%d'),
            "date_first_seen": datetime.now().isoformat(),
            "is_new": True,
            "is_featured": i < 2
        }
        
        fallback_properties.append(fallback_prop)
    
    return fallback_properties

def scrape_all_sites() -> List[Dict[str, Any]]:
    """Scrape properties from all sites"""
    logger.info("Starting comprehensive scraping of all sites")
    
    factory = ScraperFactory()
    all_properties = []
    
    sites = ['mitsui', 'royal_resort', 'besso_navi']
    target_per_site = 10
    
    for site_key in sites:
        logger.info(f"\n{'='*50}")
        logger.info(f"Scraping {site_key.upper()}")
        logger.info(f"{'='*50}")
        
        try:
            # Attempt to scrape real data
            site_results = factory.scrape_single_site(site_key)
            
            if site_results:
                # Limit to target count and convert to dict format
                limited_results = site_results[:target_per_site]
                logger.info(f"Successfully scraped {len(limited_results)} properties from {site_key}")
                
                for i, prop in enumerate(limited_results):
                    prop_dict = convert_property_to_dict(prop, site_key, i)
                    all_properties.append(prop_dict)
                
                # Add fallback properties if we didn't get enough
                if len(limited_results) < target_per_site:
                    fallback_count = target_per_site - len(limited_results)
                    logger.info(f"Adding {fallback_count} fallback properties for {site_key}")
                    fallback_props = add_fallback_properties(site_key, len(limited_results), target_per_site)
                    all_properties.extend(fallback_props)
            else:
                # No real data - use all fallback properties
                logger.warning(f"No properties scraped from {site_key}, using fallback data")
                fallback_props = add_fallback_properties(site_key, 0, target_per_site)
                all_properties.extend(fallback_props)
                
        except Exception as e:
            logger.error(f"Error scraping {site_key}: {e}")
            # Use fallback properties on error
            logger.info(f"Using fallback data for {site_key} due to error")
            fallback_props = add_fallback_properties(site_key, 0, target_per_site)
            all_properties.extend(fallback_props)
    
    logger.info(f"\nTotal properties collected: {len(all_properties)}")
    return all_properties

def generate_weekly_data(properties: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate weekly report data from properties"""
    today = datetime.now()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    
    # Select featured properties for the weekly report
    featured_properties = [prop for prop in properties if prop.get('is_featured', False)]
    
    # If not enough featured, add some regular properties
    if len(featured_properties) < 6:
        regular_properties = [prop for prop in properties if not prop.get('is_featured', False)]
        needed = 6 - len(featured_properties)
        featured_properties.extend(regular_properties[:needed])
    
    # Count property types
    property_types = {}
    for prop in properties:
        prop_type = prop.get('property_type', '一戸建て')
        property_types[prop_type] = property_types.get(prop_type, 0) + 1
    
    # Analyze price ranges (extract numeric values from price strings)
    price_ranges = {
        "under_20M": 0,
        "20M_to_50M": 0,
        "50M_to_100M": 0,
        "over_100M": 0
    }
    
    for prop in properties:
        price_str = prop.get('price', '')
        try:
            # Extract numbers from price string
            import re
            numbers = re.findall(r'[\d,]+', price_str.replace(',', ''))
            if numbers and '万円' in price_str:
                price_man = float(numbers[0])  # Price in 万円
                if price_man < 2000:
                    price_ranges["under_20M"] += 1
                elif price_man < 5000:
                    price_ranges["20M_to_50M"] += 1
                elif price_man < 10000:
                    price_ranges["50M_to_100M"] += 1
                else:
                    price_ranges["over_100M"] += 1
        except:
            # Default to middle range if can't parse
            price_ranges["20M_to_50M"] += 1
    
    # Count areas
    areas = {}
    for prop in properties:
        location = prop.get('location', '')
        if '中軽井沢' in location:
            areas['中軽井沢'] = areas.get('中軽井沢', 0) + 1
        elif '南軽井沢' in location:
            areas['南軽井沢'] = areas.get('南軽井沢', 0) + 1
        elif '旧軽井沢' in location:
            areas['旧軽井沢'] = areas.get('旧軽井沢', 0) + 1
        elif '北軽井沢' in location:
            areas['北軽井沢'] = areas.get('北軽井沢', 0) + 1
        else:
            areas['軽井沢'] = areas.get('軽井沢', 0) + 1
    
    weekly_data = {
        "week_start": week_start.strftime('%Y-%m-%d'),
        "week_end": week_end.strftime('%Y-%m-%d'),
        "total_new": len([p for p in properties if p.get('is_new', False)]),
        "price_changes": {
            "increases": 1,  # Simulated data
            "decreases": 0
        },
        "properties": featured_properties[:6],  # Limit to 6 for weekly report
        "generated_at": datetime.now().isoformat(),
        "summary": {
            "property_types": property_types,
            "price_ranges": price_ranges,
            "areas": areas
        }
    }
    
    return weekly_data

def save_json_file(data: Any, filepath: str, description: str):
    """Save data to JSON file with proper formatting"""
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ Saved {description} to {filepath}")
        
        # Log file size
        file_size = os.path.getsize(filepath)
        logger.info(f"   File size: {file_size:,} bytes")
        
    except Exception as e:
        logger.error(f"❌ Failed to save {description} to {filepath}: {e}")
        raise

def main():
    """Main execution function"""
    logger.info("🚀 Starting Karui-Search Mock Data Generation")
    logger.info(f"Timestamp: {datetime.now().isoformat()}")
    
    try:
        # Step 1: Scrape properties from all sites
        logger.info("\n📊 STEP 1: Scraping Properties")
        all_properties = scrape_all_sites()
        
        if not all_properties:
            logger.error("❌ No properties were collected!")
            return 1
        
        # Step 2: Generate weekly data
        logger.info("\n📅 STEP 2: Generating Weekly Data")
        weekly_data = generate_weekly_data(all_properties)
        
        # Step 3: Save files
        logger.info("\n💾 STEP 3: Saving Files")
        
        # Get the project root directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)
        
        properties_file = os.path.join(project_root, 'src', 'frontend', 'src', 'data', 'mockProperties.json')
        weekly_file = os.path.join(project_root, 'src', 'frontend', 'src', 'data', 'mockWeeklyData.json')
        
        save_json_file(all_properties, properties_file, "Mock Properties Data")
        save_json_file(weekly_data, weekly_file, "Mock Weekly Data")
        
        # Step 4: Summary
        logger.info("\n🎉 GENERATION COMPLETE!")
        logger.info("="*60)
        
        site_counts = {}
        for prop in all_properties:
            source_url = prop.get('source_url', '')
            if 'mitsuinomori' in source_url:
                site_counts['mitsui'] = site_counts.get('mitsui', 0) + 1
            elif 'royal-resort' in source_url:
                site_counts['royal_resort'] = site_counts.get('royal_resort', 0) + 1
            elif 'besso-navi' in source_url:
                site_counts['besso_navi'] = site_counts.get('besso_navi', 0) + 1
            else:
                site_counts['fallback'] = site_counts.get('fallback', 0) + 1
        
        logger.info(f"📈 Total Properties: {len(all_properties)}")
        for site, count in site_counts.items():
            logger.info(f"   {site}: {count} properties")
        
        logger.info(f"📊 Weekly Report Properties: {len(weekly_data['properties'])}")
        logger.info(f"🗂️  Property Types: {len(weekly_data['summary']['property_types'])}")
        logger.info(f"📍 Areas Covered: {len(weekly_data['summary']['areas'])}")
        
        # Show sample of improvements (first property)
        sample_prop = all_properties[0]
        logger.info(f"\n📸 Sample Property Images: {len(sample_prop['image_urls'])}")
        if sample_prop['image_urls']:
            first_img = sample_prop['image_urls'][0]
            if 'uploads/' in first_img:
                logger.info("   ✅ Real property photos detected")
            elif 'placeholder' in first_img:
                logger.info("   ℹ️  Placeholder images used")
            else:
                logger.info("   ⚠️  Image source unknown")
        
        logger.info(f"🔗 Sample Source URL: {sample_prop['source_url']}")
        
        logger.info("\n🎯 Files generated successfully!")
        logger.info(f"   • {properties_file}")
        logger.info(f"   • {weekly_file}")
        
        return 0
        
    except Exception as e:
        logger.error(f"❌ Fatal error during generation: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return 1

if __name__ == '__main__':
    sys.exit(main())