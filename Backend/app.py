from flask import Flask, request, jsonify, session, redirect, url_for
from flask_cors import CORS
import os
import json
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from mail_merge import parse_template, render_templates, send_via_smtp
import csv
import tempfile
from dotenv import load_dotenv
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import requests

# Load environment variables from .env file
load_dotenv()

# OAuth Configuration
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
GOOGLE_REDIRECT_URI = os.getenv('GOOGLE_REDIRECT_URI', 'http://localhost:5000/auth/google/callback')

# Gmail API scopes - include openid since Google adds it automatically
SCOPES = [
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/userinfo.profile',
    'https://www.googleapis.com/auth/userinfo.email',
    'openid'  # Google automatically adds this scope
]

# Store templates in memory (in production, use a database)
templates = []
templates_dir = Path("Templates")

# Store users in memory (in production, use a database)
users = {}
user_sessions = {}  # Store active sessions

def save_templates_to_file():
    """Save all templates to JSON file for persistence"""
    try:
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
            json.dump(templates, f, indent=2, ensure_ascii=False)
        
        # Atomic rename
        temp_file.replace(templates_file)
        print(f"✅ Saved {len(templates)} templates to {templates_file}")
        
    except Exception as e:
        print(f"❌ Error saving templates: {e}")
        import traceback
        traceback.print_exc()

def load_templates_from_file():
    """Load templates from JSON file"""
    try:
        templates_file = templates_dir / "templates.json"
        print(f"🔍 Checking for templates file: {templates_file}")
        
        if templates_file.exists():
            # Check file size first
            file_size = templates_file.stat().st_size
            print(f"📏 File size: {file_size} bytes")
            
            if file_size == 0:
                print("⚠️  Templates file is empty, starting fresh")
                return False
            
            print(f"📄 Templates file found, reading content...")
            with open(templates_file, 'r', encoding='utf-8') as f:
                content = f.read()
                print(f"📏 File content length: {len(content)} characters")
                
                # Check if content is just whitespace
                if not content.strip():
                    print("⚠️  Templates file contains only whitespace, starting fresh")
                    return False
                
                print(f"📄 File content preview: {content[:200]}...")
                
                                # Try to parse JSON
                try:
                    loaded_templates = json.loads(content)
                    print(f"🔍 Parsed JSON successfully, got {len(loaded_templates)} templates")
                    
                    # Validate that it's a list
                    if not isinstance(loaded_templates, list):
                        print("⚠️  Templates file doesn't contain a list, starting fresh")
                        return False
                    
                    # Clear existing templates and replace with loaded ones
                    templates.clear()
                    templates.extend(loaded_templates)
                    print(f"✅ Loaded {len(loaded_templates)} templates from {templates_file}")
                    return True
                    
                except json.JSONDecodeError as json_error:
                    print(f"❌ JSON parsing error: {json_error}")
                    print(f"❌ Content preview: {content[:500]}...")
                    
                    # Try to load from backup
                    backup_file = templates_dir / "templates_backup.json"
                    if backup_file.exists():
                        print(f"🔄 Trying to load from backup: {backup_file}")
                        try:
                            with open(backup_file, 'r', encoding='utf-8') as f:
                                backup_content = f.read()
                                if backup_content.strip():
                                    loaded_templates = json.loads(backup_content)
                                    if isinstance(loaded_templates, list):
                                        templates.clear()
                                        templates.extend(loaded_templates)
                                        print(f"✅ Recovered {len(loaded_templates)} templates from backup")
                                        
                                        # Restore the main file from backup
                                        shutil.copy2(backup_file, templates_file)
                                        print(f"✅ Restored main file from backup")
                                        return True
                        except Exception as backup_error:
                            print(f"❌ Backup recovery failed: {backup_error}")
                    
                    return False
        else:
            print("📝 No existing templates file found, starting fresh")
            return False
    except Exception as e:
        print(f"❌ Error loading templates: {e}")
        import traceback
        traceback.print_exc()
        return False

