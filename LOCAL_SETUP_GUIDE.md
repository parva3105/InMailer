# 🚀 Local Development Setup Guide

This guide will help you run the InMailer application locally for development and testing.

## 📋 Prerequisites

- **Python 3.8+** installed
- **Node.js 16+** and npm installed
- **Git** (if you want to clone the repository)

## 🛠️ Quick Start (Windows)

### Option 1: Automated Setup (Recommended)
```bash
# Run the automated setup script
start_local.bat
```

This will:
- Install all dependencies
- Test the setup
- Start both backend and frontend servers
- Open them in separate command windows

### Option 2: Manual Setup

#### Backend Setup
```bash
# Navigate to backend directory
cd Backend

# Install Python dependencies
pip install -r requirements.txt

# Test the setup
python test_local.py

# Start the backend server
python start_server_db.py
```

#### Frontend Setup (in a new terminal)
```bash
# Navigate to frontend directory
cd frontend

# Install Node.js dependencies
npm install

# Start the frontend server
npm start
```

## 🌐 Access Your Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5000
- **Health Check**: http://localhost:5000/api/health

## 🔧 Environment Configuration

### Backend Environment Variables
Create a `.env` file in the `Backend` directory with:

```env
# Database Configuration
DATABASE_URL=sqlite:///inmailer.db

# Google OAuth Configuration
GOOGLE_CLIENT_ID=502741004777-i80atbmb80r61sssl9u4li6u7ml6cqhf.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your_google_client_secret_here
GOOGLE_REDIRECT_URI=http://localhost:5000/auth/google/callback

# Frontend URL
FRONTEND_URL=http://localhost:3000

# Email Configuration
EMAIL_USER=ywork.parry@gmail.com
EMAIL_PASSWORD=veprhckdygvlzdzp
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587

# Flask Configuration
FLASK_ENV=development
SECRET_KEY=Howareyou@11
```

### Frontend Environment Variables
Create a `.env.local` file in the `frontend` directory with:

```env
# Backend API URL
REACT_APP_API_URL=http://localhost:5000

# Google OAuth Client ID
REACT_APP_GOOGLE_CLIENT_ID=502741004777-i80atbmb80r61sssl9u4li6u7ml6cqhf.apps.googleusercontent.com
```

## 🧪 Testing Your Setup

### Backend Tests
```bash
cd Backend
python test_local.py
```

This will test:
- ✅ All imports work correctly
- ✅ Database initializes properly
- ✅ Server can start and respond to requests

### Frontend Tests
```bash
cd frontend
npm test
```

## 🚨 Troubleshooting

### Common Issues

#### 1. Port Already in Use
```bash
# Find process using port 5000
netstat -ano | findstr :5000

# Kill the process (replace PID with actual process ID)
taskkill /PID <PID> /F
```

#### 2. Python Import Errors
```bash
# Make sure you're in the Backend directory
cd Backend

# Reinstall dependencies
pip install -r requirements.txt
```

#### 3. Node.js Issues
```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and reinstall
rmdir /s node_modules
npm install
```

#### 4. Database Issues
```bash
# Delete the database file and reinitialize
cd Backend
del inmailer.db
python db/init_db.py
```

#### 5. CORS Issues
- Make sure frontend is running on port 3000
- Make sure backend is running on port 5000
- Check that environment variables are set correctly

### Debug Mode

Both servers run in debug mode by default:
- **Backend**: Flask debug mode enabled
- **Frontend**: React development server with hot reload

## 📊 What You Get

✅ **Full Application**: Complete mail merge functionality  
✅ **User Authentication**: Google OAuth integration  
✅ **Database**: SQLite database with user isolation  
✅ **Email Sending**: SMTP email functionality  
✅ **Template Management**: Create and manage email templates  
✅ **CSV Processing**: Upload and process contact lists  
✅ **Email Tracking**: Track sent emails and campaigns  

## 🔄 Development Workflow

1. **Start both servers** using the setup script
2. **Make changes** to the code
3. **Frontend changes** will auto-reload
4. **Backend changes** require server restart
5. **Test functionality** in the browser

## 📞 Need Help?

If you encounter issues:

1. **Check the console output** for error messages
2. **Run the test script**: `python test_local.py`
3. **Verify environment variables** are set correctly
4. **Ensure all dependencies** are installed
5. **Check that ports** are not blocked by firewall

## 🎯 Next Steps

Once everything is running:

1. **Open http://localhost:3000** in your browser
2. **Sign in with Google** OAuth
3. **Create a test template**
4. **Upload a CSV file** with contacts
5. **Send test emails** to verify functionality

---

**🎉 Happy Development!** Your local InMailer environment is ready to go!
