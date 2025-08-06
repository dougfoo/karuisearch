#!/usr/bin/env python3
"""
Debug Besso Navi form submission to understand the correct parameters
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json

def debug_form_submission():
    """Debug the actual form submission process"""
    print("=== DEBUGGING BESSO NAVI FORM SUBMISSION ===")
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'ja,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive'
    })
    
    try:
        # Step 1: Get the search form
        search_url = "https://www.besso-navi.com/b-search"
        print(f"1. Getting search form from: {search_url}")
        
        response = session.get(search_url, timeout=30)
        print(f"   Status: {response.status_code}")
        
        if response.status_code != 200:
            print("Failed to get search form")
            return
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Step 2: Analyze the form in detail
        form = soup.find('form')
        if not form:
            print("No form found!")
            return
        
        print(f"2. Form found - Action: {form.get('action')}, Method: {form.get('method')}")
        
        # Get all form fields with their current values
        form_data = {}
        inputs = form.find_all(['input', 'select', 'textarea'])
        
        print("3. Form fields analysis:")
        for inp in inputs:
            name = inp.get('name')
            if not name:
                continue
                
            input_type = inp.get('type', inp.name)
            value = inp.get('value', '')
            
            print(f"   {input_type:<10} {name:<20} = '{value}'")
            
            # Collect all form data as it appears
            if input_type == 'checkbox' and not inp.get('checked'):
                continue  # Skip unchecked checkboxes
                
            if name in form_data:
                # Handle multiple values (like areaid[])
                if not isinstance(form_data[name], list):
                    form_data[name] = [form_data[name]]
                form_data[name].append(value)
            else:
                form_data[name] = value
        
        # Step 3: Try different search approaches
        result_url = urljoin(search_url, form.get('action', 'result'))
        print(f"4. Submitting to: {result_url}")
        
        # Test 1: Submit with minimal data (just area)
        test_data_1 = {
            'FromPage': 'b_search',
            'areaid[]': ['2', '3', '4'],  # Try multiple Karuizawa area IDs
            'villa_area_text': '軽井沢',
        }
        
        print("\\n=== TEST 1: Minimal search ===")
        print(f"Data: {test_data_1}")
        
        headers = session.headers.copy()
        headers['Referer'] = search_url
        
        response = session.post(result_url, data=test_data_1, headers=headers, timeout=30)
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for results
            # Try different selectors for property listings
            selectors_to_try = [
                'a[href*="view"][href*="b_id"]',  # Direct property view links
                '.property-item a',
                '.result-item a', 
                '.listing a',
                'a[href*="b_id"]'
            ]
            
            found_links = []
            for selector in selectors_to_try:
                links = soup.select(selector)
                if links:
                    print(f"   Found {len(links)} links with selector: {selector}")
                    for link in links[:3]:  # Show first 3
                        href = link.get('href', '')
                        text = link.get_text(strip=True)[:50]
                        full_url = urljoin(result_url, href)
                        found_links.append(full_url)
                        print(f"     {full_url} -> '{text}'")
                    break
            
            if not found_links:
                # Look for any meaningful content in the response
                text_content = soup.get_text()
                if '件数' in text_content or '物件' in text_content:
                    print("   Response contains property-related text")
                    
                    # Look for any links at all
                    all_links = soup.find_all('a', href=True)
                    print(f"   Total links found: {len(all_links)}")
                    
                    for link in all_links[:10]:
                        href = link.get('href', '')
                        text = link.get_text(strip=True)
                        if href and ('view' in href or 'detail' in href or 'property' in href):
                            print(f"     Potential: {href} -> '{text[:30]}'")
                else:
                    print("   No property-related content found")
                    print("   First 200 chars of response:")
                    print(f"   {text_content[:200]}")
        
        return found_links
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return []

if __name__ == "__main__":
    links = debug_form_submission()
    
    print(f"\\n=== SUMMARY ===")
    print(f"Property links found: {len(links)}")
    
    if links:
        print("SUCCESS: Found property links!")
        for i, link in enumerate(links, 1):
            print(f"  {i}. {link}")
    else:
        print("INVESTIGATION NEEDED: No property links found")