from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, text
from typing import List, Optional, Dict, Any
from datetime import datetime
from types import SimpleNamespace
from .models import User, Template, EmailLog, Campaign
from .config import get_db_session
import bcrypt
import logging
import math

class UserService:
    @staticmethod
    def create_user(email: str, name: str, password: str = None, is_google_user: bool = False) -> User:
        """Create a new user"""
        db = get_db_session()
        try:
            password_hash = None
            if password:
                password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

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
    def get_user_by_email(email: str):
        """Get user by email using raw SQL to avoid ORM detachment issues"""
        db = get_db_session()# 1. Open a database connection
        try:
            result = db.execute(# 2. Run the query
                text("SELECT id, email, name, password_hash, is_google_user, created_at, updated_at FROM users WHERE email = :email LIMIT 1"),
                {"email": email}
            )
            row = result.fetchone()# 3. Get one result row
            if not row:
                return None
            user = SimpleNamespace(
                id=row[0], email=row[1], name=row[2],
                password_hash=row[3], is_google_user=row[4],
                created_at=row[5], updated_at=row[6]
            )
            logging.debug(f"🔍 get_user_by_email: raw SQL returned id={user.id} for email={email}")
            return user
        finally:
            db.close()

    @staticmethod
    def get_user_by_id(user_id: int):
        """Get user by ID using raw SQL"""
        db = get_db_session()
        try:
            result = db.execute(
                text("SELECT id, email, name, password_hash, is_google_user, created_at, updated_at FROM users WHERE id = :uid LIMIT 1"),
                {"uid": user_id}
            )
            row = result.fetchone()
            if not row:
                return None
            return SimpleNamespace(
                id=row[0], email=row[1], name=row[2],
                password_hash=row[3], is_google_user=row[4],
                created_at=row[5], updated_at=row[6]
            )
        finally:
            db.close()

    @staticmethod
    def verify_password(user: User, password: str) -> bool:
        """Verify user password"""
        if not user.password_hash:
            return False
        stored_hash = user.password_hash
        if isinstance(stored_hash, str):
            stored_hash = stored_hash.encode()
        try:
            return bcrypt.checkpw(password.encode(), stored_hash)
        except (ValueError, TypeError):
            # Stored hash is not a valid bcrypt hash (e.g. legacy format)
            return False

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

    @staticmethod
    def get_total_user_count() -> int:
        """Get total number of users in the system"""
        db = get_db_session()
        try:
            return db.query(User).count()
        finally:
            db.close()

    @staticmethod
    def is_user_registration_allowed(max_users: int = 50) -> bool:
        """Check if new user registration is allowed based on user limit"""
        current_count = UserService.get_total_user_count()
        return current_count < max_users

    @staticmethod
    def save_oauth_credentials(user_id: int, credentials_dict: dict) -> bool:
        """Persist OAuth credentials to the database so they survive server restarts"""
        db = get_db_session()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return False
            user.oauth_credentials = credentials_dict
            user.updated_at = datetime.now()
            db.commit()
            return True
        finally:
            db.close()

    @staticmethod
    def get_oauth_credentials(user_id: int) -> Optional[dict]:
        """Retrieve persisted OAuth credentials from the database"""
        db = get_db_session()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return None
            return user.oauth_credentials
        finally:
            db.close()

    @staticmethod
    def clear_oauth_credentials(user_id: int) -> bool:
        """Clear stored OAuth credentials (used during re-auth flow)"""
        db = get_db_session()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return False
            user.oauth_credentials = None
            user.updated_at = datetime.now()
            db.commit()
            return True
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
    def get_user_templates(user_id: int) -> list:
        """Get all templates for a specific user using raw SQL"""
        db = get_db_session()
        try:
            result = db.execute(
                text("SELECT id, user_id, name, subject, content, variables, attachment_path, attachment_name, created_at, updated_at FROM templates WHERE user_id = :uid ORDER BY updated_at DESC"),
                {"uid": user_id}
            )
            rows = result.fetchall()
            templates = []
            for row in rows:
                templates.append(SimpleNamespace(
                    id=row[0], user_id=row[1], name=row[2], subject=row[3],
                    content=row[4], variables=row[5], attachment_path=row[6],
                    attachment_name=row[7], created_at=row[8], updated_at=row[9]
                ))
            logging.debug(f"🔍 get_user_templates: raw SQL returned {len(templates)} templates for user_id={user_id}")
            return templates
        finally:
            db.close()

    @staticmethod
    def get_template_by_id(template_id: int, user_id: int):
        """Get a specific template for a user using raw SQL"""
        db = get_db_session()
        try:
            result = db.execute(
                text("SELECT id, user_id, name, subject, content, variables, attachment_path, attachment_name, created_at, updated_at FROM templates WHERE id = :tid AND user_id = :uid LIMIT 1"),
                {"tid": template_id, "uid": user_id}
            )
            row = result.fetchone()
            if not row:
                return None
            return SimpleNamespace(
                id=row[0], user_id=row[1], name=row[2], subject=row[3],
                content=row[4], variables=row[5], attachment_path=row[6],
                attachment_name=row[7], created_at=row[8], updated_at=row[9]
            )
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
            logging.debug(f"🔍 === COUNT USER TEMPLATES DEBUG ===")
            logging.debug(f"🔍 User ID: {user_id}")
            logging.debug(f"🔍 Database session: {db}")

            # Get all templates for debugging
            all_templates = db.query(Template).all()
            logging.debug(f"🔍 Total templates in database: {len(all_templates)}")

            # Show template details
            for template in all_templates:
                logging.debug(f"🔍   - Template ID: {template.id}, User ID: {template.user_id}, Name: {template.name}")

            # Get filtered templates
            user_templates = db.query(Template).filter(Template.user_id == user_id).all()
            logging.debug(f"🔍 Templates for user {user_id}: {len(user_templates)}")

            # Show filtered template details
            for template in user_templates:
                logging.debug(f"🔍   - Template ID: {template.id}, Name: {template.name}")

            # Get count
            count = db.query(Template).filter(Template.user_id == user_id).count()
            logging.debug(f"🔍 Final count returned: {count}")
            logging.debug(f"🔍 =================================")

            return count
        finally:
            db.close()