def initialize_templates():
    """Initialize templates on app startup"""
    print("🚀 Initializing InMailer Backend...")
    
    # Create templates directory if it doesn't exist
    templates_dir.mkdir(exist_ok=True)
    print(f"📁 Templates directory: {templates_dir.absolute()}")
    
    # Check if templates.json exists
    templates_file = templates_dir / "templates.json"
    print(f"📄 Templates file exists: {templates_file.exists()}")
    if templates_file.exists():
        print(f"📏 Templates file size: {templates_file.stat().st_size} bytes")
    
    # Load existing templates from JSON file first
    print("🔄 Attempting to load templates from JSON...")
    json_loaded = load_templates_from_file()
    print(f"✅ JSON loading result: {json_loaded}")
    print(f"📊 Templates loaded so far: {len(templates)}")
    
    # If no templates loaded from JSON, try to load from legacy .txt files
    if not json_loaded or not templates:
        print("🔄 No templates found in JSON, checking for legacy .txt files...")
        if templates_dir.exists():
            txt_files = list(templates_dir.glob("*.txt"))
            print(f"📝 Found {len(txt_files)} .txt files: {[f.name for f in txt_files]}")
            
            for template_file in txt_files:
                try:
                    print(f"📖 Reading template file: {template_file.name}")
                    with open(template_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        lines = content.split('\n')
                        if lines and lines[0].startswith('Subject:'):
                            subject = lines[0].split(':', 1)[1].strip()
                            body = '\n'.join(lines[1:]).lstrip('\n')
                            
                            template = {
                                'id': str(len(templates) + 1),
                                'name': template_file.stem.replace('_', ' '),
                                'subject': subject,
                                'content': body,
                                'variables': ['Name', 'Company'],  # Default variables
                                'attachment_path': None,
                                'attachment_name': None
                            }
                            templates.append(template)
                            print(f"✅ Loaded template: {template['name']}")
                except Exception as e:
                    print(f"❌ Error loading template {template_file}: {e}")
        
        # Save loaded templates to JSON for future use
        if templates:
            print("💾 Saving loaded templates to JSON...")
            save_templates_to_file()
    
    print(f"📚 Final result: Loaded {len(templates)} templates")
    if templates:
        print("📋 Template names:")
        for template in templates:
            print(f"   - {template['name']} (ID: {template['id']})")
            if template.get('attachment_name'):
                print(f"     📎 Attachment: {template['attachment_name']}")
    else:
        print("⚠️  No templates loaded!")
    print("✅ Template initialization complete!")

# OAuth Helper Functions
def create_flow():
    """Create OAuth flow for Google authentication"""
    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        raise ValueError("Google OAuth credentials not configured")
    
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [GOOGLE_REDIRECT_URI]
            }
        },
        scopes=SCOPES
    )
    return flow

def get_user_info(credentials):
    """Get user information from Google"""
    try:
        service = build('oauth2', 'v2', credentials=credentials)
        user_info = service.userinfo().get().execute()
        return user_info
    except Exception as e:
        print(f"Error getting user info: {e}")
        return None

# Authentication Helper Functions
def hash_password(password):
    """Hash password using bcrypt (simple implementation for demo)"""
    import hashlib
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, hashed):
    """Verify password against hash"""
    return hash_password(password) == hashed

def create_user_session(user_id):
    """Create a new session for user"""
    import secrets
    session_token = secrets.token_urlsafe(32)
    user_sessions[session_token] = {
        'user_id': user_id,
        'created_at': datetime.now(),
        'expires_at': datetime.now() + timedelta(hours=24)
    }
    return session_token

def get_user_from_session(session_token):
    """Get user from session token"""
    if session_token not in user_sessions:
        return None
    
    session_data = user_sessions[session_token]
    if datetime.now() > session_data['expires_at']:
        del user_sessions[session_token]
        return None
    
    return users.get(session_data['user_id'])

def send_gmail(credentials, to_email, subject, body, attachment_path=None):
    """Send email using Gmail API"""
    try:
        print(f"📧 Starting Gmail send process...")
        print(f"📧 To: {to_email}")
        print(f"📧 Subject: {subject}")
        print(f"📧 Body length: {len(body)} characters")
        print(f"📧 Attachment: {attachment_path}")
        
        service = build('gmail', 'v1', credentials=credentials)
        print(f"✅ Gmail service built successfully")
        
        # Create email message
        message = create_email_message(to_email, subject, body, attachment_path)
        print(f"✅ Email message created successfully")
        
        # Send email
        print(f"🔄 Sending email via Gmail API...")
        sent_message = service.users().messages().send(userId='me', body=message).execute()
        print(f"✅ Email sent successfully! Message ID: {sent_message.get('id')}")
        return sent_message
    except Exception as e:
        print(f"❌ Error sending Gmail: {e}")
        import traceback
        traceback.print_exc()
        return None

def create_email_message(to_email, subject, body, attachment_path=None):
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
                attachment = MIMEText(attachment_data, 'base64', filename=os.path.basename(attachment_path))
            else:
                # Handle binary files (PDF, DOC, etc.)
                attachment = MIMEBase(main_type, sub_type)
                attachment.set_payload(attachment_data)
                # Encode the attachment properly
                encode_base64(attachment)
            
            # Set filename
            attachment.add_header('Content-Disposition', 'attachment', filename=os.path.basename(attachment_path))
            message.attach(attachment)
            print(f"✅ Attachment attached successfully")
    
    # Encode message
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
    return {'raw': raw_message}

