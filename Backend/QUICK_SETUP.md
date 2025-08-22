# 🚀 Quick Setup Guide - InMailer Database System

Get your user-specific InMailer system running in 5 minutes!

## ⚡ Quick Start

### 1. Install Dependencies
```bash
cd Backend
pip install -r requirements.txt
```

### 2. Initialize Database
```bash
python db/init_db.py
```
- Choose `y` for sample data (recommended for testing)
- Choose `y` for template migration (if you have existing templates)

### 3. Start the Server
```bash
python start_server_db.py
```

That's it! Your database-enabled InMailer is now running.

## 🔍 What Happens Next

1. **Database Created**: SQLite database file `inmailer.db` is created
2. **Tables Created**: Users, templates, campaigns, and email logs tables
3. **Sample Data**: Test user and templates are created (if you chose yes)
4. **Migration**: Existing templates are moved to database (if you chose yes)
5. **Server Running**: Flask server starts on port 5000

## 🌐 Access Your App

- **Frontend**: http://localhost:3001
- **Backend**: http://localhost:5000
- **Health Check**: http://localhost:5000/api/health

## 🧪 Test Everything Works

```bash
python test_db.py
```

This will run comprehensive tests to ensure your database is working correctly.

## 🔧 Troubleshooting

### Database File Not Found
```bash
# Check if database was created
ls -la inmailer.db

# Reinitialize if needed
python db/init_db.py
```

### Import Errors
```bash
# Make sure you're in the Backend directory
pwd
# Should show: /path/to/mail_merge_kit/Backend
```

### Permission Errors
```bash
# On Windows, run PowerShell as Administrator
# On Mac/Linux, check file permissions
ls -la inmailer.db
```

## 📊 What You Get

✅ **User Isolation**: Each user sees only their own templates  
✅ **Data Persistence**: All data survives server restarts  
✅ **Email Tracking**: Complete history of sent emails  
✅ **Campaign Management**: Track email campaign performance  
✅ **Statistics**: Success rates, email counts, recent activity  

## 🔄 Migrating from Old System

Your existing templates are automatically migrated to the database. The system:
- Creates a default user account
- Moves all templates to that user
- Creates a backup of your original file
- Preserves all template data and attachments

## 🎯 Next Steps

1. **Test the system** with the test script
2. **Log in** with Google OAuth
3. **Create your own templates** (they'll be user-specific now)
4. **Send test emails** to see the tracking in action
5. **Check your stats** at `/api/user/stats`

## 📞 Need Help?

- Check the console output for error messages
- Run `python test_db.py` to diagnose issues
- Review `DATABASE_README.md` for detailed documentation
- Ensure all dependencies are installed correctly

---

**🎉 Congratulations!** You now have a multi-user, database-driven email system where each user has their own workspace, templates, and analytics.
