#!/usr/bin/env python3
"""
Debug version to analyze page structure
"""
import sys
import os
import re

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from scrapers.mitsui_scraper import MitsuiNoMoriScraper

def debug_page_structure():
    """Debug the actual page structure"""
    print("Debugging Page Structure")
    print("=" * 40)
    
    scraper = MitsuiNoMoriScraper()
    
    # Get the main page
    url = "https://www.mitsuinomori.co.jp/karuizawa/"
    soup = scraper.get_soup(url)
    
    if not soup:
        print("Could not load page")
        return
        
    print(f"Successfully loaded: {url}")
    print(f"Page length: {len(str(soup))} characters")
    
    # Look for text containing common real estate terms
    page_text = soup.get_text()
    
    # Check for Japanese real estate terms
    real_estate_terms = [
        '万円', '円', '価格', '土地', '建物', '一戸建て', '物件',
        'yen', 'price', 'property', 'house', 'land'
    ]
    
    print(f"\nReal estate terms found:")
    for term in real_estate_terms:
        count = page_text.lower().count(term.lower())
        if count > 0:
            print(f"  '{term}': {count} times")
            
    # Look for price patterns in text
    price_patterns = [
        r'[\d,]+\s*万円',
        r'¥[\d,]+',
        r'[\d,]+\s*円'
    ]
    
    print(f"\nPrice patterns found:")
    for pattern in price_patterns:
        matches = re.findall(pattern, page_text)
        if matches:
            print(f"  Pattern '{pattern}': {matches[:5]}")  # Show first 5
            
    # Analyze HTML structure
    print(f"\nHTML Structure Analysis:")
    
    # Common container types
    containers = {
        'div': soup.find_all('div'),
        'section': soup.find_all('section'),
        'article': soup.find_all('article'),
        'ul': soup.find_all('ul'),
        'li': soup.find_all('li')
    }
    
    for tag_name, elements in containers.items():
        print(f"  {tag_name}: {len(elements)} elements")
        
    # Look for class names that might contain properties
    all_elements = soup.find_all(True)  # Find all elements
    class_names = set()
    
    for element in all_elements:
        classes = element.get('class', [])
        for cls in classes:
            if any(keyword in cls.lower() for keyword in ['property', 'item', 'card', 'list', 'bukken']):
                class_names.add(cls)
                
    print(f"\nPotential property-related classes:")
    for cls in sorted(class_names):
        print(f"  .{cls}")
        
    # Look for specific content sections
    print(f"\nContent sections found:")
    
    # Find elements containing property-like content
    elements_with_prices = soup.find_all(text=re.compile(r'[\d,]+[万円]+'))
    print(f"  Elements with prices: {len(elements_with_prices)}")
    
    if elements_with_prices:
        print("  Sample price elements:")
        for i, elem in enumerate(elements_with_prices[:3]):
            parent = elem.parent if elem.parent else None
            parent_tag = parent.name if parent else "None"
            parent_class = parent.get('class', []) if parent else []
            print(f"    {i+1}. '{elem.strip()}' in <{parent_tag} class='{' '.join(parent_class)}'>")

def debug_individual_property_page():
    """Debug an individual property page"""
    print("\nDebugging Individual Property Page")
    print("=" * 40)
    
    scraper = MitsuiNoMoriScraper()
    
    # Try one of the property detail URLs we found
    property_url = "https://www.mitsuinomori.co.jp/karuizawa/realestate/nk0405h/"
    soup = scraper.get_soup(property_url)
    
    if not soup:
        print("Could not load property page")
        return
        
    print(f"Successfully loaded: {property_url}")
    
    # Extract key information
    page_text = soup.get_text()
    
    # Look for price information
    price_matches = re.findall(r'[\d,]+[万円円]+', page_text)
    print(f"Prices found: {price_matches[:5]}")
    
    # Look for size information
    size_matches = re.findall(r'[\d,]+\.?\d*\s*[㎡坪平米]+', page_text)
    print(f"Sizes found: {size_matches[:5]}")
    
    # Look for headings
    headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5'])
    print(f"Headings found: {len(headings)}")
    
    if headings:
        print("Sample headings:")
        for i, heading in enumerate(headings[:3]):
            try:
                text = heading.get_text(strip=True)
                # Safe print for ASCII
                safe_text = text.encode('ascii', 'ignore').decode('ascii')
                print(f"  {i+1}. {safe_text[:50]}...")
            except:
                print(f"  {i+1}. [Could not display heading]")
                
    # Look for tables (often contain property details)
    tables = soup.find_all('table')
    print(f"Tables found: {len(tables)}")
    
    # Look for lists
    lists = soup.find_all(['ul', 'ol'])
    print(f"Lists found: {len(lists)}")

def analyze_selectors():
    """Analyze what selectors might work"""
    print("\nAnalyzing Potential Selectors")
    print("=" * 40)
    
    scraper = MitsuiNoMoriScraper()
    
    # Test different pages
    urls_to_test = [
        "https://www.mitsuinomori.co.jp/karuizawa/",
        "https://www.mitsuinomori.co.jp/karuizawa/realestate_all/",
        "https://www.mitsuinomori.co.jp/karuizawa/realestate/nk0405h/"
    ]
    
    for url in urls_to_test:
        print(f"\nTesting: {url}")
        soup = scraper.get_soup(url)
        
        if not soup:
            print("  Could not load")
            continue
            
        # Test various selectors
        selectors_to_test = [
            ('div', 'All divs'),
            ('[class*="property"]', 'Property classes'),
            ('[class*="item"]', 'Item classes'),
            ('[class*="card"]', 'Card classes'),
            ('table', 'Tables'),
            ('ul li', 'List items'),
            ('.content', 'Content class'),
            ('.main', 'Main class'),
            ('#content', 'Content ID'),
            ('#main', 'Main ID')
        ]
        
        for selector, description in selectors_to_test:
            try:
                elements = soup.select(selector)
                if elements:
                    print(f"  {description}: {len(elements)} found")
                    
                    # Check if any contain price-like text
                    price_count = 0
                    for elem in elements:
                        if re.search(r'[\d,]+[万円]+', elem.get_text()):
                            price_count += 1
                            
                    if price_count > 0:
                        print(f"    --> {price_count} contain prices!")
                        
            except Exception as e:
                print(f"  {description}: Error - {e}")

if __name__ == "__main__":
    debug_page_structure()
    debug_individual_property_page()
    analyze_selectors()