#!/usr/bin/env python3
"""
Test script to verify local development setup
"""

import os
import sys
import requests
import time
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test if all required modules can be imported"""
    print("🧪 Testing imports...")
    
    try:
        from app_db import app
        print("✅ app_db imported successfully")
        
        from db.config import init_db
        print("✅ Database config imported successfully")
        
        from db.models import User, Template, EmailLog
        print("✅ Database models imported successfully")
        
        from mail_merge import parse_template, render_templates
        print("✅ Mail merge functions imported successfully")
        
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_database():
    """Test database initialization"""
    print("\n📊 Testing database...")
    
    try:
        from db.init_db import main as init_database
        init_database()
        print("✅ Database initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False

def test_server_start():
    """Test if server can start"""
    print("\n🌐 Testing server startup...")
    
    try:
        from app_db import app
        
        # Start server in a separate thread for testing
        import threading
        import time
        
        def run_server():
            app.run(host='127.0.0.1', port=5001, debug=False, use_reloader=False)
        
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        
        # Wait for server to start
        time.sleep(3)
        
        # Test health endpoint
        try:
            response = requests.get('http://127.0.0.1:5001/api/health', timeout=5)
            if response.status_code == 200:
                print("✅ Server started and health check passed")
                return True
            else:
                print(f"❌ Health check failed: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Server health check failed: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Server startup failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 InMailer Local Development Test Suite")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_imports),
        ("Database Test", test_database),
        ("Server Test", test_server_start)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name}...")
        result = test_func()
        results.append((test_name, result))
    
    print("\n" + "=" * 50)
    print("📋 Test Results:")
    
    all_passed = True
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name}: {status}")
        if not result:
            all_passed = False
    
    if all_passed:
        print("\n🎉 All tests passed! Your local setup is ready.")
        print("\n📝 Next steps:")
        print("  1. Run: python start_server_db.py")
        print("  2. In another terminal, start the frontend")
        print("  3. Open http://localhost:3000 in your browser")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
        print("\n🔧 Troubleshooting:")
        print("  1. Make sure all dependencies are installed: pip install -r requirements.txt")
        print("  2. Check if you have a .env file with proper configuration")
        print("  3. Ensure no other process is using port 5000")

if __name__ == "__main__":
    main()