class CampaignService:
    @staticmethod
    def create_campaign(user_id: int, template_id: int, name: str, contacts: list,
                        scheduled_at: datetime, total_count: int) -> Campaign:
        """Create a new campaign"""
        db = get_db_session()
        try:
            campaign = Campaign(
                user_id=user_id,
                template_id=template_id,
                name=name,
                contacts=contacts,
                scheduled_at=scheduled_at,
                total_count=total_count,
                status='scheduled'
            )
            db.add(campaign)
            db.commit()
            db.refresh(campaign)
            return campaign
        finally:
            db.close()

    @staticmethod
    def get_user_campaigns(user_id: int) -> list:
        """Get all campaigns for a user with template name via LEFT JOIN"""
        db = get_db_session()
        try:
            result = db.execute(
                text("""
                    SELECT c.id, c.user_id, c.template_id, c.name, c.status,
                           c.scheduled_at, c.sent_at, c.total_count, c.success_count,
                           c.error_count, c.created_at, t.name AS template_name
                    FROM campaigns c
                    LEFT JOIN templates t ON c.template_id = t.id
                    WHERE c.user_id = :uid
                    ORDER BY c.created_at DESC
                """),
                {"uid": user_id}
            )
            rows = result.fetchall()
            campaigns = []
            for row in rows:
                campaigns.append(SimpleNamespace(
                    id=row[0], user_id=row[1], template_id=row[2], name=row[3],
                    status=row[4],
                    scheduled_at=row[5].isoformat() if row[5] and not isinstance(row[5], str) else row[5],
                    sent_at=row[6].isoformat() if row[6] and not isinstance(row[6], str) else row[6],
                    total_count=row[7], success_count=row[8], error_count=row[9],
                    created_at=row[10].isoformat() if row[10] and not isinstance(row[10], str) else row[10],
                    template_name=row[11]
                ))
            return campaigns
        finally:
            db.close()

    @staticmethod
    def get_campaign_by_id(campaign_id: int, user_id: int):
        """Get a specific campaign scoped to user, with template name"""
        db = get_db_session()
        try:
            result = db.execute(
                text("""
                    SELECT c.id, c.user_id, c.template_id, c.name, c.status,
                           c.scheduled_at, c.sent_at, c.total_count, c.success_count,
                           c.error_count, c.created_at, t.name AS template_name
                    FROM campaigns c
                    LEFT JOIN templates t ON c.template_id = t.id
                    WHERE c.id = :cid AND c.user_id = :uid
                    LIMIT 1
                """),
                {"cid": campaign_id, "uid": user_id}
            )
            row = result.fetchone()
            if not row:
                return None
            return SimpleNamespace(
                id=row[0], user_id=row[1], template_id=row[2], name=row[3],
                status=row[4],
                scheduled_at=row[5].isoformat() if row[5] and not isinstance(row[5], str) else row[5],
                sent_at=row[6].isoformat() if row[6] and not isinstance(row[6], str) else row[6],
                total_count=row[7], success_count=row[8], error_count=row[9],
                created_at=row[10].isoformat() if row[10] and not isinstance(row[10], str) else row[10],
                template_name=row[11]
            )
        finally:
            db.close()

    @staticmethod
    def update_campaign_status(campaign_id: int, status: str, sent_at: datetime = None,
                                success_count: int = None, error_count: int = None) -> bool:
        """Update campaign status and optional counters/timestamps"""
        db = get_db_session()
        try:
            campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
            if not campaign:
                return False
            campaign.status = status
            if sent_at is not None:
                campaign.sent_at = sent_at
            if success_count is not None:
                campaign.success_count = success_count
            if error_count is not None:
                campaign.error_count = error_count
            db.commit()
            return True
        finally:
            db.close()

    @staticmethod
    def cancel_campaign(campaign_id: int, user_id: int) -> bool:
        """Cancel a campaign only if it is currently scheduled"""
        db = get_db_session()
        try:
            campaign = db.query(Campaign).filter(
                and_(Campaign.id == campaign_id, Campaign.user_id == user_id)
            ).first()
            if not campaign:
                return False
            if campaign.status != 'scheduled':
                return False
            campaign.status = 'cancelled'
            db.commit()
            return True
        finally:
            db.close()

    @staticmethod
    def get_due_campaigns() -> list:
        """Get all scheduled campaigns whose scheduled_at is now or in the past (for cron use)"""
        db = get_db_session()
        try:
            result = db.execute(
                text("""
                    SELECT c.id, c.user_id, c.template_id, c.name, c.status,
                           c.scheduled_at, c.sent_at, c.total_count, c.success_count,
                           c.error_count, c.created_at, c.contacts
                    FROM campaigns c
                    WHERE c.status = 'scheduled' AND c.scheduled_at <= :now
                    ORDER BY c.scheduled_at ASC
                """),
                {"now": datetime.utcnow()}
            )
            rows = result.fetchall()
            campaigns = []
            for row in rows:
                campaigns.append(SimpleNamespace(
                    id=row[0], user_id=row[1], template_id=row[2], name=row[3],
                    status=row[4],
                    scheduled_at=row[5].isoformat() if row[5] and not isinstance(row[5], str) else row[5],
                    sent_at=row[6].isoformat() if row[6] and not isinstance(row[6], str) else row[6],
                    total_count=row[7], success_count=row[8], error_count=row[9],
                    created_at=row[10].isoformat() if row[10] and not isinstance(row[10], str) else row[10],
                    contacts=row[11]
                ))
            return campaigns
        finally:
            db.close()

