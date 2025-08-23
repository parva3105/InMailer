#!/usr/bin/env python3
"""
Database initialization script for InMailer
This script will create the database tables and migrate existing data if needed.
"""

import os
import sys
import json
from pathlib import Path

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.config import init_db, get_db_session
from db.models import User, Template, EmailLog
from db.services import UserService, TemplateService

def migrate_existing_templates():
    """Migrate existing templates from JSON file to database"""
    templates_dir = Path("Templates")
    templates_file = templates_dir / "templates.json"
    
    if not templates_file.exists():
        print("📝 No existing templates file found, skipping migration")
        return
    
    try:
        # Load existing templates
        with open(templates_file, 'r', encoding='utf-8') as f:
            existing_templates = json.load(f)
        
        if not existing_templates:
            print("📝 No templates found in existing file")
            return
        
        print(f"🔄 Found {len(existing_templates)} existing templates to migrate")
        
        # Create a default user for existing templates
        default_user = UserService.create_user(
            email="default@inmailer.local",
            name="Default User",
            is_google_user=False
        )
        
        print(f"✅ Created default user: {default_user.email}")
        
        # Migrate each template
        migrated_count = 0
        for template_data in existing_templates:
            try:
                # Create template in database
                template = TemplateService.create_template(
                    user_id=default_user.id,
                    name=template_data.get('name', 'Unnamed Template'),
                    subject=template_data.get('subject', 'No Subject'),
                    content=template_data.get('content', ''),
                    variables=template_data.get('variables', []),
                    attachment_path=template_data.get('attachment_path'),
                    attachment_name=template_data.get('attachment_name')
                )
                
                print(f"✅ Migrated template: {template.name}")
                migrated_count += 1
                
            except Exception as e:
                print(f"❌ Failed to migrate template {template_data.get('name', 'Unknown')}: {e}")
        
        print(f"✅ Migration complete: {migrated_count}/{len(existing_templates)} templates migrated")
        
        # Create backup of original file
        backup_file = templates_dir / "templates_migrated_backup.json"
        import shutil
        shutil.copy2(templates_file, backup_file)
        print(f"💾 Created backup: {backup_file}")
        
    except Exception as e:
        print(f"❌ Error during template migration: {e}")
        import traceback
        traceback.print_exc()

def create_sample_data():
    """Create sample data for testing"""
    try:
        # Create a sample user
        sample_user = UserService.create_user(
            email="sample@inmailer.local",
            name="Sample User",
            is_google_user=False
        )
        
        print(f"✅ Created sample user: {sample_user.email}")
        
        # Create sample templates
        sample_templates = [
            {
                'name': 'Welcome Email',
                'subject': 'Welcome to ${Company}, ${First_Name}!',
                'content': 'Dear ${First_Name},\n\nWelcome to ${Company}! We are excited to have you on board.\n\nBest regards,\nThe Team',
                'variables': ['First_Name', 'Company']
            },
            {
                'name': 'Follow-up Email',
                'subject': 'Following up on our conversation',
                'content': 'Hi ${First_Name},\n\nI wanted to follow up on our recent conversation about ${Topic}.\n\nLooking forward to hearing from you.\n\nBest regards,\n${Your_Name}',
                'variables': ['First_Name', 'Topic', 'Your_Name']
            }
        ]
        
        for template_data in sample_templates:
            template = TemplateService.create_template(
                user_id=sample_user.id,
                name=template_data['name'],
                subject=template_data['subject'],
                content=template_data['content'],
                variables=template_data['variables']
            )
            print(f"✅ Created sample template: {template.name}")
        
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")

def main():
    """Main initialization function"""
    print("🚀 Initializing InMailer Database...")
    
    try:
        # Initialize database tables
        print("📊 Creating database tables...")
        init_db()
        print("✅ Database tables created successfully")
        
        # Check if we should create sample data
        create_samples = input("Create sample data for testing? (y/n): ").lower().strip() == 'y'
        
        if create_samples:
            print("📝 Creating sample data...")
            create_sample_data()
        
        # Check if we should migrate existing templates
        migrate_templates = input("Migrate existing templates from JSON file? (y/n): ").lower().strip() == 'y'
        
        if migrate_templates:
            print("🔄 Migrating existing templates...")
            migrate_existing_templates()
        
        print("✅ Database initialization complete!")
        print("\n📋 Next steps:")
        print("1. Update your .env file with DATABASE_URL if using PostgreSQL")
        print("2. Restart your Flask application")
        print("3. Templates will now be user-specific and stored in the database")
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