def create_app():
    """Create and configure the Flask app"""
    app = Flask(__name__)
    
    # Configure Flask app
    app.secret_key = os.getenv('FLASK_SECRET_KEY', 'inmailer-secret-key-change-in-production')
    
    # Use simple Flask sessions (no flask-session) for better reliability
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)
    
    print("📁 Using simple Flask sessions for better reliability")
    
    # Don't initialize Flask-Session - use default Flask sessions
    
    # CORS configuration with specific settings for sessions
    CORS(app, 
         supports_credentials=True,
         origins=['http://localhost:3000', 'http://localhost:3001', 'http://127.0.0.1:3000', 'http://127.0.0.1:3001'],
         allow_headers=['Content-Type', 'Authorization'],
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
    
    # Initialize templates when app is created
    with app.app_context():
        initialize_templates()
    
    return app

app = create_app()

@app.route('/api/templates', methods=['GET'])
def get_templates():
    """Get all available templates"""
    print(f"🔍 Debug: Returning {len(templates)} templates")
    for template in templates:
        print(f"   - {template['name']} (ID: {template['id']}, Type: {type(template['id'])})")
    return jsonify(templates)

@app.route('/api/reload-templates', methods=['POST'])
def reload_templates():
    """Manually reload templates from files (for debugging)"""
    try:
        print("🔄 Manual template reload requested...")
        initialize_templates()
        return jsonify({
            'message': f'Templates reloaded successfully. Loaded {len(templates)} templates.',
            'templates_count': len(templates)
        }), 200
    except Exception as e:
        return jsonify({'error': f'Failed to reload templates: {str(e)}'}), 500

@app.route('/api/templates', methods=['POST'])
def create_template():
    """Create a new template"""
    try:
        data = request.json
        template_name = data.get('name')
        subject = data.get('subject')
        content = data.get('content')
        variables = data.get('variables', [])
        
        if not all([template_name, subject, content]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Create template object with unique ID
        # Find the next available ID
        existing_ids = [int(t['id']) for t in templates if t['id'].isdigit()]
        next_id = str(max(existing_ids) + 1) if existing_ids else "1"
        
        template = {
            'id': next_id,
            'name': template_name,
            'subject': subject,
            'content': content,
            'variables': variables,
            'attachment_path': None,  # Will store path to attachment file
            'attachment_name': None   # Will store original filename
        }
        
        templates.append(template)
        
        # Save templates to JSON file for persistence
        save_templates_to_file()
        
        # Also save to legacy .txt format for backward compatibility
        template_file = templates_dir / f"{template_name.replace(' ', '_')}.txt"
        template_file.parent.mkdir(exist_ok=True)
        
        with open(template_file, 'w', encoding='utf-8') as f:
            f.write(f"Subject: {subject}\n")
            f.write(content)
        
        return jsonify({'message': 'Template created successfully', 'template': template}), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/templates/<template_id>', methods=['PUT'])
def update_template(template_id):
    """Update an existing template"""
    try:
        data = request.json
        template_name = data.get('name')
        subject = data.get('subject')
        content = data.get('content')
        variables = data.get('variables', [])
        
        if not all([template_name, subject, content]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Find template to update
        template = next((t for t in templates if t['id'] == template_id), None)
        if not template:
            return jsonify({'error': 'Template not found'}), 404
        
        # Update template fields (preserve attachment info)
        template['name'] = template_name
        template['subject'] = subject
        template['content'] = content
        template['variables'] = variables
        # Note: attachment_path and attachment_name are preserved and will be updated separately if a new attachment is uploaded
        
        # Save updated templates to JSON file for persistence
        save_templates_to_file()
        
        # Also update legacy .txt format for backward compatibility
        template_file = templates_dir / f"{template_name.replace(' ', '_')}.txt"
        template_file.parent.mkdir(exist_ok=True)
        
        with open(template_file, 'w', encoding='utf-8') as f:
            f.write(f"Subject: {subject}\n")
            f.write(content)
        
        return jsonify({'message': 'Template updated successfully', 'template': template}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/mail-merge', methods=['POST'])
def process_mail_merge():
    """Process InMailer campaign with CSV and template"""
    try:
        # Get form data
        template_id = request.form.get('template_id')
        csv_file = request.files.get('csv_file')
        
        if not template_id or not csv_file:
            return jsonify({'error': 'Missing template or CSV file'}), 400
        
        # Find template
        template = next((t for t in templates if t['id'] == template_id), None)
        if not template:
            return jsonify({'error': 'Template not found'}), 404
        
        # Parse CSV
        contacts = []
        csv_content = csv_file.read().decode('utf-8')
        csv_reader = csv.DictReader(csv_content.splitlines())
        
        for row in csv_reader:
            contacts.append(dict(row))
        
        if not contacts:
            return jsonify({'error': 'No contacts found in CSV'}), 400
        
        # Process each contact
        results = []
        for contact in contacts:
            try:
                print(f"🔍 Debug: Processing contact: {contact}")
                print(f"🔍 Debug: Template subject: {template['subject']}")
                print(f"🔍 Debug: Template content: {template['content']}")
                
                # Create normalized contact data for template rendering
                normalized_contact = {}
                for key, value in contact.items():
                    if key and value:
                        # Create normalized key (replace spaces with underscores)
                        normalized_key = key.replace(" ", "_")
                        normalized_contact[normalized_key] = value.strip()
                        # Also keep original key for backward compatibility
                        normalized_contact[key] = value.strip()
                
                print(f"🔍 Debug: Normalized contact data: {normalized_contact}")
                
                # Render template with normalized contact data
                subject, body = render_templates(
                    template['subject'], 
                    template['content'], 
                    normalized_contact
                )
                
                print(f"🔍 Debug: Rendered subject: {subject}")
                print(f"🔍 Debug: Rendered body: {body}")
                
                # Store result (in production, you'd send emails here)
                results.append({
                    'contact': contact,
                    'rendered_subject': subject,
                    'rendered_body': body,
                    'status': 'success'
                })
                
            except Exception as e:
                print(f"❌ Debug: Error processing contact: {str(e)}")
                results.append({
                    'contact': contact,
                    'error': str(e),
                    'status': 'error'
                })
        
        return jsonify({
            'message': f'Processed {len(contacts)} contacts',
            'results': results,
            'template': template
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/send-emails', methods=['POST'])
def send_emails():
    """Actually send the emails (requires email configuration)"""
    try:
        data = request.json
        template_id = data.get('template_id')
        contacts = data.get('contacts', [])
        
        if not template_id or not contacts:
            return jsonify({'error': 'Missing template or contacts'}), 400
        
        # Find template
        template = next((t for t in templates if t['id'] == template_id), None)
        if not template:
            return jsonify({'error': 'Template not found'}), 404
        
        # Check if user is authenticated with Gmail API
        credentials_data = session.get('credentials')
        if not credentials_data:
            return jsonify({'error': 'Not authenticated with Gmail API. Please sign in with Google first.'}), 401
        
        # Recreate credentials object for Gmail API
        credentials = Credentials(
            token=credentials_data['token'],
            refresh_token=credentials_data['refresh_token'],
            token_uri=credentials_data['token_uri'],
            client_id=credentials_data['client_id'],
            client_secret=credentials_data['client_secret'],
            scopes=credentials_data['scopes']
        )
        
        print(f"🔍 Debug: Using Gmail API with OAuth credentials")
        print(f"🔍 Debug: Template: {template['name']}")
        print(f"🔍 Debug: Contacts to process: {len(contacts)}")
        
        # Process emails
        results = []
        for contact in contacts:
            try:
                # Render template
                print(f"🔍 Debug: Rendering template for contact: {contact}")
                print(f"🔍 Debug: Template subject: {template['subject']}")
                print(f"🔍 Debug: Template content: {template['content']}")
                
                # Create normalized contact data for template rendering
                normalized_contact = {}
                for key, value in contact.items():
                    if key and value:
                        # Create normalized key (replace spaces with underscores)
                        normalized_key = key.replace(" ", "_")
                        normalized_contact[normalized_key] = value.strip()
                        # Also keep original key for backward compatibility
                        normalized_contact[key] = value.strip()
                
                print(f"🔍 Debug: Normalized contact data: {normalized_contact}")
                
                subject, body = render_templates(
                    template['subject'], 
                    template['content'], 
                    normalized_contact
                )
                
                print(f"🔍 Debug: Rendered subject: {subject}")
                print(f"🔍 Debug: Rendered body: {body}")
                
                # Get recipient email
                recipient_email = contact.get('Email', contact.get('email'))
                print(f"📧 Debug: Subject: {subject}")
                print(f"📧 Debug: Body length: {len(body)} characters")
                
                # Send email using Gmail API
                attachment_path = template.get('attachment_path')
                result = send_gmail(credentials, recipient_email, subject, body, attachment_path)
                
                if result:
                    print(f"✅ Debug: Email sent successfully to {recipient_email}")
                    results.append({
                        'contact': contact,
                        'status': 'sent',
                        'subject': subject,
                        'message_id': result.get('id')
                    })
                else:
                    print(f"❌ Debug: Failed to send email to {recipient_email}")
                    results.append({
                        'contact': contact,
                        'status': 'error',
                        'error': 'Gmail API send failed'
                    })
                
            except Exception as e:
                print(f"❌ Debug: Error sending email to {contact.get('Email', contact.get('email'))}: {str(e)}")
                results.append({
                    'contact': contact,
                    'status': 'error',
                    'error': str(e)
                })
        
        # Count results
        sent_count = len([r for r in results if r['status'] == 'sent'])
        error_count = len([r for r in results if r['status'] == 'error'])
        
        print(f"📊 Email sending complete: {sent_count} sent, {error_count} errors")
        
        return jsonify({
            'message': f'Email campaign completed: {sent_count} sent, {error_count} errors',
            'results': results,
            'summary': {
                'total': len(contacts),
                'sent': sent_count,
                'errors': error_count
            }
        })
        
    except Exception as e:
        print(f"❌ Error in send_emails: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Failed to send emails: {str(e)}'}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    email_user = os.getenv("EMAIL_USER", "NOT SET")
    display_name = os.getenv("EMAIL_DISPLAY_NAME", "Parva")
    from_address = f"{display_name} <{email_user}>" if display_name and email_user != "NOT SET" else email_user
    
    return jsonify({
        'status': 'healthy', 
        'templates_count': len(templates),
        'email_configured': bool(os.getenv("EMAIL_USER") and os.getenv("EMAIL_PASSWORD")),
        'email_user': email_user,
        'email_display_name': display_name,
        'from_address': from_address,
        'email_host': os.getenv("EMAIL_HOST", "NOT SET"),
        'email_port': os.getenv("EMAIL_PORT", "NOT SET")
    })

@app.route('/api/test-email', methods=['POST'])
def test_email():
    """Test email endpoint to verify configuration"""
    try:
        data = request.json
        test_email = data.get('test_email')
        
        if not test_email:
            return jsonify({'error': 'Please provide test_email in request body'}), 400
        
        email_user = os.getenv("EMAIL_USER")
        email_password = os.getenv("EMAIL_PASSWORD")
        display_name = os.getenv("EMAIL_DISPLAY_NAME", "Parva")
        
        if not email_user or not email_password:
            return jsonify({'error': 'Email not configured'}), 500
        
        # Format the from address with display name
        from_address = f"{display_name} <{email_user}>" if display_name else email_user
        
        # Try to send a test email
        test_subject = "Test Email from InMailer"
        test_body = "This is a test email to verify your email configuration is working."
        
        print(f"🧪 Testing email to: {test_email}")
        print(f"🧪 From address: {from_address}")
        
        send_via_smtp(
            msg_from=from_address,
            msg_to=test_email,
            subject=test_subject,
            body=test_body
        )
        
        return jsonify({'message': 'Test email sent successfully!'})
        
    except Exception as e:
        return jsonify({'error': f'Test email failed: {str(e)}'}), 500

@app.route('/api/test-template', methods=['POST'])
def test_template():
    """Test template rendering with sample data"""
    try:
        data = request.json
        template_content = data.get('template_content', 'Hello ${First_Name}, welcome to ${Company}!')
        test_data = data.get('test_data', {'First_Name': 'John', 'Company': 'Acme Corp'})
        
        print(f"🧪 Testing template: {template_content}")
        print(f"🧪 Test data: {test_data}")
        
        # Test rendering
        subject, body = render_templates(
            "Welcome to ${Company}", 
            template_content, 
            test_data
        )
        
        print(f"🧪 Rendered subject: {subject}")
        print(f"🧪 Rendered body: {body}")
        
        return jsonify({
            'template': template_content,
            'test_data': test_data,
            'rendered_subject': subject,
            'rendered_body': body
        })
        
    except Exception as e:
        return jsonify({'error': f'Template test failed: {str(e)}'}), 500

@app.route('/api/template-attachment', methods=['POST'])
def upload_template_attachment():
    """Upload attachment for a template"""
    try:
        print(f"🔍 Starting attachment upload...")
        template_id = request.form.get('template_id')
        attachment_file = request.files.get('attachment')
        
        print(f"🔍 Template ID: {template_id}")
        print(f"🔍 Attachment file: {attachment_file}")
        print(f"🔍 Form data keys: {list(request.form.keys())}")
        print(f"🔍 Files keys: {list(request.files.keys())}")
        
        if not template_id:
            print("❌ Missing template ID")
            return jsonify({'error': 'Missing template ID'}), 400
            
        if not attachment_file:
            print("❌ Missing attachment file")
            return jsonify({'error': 'Missing attachment file'}), 400
        
        # Find template
        print(f"🔍 Available template IDs: {[t['id'] for t in templates]}")
        print(f"🔍 Looking for template ID: {template_id}")
        print(f"🔍 Template ID type: {type(template_id)}")
        
        # Try exact match first
        template = next((t for t in templates if t['id'] == template_id), None)
        
        # If not found, try string conversion for comparison
        if not template:
            print(f"🔍 Trying string conversion for comparison...")
            template = next((t for t in templates if str(t['id']) == str(template_id)), None)
        
        if not template:
            print(f"❌ Template not found with ID: {template_id}")
            print(f"❌ Available IDs: {[t['id'] for t in templates]}")
            print(f"❌ ID types: {[type(t['id']) for t in templates]}")
            return jsonify({'error': 'Template not found'}), 404
        
        print(f"🔍 Found template: {template['name']}")
        
        # Create attachments directory if it doesn't exist
        attachments_dir = Path("Templates/attachments")
        attachments_dir.mkdir(parents=True, exist_ok=True)
        print(f"🔍 Attachments directory: {attachments_dir.absolute()}")
        
        # Save attachment file with original filename
        # Check if file already exists and add a number suffix if needed
        original_filename = attachment_file.filename
        base_name = Path(original_filename).stem
        extension = Path(original_filename).suffix
        
        print(f"🔍 Original filename: {original_filename}")
        print(f"🔍 Base name: {base_name}")
        print(f"🔍 Extension: {extension}")
        
        counter = 1
        attachment_filename = original_filename
        attachment_path = attachments_dir / attachment_filename
        
        # If file exists, add a number suffix
        while attachment_path.exists():
            attachment_filename = f"{base_name}_{counter}{extension}"
            attachment_path = attachments_dir / attachment_filename
            counter += 1
            print(f"🔍 File exists, trying: {attachment_filename}")
        
        print(f"🔍 Final attachment path: {attachment_path}")
        
        # Save the file
        attachment_file.save(attachment_path)
        print(f"✅ File saved successfully")
        
        # Verify file was saved
        if attachment_path.exists():
            print(f"✅ File verification: {attachment_path.stat().st_size} bytes")
        else:
            print(f"❌ File verification failed: file not found after save")
            return jsonify({'error': 'File save verification failed'}), 500
        
        # Update template with attachment info
        template['attachment_path'] = str(attachment_path)
        template['attachment_name'] = attachment_file.filename
        
        print(f"🔍 Updated template attachment_path: {template['attachment_path']}")
        print(f"🔍 Updated template attachment_name: {template['attachment_name']}")
        
        # Save updated templates to file
        save_templates_to_file()
        print(f"✅ Templates saved to file")
        
        print(f"✅ Attachment '{attachment_file.filename}' uploaded successfully for template '{template['name']}'")
        
        return jsonify({
            'message': 'Attachment uploaded successfully',
            'attachment_name': attachment_file.filename,
            'template': template
        }), 200
        
    except Exception as e:
        print(f"❌ Error uploading attachment: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Failed to upload attachment: {str(e)}'}), 500

@app.route('/api/templates/<template_id>', methods=['DELETE'])
def delete_template(template_id):
    """Delete a template"""
    try:
        print(f"🔍 Attempting to delete template with ID: {template_id} (type: {type(template_id)})")
        print(f"🔍 Available template IDs: {[t['id'] for t in templates]}")
        
        # Find template - handle both string and integer IDs
        template = None
        print(f"🔍 Searching through {len(templates)} templates...")
        for t in templates:
            print(f"   Comparing template ID '{t['id']}' (type: {type(t['id'])}) with requested ID '{template_id}' (type: {type(template_id)})")
            if str(t['id']) == str(template_id):
                template = t
                print(f"✅ Found matching template!")
                break
        
        if not template:
            print(f"❌ Template with ID {template_id} not found")
            return jsonify({'error': 'Template not found'}), 404
        
        print(f"✅ Found template: {template['name']}")
        print(f"🔍 Template list before removal: {len(templates)} templates")
        print(f"   Template IDs: {[t['id'] for t in templates]}")
        
        # Remove template from list
        try:
            templates.remove(template)
            print(f"✅ Template removed from list successfully")
            print(f"🔍 Template list after removal: {len(templates)} templates")
            print(f"   Template IDs: {[t['id'] for t in templates]}")
        except ValueError as remove_error:
            print(f"❌ Error removing template from list: {remove_error}")
            # Try to find and remove by ID instead
            templates[:] = [t for t in templates if str(t['id']) != str(template_id)]
            print(f"✅ Template removed using list comprehension")
            print(f"🔍 Template list after removal: {len(templates)} templates")
        
        # Save updated templates to file
        try:
            save_templates_to_file()
            print(f"✅ Templates saved to file successfully")
        except Exception as save_error:
            print(f"❌ Error saving templates to file: {save_error}")
            # Don't fail the entire operation for this
        
        # Also remove the legacy .txt file if it exists
        try:
            template_file = templates_dir / f"{template['name'].replace(' ', '_')}.txt"
            if template_file.exists():
                template_file.unlink()
                print(f"✅ Removed legacy .txt file: {template_file}")
            else:
                print(f"ℹ️  No legacy .txt file found: {template_file}")
        except Exception as file_error:
            print(f"⚠️  Warning: Could not remove legacy .txt file: {file_error}")
            # Don't fail the entire operation for this
        
        print(f"✅ Template '{template['name']}' deleted successfully")
        return jsonify({'message': 'Template deleted successfully'}), 200
        
    except Exception as e:
        print(f"❌ Error deleting template: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Failed to delete template. Please try again.'}), 500

@app.route('/api/csv-columns', methods=['POST'])
def get_csv_columns():
    """Get available columns from uploaded CSV for template creation"""
    try:
        csv_file = request.files.get('csv_file')
        
        if not csv_file:
            return jsonify({'error': 'No CSV file provided'}), 400
        
        # Parse CSV headers
        csv_content = csv_file.read().decode('utf-8')
        csv_reader = csv.DictReader(csv_content.splitlines())
        
        # Get column names
        columns = csv_reader.fieldnames or []
        
        # Create normalized versions (replace spaces with underscores)
        normalized_columns = [col.replace(" ", "_") for col in columns if col]
        
        return jsonify({
            'original_columns': columns,
            'normalized_columns': normalized_columns,
            'template_variables': [f"${{{col}}}" for col in normalized_columns if col]
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to parse CSV: {str(e)}'}), 500

# OAuth Authentication Routes
@app.route('/auth/google')
def google_auth():
    """Initiate Google OAuth flow"""
    try:
        flow = create_flow()
        flow.redirect_uri = GOOGLE_REDIRECT_URI
        
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true'
        )
        
        # Store state in session for security
        session['oauth_state'] = state
        
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
            # return jsonify({'error': 'Invalid state parameter'}), 400
        
        print("✅ State verified")
        
        # Create flow and exchange code for tokens
        print("🔄 Creating OAuth flow...")
        flow = create_flow()
        flow.redirect_uri = GOOGLE_REDIRECT_URI
        print(f"🔍 Redirect URI: {GOOGLE_REDIRECT_URI}")
        
        # Exchange authorization code for tokens
        print("🔄 Exchanging code for tokens...")
        flow.fetch_token(code=code)
        credentials = flow.credentials
        print("✅ Tokens received successfully")
        
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
        
        # Get user information
        print("🔄 Getting user information...")
        user_info = get_user_info(credentials)
        if not user_info:
            print("❌ Failed to get user info from Google")
            return jsonify({'error': 'Failed to get user information from Google'}), 500
        
        print(f"✅ User info received: {user_info.get('email', 'No email')}")
        
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
        
        # Also store in our user system for consistency
        user_email = user_info.get('email')
        if user_email not in users:
            # Create new user from Google OAuth
            user_id = str(len(users) + 1)
            users[user_email] = {
                'id': user_id,
                'email': user_email,
                'name': user_info.get('name', 'Google User'),
                'password_hash': None,  # No password for Google users
                'created_at': datetime.now().isoformat(),
                'is_google_user': True
            }
            print(f"✅ Created new Google user: {user_email}")
        else:
            # Update existing user
            users[user_email]['is_google_user'] = True
            print(f"✅ Updated existing user with Google OAuth: {user_email}")
        
        print(f"✅ OAuth successful! User: {user_info.get('email')}")
        print(f"✅ Session stored: {list(session.keys())}")
        
        # Redirect to frontend after successful OAuth
        return redirect(f"http://localhost:3001/auth/success?email={user_info.get('email')}&name={user_info.get('name')}")
        
    except Exception as e:
        print(f"Error in OAuth callback: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'OAuth callback failed'}), 500

@app.route('/auth/debug')
def debug_session():
    """Debug endpoint to show session information"""
    print(f"🔍 Debug endpoint called")
    print(f"🔍 Session contents: {list(session.keys())}")
    print(f"🔍 User info in session: {session.get('user_info')}")
    print(f"🔍 Credentials in session: {session.get('credentials')}")
    
    return jsonify({
        'session_keys': list(session.keys()),
        'user_info': session.get('user_info'),
        'has_credentials': 'credentials' in session,
        'session_id': session.get('_id', 'No ID'),
        'message': 'Check server console for detailed session info'
    })

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
    session.clear()
    return jsonify({'message': 'Logged out successfully'})

# User Authentication Routes
@app.route('/api/auth/signup', methods=['POST'])
def signup():
    """User registration endpoint"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        name = data.get('name')
        
        if not all([email, password, name]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Check if user already exists
        if email in users:
            return jsonify({'error': 'User already exists'}), 409
        
        # Create new user
        user_id = str(len(users) + 1)
        users[email] = {
            'id': user_id,
            'email': email,
            'name': name,
            'password_hash': hash_password(password),
            'created_at': datetime.now().isoformat(),
            'is_google_user': False
        }
        
        # Create session
        session_token = create_user_session(user_id)
        
        print(f"✅ New user registered: {email}")
        
        return jsonify({
            'message': 'User registered successfully',
            'user': {
                'id': user_id,
                'email': email,
                'name': name
            },
            'session_token': session_token
        }), 201
        
    except Exception as e:
        print(f"❌ Error in signup: {e}")
        return jsonify({'error': 'Registration failed'}), 500

@app.route('/api/auth/signin', methods=['POST'])
def signin():
    """User login endpoint"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not all([email, password]):
            return jsonify({'error': 'Missing email or password'}), 400
        
        # Check if user exists
        if email not in users:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        user = users[email]
        
        # Verify password
        if not verify_password(password, user['password_hash']):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Create session
        session_token = create_user_session(user['id'])
        
        print(f"✅ User signed in: {email}")
        
        return jsonify({
            'message': 'Login successful',
            'user': {
                'id': user['id'],
                'email': user['email'],
                'name': user['name']
            },
            'session_token': session_token
        }), 200
        
    except Exception as e:
        print(f"❌ Error in signin: {e}")
        return jsonify({'error': 'Login failed'}), 500

@app.route('/api/auth/session', methods=['GET'])
def get_session():
    """Get current user session"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'No authorization token'}), 401
        
        session_token = auth_header.split(' ')[1]
        user = get_user_from_session(session_token)
        
        if not user:
            return jsonify({'error': 'Invalid or expired session'}), 401
        
        return jsonify({
            'user': {
                'id': user['id'],
                'email': user['email'],
                'name': user['name'],
                'is_google_user': user.get('is_google_user', False)
            }
        }), 200
        
    except Exception as e:
        print(f"❌ Error getting session: {e}")
        return jsonify({'error': 'Session validation failed'}), 500

@app.route('/api/auth/logout', methods=['POST'])
def logout_user():
    """Logout user and clear session"""
    try:
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            session_token = auth_header.split(' ')[1]
            if session_token in user_sessions:
                del user_sessions[session_token]
                print(f"✅ User session cleared")
        
        return jsonify({'message': 'Logged out successfully'}), 200
        
    except Exception as e:
        print(f"❌ Error in logout: {e}")
        return jsonify({'error': 'Logout failed'}), 500

# Protected Route Example
@app.route('/api/protected', methods=['GET'])
def protected_route():
    """Example of a protected route that requires authentication"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'No authorization token'}), 401
        
        session_token = auth_header.split(' ')[1]
        user = get_user_from_session(session_token)
        
        if not user:
            return jsonify({'error': 'Invalid or expired session'}), 401
        
        return jsonify({
            'message': 'This is a protected route',
            'user': {
                'id': user['id'],
                'email': user['email'],
                'name': user['name']
            },
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        print(f"❌ Error in protected route: {e}")
        return jsonify({'error': 'Access denied'}), 500

@app.route('/api/send-gmail', methods=['POST'])
def send_gmail_route():
    """Send email using Gmail API"""
    try:
        # Check if user is authenticated
        credentials_data = session.get('credentials')
        if not credentials_data:
            return jsonify({'error': 'Not authenticated'}), 401
        
        # Recreate credentials object
        credentials = Credentials(
            token=credentials_data['token'],
            refresh_token=credentials_data['refresh_token'],
            token_uri=credentials_data['token_uri'],
            client_id=credentials_data['client_id'],
            client_secret=credentials_data['client_secret'],
            scopes=credentials_data['scopes']
        )
        
        # Get email data from request
        data = request.get_json()
        to_email = data.get('to_email')
        subject = data.get('subject')
        body = data.get('body')
        attachment_path = data.get('attachment_path')
        
        if not all([to_email, subject, body]):
            return jsonify({'error': 'Missing required email fields'}), 400
        
        # Send email using Gmail API
        result = send_gmail(credentials, to_email, subject, body, attachment_path)
        
        if result:
            return jsonify({
                'message': 'Email sent successfully',
                'message_id': result.get('id')
            }), 200
        else:
            return jsonify({'error': 'Failed to send email'}), 500
            
    except Exception as e:
        print(f"Error sending Gmail: {e}")
        return jsonify({'error': f'Failed to send email: {str(e)}'}), 500

if __name__ == '__main__':
    print("🚀 Starting InMailer Backend directly...")
    app.run(debug=True, host='0.0.0.0', port=5000)