class EmailLogService:
    @staticmethod
    def log_email(user_id: int, template_id: int, recipient_email: str, subject: str,
                  status: str, error_message: str = None, gmail_message_id: str = None,
                  campaign_id: int = None) -> EmailLog:
        """Log an email send attempt"""
        db = get_db_session()
        try:
            email_log = EmailLog(
                user_id=user_id,
                template_id=template_id,
                campaign_id=campaign_id,
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
                         status: str, error_message: str = None, gmail_message_id: str = None,
                         campaign_id: int = None) -> EmailLog:
        """Create an email log entry (alias for log_email)"""
        return EmailLogService.log_email(
            user_id=user_id,
            template_id=template_id,
            recipient_email=recipient_email,
            subject=subject,
            status=status,
            error_message=error_message,
            gmail_message_id=gmail_message_id,
            campaign_id=campaign_id
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
                    'sent_at': log.sent_at if isinstance(log.sent_at, str) else (log.sent_at.isoformat() if log.sent_at else None),
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

    @staticmethod
    def get_user_email_history(user_id: int, page: int = 1, per_page: int = 20,
                                filters: Dict[str, Any] = None,
                                sort_by: str = 'sent_at',
                                sort_order: str = 'desc') -> Dict[str, Any]:
        """
        Paginated email history for a user with optional filters.

        filters keys (all optional):
          status, date_from, date_to, campaign_id, template_id, search
        """
        db = get_db_session()
        try:
            # Whitelist sort columns to prevent injection
            allowed_sort_columns = {'sent_at', 'status', 'recipient_email'}
            if sort_by not in allowed_sort_columns:
                sort_by = 'sent_at'
            sort_order = 'DESC' if sort_order.lower() == 'desc' else 'ASC'

            filters = filters or {}

            # Build WHERE clauses dynamically
            where_clauses = ["el.user_id = :user_id"]
            params: Dict[str, Any] = {"user_id": user_id}

            if filters.get('status'):
                where_clauses.append("el.status = :status")
                params['status'] = filters['status']

            if filters.get('date_from'):
                where_clauses.append("el.sent_at >= :date_from")
                params['date_from'] = filters['date_from']

            if filters.get('date_to'):
                where_clauses.append("el.sent_at <= :date_to")
                params['date_to'] = filters['date_to']

            if filters.get('campaign_id') is not None:
                where_clauses.append("el.campaign_id = :campaign_id")
                params['campaign_id'] = filters['campaign_id']

            if filters.get('template_id') is not None:
                where_clauses.append("el.template_id = :template_id")
                params['template_id'] = filters['template_id']

            if filters.get('search'):
                # Use LOWER() for cross-database compatibility (SQLite has no ILIKE)
                where_clauses.append(
                    "(LOWER(el.recipient_email) LIKE LOWER(:search) OR LOWER(el.subject) LIKE LOWER(:search))"
                )
                params['search'] = f"%{filters['search']}%"

            where_sql = " AND ".join(where_clauses)

            # Count total matching rows
            count_sql = text(f"""
                SELECT COUNT(*)
                FROM email_logs el
                WHERE {where_sql}
            """)
            total = db.execute(count_sql, params).scalar() or 0

            # Paginate
            offset = (page - 1) * per_page
            data_sql = text(f"""
                SELECT el.id, el.recipient_email, el.subject, el.status, el.sent_at,
                       el.template_id, t.name AS template_name,
                       el.campaign_id, c.name AS campaign_name,
                       el.error_message, el.gmail_message_id
                FROM email_logs el
                LEFT JOIN templates t ON el.template_id = t.id
                LEFT JOIN campaigns c ON el.campaign_id = c.id
                WHERE {where_sql}
                ORDER BY el.{sort_by} {sort_order}
                LIMIT :limit OFFSET :offset
            """)
            params['limit'] = per_page
            params['offset'] = offset

            rows = db.execute(data_sql, params).fetchall()
            emails = []
            for row in rows:
                sent_at_val = row[4]
                emails.append({
                    'id': row[0],
                    'recipient_email': row[1],
                    'subject': row[2],
                    'status': row[3],
                    'sent_at': sent_at_val.isoformat() if sent_at_val and not isinstance(sent_at_val, str) else sent_at_val,
                    'template_id': row[5],
                    'template_name': row[6],
                    'campaign_id': row[7],
                    'campaign_name': row[8],
                    'error_message': row[9],
                    'gmail_message_id': row[10]
                })

            total_pages = math.ceil(total / per_page) if per_page > 0 else 0
            return {
                'emails': emails,
                'total': total,
                'page': page,
                'per_page': per_page,
                'total_pages': total_pages
            }
        finally:
            db.close()

    @staticmethod
    def get_grouped_summary(user_id: int, group_by: str = 'campaign') -> list:
        """
        Return aggregated email counts grouped by campaign, template, or status.

        group_by: 'campaign' | 'template' | 'status'
        """
        db = get_db_session()
        try:
            if group_by == 'campaign':
                result = db.execute(
                    text("""
                        SELECT el.campaign_id,
                               c.name AS group_name,
                               COUNT(*) AS total,
                               SUM(CASE WHEN el.status = 'sent' THEN 1 ELSE 0 END) AS success_count,
                               SUM(CASE WHEN el.status = 'failed' THEN 1 ELSE 0 END) AS error_count,
                               MAX(el.sent_at) AS last_sent_at
                        FROM email_logs el
                        LEFT JOIN campaigns c ON el.campaign_id = c.id
                        WHERE el.user_id = :uid
                        GROUP BY el.campaign_id, c.name
                        ORDER BY last_sent_at DESC
                    """),
                    {"uid": user_id}
                )
                rows = result.fetchall()
                summaries = []
                for row in rows:
                    last_sent_at = row[5]
                    summaries.append({
                        'group_id': row[0],
                        'group_name': row[1] if row[1] is not None else 'No campaign',
                        'total': row[2],
                        'success_count': row[3],
                        'error_count': row[4],
                        'last_sent_at': last_sent_at.isoformat() if last_sent_at and not isinstance(last_sent_at, str) else last_sent_at
                    })
                return summaries

            elif group_by == 'template':
                result = db.execute(
                    text("""
                        SELECT el.template_id,
                               t.name AS group_name,
                               COUNT(*) AS total,
                               SUM(CASE WHEN el.status = 'sent' THEN 1 ELSE 0 END) AS success_count,
                               SUM(CASE WHEN el.status = 'failed' THEN 1 ELSE 0 END) AS error_count,
                               MAX(el.sent_at) AS last_sent_at
                        FROM email_logs el
                        LEFT JOIN templates t ON el.template_id = t.id
                        WHERE el.user_id = :uid
                        GROUP BY el.template_id, t.name
                        ORDER BY last_sent_at DESC
                    """),
                    {"uid": user_id}
                )
                rows = result.fetchall()
                summaries = []
                for row in rows:
                    last_sent_at = row[5]
                    summaries.append({
                        'group_id': row[0],
                        'group_name': row[1] if row[1] is not None else 'No template',
                        'total': row[2],
                        'success_count': row[3],
                        'error_count': row[4],
                        'last_sent_at': last_sent_at.isoformat() if last_sent_at and not isinstance(last_sent_at, str) else last_sent_at
                    })
                return summaries

            elif group_by == 'status':
                result = db.execute(
                    text("""
                        SELECT el.status,
                               COUNT(*) AS total,
                               SUM(CASE WHEN el.status = 'sent' THEN 1 ELSE 0 END) AS success_count,
                               SUM(CASE WHEN el.status = 'failed' THEN 1 ELSE 0 END) AS error_count,
                               MAX(el.sent_at) AS last_sent_at
                        FROM email_logs el
                        WHERE el.user_id = :uid
                        GROUP BY el.status
                        ORDER BY total DESC
                    """),
                    {"uid": user_id}
                )
                rows = result.fetchall()
                summaries = []
                for row in rows:
                    last_sent_at = row[4]
                    summaries.append({
                        'group_id': row[0],
                        'group_name': row[0],
                        'total': row[1],
                        'success_count': row[2],
                        'error_count': row[3],
                        'last_sent_at': last_sent_at.isoformat() if last_sent_at and not isinstance(last_sent_at, str) else last_sent_at
                    })
                return summaries

            else:
                return []
        finally:
            db.close()

    @staticmethod
    def get_group_detail(user_id: int, group_type: str, group_id,
                          page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """
        Paginated email log detail for a specific group.

        group_type: 'campaign' | 'template' | 'status'
        group_id: integer FK, None (for NULL FK rows), or string (for status)
        """
        db = get_db_session()
        try:
            params: Dict[str, Any] = {"user_id": user_id}

            if group_type == 'campaign':
                if group_id is None:
                    filter_clause = "el.campaign_id IS NULL"
                else:
                    filter_clause = "el.campaign_id = :group_id"
                    params['group_id'] = group_id
            elif group_type == 'template':
                if group_id is None:
                    filter_clause = "el.template_id IS NULL"
                else:
                    filter_clause = "el.template_id = :group_id"
                    params['group_id'] = group_id
            elif group_type == 'status':
                filter_clause = "el.status = :group_id"
                params['group_id'] = group_id
            else:
                return {'emails': [], 'total': 0, 'page': page, 'per_page': per_page, 'total_pages': 0}

            count_sql = text(f"""
                SELECT COUNT(*)
                FROM email_logs el
                WHERE el.user_id = :user_id AND {filter_clause}
            """)
            total = db.execute(count_sql, params).scalar() or 0

            offset = (page - 1) * per_page
            params['limit'] = per_page
            params['offset'] = offset

            data_sql = text(f"""
                SELECT el.id, el.recipient_email, el.subject, el.status, el.sent_at
                FROM email_logs el
                WHERE el.user_id = :user_id AND {filter_clause}
                ORDER BY el.sent_at DESC
                LIMIT :limit OFFSET :offset
            """)
            rows = db.execute(data_sql, params).fetchall()
            emails = []
            for row in rows:
                sent_at_val = row[4]
                emails.append({
                    'id': row[0],
                    'recipient_email': row[1],
                    'subject': row[2],
                    'status': row[3],
                    'sent_at': sent_at_val.isoformat() if sent_at_val and not isinstance(sent_at_val, str) else sent_at_val
                })

            total_pages = math.ceil(total / per_page) if per_page > 0 else 0
            return {
                'emails': emails,
                'total': total,
                'page': page,
                'per_page': per_page,
                'total_pages': total_pages
            }
        finally:
            db.close()
