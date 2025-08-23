from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from typing import List, Optional, Dict, Any
from datetime import datetime
from .models import User, Template, EmailLog
from .config import get_db_session
import hashlib

class UserService:
    @staticmethod
    def create_user(email: str, name: str, password: str = None, is_google_user: bool = False) -> User:
        """Create a new user"""
        db = get_db_session()
        try:
            password_hash = None
            if password:
                password_hash = hashlib.sha256(password.encode()).hexdigest()
            
            user = User(
                email=email,
                name=name,
                password_hash=password_hash,
                is_google_user=is_google_user
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            return user
        finally:
            db.close()
    
    @staticmethod
    def get_user_by_email(email: str) -> Optional[User]:
        """Get user by email"""
        db = get_db_session()
        try:
            return db.query(User).filter(User.email == email).first()
        finally:
            db.close()
    
    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[User]:
        """Get user by ID"""
        db = get_db_session()
        try:
            return db.query(User).filter(User.id == user_id).first()
        finally:
            db.close()
    
    @staticmethod
    def verify_password(user: User, password: str) -> bool:
        """Verify user password"""
        if not user.password_hash:
            return False
        return user.password_hash == hashlib.sha256(password.encode()).hexdigest()
    
    @staticmethod
    def update_user_google_oauth(user_id: int, new_name: str = None) -> User:
        """Update user to mark as Google OAuth user and optionally update name"""
        db = get_db_session()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                user.is_google_user = True
                if new_name:
                    user.name = new_name
                user.updated_at = datetime.now()
                db.commit()
                db.refresh(user)
            return user
        finally:
            db.close()

class TemplateService:
    @staticmethod
    def create_template(user_id: int, name: str, subject: str, content: str, 
                       variables: List[str] = None, attachment_path: str = None, 
                       attachment_name: str = None) -> Template:
        """Create a new template for a user"""
        db = get_db_session()
        try:
            template = Template(
                user_id=user_id,
                name=name,
                subject=subject,
                content=content,
                variables=variables or [],
                attachment_path=attachment_path,
                attachment_name=attachment_name
            )
            db.add(template)
            db.commit()
            db.refresh(template)
            return template
        finally:
            db.close()
    
    @staticmethod
    def get_user_templates(user_id: int) -> List[Template]:
        """Get all templates for a specific user"""
        db = get_db_session()
        try:
            return db.query(Template).filter(Template.user_id == user_id).order_by(desc(Template.updated_at)).all()
        finally:
            db.close()
    
    @staticmethod
    def get_template_by_id(template_id: int, user_id: int) -> Optional[Template]:
        """Get a specific template for a user"""
        db = get_db_session()
        try:
            return db.query(Template).filter(
                and_(Template.id == template_id, Template.user_id == user_id)
            ).first()
        finally:
            db.close()
    
    @staticmethod
    def update_template(template_id: int, user_id: int, **kwargs) -> Optional[Template]:
        """Update a template"""
        db = get_db_session()
        try:
            template = db.query(Template).filter(
                and_(Template.id == template_id, Template.user_id == user_id)
            ).first()
            if template:
                for key, value in kwargs.items():
                    if hasattr(template, key):
                        setattr(template, key, value)
                template.updated_at = datetime.now()
                db.commit()
                db.refresh(template)
            return template
        finally:
            db.close()
    
    @staticmethod
    def delete_template(template_id: int, user_id: int) -> bool:
        """Delete a template while preserving related email logs"""
        db = get_db_session()
        try:
            template = db.query(Template).filter(
                and_(Template.id == template_id, Template.user_id == user_id)
            ).first()
            if template:
                # Instead of deleting email logs, set their template_id to NULL
                # This preserves email history while allowing template deletion
                from .models import EmailLog
                email_logs = db.query(EmailLog).filter(
                    and_(EmailLog.template_id == template_id, EmailLog.user_id == user_id)
                ).all()
                
                for email_log in email_logs:
                    email_log.template_id = None
                
                # Now delete the template
                db.delete(template)
                db.commit()
                return True
            return False
        finally:
            db.close()
    
    @staticmethod
    def count_user_templates(user_id: int) -> int:
        """Count templates for a specific user"""
        db = get_db_session()
        try:
            print(f"🔍 === COUNT USER TEMPLATES DEBUG ===")
            print(f"🔍 User ID: {user_id}")
            print(f"🔍 Database session: {db}")
            
            # Get all templates for debugging
            all_templates = db.query(Template).all()
            print(f"🔍 Total templates in database: {len(all_templates)}")
            
            # Show template details
            for template in all_templates:
                print(f"🔍   - Template ID: {template.id}, User ID: {template.user_id}, Name: {template.name}")
            
            # Get filtered templates
            user_templates = db.query(Template).filter(Template.user_id == user_id).all()
            print(f"🔍 Templates for user {user_id}: {len(user_templates)}")
            
            # Show filtered template details
            for template in user_templates:
                print(f"🔍   - Template ID: {template.id}, Name: {template.name}")
            
            # Get count
            count = db.query(Template).filter(Template.user_id == user_id).count()
            print(f"🔍 Final count returned: {count}")
            print(f"🔍 =================================")
            
            return count
        finally:
            db.close()

class EmailLogService:
    @staticmethod
    def log_email(user_id: int, template_id: int, recipient_email: str, subject: str,
                  status: str, error_message: str = None, gmail_message_id: str = None) -> EmailLog:
        """Log an email send attempt"""
        db = get_db_session()
        try:
            email_log = EmailLog(
                user_id=user_id,
                template_id=template_id,
                recipient_email=recipient_email,
                subject=subject,
                status=status,
                error_message=error_message,
                gmail_message_id=gmail_message_id
            )
            db.add(email_log)
            db.commit()
            db.refresh(email_log)
            return email_log
        finally:
            db.close()
    
    @staticmethod
    def create_email_log(user_id: int, template_id: int, recipient_email: str, subject: str,
                         status: str, error_message: str = None, gmail_message_id: str = None) -> EmailLog:
        """Create an email log entry (alias for log_email)"""
        return EmailLogService.log_email(
            user_id=user_id,
            template_id=template_id,
            recipient_email=recipient_email,
            subject=subject,
            status=status,
            error_message=error_message,
            gmail_message_id=gmail_message_id
        )
    
    @staticmethod
    def get_user_email_logs(user_id: int, limit: int = 100) -> List[EmailLog]:
        """Get email logs for a user"""
        db = get_db_session()
        try:
            return db.query(EmailLog).filter(
                EmailLog.user_id == user_id
            ).order_by(desc(EmailLog.sent_at)).limit(limit).all()
        finally:
            db.close()
    
    @staticmethod
    def get_user_email_logs_with_template_info(user_id: int, limit: int = 100) -> List[Dict[str, Any]]:
        """Get email logs for a user with template information, handling deleted templates"""
        db = get_db_session()
        try:
            # Get email logs with left join to templates to handle NULL template_id
            from .models import Template
            logs = db.query(EmailLog, Template).outerjoin(
                Template, EmailLog.template_id == Template.id
            ).filter(
                EmailLog.user_id == user_id
            ).order_by(desc(EmailLog.sent_at)).limit(limit).all()
            
            result = []
            for log, template in logs:
                log_info = {
                    'id': log.id,
                    'recipient_email': log.recipient_email,
                    'subject': log.subject,
                    'status': log.status,
                    'error_message': log.error_message,
                    'gmail_message_id': log.gmail_message_id,
                    'sent_at': log.sent_at.isoformat() if log.sent_at else None,
                    'template_info': {
                        'id': template.id if template else None,
                        'name': template.name if template else 'Template Deleted',
                        'exists': template is not None
                    }
                }
                result.append(log_info)
            
            return result
        finally:
            db.close()
    
    @staticmethod
    def get_template_email_logs(template_id: int, user_id: int) -> List[EmailLog]:
        """Get email logs for a specific template"""
        db = get_db_session()
        try:
            return db.query(EmailLog).filter(
                and_(EmailLog.template_id == template_id, EmailLog.user_id == user_id)
            ).order_by(desc(EmailLog.sent_at)).all()
        finally:
            db.close()
    
    @staticmethod
    def get_user_stats(user_id: int) -> Dict[str, Any]:
        """Get email statistics for a user"""
        db = get_db_session()
        try:
            total_emails = db.query(EmailLog).filter(EmailLog.user_id == user_id).count()
            sent_emails = db.query(EmailLog).filter(
                and_(EmailLog.user_id == user_id, EmailLog.status == 'sent')
            ).count()
            failed_emails = db.query(EmailLog).filter(
                and_(EmailLog.user_id == user_id, EmailLog.status == 'failed')
            ).count()
            
            # Get template count
            template_count = TemplateService.count_user_templates(user_id)
            
            # Get recent activity with template information
            recent_emails = EmailLogService.get_user_email_logs_with_template_info(user_id, 10)
            
            return {
                'total_emails': total_emails,
                'sent_emails': sent_emails,
                'failed_emails': failed_emails,
                'template_count': template_count,
                'success_rate': (sent_emails / total_emails * 100) if total_emails > 0 else 0,
                'recent_emails': recent_emails
            }
        finally:
            db.close()
