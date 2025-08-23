#!/usr/bin/env python3
"""
Check environment variables and DATABASE_URL configuration
"""

import os
from dotenv import load_dotenv

def check_environment():
    """Check environment variables"""
    print("🔍 Environment Variables Check")
    print("=" * 50)
    
    # Load .env file
    print("🔍 Loading .env file...")
    load_dotenv()
    
    # Check DATABASE_URL
    database_url = os.getenv('DATABASE_URL')
    print(f"🔍 DATABASE_URL: {database_url}")
    
    if database_url:
        # Check for SSL parameters
        if 'sslmode=' in database_url:
            print("🔍 SSL mode found in DATABASE_URL")
            # Extract SSL mode
            ssl_part = database_url.split('sslmode=')[1]
            if '&' in ssl_part:
                ssl_mode = ssl_part.split('&')[0]
            else:
                ssl_mode = ssl_part
            print(f"🔍 SSL mode value: {ssl_mode}")
            
            # Check for duplicate SSL parameters
            ssl_count = database_url.count('sslmode=')
            if ssl_count > 1:
                print(f"❌ WARNING: Multiple sslmode parameters found ({ssl_count})")
                # Show all occurrences
                parts = database_url.split('sslmode=')
                for i, part in enumerate(parts[1:], 1):
                    if '&' in part:
                        ssl_value = part.split('&')[0]
                    else:
                        ssl_value = part
                    print(f"🔍   sslmode {i}: {ssl_value}")
        else:
            print("🔍 No SSL mode found in DATABASE_URL")
        
        # Check for other connection parameters
        connection_params = []
        if '?' in database_url:
            params_part = database_url.split('?')[1]
            if '&' in params_part:
                params = params_part.split('&')
            else:
                params = [params_part]
            
            for param in params:
                if '=' in param:
                    key, value = param.split('=', 1)
                    connection_params.append((key, value))
        
        if connection_params:
            print("🔍 Connection parameters:")
            for key, value in connection_params:
                print(f"🔍   {key}: {value}")
    
    # Check other relevant environment variables
    print("\n🔍 Other Environment Variables:")
    relevant_vars = [
        'FLASK_ENV',
        'GOOGLE_CLIENT_ID',
        'GOOGLE_CLIENT_SECRET',
        'FRONTEND_URL',
        'MAX_FREE_USERS',
        'EMAIL_USER',
        'EMAIL_PASSWORD',
        'SECRET_KEY'
    ]
    
    for var in relevant_vars:
        value = os.getenv(var)
        if value:
            # Mask sensitive values
            if 'SECRET' in var or 'PASSWORD' in var or 'KEY' in var:
                masked_value = value[:8] + '...' if len(value) > 8 else '***'
                print(f"🔍   {var}: {masked_value}")
            else:
                print(f"🔍   {var}: {value}")
        else:
            print(f"🔍   {var}: NOT SET")
    
    # Check if we're in Render environment
    print(f"\n🔍 Environment Info:")
    print(f"🔍   Platform: {os.name}")
    print(f"🔍   Python version: {os.sys.version}")
    print(f"🔍   Current working directory: {os.getcwd()}")
    print(f"🔍   Render environment: {'RENDER' in os.environ}")
    
    if 'RENDER' in os.environ:
        print("🔍   Render specific variables:")
        for key, value in os.environ.items():
            if 'RENDER' in key:
                print(f"🔍     {key}: {value}")

if __name__ == "__main__":
    check_environment()
    print("\n" + "=" * 50)
    print("✅ Environment check completed!")
