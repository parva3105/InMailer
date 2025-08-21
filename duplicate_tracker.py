#!/usr/bin/env python3
"""
Duplicate Tracker Module
Identifies and tracks duplicate emails to prevent re-sending
"""

import csv
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple
from email_logger import EmailLogger


class DuplicateTracker:
    def __init__(self, email_logger: EmailLogger):
        """
        Initialize the duplicate tracker
        
        Args:
            email_logger: Instance of EmailLogger to check for duplicates
        """
        self.email_logger = email_logger
    
    def check_for_duplicates(self, contacts_data: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
        """
        Check contacts for duplicates and separate them
        
        Args:
            contacts_data: List of contact dictionaries from CSV
            
        Returns:
            Tuple of (unique_contacts, duplicate_contacts)
        """
        unique_contacts = []
        duplicate_contacts = []
        
        for contact in contacts_data:
            email = contact.get("Email", "").strip()
            if not email:
                continue
                
            if self.email_logger.is_email_sent(email):
                # This is a duplicate - add to duplicates list
                duplicate_contacts.append(contact)
            else:
                # This is a new contact - add to unique list
                unique_contacts.append(contact)
        
        return unique_contacts, duplicate_contacts
    
    def save_duplicates_to_csv(self, duplicates: List[Dict], filename: str = None) -> str:
        """
        Save duplicate contacts to a CSV file
        
        Args:
            duplicates: List of duplicate contact dictionaries
            filename: Optional custom filename, defaults to duplicates_<date>.csv
            
        Returns:
            Path to the saved duplicates file
        """
        # Ensure duplicates directory exists
        duplicates_dir = Path("duplicates")
        duplicates_dir.mkdir(exist_ok=True)
        
        if not filename:
            current_date = datetime.now().strftime("%Y%m%d")
            filename = f"duplicates/duplicates_{current_date}.csv"
        
        duplicates_path = Path(filename)
        
        if not duplicates:
            print(f"[INFO] No duplicates found to save")
            return str(duplicates_path)
        
        # Determine fieldnames from the first duplicate contact
        if duplicates:
            fieldnames = list(duplicates[0].keys())
        else:
            fieldnames = ["Email", "First_Name", "Company"]
        
        with open(duplicates_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for duplicate in duplicates:
                writer.writerow(duplicate)
        
        print(f"[INFO] Saved {len(duplicates)} duplicates to {duplicates_path}")
        return str(duplicates_path)
    
    def get_duplicate_summary(self, duplicates: List[Dict]) -> Dict[str, int]:
        """
        Get a summary of duplicate contacts
        
        Args:
            duplicates: List of duplicate contact dictionaries
            
        Returns:
            Dictionary with summary statistics
        """
        if not duplicates:
            return {"total": 0, "by_company": {}}
        
        summary = {
            "total": len(duplicates),
            "by_company": {}
        }
        
        for duplicate in duplicates:
            company = duplicate.get("Company", "Unknown Company")
            summary["by_company"][company] = summary["by_company"].get(company, 0) + 1
        
        return summary
    
    def print_duplicate_report(self, duplicates: List[Dict]):
        """
        Print a formatted report of duplicate contacts
        
        Args:
            duplicates: List of duplicate contact dictionaries
        """
        if not duplicates:
            print("[INFO] No duplicate contacts found")
            return
        
        print(f"\n[DUPLICATE REPORT] Found {len(duplicates)} duplicate contacts:")
        print("-" * 80)
        
        # Group by company for better readability
        by_company = {}
        for duplicate in duplicates:
            company = duplicate.get("Company", "Unknown Company")
            if company not in by_company:
                by_company[company] = []
            by_company[company].append(duplicate)
        
        for company, company_duplicates in by_company.items():
            print(f"\nCompany: {company}")
            print(f"  Duplicates: {len(company_duplicates)}")
            for duplicate in company_duplicates:
                email = duplicate.get("Email", "No Email")
                first_name = duplicate.get("First_Name", "No Name")
                print(f"    - {first_name} ({email})")
        
        print("-" * 80)
    
    def get_contacts_with_company_info(self, contacts: List[Dict]) -> List[Dict]:
        """
        Ensure contacts have the required fields for duplicate tracking
        
        Args:
            contacts: List of contact dictionaries
            
        Returns:
            List of contacts with normalized company and first name fields
        """
        normalized_contacts = []
        
        for contact in contacts:
            normalized_contact = contact.copy()
            
            # Ensure we have the required fields
            email = contact.get("Email", "").strip()
            first_name = contact.get("First_Name", contact.get("First Name", "")).strip()
            company = contact.get("Company", "").strip()
            
            # Normalize field names
            normalized_contact["Email"] = email
            normalized_contact["First_Name"] = first_name
            normalized_contact["Company"] = company
            
            normalized_contacts.append(normalized_contact)
        
        return normalized_contacts
