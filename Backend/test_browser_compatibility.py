#!/usr/bin/env python3
"""
Browser Compatibility Test Script
This script helps debug authentication issues with Mozilla Firefox and Safari browsers.
"""

import requests
import json
import time

# Configuration
BASE_URL = "https://inmailer.onrender.com"
TEST_ENDPOINTS = [
    "/auth/session-status",
    "/auth/debug-browser",
    "/auth/user"
]

def test_endpoint(endpoint, description=""):
    """Test a specific endpoint and return results"""
    print(f"\n🔍 Testing {endpoint} {description}")
    print("=" * 50)
    
    try:
        # Test with different headers to simulate different browsers
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
            'Accept': 'application/json,text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Origin': 'https://inmailer.vercel.app',
            'Referer': 'https://inmailer.vercel.app/',
        }
        
        response = requests.get(
            f"{BASE_URL}{endpoint}",
            headers=headers,
            timeout=10
        )
        
        print(f"✅ Status Code: {response.status_code}")
        print(f"📋 Response Headers:")
        for key, value in response.headers.items():
            if key.lower().startswith(('access-control', 'set-cookie', 'content-type')):
                print(f"   {key}: {value}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"📊 Response Data:")
                print(json.dumps(data, indent=2))
            except json.JSONDecodeError:
                print(f"📄 Response Text: {response.text[:200]}...")
        else:
            print(f"❌ Error Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
    
    print("-" * 50)

def test_cors_preflight():
    """Test CORS preflight request"""
    print(f"\n🔍 Testing CORS Preflight")
    print("=" * 50)
    
    try:
        headers = {
            'Origin': 'https://inmailer.vercel.app',
            'Access-Control-Request-Method': 'GET',
            'Access-Control-Request-Headers': 'Content-Type, Authorization',
        }
        
        response = requests.options(
            f"{BASE_URL}/auth/user",
            headers=headers,
            timeout=10
        )
        
        print(f"✅ Status Code: {response.status_code}")
        print(f"📋 CORS Headers:")
        for key, value in response.headers.items():
            if key.lower().startswith('access-control'):
                print(f"   {key}: {value}")
                
    except requests.exceptions.RequestException as e:
        print(f"❌ CORS preflight failed: {e}")
    
    print("-" * 50)

def test_session_cookies():
    """Test session cookie handling"""
    print(f"\n🔍 Testing Session Cookie Handling")
    print("=" * 50)
    
    try:
        # Create a session to test cookie handling
        session = requests.Session()
        
        # Set some test cookies
        session.cookies.set('test_cookie', 'test_value', domain='.onrender.com')
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
            'Origin': 'https://inmailer.vercel.app',
        }
        
        response = session.get(
            f"{BASE_URL}/auth/session-status",
            headers=headers,
            timeout=10
        )
        
        print(f"✅ Status Code: {response.status_code}")
        print(f"🍪 Cookies sent: {dict(session.cookies)}")
        print(f"🍪 Cookies received: {dict(response.cookies)}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"📊 Session Status: {data.get('cookies', {})}")
            except json.JSONDecodeError:
                print(f"📄 Response Text: {response.text[:200]}...")
                
    except requests.exceptions.RequestException as e:
        print(f"❌ Session cookie test failed: {e}")
    
    print("-" * 50)

def main():
    """Main test function"""
    print("🚀 Browser Compatibility Test Suite")
    print("=" * 60)
    print(f"🎯 Testing backend: {BASE_URL}")
    print(f"🕐 Test started at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test basic endpoints
    for endpoint in TEST_ENDPOINTS:
        test_endpoint(endpoint)
    
    # Test CORS preflight
    test_cors_preflight()
    
    # Test session cookies
    test_session_cookies()
    
    print(f"\n✅ Test suite completed at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n📋 Summary of potential issues:")
    print("1. Check if CORS headers are properly set")
    print("2. Verify session cookies are being sent/received")
    print("3. Ensure SameSite cookie policy is compatible")
    print("4. Check if browser-specific headers are handled")

if __name__ == "__main__":
    main()
