#!/usr/bin/env python3
"""
Test script to debug backend connection and endpoints
"""

import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Backend URL
BACKEND_URL = "https://inmailer.onrender.com"

def test_health_endpoint():
    """Test the health check endpoint"""
    print("🔍 Testing health endpoint...")
    try:
        response = requests.get(f"{BACKEND_URL}/api/health", timeout=10)
        print(f"✅ Health endpoint status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend status: {data.get('status')}")
            print(f"✅ Database status: {data.get('database')}")
            if data.get('database') == 'error':
                print(f"❌ Database error: {data.get('database_error')}")
        else:
            print(f"❌ Health endpoint failed: {response.text}")
    except Exception as e:
        print(f"❌ Health endpoint error: {e}")

def test_dashboard_endpoint():
    """Test the dashboard stats endpoint (will fail without auth)"""
    print("\n🔍 Testing dashboard endpoint (expecting 401)...")
    try:
        response = requests.get(f"{BACKEND_URL}/api/dashboard/stats", timeout=10)
        print(f"✅ Dashboard endpoint status: {response.status_code}")
        if response.status_code == 401:
            print("✅ Correctly returned 401 (not authenticated)")
        else:
            print(f"❌ Unexpected status: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Dashboard endpoint error: {e}")

def test_templates_endpoint():
    """Test the templates endpoint (will fail without auth)"""
    print("\n🔍 Testing templates endpoint (expecting 401)...")
    try:
        response = requests.get(f"{BACKEND_URL}/api/templates", timeout=10)
        print(f"✅ Templates endpoint status: {response.status_code}")
        if response.status_code == 401:
            print("✅ Correctly returned 401 (not authenticated)")
        else:
            print(f"❌ Unexpected status: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Templates endpoint error: {e}")

def test_cors():
    """Test CORS headers"""
    print("\n🔍 Testing CORS headers...")
    try:
        response = requests.options(f"{BACKEND_URL}/api/health", timeout=10)
        print(f"✅ OPTIONS request status: {response.status_code}")
        cors_headers = {
            'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
            'Access-Control-Allow-Credentials': response.headers.get('Access-Control-Allow-Credentials'),
            'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods')
        }
        print(f"✅ CORS headers: {cors_headers}")
    except Exception as e:
        print(f"❌ CORS test error: {e}")

if __name__ == "__main__":
    print("🚀 Backend Connection Test")
    print("=" * 50)
    print(f"🔍 Backend URL: {BACKEND_URL}")
    print(f"🔍 Environment: {os.getenv('FLASK_ENV', 'not_set')}")
    
    test_health_endpoint()
    test_dashboard_endpoint()
    test_templates_endpoint()
    test_cors()
    
    print("\n" + "=" * 50)
    print("✅ Test completed!")
