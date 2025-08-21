#!/usr/bin/env python3
import os
import csv
import time
import ssl
import argparse
from pathlib import Path
from string import Template
from typing import Dict, Tuple, Optional
from dotenv import load_dotenv
load_dotenv()

# --- SMTP imports ---
import smtplib
from email.message import EmailMessage

# --- SendGrid (optional) ---
try:
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail
    HAS_SENDGRID = True
except Exception:
    HAS_SENDGRID = False

# --- Custom modules ---
from email_logger import EmailLogger
from duplicate_tracker import DuplicateTracker
from contact_processor import ContactProcessor

DEFAULT_RATE_LIMIT_SECONDS = float(os.getenv("RATE_LIMIT_SECONDS", "2.0"))

def parse_template(path: Path) -> Tuple[str, str]:
    """
    Template file format:
    First line must start with 'Subject: ' then the subject template.
    The rest of the file is the email body template.
    Placeholders use ${first_name}, ${company}, etc. (string.Template)
    """
    raw = path.read_text(encoding="utf-8")
    lines = raw.splitlines()
    if not lines or not lines[0].lower().startswith("subject:"):
        raise ValueError("Template must start with a line like 'Subject: Your subject here'")
    subject_tmpl = lines[0].split(":", 1)[1].strip()
    body_tmpl = "\n".join(lines[1:]).lstrip("\n")
    return subject_tmpl, body_tmpl

def render_templates(subject_tmpl: str, body_tmpl: str, row: Dict[str, str]) -> Tuple[str, str]:
    # Create a safe row with normalized keys (replace spaces with underscores)
    safe_row = {}
    for k, v in row.items():
        if k and v:
            # Normalize key names by replacing spaces with underscores
            normalized_key = k.replace(" ", "_")
            safe_row[normalized_key] = v.strip()
            # Also keep the original key for backward compatibility
            safe_row[k] = v.strip()
    
    return Template(subject_tmpl).safe_substitute(safe_row), Template(body_tmpl).safe_substitute(safe_row)

def send_via_smtp(msg_from: str, msg_to: str, subject: str, body: str, attachment_path: Optional[str] = None) -> None:
    host = os.getenv("EMAIL_HOST", "smtp.gmail.com")
    port = int(os.getenv("EMAIL_PORT", "587"))
    username = os.getenv("EMAIL_USER")
    password = os.getenv("EMAIL_PASSWORD")
    use_ssl = os.getenv("EMAIL_USE_SSL", "false").lower() == "true"
    use_starttls = os.getenv("EMAIL_USE_STARTTLS", "true").lower() == "true"

    if not (username and password):
        raise RuntimeError("Missing EMAIL_USER or EMAIL_PASSWORD. For Gmail, use an App Password.")

    email = EmailMessage()
    email["From"] = msg_from
    email["To"] = msg_to
    email["Subject"] = subject
    
    # Check if body contains HTML tags and set content accordingly
    if "<" in body and ">" in body:
        # Body contains HTML, set as HTML content
        email.set_content(body, subtype='html')
    else:
        # Body is plain text
        email.set_content(body)

    # Add attachment if provided
    if attachment_path:
        attachment_file = Path(attachment_path)
        if attachment_file.exists():
            with open(attachment_file, "rb") as f:
                file_data = f.read()
                file_name = attachment_file.name
                email.add_attachment(
                    file_data,
                    maintype="application",
                    subtype="octet-stream",
                    filename=file_name
                )
        else:
            print(f"[WARNING] Attachment file not found: {attachment_path}")

    if use_ssl:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(host, port, context=context) as server:
            server.login(username, password)
            server.send_message(email)
    else:
        with smtplib.SMTP(host, port) as server:
            if use_starttls:
                server.starttls(context=ssl.create_default_context())
            server.login(username, password)
            server.send_message(email)

def send_via_sendgrid(msg_from: str, msg_to: str, subject: str, body: str, attachment_path: Optional[str] = None) -> None:
    if not HAS_SENDGRID:
        raise RuntimeError("SendGrid not installed. Run `pip install sendgrid` or use SMTP.")
    api_key = os.getenv("SENDGRID_API_KEY")
    if not api_key:
        raise RuntimeError("Missing SENDGRID_API_KEY.")
    sg = SendGridAPIClient(api_key)
    
    # Create message
    message = Mail(from_email=msg_from, to_emails=msg_to, subject=subject, plain_text_content=body)
    
    # Add attachment if provided
    if attachment_path:
        attachment_file = Path(attachment_path)
        if attachment_file.exists():
            with open(attachment_file, "rb") as f:
                file_data = f.read()
                file_name = attachment_file.name
                message.add_attachment(
                    file_data,
                    file_name=file_name,
                    disposition="attachment"
                )
        else:
            print(f"[WARNING] Attachment file not found: {attachment_path}")
    
    response = sg.send(message)
    if response.status_code >= 400:
        raise RuntimeError(f"SendGrid error: status={{response.status_code}} body={{response.body}}")

