#!/usr/bin/env python3
"""
Email Logger Module
Handles logging of email operations and tracking sent emails
"""

import logging
import csv
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import json


class EmailLogger:
    def __init__(self, log_file: str = "logs/email_log.csv", tracking_file: str = "logs/sent_emails.json"):
        """
        Initialize the email logger
        
        Args:
            log_file: CSV file to log email operations
            tracking_file: JSON file to track sent emails for duplicate prevention
        """
        # Ensure logs directory exists
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)
        
        self.log_file = Path(log_file)
        self.tracking_file = Path(tracking_file)
        self.sent_emails = self._load_tracking_data()
        
        # Setup logging
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def _load_tracking_data(self) -> Dict[str, Dict]:
        """Load existing tracking data from JSON file"""
        if self.tracking_file.exists():
            try:
                with open(self.tracking_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return {}
        return {}
    
    def _save_tracking_data(self):
        """Save tracking data to JSON file"""
        with open(self.tracking_file, 'w', encoding='utf-8') as f:
            json.dump(self.sent_emails, f, indent=2, ensure_ascii=False)
    
    def log_email_sent(self, email: str, first_name: str = "", company: str = "", subject: str = ""):
        """
        Log that an email was sent
        
        Args:
            email: Email address
            first_name: First name of recipient
            company: Company name
            subject: Email subject
        """
        # Log to console and file
        self.logger.info(f"Mail #{len(self.sent_emails) + 1} sent to {email}")
        
        # Add to tracking data
        self.sent_emails[email] = {
            "first_name": first_name,
            "company": company,
            "subject": subject,
            "sent_date": datetime.now().isoformat(),
            "mail_number": len(self.sent_emails) + 1
        }
        
        # Save tracking data
        self._save_tracking_data()
        
        # Log to CSV
        self._log_to_csv(email, "sent", "", subject)
    
    def log_email_failed(self, email: str, error: str, subject: str = ""):
        """Log that an email failed to send"""
        self.logger.error(f"Failed to send email to {email}: {error}")
        self._log_to_csv(email, "failed", error, subject)
    
    def log_email_skipped(self, email: str, reason: str, subject: str = ""):
        """Log that an email was skipped"""
        self.logger.warning(f"Skipped email to {email}: {reason}")
        self._log_to_csv(email, "skipped", reason, subject)
    
    def _log_to_csv(self, email: str, status: str, error: str, subject: str):
        """Log email operation to CSV file"""
        log_exists = self.log_file.exists()
        
        with open(self.log_file, "a", newline="", encoding="utf-8") as f:
            fieldnames = ["timestamp", "email", "status", "error", "subject"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            if not log_exists:
                writer.writeheader()
            
            writer.writerow({
                "timestamp": datetime.now().isoformat(),
                "email": email,
                "status": status,
                "error": error,
                "subject": subject
            })
    
    def is_email_sent(self, email: str) -> bool:
        """Check if an email was previously sent"""
        return email.lower() in [e.lower() for e in self.sent_emails.keys()]
    
    def get_sent_email_info(self, email: str) -> Optional[Dict]:
        """Get information about a previously sent email"""
        for stored_email, info in self.sent_emails.items():
            if stored_email.lower() == email.lower():
                return info
        return None
    
    def get_all_sent_emails(self) -> Dict[str, Dict]:
        """Get all sent email information"""
        return self.sent_emails.copy()
    
    def get_stats(self) -> Dict[str, int]:
        """Get email statistics"""
        return {
            "total_sent": len(self.sent_emails),
            "total_logged": len([1 for _ in self._read_csv_log() if _])
        }
    
    def _read_csv_log(self) -> List[Dict]:
        """Read the CSV log file"""
        if not self.log_file.exists():
            return []
        
        with open(self.log_file, 'r', newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            return list(reader)
