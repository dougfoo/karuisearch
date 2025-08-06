#!/usr/bin/env python3
"""
Test just villa search with debugging output
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def test_villa_search_detailed():
    """Test villa search with detailed debugging"""
    print("=== TESTING VILLA SEARCH (DETAILED) ===")
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'ja,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive'
    })
    
    try:
        # Step 1: Get search page
        search_url = "https://www.besso-navi.com/b-search"
        print(f"1. Getting search page: {search_url}")
        
        response = session.get(search_url, timeout=30)
        if response.status_code != 200:
            print(f"Failed to get search page: {response.status_code}")
            return
        
        # Step 2: Submit search for villas specifically
        search_data = {
            'FromPage': 'b_search',
            'areaid[]': ['2', '3', '4'],  # Karuizawa areas
            'villa_area_text': '軽井沢',
            'kind_check': '1',  # Villa type
            'price_start': '',
            'price_end': '',
            'tochi_start': '',
            'tochi_end': ''
        }
        
        result_url = "https://www.besso-navi.com/b-search/result"
        print(f"2. Submitting search to: {result_url}")
        print(f"   Data: {search_data}")
        
        headers = session.headers.copy()
        headers['Referer'] = search_url
        
        response = session.post(result_url, data=search_data, headers=headers, timeout=30)
        print(f"3. Response status: {response.status_code}")
        
        if response.status_code == 200:
            # Save response for analysis
            with open('besso_response.html', 'w', encoding='utf-8') as f:
                f.write(response.text)
            print("   Response saved to besso_response.html")
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for property links
            property_links = []
            
            print("4. Looking for property links...")
            
            # All links with b_id
            for link in soup.find_all('a', href=True):
                href = link.get('href', '')
                if 'b_id=' in href:
                    full_url = urljoin(result_url, href)
                    property_links.append(full_url)
                    text = link.get_text(strip=True)
                    print(f"   Found: {full_url} -> '{text[:50]}'")
            
            print(f"5. Total property links found: {len(property_links)}")
            
            # If no property links, show some page content for debugging
            if not property_links:
                print("6. No property links found. Page analysis:")
                
                # Check for error messages or empty results
                text_content = soup.get_text()
                
                if 'エラー' in text_content or 'error' in text_content.lower():
                    print("   Page contains error message")
                elif '0件' in text_content or '該当なし' in text_content:
                    print("   Page indicates no results found")
                elif '件' in text_content:
                    print("   Page contains result count information")
                
                # Show first 500 characters of page content
                print("   First 500 chars of page:")
                print(f"   {text_content[:500]}")
                
                # Show all links for debugging
                all_links = soup.find_all('a', href=True)
                print(f"   All links on page ({len(all_links)}):")
                for i, link in enumerate(all_links[:10]):
                    href = link.get('href', '')
                    text = link.get_text(strip=True)
                    print(f"     {i+1}. {href} -> '{text[:30]}'")
            
            return property_links
        else:
            print(f"Failed to get results: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return []

if __name__ == "__main__":
    links = test_villa_search_detailed()
    
    print(f"\\n=== SUMMARY ===")
    print(f"Villa properties found: {len(links)}")
    
    if len(links) >= 4:
        print("SUCCESS: Found expected ~4 villa results!")
    elif len(links) > 0:
        print(f"PARTIAL: Found {len(links)} villas")
    else:
        print("FAILED: No villas found - check besso_response.html for details")