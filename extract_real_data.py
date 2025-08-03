#!/usr/bin/env python3
"""
Extract real property data from all 3 sites and format for frontend consumption
"""
import sys
import os
import json
import time
from datetime import datetime, timezone
from typing import List, Dict, Any
import hashlib

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from scrapers.scraper_factory import ScraperFactory

def safe_print(text):
    """Print text safely, converting Unicode to ASCII if needed"""
    if isinstance(text, str):
        return text.encode('ascii', 'ignore').decode('ascii')
    return str(text)

def generate_property_id(title: str, source_url: str) -> str:
    """Generate unique property ID from title and URL"""
    # Create hash from title and URL for consistent IDs
    content = f"{title}_{source_url}".encode('utf-8')
    hash_obj = hashlib.md5(content)
    return f"prop_{hash_obj.hexdigest()[:8]}"

def format_price_yen(price_str: str) -> str:
    """Format price string to yen format"""
    if not price_str:
        return "価格応談"
        
    # Handle Japanese 万円 format
    if '万円' in price_str:
        try:
            # Extract number and convert
            import re
            numbers = re.findall(r'[\d,]+', price_str.replace(',', ''))
            if numbers:
                price_value = int(numbers[0]) * 10000
                return f"¥{price_value:,}"
        except:
            pass
    
    # Handle other formats
    if '円' in price_str:
        return f"¥{price_str.replace('円', '')}"
    elif price_str.isdigit():
        return f"¥{int(price_str):,}"
    
    return price_str

def map_property_type(prop_type: str) -> str:
    """Map property type to standard format"""
    type_mapping = {
        '一戸建て': '一戸建て',
        '土地': '土地', 
        'マンション': 'マンション',
        'ヴィラ': '別荘',
        'villa': '別荘',
        'house': '一戸建て',
        'land': '土地',
        'apartment': 'マンション'
    }
    
    if not prop_type:
        return '一戸建て'  # Default
        
    prop_type_lower = prop_type.lower()
    for key, value in type_mapping.items():
        if key.lower() in prop_type_lower:
            return value
            
    return prop_type  # Return as-is if no mapping found

def extract_location_area(location: str) -> str:
    """Extract area name from location string"""
    if not location:
        return '軽井沢'
        
    # Common Karuizawa area mappings
    if '中軽井沢' in location or 'naka-karuizawa' in location.lower():
        return '中軽井沢'
    elif '南軽井沢' in location or 'minami-karuizawa' in location.lower():
        return '南軽井沢'
    elif '旧軽井沢' in location or 'kyu-karuizawa' in location.lower():
        return '旧軽井沢'
    elif '新軽井沢' in location:
        return '新軽井沢'
    elif '追分' in location:
        return '追分'
    elif '発地' in location:
        return '発地'
    elif '長倉' in location:
        return '長倉'
    else:
        return '軽井沢'

def determine_building_age(building_age: str, scraped_date: str) -> str:
    """Determine building age or default"""
    if not building_age:
        return '築年不詳'
        
    if '新築' in building_age or 'new' in building_age.lower():
        return '新築'
    elif '築' in building_age:
        return building_age
    else:
        return f"築{building_age}年" if building_age.isdigit() else building_age

