from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
import shutil
from pathlib import Path
from mail_merge import parse_template, render_templates, send_via_smtp
import csv
import tempfile
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Store templates in memory (in production, use a database)
templates = []
templates_dir = Path("Templates")

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

def create_app():
    """Create and configure the Flask app"""
    app = Flask(__name__)
    CORS(app)  # Enable CORS for frontend communication
    
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
        print(f"   - {template['name']} (ID: {template['id']})")
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
        
        # Check if email is configured - use same method as mail_merge.py
        email_user = os.getenv("EMAIL_USER")
        email_password = os.getenv("EMAIL_PASSWORD")
        email_host = os.getenv("EMAIL_HOST", "smtp.gmail.com")
        email_port = int(os.getenv("EMAIL_PORT", "587"))
        display_name = os.getenv("EMAIL_DISPLAY_NAME", "Parva")  # Default to "Parva"
        
        # Format the from address with display name
        from_address = f"{display_name} <{email_user}>" if display_name else email_user
        
        print(f"🔍 Debug: EMAIL_USER = {email_user}")
        print(f"🔍 Debug: EMAIL_PASSWORD = {'*' * len(email_password) if email_password else 'NOT SET'}")
        print(f"🔍 Debug: EMAIL_HOST = {email_host}")
        print(f"🔍 Debug: EMAIL_PORT = {email_port}")
        print(f"🔍 Debug: DISPLAY_NAME = {display_name}")
        print(f"🔍 Debug: FROM_ADDRESS = {from_address}")
        
        if not email_user or not email_password:
            return jsonify({
                'error': 'Email not configured. Please set EMAIL_USER and EMAIL_PASSWORD environment variables.'
            }), 500
        
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
                
                # Send email using your working email system
                attachment_path = template.get('attachment_path')
                send_via_smtp(
                    msg_from=from_address,
                    msg_to=recipient_email,
                    subject=subject,
                    body=body,
                    attachment_path=attachment_path
                )
                
                print(f"✅ Debug: Email sent successfully to {recipient_email}")
                
                results.append({
                    'contact': contact,
                    'status': 'sent',
                    'subject': subject
                })
                
            except Exception as e:
                print(f"❌ Debug: Error sending email to {contact.get('Email', contact.get('email'))}: {str(e)}")
                results.append({
                    'contact': contact,
                    'status': 'error',
                    'error': str(e)
                })
        
        return jsonify({
            'message': f'Processed {len(contacts)} emails',
            'results': results
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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
        # Find template
        template = next((t for t in templates if t['id'] == template_id), None)
        if not template:
            return jsonify({'error': 'Template not found'}), 404
        
        # Remove template from list
        templates.remove(template)
        
        # Save updated templates to file
        save_templates_to_file()
        
        # Also remove the legacy .txt file if it exists
        template_file = templates_dir / f"{template['name'].replace(' ', '_')}.txt"
        if template_file.exists():
            template_file.unlink()
        
        return jsonify({'message': 'Template deleted successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to delete template: {str(e)}'}), 500

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

if __name__ == '__main__':
    print("🚀 Starting InMailer Backend directly...")
    app.run(debug=True, host='0.0.0.0', port=5000)
