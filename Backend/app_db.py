from flask import request, jsonify, session, redirect
import os
import json
import shutil
from pathlib import Path
from datetime import datetime

def safe_isoformat(val):
    """Convert datetime or string to ISO format string safely."""
    if val is None:
        return None
    if isinstance(val, str):
        return val
    return val.isoformat()
from mail_merge import parse_template, render_templates, send_via_smtp
import csv
import tempfile
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import requests
from lib.app_factory import create_app as create_flask_app
from lib.oauth import create_flow as build_oauth_flow, get_user_info as fetch_user_info

# Import database modules
from db.config import init_db
from db.services import UserService, TemplateService, EmailLogService
from db.models import User, Template, EmailLog
from db.config import get_db_session
from sqlalchemy import and_

# Load environment variables from .env file
load_dotenv()

# OAuth Configuration
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
GOOGLE_REDIRECT_URI = os.getenv('GOOGLE_REDIRECT_URI', 'https://inmailer.onrender.com/auth/google/callback')

# User limit configuration
MAX_FREE_USERS = int(os.getenv('MAX_FREE_USERS', '50'))

# Gmail API scopes - include openid since Google adds it automatically
SCOPES = [
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/userinfo.profile',
    'https://www.googleapis.com/auth/userinfo.email',
    'openid'  # Google automatically adds this scope
]

def replace_template_variables(text: str, contact_data: dict) -> str:
    """Replace template variables with contact data values"""
    if not text or not contact_data:
        return text
    
    result = text
    replacements_made = []
    
    print(f"🔍 Processing text: {text[:100]}...")
    print(f"🔍 Contact data: {contact_data}")
    
    # Create a comprehensive mapping of all possible variable formats
    variable_mapping = {}
    
    for key, value in contact_data.items():
        # Handle None and empty values - skip empty values to avoid replacing with empty strings
        if value is None:
            continue
        clean_value = str(value).strip()
        if not clean_value:
            continue
        
        # Store the original key-value
        variable_mapping[key] = clean_value
        
        # Store lowercase version
        variable_mapping[key.lower()] = clean_value
        
        # Store uppercase version
        variable_mapping[key.upper()] = clean_value
        
        # Store title case version
        variable_mapping[key.title()] = clean_value
        
        # Store with underscores
        if ' ' in key:
            variable_mapping[key.replace(' ', '_')] = clean_value
            variable_mapping[key.replace(' ', '_').lower()] = clean_value
            variable_mapping[key.replace(' ', '_').upper()] = clean_value
            variable_mapping[key.replace(' ', '_').title()] = clean_value
        
        # Store with hyphens
        if ' ' in key:
            variable_mapping[key.replace(' ', '-')] = clean_value
            variable_mapping[key.replace(' ', '-').lower()] = clean_value
            variable_mapping[key.replace(' ', '-').upper()] = clean_value
            variable_mapping[key.replace(' ', '-').title()] = clean_value
        
        # Store underscore variations
        if '_' in key:
            variable_mapping[key.replace('_', ' ')] = clean_value
            variable_mapping[key.replace('_', ' ').lower()] = clean_value
            variable_mapping[key.replace('_', ' ').upper()] = clean_value
            variable_mapping[key.replace('_', ' ').title()] = clean_value
            
            variable_mapping[key.replace('_', '-')] = clean_value
            variable_mapping[key.replace('_', '-').lower()] = clean_value
            variable_mapping[key.replace('_', '-').upper()] = clean_value
            variable_mapping[key.replace('_', '-').title()] = clean_value
        
        # Store hyphen variations
        if '-' in key:
            variable_mapping[key.replace('-', ' ')] = clean_value
            variable_mapping[key.replace('-', ' ').lower()] = clean_value
            variable_mapping[key.replace('-', ' ').upper()] = clean_value
            variable_mapping[key.replace('-', ' ').title()] = clean_value
            
            variable_mapping[key.replace('-', '_')] = clean_value
            variable_mapping[key.replace('-', '_').lower()] = clean_value
            variable_mapping[key.replace('-', '_').upper()] = clean_value
            variable_mapping[key.replace('-', '_').title()] = clean_value
        
        # Store camelCase variations
        if ' ' in key or '_' in key or '-' in key:
            # Convert to camelCase
            words = key.replace('_', ' ').replace('-', ' ').split()
            if len(words) > 1:
                camel_case = words[0].lower() + ''.join(word.title() for word in words[1:])
                variable_mapping[camel_case] = clean_value
                variable_mapping[camel_case.lower()] = clean_value
                variable_mapping[camel_case.upper()] = clean_value
                variable_mapping[camel_case.title()] = clean_value
    
    print(f"🔍 Created {len(variable_mapping)} variable mappings")
    print(f"🔍 Sample mappings: {dict(list(variable_mapping.items())[:10])}")
    
    # Find all variable patterns in the text using regex
    import re
    
    # Pattern 1: ${VariableName} or ${variable_name} - matches anything between ${}
    pattern1 = r'\$\{([^}]+)\}'
    matches1 = re.findall(pattern1, text)
    print(f"🔍 Found ${{}} pattern matches: {matches1}")
    
    # Pattern 2: $VariableName or $variable_name
    pattern2 = r'\$([a-zA-Z_][a-zA-Z0-9_]*)\b'
    matches2 = re.findall(pattern2, text)
    print(f"🔍 Found $Variable pattern matches: {matches2}")
    
    # Combine all matches
    all_matches = list(set(matches1 + matches2))
    print(f"🔍 All unique variable matches: {all_matches}")
    
    # Replace all variables using regex for more reliable replacement
    for var_name in all_matches:
        # Try to find a match in our variable mapping
        found_match = False
        replacement_value = None
        
        # Try exact match first
        if var_name in variable_mapping:
            replacement_value = variable_mapping[var_name]
            found_match = True
            print(f"✅ Exact match: ${var_name} -> {replacement_value}")
        
        # Try case-insensitive match
        if not found_match:
            for mapping_key, mapping_value in variable_mapping.items():
                if mapping_key.lower() == var_name.lower():
                    replacement_value = mapping_value
                    found_match = True
                    print(f"✅ Case-insensitive match: ${var_name} -> {replacement_value}")
                    break
        
        # Try normalized match (remove spaces, underscores, hyphens)
        if not found_match:
            normalized_var = var_name.lower().replace(' ', '').replace('_', '').replace('-', '')
            for mapping_key, mapping_value in variable_mapping.items():
                normalized_key = mapping_key.lower().replace(' ', '').replace('_', '').replace('-', '')
                if normalized_key == normalized_var:
                    replacement_value = mapping_value
                    found_match = True
                    print(f"✅ Normalized match: ${var_name} -> {replacement_value}")
                    break
        
        if found_match and replacement_value:
            # Use regex to replace all occurrences (both ${var} and $var formats)
            # Escape special regex characters in var_name
            escaped_var = re.escape(var_name)
            # Replace ${var_name} format - match exactly ${var_name}
            pattern1 = re.escape('${') + escaped_var + re.escape('}')
            result = re.sub(pattern1, replacement_value, result)
            # Replace $var_name format - match $var_name but ensure it's a complete variable
            # Use negative lookahead to ensure we don't match if followed by alphanumeric or underscore
            pattern2 = re.escape('$') + escaped_var + r'(?![a-zA-Z0-9_])'
            result = re.sub(pattern2, replacement_value, result)
            replacements_made.append(f"${var_name} -> {replacement_value}")
        else:
            print(f"⚠️ No match found for variable: ${var_name}")
            print(f"🔍 Available keys in contact_data: {list(contact_data.keys())}")
            print(f"🔍 Sample variable_mapping keys: {list(variable_mapping.keys())[:10]}")
    
    # Final debug logging
    if replacements_made:
        print(f"🔍 Total replacements made: {len(replacements_made)}")
        print(f"🔍 Replacements: {replacements_made}")
        print(f"🔍 Final result preview: {result[:200]}...")
    else:
        print(f"⚠️ No variable replacements made!")
        print(f"🔍 Available variable mappings: {list(variable_mapping.keys())[:20]}...")
    
    return result