def convert_property_to_frontend_format(prop_data, site_name: str, scraped_date: str) -> Dict[str, Any]:
    """Convert PropertyData to frontend JSON format"""
    
    # Generate unique ID
    prop_id = generate_property_id(prop_data.title or "Property", prop_data.source_url or "")
    
    # Format price
    formatted_price = format_price_yen(prop_data.price or "")
    
    # Map property type
    property_type = map_property_type(prop_data.property_type or "")
    
    # Extract area
    area = extract_location_area(prop_data.location or "")
    location = f"長野県北佐久郡軽井沢町{area}" if area else "長野県北佐久郡軽井沢町"
    
    # Building age
    building_age = determine_building_age(prop_data.building_age or "", scraped_date)
    
    # Create description
    description_parts = []
    if area != '軽井沢':
        description_parts.append(f"{area}の")
    
    if property_type == '別荘':
        description_parts.append("リゾート別荘")
    elif property_type == '一戸建て':
        description_parts.append("住宅")
    elif property_type == '土地':
        description_parts.append("建築用地")
    elif property_type == 'マンション':
        description_parts.append("リゾートマンション")
        
    if prop_data.size_info:
        description_parts.append(f"。{prop_data.size_info}")
        
    if building_age and building_age != '築年不詳':
        description_parts.append(f"。{building_age}")
        
    description_parts.append("。軽井沢の自然豊かな環境でリゾートライフをお楽しみいただけます。")
    
    description = "".join(description_parts)
    
    # Handle images - use placeholders if no real images
    image_urls = prop_data.image_urls[:5] if prop_data.image_urls else []
    if not image_urls:
        # Generate placeholder images based on property type
        if property_type == '別荘':
            image_urls = ["https://via.placeholder.com/400x300/2E7D32/ffffff?text=Villa+Exterior"]
        elif property_type == '一戸建て':
            image_urls = ["https://via.placeholder.com/400x300/1976D2/ffffff?text=House+Exterior"]
        elif property_type == '土地':
            image_urls = ["https://via.placeholder.com/400x300/4CAF50/ffffff?text=Land+Plot"]
        else:
            image_urls = ["https://via.placeholder.com/400x300/FF9800/ffffff?text=Property"]
    
    # Parse scraped timestamp
    try:
        if prop_data.scraped_at:
            scraped_dt = datetime.fromtimestamp(prop_data.scraped_at, tz=timezone.utc)
            date_first_seen = scraped_dt.isoformat()
            scraped_date_str = scraped_dt.strftime("%Y-%m-%d")
        else:
            now = datetime.now(timezone.utc)
            date_first_seen = now.isoformat()
            scraped_date_str = now.strftime("%Y-%m-%d")
    except:
        now = datetime.now(timezone.utc)
        date_first_seen = now.isoformat()
        scraped_date_str = now.strftime("%Y-%m-%d")
    
    # Determine if property is new (scraped today)
    is_new = scraped_date_str == datetime.now().strftime("%Y-%m-%d")
    
    # Determine featured status (luxury properties over 50M yen)
    is_featured = False
    try:
        if formatted_price and '¥' in formatted_price:
            price_num = int(formatted_price.replace('¥', '').replace(',', ''))
            is_featured = price_num >= 50000000  # 50M yen or more
    except:
        pass
    
    return {
        "id": prop_id,
        "title": prop_data.title or f"{area}{property_type}",
        "price": formatted_price,
        "location": location,
        "property_type": property_type,
        "size_info": prop_data.size_info or "",
        "building_age": building_age,
        "description": description,
        "image_urls": image_urls,
        "rooms": prop_data.rooms or "",
        "source_url": prop_data.source_url or "",
        "scraped_date": scraped_date_str,
        "date_first_seen": date_first_seen,
        "is_new": is_new,
        "is_featured": is_featured
    }