def main():
    parser = argparse.ArgumentParser(description="CSV Mail Merge Sender")
    parser.add_argument("--csv", required=True, help="Path to contacts CSV with columns: email, first_name, company")
    parser.add_argument("--template", required=True, help="Path to template.txt (first line 'Subject: ...')")
    parser.add_argument("--from", dest="from_addr", required=True, help="From email address")
    parser.add_argument("--mode", choices=["smtp", "sendgrid"], default=os.getenv("MODE", "smtp"), help="Send mode")
    parser.add_argument("--dry-run", action="store_true", help="Render only; do not send")
    parser.add_argument("--limit", type=int, default=0, help="Max number of emails to process (0 = all)")
    parser.add_argument("--rate", type=float, default=DEFAULT_RATE_LIMIT_SECONDS, help="Seconds to wait between sends")
    parser.add_argument("--log", default="logs/email_log.csv", help="Path to email log CSV file")
    parser.add_argument("--attachment", help="Path to an attachment file to include with emails (optional)")
    parser.add_argument("--tracking-file", default="logs/sent_emails.json", help="Path to email tracking JSON file")
    args = parser.parse_args()

    csv_path = Path(args.csv)
    tmpl_path = Path(args.template)
    
    # Initialize modules
    email_logger = EmailLogger(log_file=args.log, tracking_file=args.tracking_file)
    duplicate_tracker = DuplicateTracker(email_logger)
    contact_processor = ContactProcessor()

    # Auto-detect resume file in Resume/ folder if no attachment specified
    attachment_path = args.attachment
    if not attachment_path:
        # Look for resume in the Resume/ folder first, then fallback to template directory
        resume_dir = Path("Resume")
        template_dir = tmpl_path.parent
        
        # Look for common resume file names
        resume_patterns = [
            "ParvaShah_Resume.pdf",  # User's specific resume file
            "parvashah_resume.pdf", "Parvashah_Resume.pdf",
            "resume.pdf", "Resume.pdf", "RESUME.pdf",
            "resume.docx", "Resume.docx", "RESUME.docx",
            "parva_resume.pdf", "Parva_Resume.pdf", "Parva_Shah_Resume.pdf",
            "cv.pdf", "CV.pdf", "cv.docx", "CV.docx"
        ]
        
        # First try to find resume in Resume/ folder
        if resume_dir.exists():
            for pattern in resume_patterns:
                potential_resume = resume_dir / pattern
                if potential_resume.exists():
                    attachment_path = str(potential_resume)
                    print(f"[INFO] Auto-detected resume in Resume/ folder: {attachment_path}")
                    break
        
        # If not found in Resume/ folder, try template directory as fallback
        if not attachment_path:
            for pattern in resume_patterns:
                potential_resume = template_dir / pattern
                if potential_resume.exists():
                    attachment_path = str(potential_resume)
                    print(f"[INFO] Auto-detected resume in template directory: {attachment_path}")
                    break
        
        if not attachment_path:
            print("[INFO] No resume file auto-detected. Emails will be sent without attachments.")

    subject_tmpl, body_tmpl = parse_template(tmpl_path)

    # Read and process contacts
    print("[INFO] Reading contacts from CSV...")
    contacts = contact_processor.read_contacts_from_csv(csv_path)
    contacts = contact_processor.validate_contact_data(contacts)
    
    if args.limit > 0:
        contacts = contact_processor.filter_contacts_by_limit(contacts, args.limit)
    
    # Print contact summary
    contact_processor.print_contact_summary(contacts)
    
    # Check for duplicates
    print("[INFO] Checking for duplicate emails...")
    unique_contacts, duplicate_contacts = duplicate_tracker.check_for_duplicates(contacts)
    
    # Save duplicates to CSV if any found
    if duplicate_contacts:
        duplicates_file = duplicate_tracker.save_duplicates_to_csv(duplicate_contacts)
        duplicate_tracker.print_duplicate_report(duplicate_contacts)
    
    # Process unique contacts
    print(f"[INFO] Processing {len(unique_contacts)} unique contacts...")
    
    sent = 0
    processed = 0
    
    for contact in unique_contacts:
        email = contact.get("Email", "").strip()
        first_name = contact.get("First_Name", "")
        company = contact.get("Company", "")
        
        if not email:
            email_logger.log_email_skipped("", "missing email")
            continue

        subject, body = render_templates(subject_tmpl, body_tmpl, contact)
        processed += 1
        
        if args.dry_run:
            print(f"[DRY RUN] Would send to {email!r} | Subject: {subject}")
            email_logger.log_email_skipped(email, "dry run", subject)
        else:
            try:
                if args.mode == "smtp":
                    send_via_smtp(args.from_addr, email, subject, body, attachment_path)
                else:
                    send_via_sendgrid(args.from_addr, email, subject, body, attachment_path)
                
                # Log successful send
                email_logger.log_email_sent(email, first_name, company, subject)
                sent += 1
                
                if args.rate > 0:
                    time.sleep(args.rate)
            except Exception as e:
                email_logger.log_email_failed(email, str(e), subject)
                print(f"[ERROR] {email}: {e}")

    # Print final summary
    stats = email_logger.get_stats()
    print(f"\n[FINAL SUMMARY]")
    print(f"Processed: {processed}")
    print(f"Sent: {sent}")
    print(f"Duplicates found: {len(duplicate_contacts)}")
    print(f"Total emails sent (including previous runs): {stats['total_sent']}")
    print(f"Log file: {args.log}")
    print(f"Tracking file: {args.tracking_file}")
    
    if duplicate_contacts:
        print(f"Duplicates saved to: {duplicates_file}")

if __name__ == "__main__":
    main()
