#!/usr/bin/env python3
"""
Test OAuth redirect URLs and environment variables
"""

import os
from dotenv import load_dotenv

def test_oauth_configuration():
    """Test OAuth configuration and redirect URLs"""
    print("🔍 OAuth Configuration Test")
    print("=" * 50)
    
    # Load .env file
    print("🔍 Loading .env file...")
    load_dotenv()
    
    # Check OAuth-related environment variables
    oauth_vars = {
        'GOOGLE_CLIENT_ID': os.getenv('GOOGLE_CLIENT_ID'),
        'GOOGLE_CLIENT_SECRET': os.getenv('GOOGLE_CLIENT_SECRET'),
        'GOOGLE_REDIRECT_URI': os.getenv('GOOGLE_REDIRECT_URI'),
        'FRONTEND_URL': os.getenv('FRONTEND_URL')
    }
    
    print("🔍 OAuth Environment Variables:")
    for key, value in oauth_vars.items():
        if value:
            if 'SECRET' in key:
                masked_value = value[:8] + '...' if len(value) > 8 else '***'
                print(f"🔍   {key}: {masked_value}")
            else:
                print(f"🔍   {key}: {value}")
        else:
            print(f"🔍   {key}: NOT SET")
    
    # Check what the code would use as defaults
    print("\n🔍 Default Values (if env vars not set):")
    
    # Simulate the code logic
    google_redirect_uri = os.getenv('GOOGLE_REDIRECT_URI', 'https://inmailer.onrender.com/auth/google/callback')
    frontend_url = os.getenv('FRONTEND_URL', 'https://inmailer.vercel.app')
    
    print(f"🔍   GOOGLE_REDIRECT_URI (default): {google_redirect_uri}")
    print(f"🔍   FRONTEND_URL (default): {frontend_url}")
    
    # Check if URLs are production URLs
    print("\n🔍 URL Analysis:")
    
    if 'localhost' in google_redirect_uri or '127.0.0.1' in google_redirect_uri:
        print(f"❌ GOOGLE_REDIRECT_URI contains localhost: {google_redirect_uri}")
    else:
        print(f"✅ GOOGLE_REDIRECT_URI is production: {google_redirect_uri}")
    
    if 'localhost' in frontend_url or '127.0.0.1' in frontend_url:
        print(f"❌ FRONTEND_URL contains localhost: {frontend_url}")
    else:
        print(f"✅ FRONTEND_URL is production: {frontend_url}")
    
    # Check OAuth flow URLs
    print("\n🔍 OAuth Flow URLs:")
    
    # Google OAuth initiation
    oauth_init_url = f"https://inmailer.onrender.com/auth/google"
    print(f"🔍   OAuth Initiation: {oauth_init_url}")
    
    # OAuth callback
    oauth_callback_url = google_redirect_uri
    print(f"🔍   OAuth Callback: {oauth_callback_url}")
    
    # Final redirect after OAuth
    final_redirect_url = f"{frontend_url}/auth/success"
    print(f"🔍   Final Redirect: {final_redirect_url}")
    
    # Check for potential issues
    print("\n🔍 Potential Issues:")
    
    issues_found = []
    
    if not oauth_vars['GOOGLE_CLIENT_ID']:
        issues_found.append("GOOGLE_CLIENT_ID not set")
    
    if not oauth_vars['GOOGLE_CLIENT_SECRET']:
        issues_found.append("GOOGLE_CLIENT_SECRET not set")
    
    if not oauth_vars['GOOGLE_REDIRECT_URI']:
        issues_found.append("GOOGLE_REDIRECT_URI not set (will use default)")
    
    if not oauth_vars['FRONTEND_URL']:
        issues_found.append("FRONTEND_URL not set (will use default)")
    
    if 'localhost' in google_redirect_uri or '127.0.0.1' in google_redirect_uri:
        issues_found.append("GOOGLE_REDIRECT_URI contains localhost")
    
    if 'localhost' in frontend_url or '127.0.0.1' in frontend_url:
        issues_found.append("FRONTEND_URL contains localhost")
    
    if issues_found:
        print("❌ Issues found:")
        for issue in issues_found:
            print(f"❌   - {issue}")
    else:
        print("✅ No issues found - OAuth configuration looks good!")
    
    # Recommendations
    print("\n🔍 Recommendations:")
    
    if not oauth_vars['GOOGLE_REDIRECT_URI']:
        print("🔍   - Set GOOGLE_REDIRECT_URI=https://inmailer.onrender.com/auth/google/callback")
    
    if not oauth_vars['FRONTEND_URL']:
        print("🔍   - Set FRONTEND_URL=https://inmailer.vercel.app")
    
    if 'localhost' in google_redirect_uri or '127.0.0.1' in google_redirect_uri:
        print("🔍   - Update GOOGLE_REDIRECT_URI to use production URL")
    
    if 'localhost' in frontend_url or '127.0.0.1' in frontend_url:
        print("🔍   - Update FRONTEND_URL to use production URL")

if __name__ == "__main__":
    test_oauth_configuration()
    print("\n" + "=" * 50)
    print("✅ OAuth configuration test completed!")

