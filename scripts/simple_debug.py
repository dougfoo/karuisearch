#!/usr/bin/env python3
"""
Simple debug - check what's on the page
"""
import sys
import os
import re

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from scrapers.mitsui_scraper import MitsuiNoMoriScraper

def simple_debug():
    """Simple page analysis"""
    print("Simple Debug Analysis")
    print("=" * 30)
    
    scraper = MitsuiNoMoriScraper()
    
    # Get main page
    soup = scraper.get_soup("https://www.mitsuinomori.co.jp/karuizawa/")
    
    if not soup:
        print("Failed to load page")
        return
        
    print("Page loaded successfully")
    
    # Basic structure
    divs = soup.find_all('div')
    tables = soup.find_all('table')
    links = soup.find_all('a', href=True)
    
    print(f"Divs: {len(divs)}")
    print(f"Tables: {len(tables)}")
    print(f"Links: {len(links)}")
    
    # Look for price patterns
    page_text = soup.get_text()
    yen_count = page_text.count('yen')
    price_count = page_text.count('price')
    
    print(f"'yen' mentions: {yen_count}")
    print(f"'price' mentions: {price_count}")
    
    # Find elements with numbers that might be prices
    price_elements = soup.find_all(text=re.compile(r'\d{1,3}(,\d{3})*'))
    print(f"Elements with numbers: {len(price_elements)}")
    
    # Look at table content (often where property data is)
    if tables:
        print(f"\nTable analysis:")
        for i, table in enumerate(tables[:3]):
            rows = table.find_all('tr')
            print(f"  Table {i+1}: {len(rows)} rows")
            
            # Check if table contains property-like data
            table_text = table.get_text().lower()
            has_price = 'price' in table_text or 'yen' in table_text
            has_size = 'size' in table_text or 'area' in table_text
            print(f"    Has price info: {has_price}")
            print(f"    Has size info: {has_size}")
            
    # Look for specific property detail page
    print(f"\nTesting property detail page...")
    detail_soup = scraper.get_soup("https://www.mitsuinomori.co.jp/karuizawa/realestate/nk0405h/")
    
    if detail_soup:
        print("Property page loaded")
        
        # Look for tables on property page
        detail_tables = detail_soup.find_all('table')
        print(f"Property page tables: {len(detail_tables)}")
        
        if detail_tables:
            # Often property details are in tables
            for i, table in enumerate(detail_tables[:2]):
                print(f"  Property table {i+1}:")
                rows = table.find_all('tr')
                print(f"    Rows: {len(rows)}")
                
                # Extract text from first few rows
                for j, row in enumerate(rows[:3]):
                    cells = row.find_all(['td', 'th'])
                    if cells:
                        row_text = ' | '.join([cell.get_text(strip=True) for cell in cells])
                        # Safe ASCII print
                        safe_text = row_text.encode('ascii', 'ignore').decode('ascii')
                        print(f"      Row {j+1}: {safe_text[:80]}...")
    else:
        print("Could not load property page")

if __name__ == "__main__":
    simple_debug()