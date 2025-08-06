#!/usr/bin/env python3
"""
Simple Besso Navi test without Unicode issues
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def simple_villa_test():
    """Simple villa search test"""
    print("=== SIMPLE VILLA TEST ===")
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'ja,en;q=0.5',
        'Connection': 'keep-alive'
    })
    
    try:
        # Get search page first
        search_url = "https://www.besso-navi.com/b-search"
        print("1. Getting search page...")
        
        response = session.get(search_url, timeout=30)
        print(f"   Status: {response.status_code}")
        
        if response.status_code != 200:
            return 0
        
        # Submit search - try villa search
        search_data = {
            'FromPage': 'b_search',
            'areaid[]': ['2', '3', '4'],  # Karuizawa areas
            'kind_check': '1',  # Villa type
            'price_start': '',
            'price_end': '',
            'tochi_start': '',
            'tochi_end': ''
        }
        
        result_url = "https://www.besso-navi.com/b-search/result"
        print("2. Submitting villa search...")
        
        headers = session.headers.copy()
        headers['Referer'] = search_url
        
        response = session.post(result_url, data=search_data, headers=headers, timeout=30)
        print(f"   Response status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"   Failed with status: {response.status_code}")
            return 0
        
        # Parse results
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Look for property links
        property_count = 0
        
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            if 'b_id=' in href:
                property_count += 1
                print(f"   Found property: {href}")
        
        # Also check for any result indicators
        text = soup.get_text()
        if '件' in text:
            print("   Page contains result count text")
        
        return property_count
        
    except Exception as e:
        print(f"Error: {e}")
        return 0

if __name__ == "__main__":
    count = simple_villa_test()
    print(f"\\nProperties found: {count}")
    
    if count >= 4:
        print("SUCCESS: Found expected villa count!")
    elif count > 0:
        print("PARTIAL: Found some properties")
    else:
        print("FAILED: No properties found")