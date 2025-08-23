#!/usr/bin/env python3
"""
Test Neon database connection directly with psycopg2
"""

import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_neon_connection():
    """Test direct connection to Neon database"""
    print("🔍 Testing Neon database connection...")
    
    # Get DATABASE_URL from environment
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL not found in environment variables")
        return False
    
    print(f"🔍 Database URL: {database_url[:50]}..." if len(database_url) > 50 else f"🔍 Database URL: {database_url}")
    
    try:
        # Test connection with psycopg2
        print("🔍 Attempting to connect with psycopg2...")
        conn = psycopg2.connect(database_url)
        
        # Test a simple query
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        
        print(f"✅ Successfully connected to Neon database!")
        print(f"✅ PostgreSQL version: {version[0] if version else 'Unknown'}")
        
        # Test if we can create a simple table (this will fail if we don't have permissions, but connection works)
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS connection_test (
                    id SERIAL PRIMARY KEY,
                    test_column VARCHAR(50),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            print("✅ Successfully created test table")
            
            # Insert a test row
            cursor.execute("INSERT INTO connection_test (test_column) VALUES (%s) RETURNING id;", ("connection_test",))
            test_id = cursor.fetchone()[0]
            print(f"✅ Successfully inserted test row with ID: {test_id}")
            
            # Clean up test table
            cursor.execute("DROP TABLE connection_test;")
            print("✅ Successfully cleaned up test table")
            
        except Exception as table_error:
            print(f"⚠️ Table operations failed (this is normal if no write permissions): {table_error}")
        
        # Close connection
        cursor.close()
        conn.close()
        print("✅ Connection closed successfully")
        return True
        
    except psycopg2.OperationalError as e:
        print(f"❌ Connection failed with OperationalError: {e}")
        return False
    except psycopg2.Error as e:
        print(f"❌ Connection failed with psycopg2 error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_ssl_parameters():
    """Test different SSL parameter combinations"""
    print("\n🔍 Testing SSL parameter combinations...")
    
    base_url = os.getenv('DATABASE_URL')
    if not base_url:
        print("❌ DATABASE_URL not found")
        return
    
    # Remove any existing SSL parameters
    if 'sslmode=' in base_url:
        if '?' in base_url and '&' in base_url:
            # URL has both ? and &, need to handle carefully
            parts = base_url.split('?')
            base_part = parts[0]
            params = parts[1].split('&')
            # Remove sslmode parameter
            params = [p for p in params if not p.startswith('sslmode=')]
            if params:
                base_url = f"{base_part}?{'&'.join(params)}"
            else:
                base_url = base_part
        elif '?' in base_url:
            # URL has only ?, remove sslmode
            parts = base_url.split('?')
            base_part = parts[0]
            params = parts[1].split('&')
            params = [p for p in params if not p.startswith('sslmode=')]
            if params:
                base_url = f"{base_part}?{'&'.join(params)}"
            else:
                base_url = base_part
    
    print(f"🔍 Base URL (without SSL): {base_url}")
    
    # Test different SSL modes
    ssl_modes = ['require', 'prefer', 'allow', 'disable']
    
    for ssl_mode in ssl_modes:
        test_url = f"{base_url}?sslmode={ssl_mode}"
        print(f"\n🔍 Testing sslmode={ssl_mode}")
        print(f"🔍 Test URL: {test_url[:80]}...")
        
        try:
            conn = psycopg2.connect(test_url)
            print(f"✅ sslmode={ssl_mode} - Connection successful!")
            conn.close()
        except Exception as e:
            print(f"❌ sslmode={ssl_mode} - Connection failed: {e}")

if __name__ == "__main__":
    print("🚀 Neon Database Connection Test")
    print("=" * 50)
    
    # Test basic connection
    success = test_neon_connection()
    
    if success:
        print("\n✅ Basic connection test passed!")
    else:
        print("\n❌ Basic connection test failed!")
    
    # Test SSL parameters
    test_ssl_parameters()
    
    print("\n" + "=" * 50)
    print("✅ Test completed!")
