#!/usr/bin/env python3
"""
Verify production environment setup for OAuth and routing
"""

import os
from dotenv import load_dotenv

def verify_production_setup():
    """Verify all production environment variables are set correctly"""
    print("🔍 Production Environment Verification")
    print("=" * 50)
    
    # Load .env file
    print("🔍 Loading .env file...")
    load_dotenv()
    
    # Critical environment variables for production
    critical_vars = {
        'GOOGLE_CLIENT_ID': os.getenv('GOOGLE_CLIENT_ID'),
        'GOOGLE_CLIENT_SECRET': os.getenv('GOOGLE_CLIENT_SECRET'),
        'GOOGLE_REDIRECT_URI': os.getenv('GOOGLE_REDIRECT_URI'),
        'FRONTEND_URL': os.getenv('FRONTEND_URL'),
        'DATABASE_URL': os.getenv('DATABASE_URL'),
        'FLASK_ENV': os.getenv('FLASK_ENV'),
        'SECRET_KEY': os.getenv('SECRET_KEY')
    }
    
    print("🔍 Critical Environment Variables:")
    issues_found = []
    
    for key, value in critical_vars.items():
        if value:
            if 'SECRET' in key or 'PASSWORD' in key:
                masked_value = value[:8] + '...' if len(value) > 8 else '***'
                print(f"✅ {key}: {masked_value}")
            else:
                print(f"✅ {key}: {value}")
                
                # Check for localhost in production URLs
                if key in ['GOOGLE_REDIRECT_URI', 'FRONTEND_URL'] and value:
                    if 'localhost' in value or '127.0.0.1' in value:
                        issues_found.append(f"{key} contains localhost: {value}")
                        print(f"   ⚠️  WARNING: Contains localhost!")
        else:
            print(f"❌ {key}: NOT SET")
            issues_found.append(f"{key} not set")
    
    # Check default values that would be used
    print("\n🔍 Default Values (if env vars not set):")
    
    google_redirect_uri = os.getenv('GOOGLE_REDIRECT_URI', 'https://inmailer.onrender.com/auth/google/callback')
    frontend_url = os.getenv('FRONTEND_URL', 'https://inmailer.vercel.app')
    
    print(f"🔍 GOOGLE_REDIRECT_URI (default): {google_redirect_uri}")
    print(f"🔍 FRONTEND_URL (default): {frontend_url}")
    
    # Verify OAuth flow URLs
    print("\n🔍 OAuth Flow Analysis:")
    print(f"🔍 Backend OAuth endpoint: {google_redirect_uri}")
    print(f"🔍 Frontend success redirect: {frontend_url}/auth/success")
    print(f"🔍 Final dashboard URL: {frontend_url}/dashboard")
    
    # Check for potential issues
    print("\n🔍 Issue Analysis:")
    if not issues_found:
        print("✅ No critical issues found!")
    else:
        print("❌ Issues found:")
        for issue in issues_found:
            print(f"   - {issue}")
    
    # Recommendations
    print("\n🔧 Production Setup Recommendations:")
    print("1. Ensure FLASK_ENV=production in your Render environment")
    print("2. Set FRONTEND_URL=https://inmailer.vercel.app")
    print("3. Set GOOGLE_REDIRECT_URI=https://inmailer.onrender.com/auth/google/callback")
    print("4. Update Google OAuth console with production redirect URI")
    print("5. Ensure DATABASE_URL is set by Render automatically")
    
    return len(issues_found) == 0

if __name__ == "__main__":
    success = verify_production_setup()
    exit(0 if success else 1)
