#!/usr/bin/env python3
"""
Startup script for the InMailer database-enabled backend server
"""

import os
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Set environment variables for local development
os.environ.setdefault('FLASK_ENV', 'development')
os.environ.setdefault('FLASK_DEBUG', '1')

# Import and initialize the database
from db.init_db import main as init_database
from app_db import app

def main():
    """Main startup function"""
    print("🚀 Starting InMailer Backend Server...")
    
    # Initialize database
    print("📊 Initializing database...")
    try:
        init_database()
        print("✅ Database initialized successfully!")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return
    
    # Start the Flask server
    print("🌐 Starting Flask server...")
    print("📍 Backend will be available at: http://localhost:5000")
    print("📍 Frontend should run at: http://localhost:3000")
    print("📍 Health check: http://localhost:5000/api/health")
    print("\n" + "="*50)
    
    try:
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=True,
            threaded=True
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Server failed to start: {e}")

if __name__ == "__main__":
    main()
