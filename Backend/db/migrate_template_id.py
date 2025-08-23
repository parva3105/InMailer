#!/usr/bin/env python3
"""
Migration script to make template_id nullable in email_logs table
This fixes the issue where template deletion fails due to NOT NULL constraint
"""

import os
import sys
from pathlib import Path

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.config import get_db_session, engine
from sqlalchemy import text

def migrate_template_id_nullable():
    """Make template_id column nullable in email_logs table"""
    print("🔄 Starting migration to make template_id nullable...")
    
    db = get_db_session()
    try:
        # Check if we're using SQLite or PostgreSQL
        if 'sqlite' in str(engine.url):
            print("📱 Using SQLite database")
            # SQLite doesn't support ALTER COLUMN easily, so we'll recreate the table
            migrate_sqlite_template_id()
        else:
            print("🐘 Using PostgreSQL database")
            # PostgreSQL supports ALTER COLUMN
            migrate_postgresql_template_id()
            
        print("✅ Migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()

def migrate_postgresql_template_id():
    """Migrate PostgreSQL database to make template_id nullable"""
    db = get_db_session()
    try:
        # Check if template_id is already nullable
        result = db.execute(text("""
            SELECT is_nullable 
            FROM information_schema.columns 
            WHERE table_name = 'email_logs' 
            AND column_name = 'template_id'
        """))
        
        nullable_info = result.fetchone()
        if nullable_info and nullable_info[0] == 'YES':
            print("✅ template_id is already nullable, no migration needed")
            return
        
        print("🔄 Making template_id column nullable...")
        
        # Alter the column to be nullable
        db.execute(text("ALTER TABLE email_logs ALTER COLUMN template_id DROP NOT NULL"))
        db.commit()
        
        print("✅ Successfully made template_id nullable")
        
    except Exception as e:
        db.rollback()
        raise
    finally:
        db.close()

def migrate_sqlite_template_id():
    """Migrate SQLite database to make template_id nullable"""
    db = get_db_session()
    try:
        print("🔄 SQLite migration: Recreating email_logs table with nullable template_id...")
        
        # Get all data from the current email_logs table
        result = db.execute(text("SELECT * FROM email_logs"))
        email_logs_data = result.fetchall()
        
        # Get column names
        columns = [desc[0] for desc in result.description]
        print(f"📊 Found {len(email_logs_data)} email log records to migrate")
        
        # Drop the old table
        db.execute(text("DROP TABLE email_logs"))
        
        # Create the new table with nullable template_id
        db.execute(text("""
            CREATE TABLE email_logs (
                id INTEGER PRIMARY KEY,
                user_id INTEGER NOT NULL,
                template_id INTEGER,
                recipient_email VARCHAR(255) NOT NULL,
                subject TEXT NOT NULL,
                status VARCHAR(50) NOT NULL,
                error_message TEXT,
                gmail_message_id VARCHAR(255),
                sent_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (template_id) REFERENCES templates (id)
            )
        """))
        
        # Re-insert the data
        if email_logs_data:
            placeholders = ', '.join(['?' for _ in columns])
            insert_sql = f"INSERT INTO email_logs ({', '.join(columns)}) VALUES ({placeholders})"
            
            for row in email_logs_data:
                db.execute(text(insert_sql), row)
            
            print(f"✅ Migrated {len(email_logs_data)} email log records")
        
        db.commit()
        print("✅ Successfully recreated email_logs table with nullable template_id")
        
    except Exception as e:
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    migrate_template_id_nullable()
