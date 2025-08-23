#!/usr/bin/env python3
"""
Simple startup script for the InMailer Flask API server
"""

import os
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from app import app
    
    if __name__ == '__main__':
        print("🚀 Starting InMailer API Server...")
        print("📍 Server will run on: http://localhost:5000")
        print("🔗 API endpoints available at: http://localhost:5000/api/")
        print("📧 Make sure to set EMAIL_USER and EMAIL_PASSWORD environment variables for email functionality")
        print("\n" + "="*50)
        
        app.run(debug=True, host='0.0.0.0', port=5000)
        
except ImportError as e:
    print(f"❌ Error importing Flask app: {e}")
    print("💡 Make sure you have installed the requirements:")
    print("   pip install -r requirements.txt")
    sys.exit(1)
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    sys.exit(1)
