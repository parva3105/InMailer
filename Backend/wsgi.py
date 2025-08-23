#!/usr/bin/env python3
"""
WSGI entry point for production deployment
This ensures the correct app_db.py file is used
"""

from app_db import app

if __name__ == "__main__":
    app.run()
