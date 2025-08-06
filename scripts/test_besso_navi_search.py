#!/usr/bin/env python3
"""
Test script to verify Besso Navi search functionality and understand form structure
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json

def test_search_page():
    """Test the search page structure"""
    print("=== TESTING BESSO NAVI SEARCH PAGE ===")
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'ja,en-US;q=0.7,en;q=0.3',
    })
    
    try:
        # Test the main search page
        url = "https://www.besso-navi.com/b-search"
        print(f"Fetching: {url}")
        
        response = session.get(url, timeout=30)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for forms
            forms = soup.find_all('form')
            print(f"Found {len(forms)} forms")
            
            for i, form in enumerate(forms):
                print(f"\n--- FORM {i+1} ---")
                print(f"Action: {form.get('action', 'No action')}")
                print(f"Method: {form.get('method', 'GET')}")
                
                # Look for relevant input fields
                inputs = form.find_all(['input', 'select', 'textarea'])
                print(f"Input fields: {len(inputs)}")
                
                for inp in inputs:
                    inp_type = inp.get('type', inp.name)
                    inp_name = inp.get('name', 'no-name')
                    inp_value = inp.get('value', '')
                    
                    # Focus on relevant fields
                    if any(keyword in inp_name.lower() for keyword in ['area', 'type', 'category', 'villa', 'land', 'price']):
                        print(f"  {inp_type}: {inp_name} = '{inp_value}'")
                        
                        # If it's a select, show options
                        if inp.name == 'select':
                            options = inp.find_all('option')
                            for opt in options:
                                print(f"    Option: {opt.get('value', '')} = '{opt.get_text(strip=True)}'")
            
            # Look for any links that might lead to results
            links = soup.find_all('a', href=True)
            result_links = []
            for link in links:
                href = link.get('href', '')
                text = link.get_text(strip=True)
                if any(keyword in href.lower() for keyword in ['search', 'result', 'villa', 'land', 'property']) or \
                   any(keyword in text.lower() for keyword in ['villa', 'ヴィラ', '別荘', '土地', '検索']):
                    result_links.append((href, text))
            
            print(f"\nRelevant links found: {len(result_links)}")
            for href, text in result_links[:10]:  # Show first 10
                print(f"  {href} -> '{text}'")
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_villa_search():
    """Test specific villa search"""
    print("\n=== TESTING VILLA SEARCH ===")
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'ja,en-US;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Referer': 'https://www.besso-navi.com/b-search'
    })
    
    try:
        # Try to submit a search for villas
        search_data = {
            'FromPage': 'b_search',
            'areaid[]': '軽井沢',
            'villa_area_text': '軽井沢',
            'category': 'villa',  # Try villa category
            'price_start': '',
            'price_end': '',
            'tochi_start': '',
            'tochi_end': ''
        }
        
        result_url = "https://www.besso-navi.com/b-search/result"
        print(f"Submitting search to: {result_url}")
        print(f"Search data: {search_data}")
        
        response = session.post(result_url, data=search_data, timeout=30)
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for property listings
            property_elements = soup.find_all(['div', 'li', 'article'], class_=lambda x: x and any(
                keyword in x.lower() for keyword in ['property', 'item', 'listing', 'bukken', 'villa', 'result']
            ))
            
            print(f"Found {len(property_elements)} potential property elements")
            
            # Look for links to individual properties
            property_links = []
            for link in soup.find_all('a', href=True):
                href = link.get('href', '')
                if 'view' in href and 'b_id=' in href:
                    property_links.append(href)
            
            print(f"Found {len(property_links)} property detail links")
            for i, link in enumerate(property_links[:5]):  # Show first 5
                full_url = urljoin("https://www.besso-navi.com", link)
                print(f"  {i+1}. {full_url}")
            
            return len(property_links)
        
    except Exception as e:
        print(f"Villa search error: {e}")
        return 0

if __name__ == "__main__":
    print("Testing Besso Navi search functionality...")
    
    # Test search page structure
    test_search_page()
    
    # Test villa search
    villa_count = test_villa_search()
    
    print(f"\n=== SUMMARY ===")
    print(f"Villa properties found: {villa_count}")
    
    if villa_count > 0:
        print("✓ Villa search is working!")
    else:
        print("✗ Villa search needs investigation")