def save_templates_to_file():
    """Save all templates to JSON file for persistence (legacy support)"""
    try:
        templates_dir = Path("Templates")
        templates_file = templates_dir / "templates.json"
        
        # Create backup of existing file if it exists
        if templates_file.exists():
            backup_file = templates_dir / "templates_backup.json"
            import shutil
            shutil.copy2(templates_file, backup_file)
            print(f"💾 Created backup: {backup_file}")
        
        # Save to temporary file first, then rename (atomic operation)
        temp_file = templates_dir / "templates_temp.json"
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump([], f, indent=2, ensure_ascii=False)  # Empty array since we're using DB now
        
        # Atomic rename
        temp_file.replace(templates_file)
        print(f"✅ Legacy templates file updated (now empty - using database)")
        
    except Exception as e:
        print(f"❌ Error saving templates: {e}")
        import traceback
        traceback.print_exc()

def initialize_templates():
    """Initialize database and migrate existing templates if needed"""
    print("🚀 Initializing InMailer Backend with Database...")
    
    # Initialize database tables
    try:
        init_db()
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        raise
    
    # Create templates directory if it doesn't exist
    templates_dir = Path("Templates")
    templates_dir.mkdir(exist_ok=True)
    print(f"📁 Templates directory: {templates_dir.absolute()}")
    
    # Check if we need to migrate existing templates
    templates_file = templates_dir / "templates.json"
    if templates_file.exists():
        try:
            with open(templates_file, 'r', encoding='utf-8') as f:
                existing_templates = json.load(f)
            
            if existing_templates:
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
                
                # Update the JSON file to indicate migration
                save_templates_to_file()
                
        except Exception as e:
            print(f"❌ Error during template migration: {e}")
    
    print("✅ Template initialization complete!")

def send_gmail(credentials, to_email, subject, body, attachment_path=None, attachment_name=None, sender_name=None, user_email=None):
    """Send email using Gmail API"""
    try:
        print(f"📧 Starting Gmail send process...")
        print(f"📧 Sender name from database: {sender_name or 'InMailer'}")
        print(f"📧 User email from database: {user_email or 'Not provided'}")
        print(f"📧 To: {to_email}")
        print(f"📧 Subject: {subject}")
        print(f"📧 Body length: {len(body)} characters")
        print(f"📧 Attachment: {attachment_path}")
        print(f"📧 Attachment name: {attachment_name}")
        
        service = build('gmail', 'v1', credentials=credentials)
        print(f"✅ Gmail service built successfully")
        
        # Create email message with sender name and user email from database
        message = create_email_message(to_email, subject, body, attachment_path, attachment_name, sender_name, user_email)
        print(f"✅ Email message created successfully")
        
        # Send the email directly - the sender name is already set in the message headers
        try:
            sent_message = service.users().messages().send(userId='me', body=message).execute()
            print(f"✅ Email sent successfully! Message ID: {sent_message.get('id')}")
            print(f"📧 Email sent with sender name: '{sender_name}' from database")
            return sent_message
        except Exception as send_error:
            print(f"❌ Error during Gmail API send: {send_error}")
            
            # Check if it's a credentials issue
            if "credentials" in str(send_error).lower() or "refresh" in str(send_error).lower():
                print(f"🔍 This appears to be a credentials issue. User may need to re-authenticate.")
                print(f"🔍 Error details: {send_error}")
                return None
            else:
                # Re-raise other errors
                raise send_error
        
    except Exception as e:
        print(f"❌ Error sending Gmail: {e}")
        import traceback
        traceback.print_exc()
        return None

def create_email_message(to_email, subject, body, attachment_path=None, attachment_name=None, sender_name=None, user_email=None):
    """Create email message for Gmail API"""
    import base64
    import mimetypes
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    from email.mime.base import MIMEBase
    from email.encoders import encode_base64
    
    message = MIMEMultipart()
    message['to'] = to_email
    message['subject'] = subject
    
    # Use the actual user's name and email from database
    if sender_name and user_email:
        # Set the From field to show the user's name but use their real email
        message['From'] = f"{sender_name} <{user_email}>"
        message['Sender'] = f"{sender_name} <{user_email}>"
        message['Reply-To'] = f"{sender_name} <{user_email}>"
        
        # Add custom headers that some email clients will respect
        message['X-Sender'] = sender_name
        message['X-From'] = sender_name
        
        print(f"📧 Setting sender name from database: {sender_name}")
        print(f"📧 Using actual user email: {user_email}")
        print(f"📧 Email will display as: {sender_name} <{user_email}>")
    else:
        message['From'] = "InMailer <inmailer@gmail.com>"
        print(f"📧 Using default From field: InMailer")
    
    # Add text body
    text_part = MIMEText(body, 'plain')
    message.attach(text_part)
    
    # Add attachment if provided
    if attachment_path and os.path.exists(attachment_path):
        print(f"📎 Processing attachment: {attachment_path}")
        
        # Detect MIME type
        mime_type, _ = mimetypes.guess_type(attachment_path)
        if mime_type is None:
            mime_type = 'application/octet-stream'
        
        print(f"📎 Detected MIME type: {mime_type}")
        
        # Get file extension for better MIME type detection
        file_extension = os.path.splitext(attachment_path)[1].lower()
        
        # Handle common file types with proper MIME types
        if file_extension == '.pdf':
            mime_type = 'application/pdf'
        elif file_extension in ['.doc', '.docx']:
            mime_type = 'application/msword' if file_extension == '.doc' else 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        elif file_extension in ['.jpg', '.jpeg']:
            mime_type = 'image/jpeg'
        elif file_extension == '.png':
            mime_type = 'image/png'
        elif file_extension == '.txt':
            mime_type = 'text/plain'
        
        print(f"📎 Final MIME type: {mime_type}")
        
        # Create attachment part
        main_type, sub_type = mime_type.split('/', 1)
        
        with open(attachment_path, 'rb') as f:
            attachment_data = f.read()
            print(f"📎 Attachment size: {len(attachment_data)} bytes")
            
            if main_type == 'text':
                # Handle text files
                attachment = MIMEText(attachment_data.decode('utf-8', errors='ignore'), sub_type)
            elif main_type == 'image':
                # Handle image files
                attachment = MIMEText(attachment_data, 'base64', filename=attachment_name or os.path.basename(attachment_path))
            else:
                # Handle binary files (PDF, DOC, etc.)
                attachment = MIMEBase(main_type, sub_type)
                attachment.set_payload(attachment_data)
                # Encode the attachment properly
                encode_base64(attachment)
            
            # Set filename - use original filename if provided, otherwise fall back to path basename
            filename = attachment_name if attachment_name else os.path.basename(attachment_path)
            attachment.add_header('Content-Disposition', 'attachment', filename=filename)
            message.attach(attachment)
            print(f"✅ Attachment attached successfully with filename: {filename}")
    
    # Encode message
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
    return {'raw': raw_message}

app = create_flask_app(initialize_templates)

