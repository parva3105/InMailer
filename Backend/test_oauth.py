#!/usr/bin/env python3
"""
Test script to diagnose OAuth and session issues
"""

import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_environment():
    """Test if required environment variables are set"""
    print("🔍 === ENVIRONMENT TEST ===")
    
    required_vars = [
        'GOOGLE_CLIENT_ID',
        'GOOGLE_CLIENT_SECRET', 
        'FLASK_SECRET_KEY'
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if not value or value.startswith('your_'):
            print(f"❌ {var}: {'Not set' if not value else 'Using placeholder value'}")
            missing_vars.append(var)
        else:
            print(f"✅ {var}: Set")
    
    if missing_vars:
        print(f"\n⚠️  Missing or invalid environment variables: {missing_vars}")
        print("Please update your .env file with proper values.")
        return False
    
    print("✅ All required environment variables are set!")
    return True

def test_backend_health():
    """Test if backend is running and accessible"""
    print("\n🔍 === BACKEND HEALTH TEST ===")
    
    try:
        response = requests.get('http://localhost:5000/api/health')
        if response.status_code == 200:
            print("✅ Backend is running and accessible")
            data = response.json()
            print(f"📊 Backend status: {data.get('status')}")
            return True
        else:
            print(f"❌ Backend responded with status: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend at http://localhost:5000")
        print("Make sure the backend server is running with: python start_server_db.py")
        return False
    except Exception as e:
        print(f"❌ Error testing backend: {e}")
        return False

def test_oauth_flow():
    """Test OAuth flow initiation"""
    print("\n🔍 === OAUTH FLOW TEST ===")
    
    try:
        response = requests.get('http://localhost:5000/auth/google')
        if response.status_code == 302:  # Redirect expected
            print("✅ OAuth flow initiated successfully")
            print(f"🔗 Redirect URL: {response.headers.get('Location', 'No location header')}")
            return True
        else:
            print(f"❌ OAuth flow failed with status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing OAuth flow: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 InMailer OAuth & Session Diagnostic Tool")
    print("=" * 50)
    
    # Test environment
    env_ok = test_environment()
    
    if not env_ok:
        print("\n❌ Environment setup incomplete. Please fix the issues above first.")
        return
    
    # Test backend health
    backend_ok = test_backend_health()
    
    if not backend_ok:
        print("\n❌ Backend issues detected. Please fix the backend first.")
        return
    
    # Test OAuth flow
    oauth_ok = test_oauth_flow()
    
    print("\n" + "=" * 50)
    if env_ok and backend_ok and oauth_ok:
        print("🎉 All tests passed! Your setup should work correctly.")
        print("\n📋 Next steps:")
        print("1. Go to http://localhost:3001 in your browser")
        print("2. Click 'Sign in with Google'")
        print("3. Complete the OAuth flow")
        print("4. Try sending emails")
    else:
        print("❌ Some tests failed. Please fix the issues above.")
    
    print("\n💡 If you're still having issues:")
    print("- Check the backend console for error messages")
    print("- Ensure your Google OAuth credentials are correct")
    print("- Verify the redirect URI matches exactly: http://localhost:5000/auth/google/callback")

if __name__ == '__main__':
    main()
