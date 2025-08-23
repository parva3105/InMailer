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

# Load environment variables from .env file
def load_env():
    """Load environment variables from .env file"""
    env_file = Path('.env')
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                if '=' in line and not line.strip().startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value

def main():
    """Main startup function"""
    print("🚀 Starting InMailer Backend with Database...")
    
    try:
        # Load environment variables
        load_env()
        
        # Check if using PostgreSQL (Neon) or SQLite
        database_url = os.getenv('DATABASE_URL', '')
        
        if database_url.startswith('postgresql://'):
            print("🌐 Using PostgreSQL database (Neon)")
            # For PostgreSQL, we don't need to check for local files
            # The database tables should already exist
        else:
            # Check if SQLite database file exists, if not, run initialization
            db_file = Path("inmailer.db")
            if not db_file.exists():
                print("📊 SQLite database file not found. Running initialization...")
                
                # Import and run database initialization with no prompts
                from db.init_db import init_db
                init_db()
                print("✅ Database initialized without prompts")
        
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