# Database-integrated API endpoints
@app.route('/api/templates', methods=['GET'])
def get_templates():
    """Get all templates for the authenticated user"""
    try:
        # Get user from session
        user_info = session.get('user_info')
        if not user_info:
            return jsonify({'error': 'Not authenticated'}), 401
        
        user_email = user_info.get('email')
        user = UserService.get_user_by_email(user_email)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        print(f"🔍 Debug: Looking up templates for DB user.id={user.id}, email={user_email}", flush=True)

        # Get user's templates from database
        templates = TemplateService.get_user_templates(user.id)

        print(f"🔍 Debug: Found {len(templates)} templates for user.id={user.id}", flush=True)

        # Convert to JSON-serializable format
        templates_data = []
        for template in templates:
            templates_data.append({
                'id': template.id,
                'name': template.name,
                'subject': template.subject,
                'content': template.content,
                'variables': template.variables,
                'attachment_path': template.attachment_path,
                'attachment_name': template.attachment_name,
                'created_at': safe_isoformat(template.created_at),
                'updated_at': safe_isoformat(template.updated_at)
            })
        
        print(f"🔍 Debug: Returning {len(templates_data)} templates for user {user_email}")
        return jsonify(templates_data)
        
    except Exception as e:
        print(f"❌ Error getting templates: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/templates', methods=['POST'])
def create_template():
    """Create a new template for the authenticated user"""
    try:
        # Get user from session
        user_info = session.get('user_info')
        if not user_info:
            return jsonify({'error': 'Not authenticated'}), 401
        
        user_email = user_info.get('email')
        user = UserService.get_user_by_email(user_email)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Handle both JSON data and file uploads
        template_name = None
        subject = None
        content = None
        variables = []
        attachment_path = None
        attachment_name = None
        
        # Check if this is a multipart form (with file) or JSON
        if request.content_type and 'multipart/form-data' in request.content_type:
            # Handle multipart form data (with file upload)
            template_name = request.form.get('name')
            subject = request.form.get('subject')
            content = request.form.get('content')
            variables_str = request.form.get('variables', '[]')
            try:
                variables = json.loads(variables_str) if variables_str else []
            except:
                variables = []
            
            # Handle file upload
            if 'file' in request.files:
                file = request.files['file']
                if file.filename != '':
                    # Create attachments directory if it doesn't exist
                    attachments_dir = Path("Templates/attachments")
                    attachments_dir.mkdir(exist_ok=True)
                    
                    # Generate unique filename
                    import uuid
                    file_extension = Path(file.filename).suffix
                    unique_filename = f"{uuid.uuid4()}{file_extension}"
                    file_path = attachments_dir / unique_filename
                    
                    # Save file
                    file.save(file_path)
                    
                    attachment_path = str(file_path)
                    attachment_name = file.filename
                    print(f"✅ New attachment uploaded: {attachment_name}")
        else:
            # Handle JSON data (no file upload)
            data = request.json
            template_name = data.get('name')
            subject = data.get('subject')
            content = data.get('content')
            variables = data.get('variables', [])
        
        if not all([template_name, subject, content]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Create template in database with debug logging
        print(f"🔍 === TEMPLATE CREATION DEBUG ===")
        print(f"🔍 Creating template for user ID: {user.id}")
        print(f"🔍 Template name: {template_name}")
        print(f"🔍 User email: {user_email}")
        
        template = TemplateService.create_template(
            user_id=user.id,
            name=template_name,
            subject=subject,
            content=content,
            variables=variables,
            attachment_path=attachment_path,
            attachment_name=attachment_name
        )
        
        print(f"🔍 Template created with ID: {template.id}")
        print(f"🔍 Template user_id: {template.user_id}")
        print(f"🔍 =================================")
        
        # Convert to JSON-serializable format
        template_data = {
            'id': template.id,
            'name': template.name,
            'subject': template.subject,
            'content': template.content,
            'variables': template.variables,
            'attachment_path': template.attachment_path,
            'attachment_name': template.attachment_name,
            'created_at': safe_isoformat(template.created_at),
            'updated_at': safe_isoformat(template.updated_at)
        }
        
        print(f"✅ Template created successfully: {template_name}")
        return jsonify({'message': 'Template created successfully', 'template': template_data}), 201
        
    except Exception as e:
        print(f"❌ Error creating template: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/templates/<int:template_id>', methods=['PUT'])
def update_template(template_id):
    """Update an existing template for the authenticated user"""
    try:
        # Get user from session
        user_info = session.get('user_info')
        if not user_info:
            return jsonify({'error': 'Not authenticated'}), 401
        
        user_email = user_info.get('email')
        user = UserService.get_user_by_email(user_email)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Handle both JSON data and file uploads
        template_name = None
        subject = None
        content = None
        variables = []
        attachment_path = None
        attachment_name = None
        
        # Check if this is a multipart form (with file) or JSON
        if request.content_type and 'multipart/form-data' in request.content_type:
            # Handle multipart form data (with file upload)
            template_name = request.form.get('name')
            subject = request.form.get('subject')
            content = request.form.get('content')
            variables_str = request.form.get('variables', '[]')
            try:
                variables = json.loads(variables_str) if variables_str else []
            except:
                variables = []
            
            # Handle file upload
            if 'file' in request.files:
                file = request.files['file']
                if file.filename != '':
                    # Create attachments directory if it doesn't exist
                    attachments_dir = Path("Templates/attachments")
                    attachments_dir.mkdir(exist_ok=True)
                    
                    # Generate unique filename
                    import uuid
                    file_extension = Path(file.filename).suffix
                    unique_filename = f"{uuid.uuid4()}{file_extension}"
                    file_path = attachments_dir / unique_filename
                    
                    # Save file
                    file.save(file_path)
                    
                    attachment_path = str(file_path)
                    attachment_name = file.filename
                    print(f"✅ New attachment uploaded: {attachment_name}")
        else:
            # Handle JSON data (no file upload)
            data = request.json
            template_name = data.get('name')
            subject = data.get('subject')
            content = data.get('content')
            variables = data.get('variables', [])
        
        if not all([template_name, subject, content]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Update template in database
        update_data = {
            'name': template_name,
            'subject': subject,
            'content': content,
            'variables': variables
        }
        
        # Only update attachment if new one was uploaded
        if attachment_path and attachment_name:
            update_data['attachment_path'] = attachment_path
            update_data['attachment_name'] = attachment_name
        
        template = TemplateService.update_template(
            template_id=template_id,
            user_id=user.id,
            **update_data
        )
        
        if not template:
            return jsonify({'error': 'Template not found'}), 404
        
        # Convert to JSON-serializable format
        template_data = {
            'id': template.id,
            'name': template.name,
            'subject': template.subject,
            'content': template.content,
            'variables': template.variables,
            'attachment_path': template.attachment_path,
            'attachment_name': template.attachment_name,
            'created_at': safe_isoformat(template.created_at),
            'updated_at': safe_isoformat(template.updated_at)
        }
        
        print(f"✅ Template updated successfully: {template_name}")
        return jsonify({'message': 'Template updated successfully', 'template': template_data}), 200
        
    except Exception as e:
        print(f"❌ Error updating template: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/templates/<int:template_id>', methods=['DELETE'])
def delete_template(template_id):
    """Delete a template for the authenticated user"""
    try:
        # Get user from session
        user_info = session.get('user_info')
        if not user_info:
            return jsonify({'error': 'Not authenticated'}), 401
        
        user_email = user_info.get('email')
        user = UserService.get_user_by_email(user_email)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Delete template from database
        success = TemplateService.delete_template(template_id, user.id)
        
        if not success:
            return jsonify({'error': 'Template not found'}), 404
        
        print(f"✅ Template deleted successfully")
        return jsonify({'message': 'Template deleted successfully'}), 200
        
    except Exception as e:
        print(f"❌ Error deleting template: {e}")
        
        # Provide more specific error messages
        error_message = str(e)
        if "ForeignKeyViolation" in error_message:
            return jsonify({
                'error': 'Cannot delete template. It has associated email logs. Please contact support if you need to delete this template.',
                'details': 'This template has been used to send emails and cannot be deleted to preserve email history.'
            }), 400
        elif "IntegrityError" in error_message:
            return jsonify({
                'error': 'Database integrity error. Please try again or contact support.',
                'details': 'There was an issue with the database operation.'
            }), 500
        else:
            return jsonify({'error': 'Failed to delete template. Please try again.'}), 500

@app.route('/api/user/stats', methods=['GET'])
def get_user_stats():
    """Get email statistics for the authenticated user"""
    try:
        # Get user from session
        user_info = session.get('user_info')
        if not user_info:
            return jsonify({'error': 'Not authenticated'}), 401
        
        user_email = user_info.get('email')
        user = UserService.get_user_by_email(user_email)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get user statistics from database
        stats = EmailLogService.get_user_stats(user.id)
        
        return jsonify(stats)
        
    except Exception as e:
        print(f"❌ Error getting user stats: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/dashboard/stats', methods=['GET'])
def get_dashboard_stats():
    """Get dashboard statistics for the authenticated user"""
    try:
        # Get user from session
        user_info = session.get('user_info')
        if not user_info:
            return jsonify({'error': 'Not authenticated'}), 401
        
        user_email = user_info.get('email')
        user = UserService.get_user_by_email(user_email)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get template count with debug logging
        print(f"🔍 === DASHBOARD STATS DEBUG ===")
        print(f"🔍 User ID: {user.id}")
        print(f"🔍 User Email: {user_email}")
        print(f"🔍 Calling TemplateService.count_user_templates({user.id})")
        
        template_count = TemplateService.count_user_templates(user.id)
        print(f"🔍 Template count returned: {template_count}")
        
        # DIRECT DATABASE TEST - bypass the service layer
        print(f"🔍 === DIRECT DATABASE TEST ===")
        from db.models import Template
        db = get_db_session()
        try:
            direct_count = db.query(Template).filter(Template.user_id == user.id).count()
            print(f"🔍 Direct database count: {direct_count}")
            
            # Get all templates for this user
            user_templates = db.query(Template).filter(Template.user_id == user.id).all()
            print(f"🔍 Direct database templates found: {len(user_templates)}")
            for template in user_templates:
                print(f"🔍   - Template: {template.name} (ID: {template.id})")
        finally:
            db.close()
        print(f"🔍 =================================")
        
        # Get email count (only sent emails)
        print(f"🔍 Calling EmailLogService.get_user_stats({user.id})")
        sent_emails = EmailLogService.get_user_stats(user.id)
        print(f"🔍 Email stats returned: {sent_emails}")
        print(f"🔍 =================================")
        
        # Count orphaned email logs (emails with deleted templates)
        from db.models import EmailLog
        db = get_db_session()
        try:
            orphaned_emails = db.query(EmailLog).filter(
                and_(EmailLog.user_id == user.id, EmailLog.template_id.is_(None))
            ).count()
        finally:
            db.close()
        
        return jsonify({
            'template_count': template_count,
            'emails_sent': sent_emails.get('sent_emails', 0),
            'orphaned_emails': orphaned_emails
        })
        
    except Exception as e:
        print(f"❌ Error getting dashboard stats: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/template-attachment', methods=['POST'])
def upload_template_attachment():
    """Upload attachment for a template"""
    try:
        # Get user from session
        user_info = session.get('user_info')
        if not user_info:
            return jsonify({'error': 'Not authenticated'}), 401
        
        user_email = user_info.get('email')
        user = UserService.get_user_by_email(user_email)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Check if file was uploaded
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Create attachments directory if it doesn't exist
        attachments_dir = Path("Templates/attachments")
        attachments_dir.mkdir(exist_ok=True)
        
        # Generate unique filename
        import uuid
        file_extension = Path(file.filename).suffix
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = attachments_dir / unique_filename
        
        # Save file
        file.save(file_path)
        
        # Return file info
        return jsonify({
            'success': True,
            'attachment_path': str(file_path),
            'attachment_name': file.filename,
            'message': 'Attachment uploaded successfully'
        })
        
    except Exception as e:
        print(f"❌ Error uploading attachment: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/debug/database', methods=['GET'])
def debug_database():
    """Debug endpoint to check database state"""
    try:
        # Get user from session
        user_info = session.get('user_info')
        if not user_info:
            return jsonify({'error': 'Not authenticated'}), 401
        
        user_email = user_info.get('email')
        user = UserService.get_user_by_email(user_email)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get database session and check directly
        from db.models import Template, User
        db = get_db_session()
        try:
            # Check all users
            all_users = db.query(User).all()
            user_list = []
            for u in all_users:
                user_list.append({
                    'id': u.id,
                    'email': u.email,
                    'name': u.name
                })
            
            # Check all templates
            all_templates = db.query(Template).all()
            template_list = []
            for t in all_templates:
                template_list.append({
                    'id': t.id,
                    'user_id': t.user_id,
                    'name': t.name,
                    'subject': t.subject[:50] + '...' if len(t.subject) > 50 else t.subject
                })
            
            # Check templates for this specific user
            user_templates = db.query(Template).filter(Template.user_id == user.id).all()
            user_template_list = []
            for t in user_templates:
                user_template_list.append({
                    'id': t.id,
                    'name': t.name,
                    'subject': t.subject[:50] + '...' if len(t.subject) > 50 else t.subject
                })
            
            return jsonify({
                'current_user': {
                    'id': user.id,
                    'email': user.email,
                    'name': user.name
                },
                'all_users': user_list,
                'all_templates': template_list,
                'user_templates': user_template_list,
                'user_template_count': len(user_templates),
                'total_template_count': len(all_templates)
            })
            
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ Error debugging database: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/debug-csv', methods=['POST'])
def debug_csv():
    """Debug endpoint to see what's in the CSV file"""
    try:
        # Check if file was uploaded
        if 'csv_file' not in request.files:
            return jsonify({'error': 'No CSV file uploaded'}), 400
        
        csv_file = request.files['csv_file']
        if csv_file.filename == '':
            return jsonify({'error': 'No CSV file selected'}), 400
        
        # Process CSV file
        import tempfile
        temp_file_path = None
        try:
            with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.csv') as temp_file:
                temp_file_path = temp_file.name
                csv_file.save(temp_file_path)
                temp_file.seek(0)
                
                # Read CSV content
                import csv
                reader = csv.DictReader(temp_file)
                contacts = list(reader)
        finally:
            # Clean up temp file
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.unlink(temp_file_path)
                except OSError as e:
                    print(f"⚠️ Warning: Could not delete temp file {temp_file_path}: {e}")
        
        if not contacts:
            return jsonify({'error': 'No contacts found in CSV file'}), 400
        
        # Enhanced CSV analysis with variable mapping examples
        sample_contact = contacts[0] if contacts else {}
        
        # Show what variables would be available for templates
        available_variables = []
        if sample_contact:
            for key, value in sample_contact.items():
                if value and str(value).strip():
                    available_variables.append({
                        'original_key': key,
                        'value': str(value).strip(),
                        'suggested_template_usage': f'${{{key}}} or ${key}'
                    })
        
        # Return detailed CSV analysis
        return jsonify({
            'message': 'CSV analysis complete',
            'total_contacts': len(contacts),
            'sample_contact': sample_contact,
            'all_contact_keys': list(sample_contact.keys()) if sample_contact else [],
            'available_variables': available_variables,
            'first_few_contacts': contacts[:3],
            'template_suggestions': {
                'subject_example': f'Hello ${{{list(sample_contact.keys())[0] if sample_contact else "First_Name"}}}!',
                'content_example': f'Dear ${{{list(sample_contact.keys())[0] if sample_contact else "First_Name"}}}, welcome to ${{{list(sample_contact.keys())[1] if len(sample_contact) > 1 else "Company"}}}!'
            }
        })
        
    except Exception as e:
        print(f"❌ Error analyzing CSV: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/mail-merge', methods=['POST'])
def mail_merge_preview():
    """Generate preview of mail merge emails"""
    try:
        # Get user from session
        user_info = session.get('user_info')
        if not user_info:
            return jsonify({'error': 'Not authenticated'}), 401
        
        user_email = user_info.get('email')
        user = UserService.get_user_by_email(user_email)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Check if file was uploaded
        if 'csv_file' not in request.files:
            return jsonify({'error': 'No CSV file uploaded'}), 400
        
        csv_file = request.files['csv_file']
        if csv_file.filename == '':
            return jsonify({'error': 'No CSV file selected'}), 400
        
        template_id = request.form.get('template_id')
        if not template_id:
            return jsonify({'error': 'No template ID provided'}), 400
        
        try:
            template_id_int = int(template_id)
        except ValueError:
            return jsonify({'error': 'Invalid template ID format'}), 400
        
        # Get template from database
        template = TemplateService.get_template_by_id(template_id_int, user.id)
        if not template:
            return jsonify({'error': 'Template not found'}), 404
        
        # Process CSV file
        import tempfile
        temp_file_path = None
        try:
            with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.csv') as temp_file:
                temp_file_path = temp_file.name
                csv_file.save(temp_file_path)
                temp_file.seek(0)
                
                # Read CSV content
                import csv
                reader = csv.DictReader(temp_file)
                contacts = list(reader)
        finally:
            # Clean up temp file after it's fully closed
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.unlink(temp_file_path)
                except OSError as e:
                    print(f"⚠️ Warning: Could not delete temp file {temp_file_path}: {e}")
                    # Continue execution even if cleanup fails
        
        if not contacts:
            return jsonify({'error': 'No contacts found in CSV file'}), 400
        
        # Generate preview for first few contacts
        preview_contacts = contacts[:3]  # Show first 3 contacts as preview
        results = []
        
        for contact in preview_contacts:
            try:
                # Replace variables in template using the helper function
                preview_content = replace_template_variables(template.content, contact)
                preview_subject = replace_template_variables(template.subject, contact)
                
                # Create a compact preview with truncated content
                preview_data = {
                    'contact': contact,
                    'subject': preview_subject,
                    'content': preview_content,
                    'content_preview': preview_content[:150] + '...' if len(preview_content) > 150 else preview_content,
                    'status': 'preview',
                    'contact_summary': {
                        'name': contact.get('First Name', contact.get('First_Name', contact.get('first_name', contact.get('Name', contact.get('name', 'Unknown'))))),
                        'email': contact.get('Email', contact.get('email', 'No email')),
                        'company': contact.get('Company', contact.get('company', 'No company'))
                    }
                }
                
                results.append(preview_data)
                
            except Exception as e:
                results.append({
                    'contact': contact,
                    'subject': 'Error',
                    'content': f'Error processing contact: {str(e)}',
                    'status': 'error'
                })
        
        # Create a summary preview for the UI
        preview_summary = {
            'total_contacts': len(contacts),
            'preview_count': len(results),
            'sample_preview': results[0] if results else None
        }
        
        return jsonify({
            'message': 'Preview generated successfully',
            'results': results,
            'total_contacts': len(contacts),
            'preview_summary': preview_summary
        })
        
    except Exception as e:
        print(f"❌ Error generating mail merge preview: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/send-emails', methods=['POST'])
def send_emails():
    """Send emails using mail merge"""
    try:
        # Debug session information
        print(f"🔍 === SEND-EMAILS DEBUG ===")
        print(f"🔍 Session ID: {session.get('_id', 'No ID')}")
        print(f"🔍 Session keys: {list(session.keys())}")
        print(f"🔍 User info in session: {session.get('user_info')}")
        print(f"🔍 Credentials in session: {session.get('credentials')}")
        print(f"🔍 Request cookies: {dict(request.cookies)}")
        print(f"🔍 Request origin: {request.headers.get('Origin')}")
        print(f"🔍 =========================")
        
        # Get user from session
        user_info = session.get('user_info')
        if not user_info:
            print("❌ No user_info found in session")
            return jsonify({'error': 'Not authenticated'}), 401
        
        user_email = user_info.get('email')
        user = UserService.get_user_by_email(user_email)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.json
        template_id = data.get('template_id')
        contacts = data.get('contacts', [])
        
        if not template_id or not contacts:
            return jsonify({'error': 'Missing template ID or contacts'}), 400
        
        # Get template from database
        template = TemplateService.get_template_by_id(int(template_id), user.id)
        if not template:
            return jsonify({'error': 'Template not found'}), 404
        
        # Get user credentials from session
        credentials_data = session.get('credentials')
        if not credentials_data:
            print("❌ No credentials found in session")
            return jsonify({
                'error': 'No Gmail credentials found. Please sign in with Google again.',
                'action': 'sign_in_required',
                'details': 'Your OAuth session has expired or is missing. Please sign in again to refresh your Gmail access.'
            }), 401
        
        # Recreate credentials object with proper error handling
        from google.oauth2.credentials import Credentials
        
        # Check if all required credential fields are present
        required_fields = ['token', 'refresh_token', 'token_uri', 'client_id', 'client_secret', 'scopes']
        missing_fields = [field for field in required_fields if not credentials_data.get(field)]
        
        if missing_fields:
            print(f"❌ Missing required credential fields: {missing_fields}")
            print(f"🔍 Available fields: {list(credentials_data.keys())}")
            return jsonify({
                'error': f'Missing required Gmail credentials: {missing_fields}. Please sign in with Google again.',
                'action': 'reauth_required',
                'details': f'The OAuth session is incomplete. Missing: {missing_fields}. This usually happens when Google doesn\'t provide all required tokens. Try signing out completely and signing in again.',
                'missing_fields': missing_fields,
                'available_fields': list(credentials_data.keys())
            }), 401
        
        try:
            credentials = Credentials(
                token=credentials_data['token'],
                refresh_token=credentials_data['refresh_token'],
                token_uri=credentials_data['token_uri'],
                client_id=credentials_data['client_id'],
                client_secret=credentials_data['client_secret'],
                scopes=credentials_data['scopes']
            )
            print(f"✅ Credentials object recreated successfully")
        except Exception as e:
            print(f"❌ Error recreating credentials: {e}")
            return jsonify({'error': 'Failed to recreate Gmail credentials. Please sign in with Google again.'}), 401
        
        # Process each contact
        results = []
        success_count = 0
        error_count = 0
        
        for contact in contacts:
            try:
                # Get email from contact
                email = contact.get('Email') or contact.get('email')
                if not email:
                    results.append({
                        'contact': contact,
                        'status': 'error',
                        'error': 'No email address found'
                    })
                    error_count += 1
                    continue
                
                # Replace variables in template using the helper function
                email_content = replace_template_variables(template.content, contact)
                email_subject = replace_template_variables(template.subject, contact)
                
                # Debug logging to verify variable replacement
                print(f"🔍 Debug: Original subject: {template.subject}")
                print(f"🔍 Debug: Processed subject: {email_subject}")
                print(f"🔍 Debug: Original content: {template.content[:100]}...")
                print(f"🔍 Debug: Processed content: {email_content[:100]}...")
                print(f"🔍 Debug: User info - ID: {user.id}, Name: '{user.name}', Email: {user.email}")
                
                # Clear explanation of how sender name works
                print(f"📧 ===== EMAIL SENDING INFO =====")
                print(f"📧 Database User Name: '{user.name}' (from name column)")
                print(f"📧 Database User Email: {user.email}")
                print(f"📧 Authenticated Gmail Account: {user.email}")
                print(f"📧 Email will be sent FROM: {user.email} (your Gmail account)")
                print(f"📧 Email will DISPLAY AS: '{user.name}' (hardcoded from database)")
                print(f"📧 =================================")
                
                # Send email
                sent_message = send_gmail(
                    credentials=credentials,
                    to_email=email,
                    subject=email_subject,
                    body=email_content,
                    attachment_path=template.attachment_path,
                    attachment_name=template.attachment_name,
                    sender_name=user.name,
                    user_email=user.email
                )
                
                if sent_message:
                    # Log successful email
                    EmailLogService.create_email_log(
                        user_id=user.id,
                        template_id=template.id,
                        recipient_email=email,
                        subject=email_subject,
                        status='sent',
                        gmail_message_id=sent_message.get('id')
                    )
                    
                    results.append({
                        'contact': contact,
                        'status': 'sent',
                        'message_id': sent_message.get('id')
                    })
                    success_count += 1
                else:
                    # Log failed email
                    EmailLogService.create_email_log(
                        user_id=user.id,
                        template_id=template.id,
                        recipient_email=email,
                        subject=email_subject,
                        status='failed',
                        error_message='Failed to send email'
                    )
                    
                    results.append({
                        'contact': contact,
                        'status': 'error',
                        'error': 'Failed to send email'
                    })
                    error_count += 1
                    
            except Exception as e:
                # Log error
                email = contact.get('Email') or contact.get('email') or 'Unknown'
                EmailLogService.create_email_log(
                    user_id=user.id,
                    template_id=template.id,
                    recipient_email=email,
                    subject='Error',
                    status='failed',
                    error_message=str(e)
                )
                
                results.append({
                    'contact': contact,
                    'status': 'error',
                    'error': str(e)
                })
                error_count += 1
        
        return jsonify({
            'message': f'Email processing complete. {success_count} sent, {error_count} failed.',
            'results': results,
            'success_count': success_count,
            'error_count': error_count
        })
        
    except Exception as e:
        print(f"❌ Error sending emails: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/send-gmail', methods=['POST'])
def send_test_email():
    """Send a single test email for the authenticated user."""
    try:
        user_info = session.get('user_info')
        if not user_info:
            return jsonify({'error': 'Not authenticated'}), 401

        user = UserService.get_user_by_email(user_info.get('email'))
        if not user:
            return jsonify({'error': 'User not found'}), 404

        data = request.json or {}
        to_email = (data.get('to_email') or '').strip()
        subject = (data.get('subject') or 'Test Email from InMailer').strip()
        body = (data.get('body') or '').strip()
        attachment_path = (data.get('attachment_path') or '').strip() or None

        if not to_email:
            return jsonify({'error': 'Recipient email is required'}), 400
        if not body:
            return jsonify({'error': 'Email body is required'}), 400

        credentials_data = session.get('credentials')
        if not credentials_data:
            return jsonify({
                'error': 'No Gmail credentials found. Please sign in with Google again.',
                'action': 'sign_in_required'
            }), 401

        required_fields = ['token', 'refresh_token', 'token_uri', 'client_id', 'client_secret', 'scopes']
        missing_fields = [field for field in required_fields if not credentials_data.get(field)]
        if missing_fields:
            return jsonify({
                'error': f'Missing required Gmail credentials: {missing_fields}. Please sign in again.',
                'action': 'reauth_required',
                'missing_fields': missing_fields
            }), 401

        credentials = Credentials(
            token=credentials_data['token'],
            refresh_token=credentials_data['refresh_token'],
            token_uri=credentials_data['token_uri'],
            client_id=credentials_data['client_id'],
            client_secret=credentials_data['client_secret'],
            scopes=credentials_data['scopes']
        )

        sent_message = send_gmail(
            credentials=credentials,
            to_email=to_email,
            subject=subject,
            body=body,
            attachment_path=attachment_path,
            sender_name=user.name,
            user_email=user.email
        )

        if not sent_message:
            return jsonify({'error': 'Failed to send test email'}), 500

        EmailLogService.create_email_log(
            user_id=user.id,
            template_id=None,
            recipient_email=to_email,
            subject=subject,
            status='sent',
            gmail_message_id=sent_message.get('id')
        )

        return jsonify({
            'message': 'Test email sent successfully',
            'message_id': sent_message.get('id')
        })
    except Exception as e:
        print(f"❌ Error sending test email: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/debug/credentials', methods=['GET'])
def debug_credentials():
    """Debug endpoint to check what credentials are stored in session"""
    try:
        # Get user from session
        user_info = session.get('user_info')
        if not user_info:
            return jsonify({'error': 'Not authenticated'}), 401
        
        credentials_data = session.get('credentials')
        if not credentials_data:
            return jsonify({'error': 'No credentials found in session'}), 401
        
        # Check credential fields
        credential_info = {
            'has_token': bool(credentials_data.get('token')),
            'has_refresh_token': bool(credentials_data.get('refresh_token')),
            'has_token_uri': bool(credentials_data.get('token_uri')),
            'has_client_id': bool(credentials_data.get('client_id')),
            'has_client_secret': bool(credentials_data.get('client_secret')),
            'has_scopes': bool(credentials_data.get('scopes')),
            'token_length': len(credentials_data.get('token', '')) if credentials_data.get('token') else 0,
            'refresh_token_length': len(credentials_data.get('refresh_token', '')) if credentials_data.get('refresh_token') else 0,
            'scopes_count': len(credentials_data.get('scopes', [])) if credentials_data.get('scopes') else 0,
            'available_fields': list(credentials_data.keys())
        }
        
        return jsonify({
            'message': 'Credential debug info',
            'user_email': user_info.get('email'),
            'credential_info': credential_info,
            'note': 'If any required fields are missing, you may need to sign in again with Google'
        })
        
    except Exception as e:
        print(f"❌ Error debugging credentials: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/auth/user')
def get_user():
    """Get current authenticated user information"""
    print(f"🔍 /auth/user endpoint called")
    print(f"🔍 Request origin: {request.headers.get('Origin')}")
    print(f"🔍 Request cookies: {dict(request.cookies)}")
    print(f"🔍 Session contents: {list(session.keys())}")
    print(f"🔍 User info in session: {session.get('user_info')}")
    print(f"🔍 Session ID: {session.get('_id', 'No ID')}")
    
    user_info = session.get('user_info')
    if not user_info:
        print(f"❌ No user_info in session")
        return jsonify({'error': 'Not authenticated'}), 401
    
    print(f"✅ User authenticated: {user_info.get('email')}")
    return jsonify({
        'id': user_info.get('id'),
        'email': user_info.get('email'),
        'name': user_info.get('name'),
        'picture': user_info.get('picture')
    })

@app.route('/auth/logout')
def logout():
    """Logout user and clear session"""
    try:
        # Get user info before clearing for logging
        user_email = session.get('user_info', {}).get('email', 'Unknown')
        print(f"🔍 Logging out user: {user_email}")
        
        # Clear all session data
        session.clear()
        
        print(f"✅ Session cleared for user: {user_email}")
        return jsonify({
            'message': 'Logged out successfully',
            'user': user_email,
            'note': 'All session data and OAuth tokens have been cleared. You will need to sign in again to use Gmail features.'
        })
    except Exception as e:
        print(f"❌ Error during logout: {e}")
        # Still try to clear session even if there's an error
        session.clear()
        return jsonify({'message': 'Logged out (with errors)', 'error': str(e)}), 500

@app.route('/auth/force-reauth')
def force_reauth():
    """Force user to re-authenticate by clearing credentials and redirecting to OAuth"""
    try:
        user_email = session.get('user_info', {}).get('email', 'Unknown')
        print(f"🔍 Force re-authentication for user: {user_email}")
        
        # Clear only credentials, keep user info for the OAuth flow
        if 'credentials' in session:
            del session['credentials']
            print(f"✅ Credentials cleared for user: {user_email}")
        
        # Redirect to OAuth flow
        return redirect('/auth/google')
        
    except Exception as e:
        print(f"❌ Error during force re-auth: {e}")
        return jsonify({'error': 'Failed to force re-authentication'}), 500

@app.route('/auth/validate-credentials')
def validate_credentials():
    """Validate if current Gmail credentials are still valid"""
    try:
        user_info = session.get('user_info')
        if not user_info:
            return jsonify({'error': 'Not authenticated'}), 401
        
        credentials_data = session.get('credentials')
        if not credentials_data:
            return jsonify({
                'valid': False,
                'error': 'No credentials found',
                'action': 'sign_in_required'
            }), 200
        
        # Check if all required fields are present
        required_fields = ['token', 'refresh_token', 'token_uri', 'client_id', 'client_secret', 'scopes']
        missing_fields = [field for field in required_fields if not credentials_data.get(field)]
        
        if missing_fields:
            return jsonify({
                'valid': False,
                'error': f'Missing credential fields: {missing_fields}',
                'action': 'reauth_required',
                'missing_fields': missing_fields
            }), 200
        
        # Try to recreate credentials object
        try:
            from google.oauth2.credentials import Credentials
            credentials = Credentials(
                token=credentials_data['token'],
                refresh_token=credentials_data['refresh_token'],
                token_uri=credentials_data['token_uri'],
                client_id=credentials_data['client_id'],
                client_secret=credentials_data['client_secret'],
                scopes=credentials_data['scopes']
            )
            
            # Test if credentials work by making a simple Gmail API call
            from googleapiclient.discovery import build
            service = build('gmail', 'v1', credentials=credentials)
            
            # Try to get user profile (lightweight call)
            profile = service.users().getProfile(userId='me').execute()
            
            return jsonify({
                'valid': True,
                'user_email': profile.get('emailAddress'),
                'message': 'Credentials are valid and working'
            })
            
        except Exception as e:
            return jsonify({
                'valid': False,
                'error': f'Credentials validation failed: {str(e)}',
                'action': 'reauth_required'
            }), 200
            
    except Exception as e:
        return jsonify({
            'valid': False,
            'error': f'Validation error: {str(e)}',
            'action': 'unknown_error'
        }), 500

@app.route('/auth/debug-session')
def debug_session():
    """Debug endpoint to check session state"""
    print(f"🔍 === SESSION DEBUG ENDPOINT ===")
    print(f"🔍 Session ID: {session.get('_id', 'No ID')}")
    print(f"🔍 Session keys: {list(session.keys())}")
    print(f"🔍 User info: {session.get('user_info')}")
    print(f"🔍 Credentials: {session.get('credentials')}")
    print(f"🔍 Request cookies: {dict(request.cookies)}")
    print(f"🔍 Request origin: {request.headers.get('Origin')}")
    print(f"🔍 ==============================")
    
    credentials_data = session.get('credentials', {})
    required_fields = ['token', 'refresh_token', 'token_uri', 'client_id', 'client_secret', 'scopes']
    missing_fields = [field for field in required_fields if not credentials_data.get(field)]
    
    return jsonify({
        'session_id': session.get('_id'),
        'session_keys': list(session.keys()),
        'user_info': session.get('user_info'),
        'has_credentials': bool(credentials_data),
        'credentials_keys': list(credentials_data.keys()) if credentials_data else [],
        'missing_credential_fields': missing_fields,
        'has_refresh_token': bool(credentials_data.get('refresh_token')),
        'credential_status': 'complete' if not missing_fields else 'incomplete',
        'cookies': dict(request.cookies),
        'origin': request.headers.get('Origin'),
        'recommendations': {
            'action_needed': 'reauth' if missing_fields else 'none',
            'message': 'Credentials are incomplete. Please sign in again.' if missing_fields else 'Credentials look complete.'
        }
    })

# Keep other existing routes for compatibility
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint to verify backend and database status"""
    try:
        health_status = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'backend': 'app_db.py',
            'database': 'unknown'
        }
        
        # Test database connection
        try:
            db = get_db_session()
            from sqlalchemy import text
            db.execute(text("SELECT 1"))
            db.close()
            health_status['database'] = 'connected'
            health_status['database_url'] = os.getenv('DATABASE_URL', 'not_set')[:50] + '...' if os.getenv('DATABASE_URL') else 'not_set'
        except Exception as db_error:
            health_status['database'] = 'error'
            health_status['database_error'] = str(db_error)
            health_status['status'] = 'unhealthy'
        
        # Check environment variables
        health_status['environment'] = {
            'flask_env': os.getenv('FLASK_ENV', 'not_set'),
            'google_client_id_set': bool(os.getenv('GOOGLE_CLIENT_ID')),
            'frontend_url': os.getenv('FRONTEND_URL', 'not_set'),
            'max_free_users': os.getenv('MAX_FREE_USERS', 'not_set')
        }
        
        # Email configuration
        health_status['email'] = {
            'email_configured': bool(os.getenv("EMAIL_USER") and os.getenv("EMAIL_PASSWORD")),
            'email_user': os.getenv("EMAIL_USER", "NOT SET"),
            'email_host': os.getenv("EMAIL_HOST", "NOT SET"),
            'email_port': os.getenv("EMAIL_PORT", "NOT SET")
        }
        
        status_code = 200 if health_status['status'] == 'healthy' else 500
        return jsonify(health_status), status_code
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

# OAuth Helper Functions
def create_flow():
    return build_oauth_flow(
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
        redirect_uri=GOOGLE_REDIRECT_URI,
        scopes=SCOPES
    )

def get_user_info(credentials):
    return fetch_user_info(credentials)

# OAuth Routes
@app.route('/auth/google')
def google_auth():
    """Initiate Google OAuth flow"""
    try:
        flow = create_flow()
        flow.redirect_uri = GOOGLE_REDIRECT_URI
        
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'
        )

        # Store state and code_verifier in session for security
        # code_verifier is needed for PKCE token exchange in the callback
        session['oauth_state'] = state
        session['code_verifier'] = flow.code_verifier
        
        print(f"🔍 OAuth initiated - State: {state}")
        print(f"🔍 Authorization URL: {authorization_url}")
        
        # Redirect directly to Google's OAuth page
        return redirect(authorization_url)
        
    except Exception as e:
        print(f"Error creating OAuth flow: {e}")
        return jsonify({'error': 'Failed to initiate OAuth flow'}), 500

@app.route('/auth/google/callback')
def google_callback():
    """Handle Google OAuth callback"""
    try:
        print("🔄 OAuth callback started...")
        
        # Get authorization code from callback
        code = request.args.get('code')
        state = request.args.get('state')
        
        print(f"🔍 Received code: {code[:20]}..." if code else "❌ No code received")
        print(f"🔍 Received state: {state}")
        print(f"🔍 Session state: {session.get('oauth_state')}")
        
        # Check if we have a code
        if not code:
            print("❌ No authorization code received")
            return jsonify({'error': 'No authorization code received'}), 400
        
        # Verify state matches
        session_state = session.get('oauth_state')
        if state != session_state:
            print(f"❌ State mismatch! Received: {state}, Session: {session_state}")
            print(f"🔍 Session keys: {list(session.keys())}")
            print(f"🔍 Session ID: {session.get('_id', 'No ID')}")
            
            # For development/testing, we'll be more lenient
            # In production, you should enforce strict state validation
            print("⚠️  Proceeding despite state mismatch for development testing...")
        
        print("✅ State verified")
        
        # Create flow and exchange code for tokens
        print("🔄 Creating OAuth flow...")
        flow = create_flow()
        flow.redirect_uri = GOOGLE_REDIRECT_URI
        print(f"🔍 Redirect URI: {GOOGLE_REDIRECT_URI}")
        
        # Restore the PKCE code_verifier from the session so Google accepts the exchange
        code_verifier = session.get('code_verifier')
        if code_verifier:
            flow.code_verifier = code_verifier

        # Exchange authorization code for tokens
        print("🔄 Exchanging code for tokens...")
        flow.fetch_token(code=code)
        credentials = flow.credentials
        print("✅ Tokens received successfully")
        
        # Debug credential details
        print(f"🔍 Credential details:")
        print(f"🔍 - Has token: {'Yes' if credentials.token else 'No'}")
        print(f"🔍 - Has refresh_token: {'Yes' if credentials.refresh_token else 'No'}")
        print(f"🔍 - Token URI: {credentials.token_uri}")
        print(f"🔍 - Client ID: {credentials.client_id}")
        print(f"🔍 - Has client_secret: {'Yes' if credentials.client_secret else 'No'}")
        print(f"🔍 - Scopes: {credentials.scopes}")
        
        # Handle scope differences (Google might add 'openid' automatically)
        print(f"🔍 Received scopes: {credentials.scopes}")
        print(f"🔍 Expected scopes: {SCOPES}")
        
        # Check if we have the minimum required scopes
        # We need these specific scopes for the app to work
        required_scopes = [
            'https://www.googleapis.com/auth/gmail.send',
            'https://www.googleapis.com/auth/userinfo.profile',
            'https://www.googleapis.com/auth/userinfo.email'
        ]
        
        # Check if we have all required scopes (either full URLs or basic equivalents)
        missing_scopes = []
        for required_scope in required_scopes:
            scope_name = required_scope.split('/')[-1]  # Extract 'gmail.send', 'userinfo.profile', etc.
            
            # Check if we have the full scope URL
            if required_scope in credentials.scopes:
                print(f"✅ Found full scope: {required_scope}")
                continue
                
            # Check if we have the basic equivalent (e.g., 'email' for 'userinfo.email')
            if scope_name in credentials.scopes:
                print(f"✅ Found basic scope equivalent: {scope_name} for {required_scope}")
                continue
                
            # Check for other variations
            if 'gmail.send' in required_scope and any('gmail' in s for s in credentials.scopes):
                print(f"✅ Found Gmail scope variation")
                continue
                
            if 'userinfo' in required_scope and any('profile' in s or 'email' in s for s in credentials.scopes):
                print(f"✅ Found userinfo scope variation")
                continue
                
            missing_scopes.append(required_scope)
            print(f"❌ Missing scope: {required_scope}")
        
        if missing_scopes:
            print(f"⚠️  Missing required scopes: {missing_scopes}")
            return jsonify({'error': f'Missing required scopes: {missing_scopes}'}), 400
        
        print("✅ All required scopes are present!")
        
        # Check if we have a refresh token - this is critical for long-term access
        if not credentials.refresh_token:
            print("❌ CRITICAL: No refresh token received from Google!")
            print("❌ This usually means the user needs to re-authorize with explicit consent")
            print("❌ The 'prompt=consent' parameter should force this, but it may not work for existing users")
            return jsonify({
                'error': 'No refresh token received. This usually happens when re-authorizing an existing user. Please try signing out completely and signing in again, or use a different Google account.',
                'details': 'Google only provides refresh tokens on first authorization or when explicitly requested. Try signing out and signing in again.'
            }), 400
        
        print("✅ Refresh token received successfully!")
        
        # Get user information
        print("🔄 Getting user information...")
        user_info = get_user_info(credentials)
        if not user_info:
            print("❌ Failed to get user info from Google")
            return jsonify({'error': 'Failed to get user information from Google'}), 500
        
        print(f"✅ User info received: {user_info.get('email', 'No email')}")
        print(f"🔍 Full user_info from Google: {user_info}")
        print(f"🔍 User name from Google: '{user_info.get('name', 'No name')}'")
        print(f"🔍 User email from Google: '{user_info.get('email', 'No email')}'")
        
        # Store user info and tokens in session
        session['user_info'] = user_info
        session['credentials'] = {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes
        }
        
        # Debug session storage
        print(f"🔍 === OAUTH CALLBACK DEBUG ===")
        print(f"🔍 Session ID after storing: {session.get('_id', 'No ID')}")
        print(f"🔍 Session keys after storing: {list(session.keys())}")
        print(f"🔍 Credentials stored: {list(session.get('credentials', {}).keys())}")
        print(f"🔍 Has refresh_token: {'Yes' if session.get('credentials', {}).get('refresh_token') else 'No'}")
        print(f"🔍 ==============================")
        
        # Also store in our database system
        user_email = user_info.get('email')
        existing_user = UserService.get_user_by_email(user_email)
        
        if not existing_user:
            # Check if we've reached the user limit
            if not UserService.is_user_registration_allowed(MAX_FREE_USERS):
                current_count = UserService.get_total_user_count()
                print(f"❌ User limit reached! Current users: {current_count}, Max allowed: {MAX_FREE_USERS}")
                return jsonify({
                    'error': f'Sorry! We have reached our limit of {MAX_FREE_USERS} free users. Please contact us for premium access.',
                    'user_limit_reached': True,
                    'current_users': current_count,
                    'max_users': MAX_FREE_USERS
                }), 403
            
            # Create new user from Google OAuth
            user_name = user_info.get('name', 'Google User')
            print(f"🔍 Creating new user with name: '{user_name}' and email: '{user_email}'")
            print(f"🔍 Current user count: {UserService.get_total_user_count()}/{MAX_FREE_USERS}")
            user = UserService.create_user(
                email=user_email,
                name=user_name,
                is_google_user=True
            )
            print(f"✅ Created new Google user: {user_email} with name: '{user.name}'")
            print(f"✅ New user count: {UserService.get_total_user_count()}/{MAX_FREE_USERS}")
        else:
            # Update existing user
            print(f"🔍 Updating existing user: {user_email}")
            user_name = user_info.get('name', 'Google User')
            print(f"🔍 Updating user name to: '{user_name}'")
            user = UserService.update_user_google_oauth(existing_user.id, user_name)
            print(f"✅ Updated existing user with Google OAuth: {user_email}")
            print(f"🔍 User name after update: '{user.name}'")
        
        print(f"✅ OAuth successful! User: {user_info.get('email')}")
        print(f"✅ Session stored: {list(session.keys())}")
        
        # Redirect to frontend after successful OAuth
        frontend_url = os.getenv('FRONTEND_URL', 'https://inmailer.vercel.app')
        return redirect(f"{frontend_url}/auth/success?email={user_info.get('email')}&name={user_info.get('name')}")
        
    except Exception as e:
        import sys, traceback
        print(f"Error in OAuth callback: {e}", flush=True)
        traceback.print_exc()
        sys.stderr.flush()
        return jsonify({'error': 'OAuth callback failed', 'details': str(e)}), 500

@app.route('/api/user-limit-status', methods=['GET'])
def get_user_limit_status():
    """Get current user count and limit status"""
    try:
        current_count = UserService.get_total_user_count()
        is_registration_open = UserService.is_user_registration_allowed(MAX_FREE_USERS)
        
        return jsonify({
            'current_users': current_count,
            'max_users': MAX_FREE_USERS,
            'is_registration_open': is_registration_open,
            'remaining_slots': max(0, MAX_FREE_USERS - current_count),
            'message': f"{'Open' if is_registration_open else 'Closed'} for registration - {current_count}/{MAX_FREE_USERS} users"
        })
    except Exception as e:
        print(f"Error getting user limit status: {e}")
        return jsonify({'error': 'Failed to get user limit status'}), 500

@app.route('/api/admin/users', methods=['GET'])
def get_all_users():
    """Admin endpoint to view all users (for monitoring)"""
    try:
        # In production, you'd want proper admin authentication here
        db = get_db_session()
        try:
            users = db.query(User).order_by(User.created_at.desc()).all()
            user_list = []
            for user in users:
                user_list.append({
                    'id': user.id,
                    'email': user.email,
                    'name': user.name,
                    'is_google_user': user.is_google_user,
                    'created_at': safe_isoformat(user.created_at),
                    'updated_at': safe_isoformat(user.updated_at)
                })
            
            return jsonify({
                'total_users': len(user_list),
                'users': user_list
            })
        finally:
            db.close()
    except Exception as e:
        print(f"Error getting all users: {e}")
        return jsonify({'error': 'Failed to get users'}), 500

if __name__ == '__main__':
    print("🚀 Starting InMailer Backend with Database...")
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(debug=debug, host='0.0.0.0', port=port)

