#!/usr/bin/env python3
"""
Startup script for InMailer Backend with Database
This script initializes the database and starts the Flask server.
"""

import os
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """Main startup function"""
    print("🚀 Starting InMailer Backend with Database...")
    
    try:
        # Check if database file exists, if not, run initialization
        db_file = Path("inmailer.db")
        if not db_file.exists():
            print("📊 Database file not found. Running initialization...")
            
            # Import and run database initialization
            from db.init_db import main as init_db_main
            init_db_main()
        
        # Import and start the Flask app
        from app_db import app
        
        print("✅ Database backend ready!")
        print("🌐 Starting Flask server...")
        
        # Start the Flask app
        app.run(
            debug=True,
            host='0.0.0.0',
            port=5000,
            use_reloader=False  # Disable reloader to avoid duplicate database connections
        )
        
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
