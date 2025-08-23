#!/usr/bin/env python3
"""
Database migration script to add payment fields to users table
Run this after updating the models.py file
"""

import os
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from db.config import get_db_session, init_db
from db.models import User, Base
from sqlalchemy import text

def migrate_payment_fields():
    """Add payment fields to users table"""
    print("🚀 Starting payment fields migration...")
    
    try:
        # Initialize database
        init_db()
        db = get_db_session()
        
        try:
            # Check if payment fields already exist
            result = db.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'users' 
                AND column_name IN ('has_lifetime_access', 'payment_date', 'stripe_customer_id', 'stripe_payment_intent_id')
            """))
            
            existing_columns = [row[0] for row in result]
            
            if not existing_columns:
                print("📝 Adding payment fields to users table...")
                
                # Add payment fields
                db.execute(text("""
                    ALTER TABLE users 
                    ADD COLUMN has_lifetime_access BOOLEAN DEFAULT FALSE
                """))
                
                db.execute(text("""
                    ALTER TABLE users 
                    ADD COLUMN payment_date TIMESTAMP
                """))
                
                db.execute(text("""
                    ALTER TABLE users 
                    ADD COLUMN stripe_customer_id VARCHAR(255)
                """))
                
                db.execute(text("""
                    ALTER TABLE users 
                    ADD COLUMN stripe_payment_intent_id VARCHAR(255)
                """))
                
                # Commit changes
                db.commit()
                print("✅ Payment fields added successfully!")
                
            else:
                print(f"✅ Payment fields already exist: {existing_columns}")
            
            # Verify the structure
            result = db.execute(text("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = 'users' 
                ORDER BY ordinal_position
            """))
            
            print("\n📊 Current users table structure:")
            for row in result:
                print(f"  {row[0]}: {row[1]} (nullable: {row[2]}, default: {row[3]})")
            
        finally:
            db.close()
            
        print("\n🎉 Migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    migrate_payment_fields()