def generate_weekly_data(properties: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate weekly summary data from properties"""
    now = datetime.now()
    week_start = now.strftime("%Y-%m-%d")
    
    # Calculate one week later
    import datetime as dt
    week_start_dt = dt.datetime.strptime(week_start, "%Y-%m-%d")
    week_end_dt = week_start_dt + dt.timedelta(days=7)
    week_end = week_end_dt.strftime("%Y-%m-%d")
    
    # Count new properties
    new_properties = [p for p in properties if p.get('is_new', False)]
    total_new = len(new_properties)
    
    # Count property types
    property_types = {}
    for prop in new_properties:
        prop_type = prop.get('property_type', '一戸建て')
        property_types[prop_type] = property_types.get(prop_type, 0) + 1
    
    # Count price ranges (for new properties)
    price_ranges = {
        "under_20M": 0,
        "20M_to_50M": 0, 
        "50M_to_100M": 0,
        "over_100M": 0
    }
    
    for prop in new_properties:
        try:
            price_str = prop.get('price', '')
            if '¥' in price_str:
                price_num = int(price_str.replace('¥', '').replace(',', ''))
                if price_num < 20000000:
                    price_ranges["under_20M"] += 1
                elif price_num < 50000000:
                    price_ranges["20M_to_50M"] += 1
                elif price_num < 100000000:
                    price_ranges["50M_to_100M"] += 1
                else:
                    price_ranges["over_100M"] += 1
        except:
            price_ranges["under_20M"] += 1  # Default to lowest range
    
    # Count areas
    areas = {}
    for prop in new_properties:
        location = prop.get('location', '')
        if '中軽井沢' in location:
            area = '中軽井沢'
        elif '南軽井沢' in location:
            area = '南軽井沢'
        elif '旧軽井沢' in location:
            area = '旧軽井沢'
        elif '新軽井沢' in location:
            area = '新軽井沢'
        else:
            area = '軽井沢'
        areas[area] = areas.get(area, 0) + 1
    
    return {
        "week_start": week_start,
        "week_end": week_end,
        "total_new": total_new,
        "price_changes": {
            "increases": 0,  # Would need historical data
            "decreases": 0   # Would need historical data
        },
        "properties": new_properties[:10],  # Limit to 10 for weekly report
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "property_types": property_types,
            "price_ranges": price_ranges,
            "areas": areas
        }
    }

def main():
    """Main extraction function"""
    print("KARUI-SEARCH REAL DATA EXTRACTION")
    print("=" * 60)
    print()
    
    # Create factory with optimized config for data extraction
    config = {
        'browser_config': {
            'headless': True,
            'wait_timeout': 15,
            'page_load_timeout': 25
        },
        'rate_limit': {
            'requests_per_second': 0.5  # Slightly faster for data collection
        }
    }
    
    factory = ScraperFactory(config)
    scraped_date = datetime.now().strftime("%Y-%m-%d")
    
    print(f"Extraction date: {scraped_date}")
    print("Target: Up to 10 properties per site")
    print()
    
    all_properties = []
    site_results = {}
    
    # Define sites to scrape (in priority order)
    sites_to_scrape = [
        ('mitsui', 'Mitsui no Mori'),
        ('royal_resort', 'Royal Resort Karuizawa'), 
        ('besso_navi', 'Besso Navi')
    ]
    
    for site_key, site_name in sites_to_scrape:
        print(f"🏠 EXTRACTING FROM {site_name.upper()}")
        print("-" * 50)
        
        try:
            # Extract properties from site
            properties = factory.scrape_single_site(site_key)
            
            if properties:
                print(f"✅ Found {len(properties)} properties")
                
                # Limit to 10 properties per site
                limited_properties = properties[:10]
                print(f"📋 Using {len(limited_properties)} properties for frontend")
                
                # Convert to frontend format
                formatted_properties = []
                for i, prop in enumerate(limited_properties, 1):
                    try:
                        formatted_prop = convert_property_to_frontend_format(
                            prop, site_name, scraped_date
                        )
                        formatted_properties.append(formatted_prop)
                        
                        # Show sample
                        title_safe = safe_print(formatted_prop['title'])
                        price_safe = safe_print(formatted_prop['price'])
                        print(f"  {i}. {title_safe[:40]}... - {price_safe}")
                        
                    except Exception as e:
                        print(f"  ❌ Error formatting property {i}: {e}")
                        continue
                
                site_results[site_key] = formatted_properties
                all_properties.extend(formatted_properties)
                print(f"✅ {len(formatted_properties)} properties formatted successfully")
                
            else:
                print(f"⚠️ No properties extracted from {site_name}")
                site_results[site_key] = []
                
        except Exception as e:
            print(f"❌ Error extracting from {site_name}: {e}")
            site_results[site_key] = []
            
        print()
    
    # Generate summary
    total_extracted = len(all_properties)
    print(f"📊 EXTRACTION SUMMARY:")
    print("-" * 30)
    print(f"Total properties extracted: {total_extracted}")
    
    for site_key, site_name in sites_to_scrape:
        count = len(site_results.get(site_key, []))
        print(f"  {site_name}: {count} properties")
    
    if total_extracted > 0:
        print()
        print("💾 SAVING DATA FILES:")
        print("-" * 25)
        
        # Save properties data
        properties_file = "src/frontend/src/data/mockProperties.json"
        with open(properties_file, 'w', encoding='utf-8') as f:
            json.dump(all_properties, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Properties saved: {properties_file}")
        print(f"   {len(all_properties)} properties")
        
        # Generate and save weekly data
        weekly_data = generate_weekly_data(all_properties)
        weekly_file = "src/frontend/src/data/mockWeeklyData.json"
        
        with open(weekly_file, 'w', encoding='utf-8') as f:
            json.dump(weekly_data, f, indent=2, ensure_ascii=False)
            
        print(f"✅ Weekly data saved: {weekly_file}")
        print(f"   {weekly_data['total_new']} new properties")
        
        # Show sample of extracted data
        print()
        print("📋 SAMPLE EXTRACTED PROPERTIES:")
        print("-" * 35)
        
        for i, prop in enumerate(all_properties[:3], 1):
            title_safe = safe_print(prop['title'])
            price_safe = safe_print(prop['price'])
            location_safe = safe_print(prop['location'])
            
            print(f"{i}. {title_safe}")
            print(f"   Price: {price_safe}")
            print(f"   Location: {location_safe}")
            print(f"   Type: {prop['property_type']}")
            print(f"   Images: {len(prop['image_urls'])}")
            print()
        
        print("🎉 SUCCESS: Real data extraction completed!")
        print(f"Frontend data files updated with {total_extracted} live properties!")
        
    else:
        print("❌ No properties extracted - check scraper functionality")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)