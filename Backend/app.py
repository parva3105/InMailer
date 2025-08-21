from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
from pathlib import Path
from mail_merge import parse_template, render_templates, send_via_smtp
import csv
import tempfile
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# Store templates in memory (in production, use a database)
templates = []
templates_dir = Path("Templates")

@app.route('/api/templates', methods=['GET'])
def get_templates():
    """Get all available templates"""
    return jsonify(templates)

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
        
        # Create template object
        template = {
            'id': str(len(templates) + 1),
            'name': template_name,
            'subject': subject,
            'content': content,
            'variables': variables,
            'attachment_path': None,  # Will store path to attachment file
            'attachment_name': None   # Will store original filename
        }
        
        templates.append(template)
        
        # Save to file system (optional)
        template_file = templates_dir / f"{template_name.replace(' ', '_')}.txt"
        template_file.parent.mkdir(exist_ok=True)
        
        with open(template_file, 'w', encoding='utf-8') as f:
            f.write(f"Subject: {subject}\n")
            f.write(content)
        
        return jsonify({'message': 'Template created successfully', 'template': template}), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/mail-merge', methods=['POST'])
def process_mail_merge():
    """Process mail merge with CSV and template"""
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
        test_subject = "Test Email from Mail Merge Kit"
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
        template_id = request.form.get('template_id')
        attachment_file = request.files.get('attachment')
        
        if not template_id or not attachment_file:
            return jsonify({'error': 'Missing template ID or attachment file'}), 400
        
        # Find template
        template = next((t for t in templates if t['id'] == template_id), None)
        if not template:
            return jsonify({'error': 'Template not found'}), 404
        
        # Create attachments directory if it doesn't exist
        attachments_dir = Path("Templates/attachments")
        attachments_dir.mkdir(parents=True, exist_ok=True)
        
        # Save attachment file with original filename
        # Check if file already exists and add a number suffix if needed
        original_filename = attachment_file.filename
        base_name = Path(original_filename).stem
        extension = Path(original_filename).suffix
        
        counter = 1
        attachment_filename = original_filename
        attachment_path = attachments_dir / attachment_filename
        
        # If file exists, add a number suffix
        while attachment_path.exists():
            attachment_filename = f"{base_name}_{counter}{extension}"
            attachment_path = attachments_dir / attachment_filename
            counter += 1
        
        attachment_file.save(attachment_path)
        
        # Update template with attachment info
        template['attachment_path'] = str(attachment_path)
        template['attachment_name'] = attachment_file.filename
        
        return jsonify({
            'message': 'Attachment uploaded successfully',
            'attachment_name': attachment_file.filename,
            'template': template
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to upload attachment: {str(e)}'}), 500

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
    # Create templates directory if it doesn't exist
    templates_dir.mkdir(exist_ok=True)
    
    # Load existing templates from files
    if templates_dir.exists():
        for template_file in templates_dir.glob("*.txt"):
            try:
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
            except Exception as e:
                print(f"Error loading template {template_file}: {e}")
    
    print(f"Loaded {len(templates)} templates")
    print("Starting Flask server on http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
