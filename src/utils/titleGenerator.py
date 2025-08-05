"""
Title Generation Utility for Property Scrapers
Generates consistent, informative titles in the format:
[Source] [Property Type] [Building Age] [Price] - [Location Shortened]
"""

import re
from typing import Dict, Any, Optional


def get_source_name(source_url: str) -> str:
    """Extract source name from URL"""
    if 'mitsuinomori.co.jp' in source_url:
        return '三井の森'
    elif 'royal-resort.co.jp' in source_url:
        return 'Royal Resort'
    elif 'besso-navi.com' in source_url:
        return 'Besso Navi'
    else:
        return '不明'


def format_price_for_title(price: str) -> str:
    """Format price for title display"""
    if not price:
        return ''
    
    # Remove ¥ symbol and any extra characters
    clean_price = price.replace('¥', '').strip()
    
    # Handle different price formats
    if '億円' in clean_price:
        # Extract number before 億円
        match = re.search(r'([0-9.,]+)億円', clean_price)
        if match:
            return f"{match.group(1)}億円"
    elif '万円' in clean_price:
        # Convert large 万円 amounts to 億円
        match = re.search(r'([0-9.,]+)万円', clean_price)
        if match:
            man_value = float(match.group(1).replace(',', ''))
            if man_value >= 10000:  # 1億円以上
                oku_value = man_value / 10000
                if oku_value == int(oku_value):
                    return f"{int(oku_value)}億円"
                else:
                    return f"{oku_value:.1f}億円"
            else:
                return f"{match.group(1)}万円"
    
    return clean_price


def shorten_location(location: str) -> str:
    """Shorten location string for title"""
    if not location:
        return ''
    
    # Remove common prefixes and suffixes
    location = re.sub(r'長野県北佐久郡軽井沢町', '', location)
    location = re.sub(r'\s*\|\s*三井の森軽井沢販売センター', '', location)
    location = re.sub(r'\s*中古別荘\s*', '', location)
    location = re.sub(r'\s*新築別荘\s*', '', location)
    location = re.sub(r'\s*土地\s*', '', location)
    location = re.sub(r'\s*店舗付住宅\s*', '', location)
    
    # Clean up extra spaces
    location = re.sub(r'\s+', '', location)
    
    # Limit length
    if len(location) > 15:
        location = location[:15]
    
    return location.strip()


def generate_property_title(property_data: Dict[str, Any]) -> str:
    """
    Generate a consistent property title
    Format: [Source] [Property Type] [Building Age] [Price] - [Location Shortened]
    """
    source = get_source_name(property_data.get('source_url', ''))
    property_type = property_data.get('property_type', '')
    building_age = property_data.get('building_age', '')
    price = format_price_for_title(property_data.get('price', ''))
    location = shorten_location(property_data.get('location', ''))
    
    # Build title components
    components = []
    
    if source:
        components.append(source)
    if property_type:
        components.append(property_type)
    if building_age:
        components.append(building_age)
    if price:
        components.append(price)
    
    # Join main components
    main_title = ' '.join(components)
    
    # Add location if available
    if location:
        return f"{main_title} - {location}"
    else:
        return main_title


# Test examples
if __name__ == "__main__":
    # Test with sample data
    test_properties = [
        {
            "id": "prop_030bd9b3",
            "price": "3億5,000万円",
            "location": "中軽井沢 上ノ原 新築別荘 | 三井の森軽井沢販売センター",
            "property_type": "一戸建て",
            "building_age": "新築",
            "source_url": "https://www.mitsuinomori.co.jp/karuizawa/realestate/nk0405h/"
        },
        {
            "id": "prop_royal_resort_006",
            "price": "¥12,000万円",
            "location": "長野県北佐久郡軽井沢町中軽井沢",
            "property_type": "別荘",
            "building_age": "新築",
            "source_url": "https://www.royal-resort.co.jp/property/royal_resort_006"
        },
        {
            "id": "prop_besso_navi_010",
            "price": "¥28,000万円",
            "location": "長野県北佐久郡軽井沢町北軽井沢",
            "property_type": "別荘",
            "building_age": "築8年",
            "source_url": "https://www.besso-navi.com/property/besso_navi_010"
        }
    ]
    
    print("Generated Titles:")
    for prop in test_properties:
        title = generate_property_title(prop)
        print(f"- {title}")