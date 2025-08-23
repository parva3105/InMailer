# InMailer Database System

This document explains the new database system that makes InMailer user-specific, storing individual user data, templates, and statistics.

## 🚀 What's New

### Before (Generalized System)
- All users saw the same templates
- No user separation
- Templates stored in JSON files
- No user statistics or campaign tracking

### After (User-Specific System)
- Each user has their own templates
- User authentication and session management
- Database storage for all data
- Individual user statistics and campaign tracking
- Email sending history and analytics

## 🗄️ Database Schema

### Users Table
- **id**: Primary key
- **email**: Unique user email
- **name**: User's display name
- **password_hash**: Hashed password (null for Google OAuth users)
- **is_google_user**: Boolean flag for OAuth users
- **created_at**: Account creation timestamp
- **updated_at**: Last update timestamp

### Templates Table
- **id**: Primary key
- **user_id**: Foreign key to users table
- **name**: Template name
- **subject**: Email subject line
- **content**: Email body content
- **variables**: JSON array of template variables
- **attachment_path**: Path to attachment file
- **attachment_name**: Original attachment filename
- **created_at**: Template creation timestamp
- **updated_at**: Last update timestamp



### Email Logs Table
- **id**: Primary key
- **user_id**: Foreign key to users table
- **campaign_id**: Foreign key to campaigns table (optional)
- **template_id**: Foreign key to templates table
- **recipient_email**: Email address of recipient
- **subject**: Email subject sent
- **status**: Email status (sent, failed, pending)
- **error_message**: Error details if failed
- **gmail_message_id**: Gmail API message ID
- **sent_at**: Email send timestamp

## 🔧 Setup Instructions

### 1. Install Dependencies
The required packages are already in `requirements.txt`:
```bash
pip install -r requirements.txt
```

### 2. Environment Configuration
Create or update your `.env` file:
```env
# Database Configuration
DATABASE_URL=sqlite:///./inmailer.db  # For development (SQLite)
# DATABASE_URL=postgresql://user:password@localhost/inmailer  # For production (PostgreSQL)

# Google OAuth (existing)
GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_client_secret
GOOGLE_REDIRECT_URI=http://localhost:5000/auth/google/callback

# Flask Configuration
FLASK_SECRET_KEY=your-secret-key-here
```

### 3. Initialize Database
Run the database initialization script:
```bash
cd Backend
python db/init_db.py
```

This will:
- Create database tables
- Optionally create sample data
- Optionally migrate existing templates

### 4. Start the Database-Enabled Server
```bash
cd Backend
python start_server_db.py
```

## 🔄 Migration from Old System

### Automatic Migration
When you first run the database-enabled server, it will automatically:
1. Detect existing templates in `Templates/templates.json`
2. Create a default user account
3. Migrate all existing templates to the database
4. Create a backup of the original file

### Manual Migration
If you prefer manual control:
```bash
cd Backend
python db/init_db.py
# Choose 'y' for template migration when prompted
```

## 📊 New API Endpoints

### User-Specific Templates
- `GET /api/templates` - Get current user's templates
- `POST /api/templates` - Create new template for current user
- `PUT /api/templates/<id>` - Update user's template
- `DELETE /api/templates/<id>` - Delete user's template

### User Statistics
- `GET /api/user/stats` - Get email statistics for current user


### Authentication (Existing)
- `GET /auth/user` - Get current user info
- `GET /auth/logout` - Logout user
- `GET /auth/google` - Google OAuth login

## 🎯 Key Benefits

### 1. User Isolation
- Each user only sees their own templates
- No data sharing between users
- Secure user boundaries

### 2. Data Persistence
- All data stored in database
- Survives server restarts
- Backup and restore capabilities

### 3. Analytics & Tracking
- Email sending history
- Campaign performance metrics
- Success/failure rates
- Recent activity tracking

### 4. Scalability
- Easy to add more users
- Database can handle large amounts of data
- Support for multiple concurrent users

## 🔍 Database Operations

### Creating a User
```python
from db.services import UserService

user = UserService.create_user(
    email="user@example.com",
    name="John Doe",
    password="secure_password"
)
```

### Creating a Template
```python
from db.services import TemplateService

template = TemplateService.create_template(
    user_id=user.id,
    name="Welcome Email",
    subject="Welcome to ${Company}!",
    content="Dear ${Name}, welcome aboard!",
    variables=["Name", "Company"]
)
```

### Getting User Templates
```python
templates = TemplateService.get_user_templates(user.id)
```

### Logging Email Sends
```python
from db.services import EmailLogService

EmailLogService.log_email(
    user_id=user.id,
    template_id=template.id,
    recipient_email="recipient@example.com",
    subject="Welcome Email",
    status="sent",
    gmail_message_id="message_id_123"
)
```

## 🚨 Important Notes

### 1. Database File Location
- SQLite database file: `Backend/inmailer.db`
- Keep this file backed up
- Don't delete it unless you want to start fresh

### 2. User Sessions
- Sessions are stored in memory (not database)
- Sessions expire after 24 hours
- For production, consider using Redis for sessions

### 3. File Attachments
- Attachment files are still stored in the filesystem
- Database only stores file paths
- Ensure attachment directory permissions are correct

### 4. Migration Safety
- Original templates are backed up before migration
- Migration is safe and can be run multiple times
- No data loss during migration

## 🐛 Troubleshooting

### Database Connection Issues
```bash
# Check if database file exists
ls -la Backend/inmailer.db

# Reinitialize database if needed
python db/init_db.py
```

### Template Migration Issues
```bash
# Check backup file
ls -la Backend/Templates/templates_migrated_backup.json

# Restore from backup if needed
cp Backend/Templates/templates_migrated_backup.json Backend/Templates/templates.json
```

### Permission Issues
```bash
# Ensure write permissions
chmod 755 Backend/
chmod 644 Backend/inmailer.db
```

## 🔮 Future Enhancements

### Planned Features
- User roles and permissions
- Template sharing between users
- Advanced analytics dashboard
- Email scheduling
- A/B testing for templates
- Bulk contact management

### Database Upgrades
- PostgreSQL support for production
- Database migrations with Alembic
- Connection pooling
- Read replicas for scaling

## 📞 Support

If you encounter issues:
1. Check the server console for error messages
2. Verify database file permissions
3. Ensure all dependencies are installed
4. Check the `.env` file configuration

The database system transforms InMailer from a single-user tool to a multi-user platform where each user has their own workspace, templates, and analytics.
