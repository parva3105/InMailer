#!/usr/bin/env python3
"""
Contact Processor Module
Handles CSV reading and contact data processing
"""

import csv
from pathlib import Path
from typing import Dict, List, Optional


class ContactProcessor:
    def __init__(self):
        """Initialize the contact processor"""
        pass
    
    def read_contacts_from_csv(self, csv_path: Path) -> List[Dict]:
        """
        Read contacts from a CSV file
        
        Args:
            csv_path: Path to the CSV file
            
        Returns:
            List of contact dictionaries
        """
        contacts = []
        
        if not csv_path.exists():
            raise FileNotFoundError(f"CSV file not found: {csv_path}")
        
        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)  # Reads CSV with headers as keys
            
            # Validate required columns
            required_columns = ["Email"]
            if not all(col in reader.fieldnames for col in required_columns):
                raise ValueError(f"CSV must contain columns: {required_columns}")
            
            for row in reader:
                # Clean and validate the row
                cleaned_row = self._clean_contact_row(row)
                if cleaned_row:
                    contacts.append(cleaned_row)
        
        return contacts
    
    def _clean_contact_row(self, row: Dict) -> Optional[Dict]:
        """
        Clean and validate a contact row
        
        Args:
            row: Raw contact row from CSV
            
        Returns:
            Cleaned contact row or None if invalid
        """
        # Clean email
        email = row.get("Email", "").strip()
        if not email or "@" not in email:
            return None
        
        # Clean other fields
        cleaned_row = {
            "Email": email,
            "First_Name": row.get("First_Name", row.get("First Name", "")).strip(),
            "Company": row.get("Company", "").strip()
        }
        
        # Add any other fields that exist in the original row
        for key, value in row.items():
            if key not in cleaned_row:
                cleaned_row[key] = value.strip() if value else ""
        
        return cleaned_row
    
    def get_contact_summary(self, contacts: List[Dict]) -> Dict:
        """
        Get a summary of contact data
        
        Args:
            contacts: List of contact dictionaries
            
        Returns:
            Dictionary with summary statistics
        """
        if not contacts:
            return {
                "total": 0,
                "with_company": 0,
                "with_first_name": 0,
                "companies": set(),
                "sample_emails": []
            }
        
        summary = {
            "total": len(contacts),
            "with_company": sum(1 for c in contacts if c.get("Company")),
            "with_first_name": sum(1 for c in contacts if c.get("First_Name")),
            "companies": set(),
            "sample_emails": []
        }
        
        # Collect unique companies
        for contact in contacts:
            company = contact.get("Company")
            if company:
                summary["companies"].add(company)
        
        # Get sample emails (first 5)
        summary["sample_emails"] = [c["Email"] for c in contacts[:5]]
        
        return summary
    
    def print_contact_summary(self, contacts: List[Dict]):
        """
        Print a formatted summary of contact data
        
        Args:
            contacts: List of contact dictionaries
        """
        summary = self.get_contact_summary(contacts)
        
        print(f"\n[CONTACT SUMMARY]")
        print("-" * 50)
        print(f"Total contacts: {summary['total']}")
        print(f"With company info: {summary['with_company']}")
        print(f"With first name: {summary['with_first_name']}")
        print(f"Unique companies: {len(summary['companies'])}")
        
        if summary['sample_emails']:
            print(f"Sample emails: {', '.join(summary['sample_emails'])}")
        
        print("-" * 50)
    
    def filter_contacts_by_limit(self, contacts: List[Dict], limit: int) -> List[Dict]:
        """
        Limit the number of contacts to process
        
        Args:
            contacts: List of contact dictionaries
            limit: Maximum number of contacts to return
            
        Returns:
            Limited list of contacts
        """
        if limit <= 0:
            return contacts
        
        return contacts[:limit]
    
    def validate_contact_data(self, contacts: List[Dict]) -> List[Dict]:
        """
        Validate contact data and remove invalid entries
        
        Args:
            contacts: List of contact dictionaries
            
        Returns:
            List of valid contact dictionaries
        """
        valid_contacts = []
        
        for contact in contacts:
            email = contact.get("Email", "")
            
            # Basic email validation
            if not email or "@" not in email or "." not in email.split("@")[1]:
                print(f"[WARNING] Skipping invalid email: {email}")
                continue
            
            valid_contacts.append(contact)
        
        return valid_contacts
