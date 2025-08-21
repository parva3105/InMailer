# Mail Merge Kit - Backend API

A Flask-based API server that powers the Mail Merge Kit frontend application.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables (Optional)
Create a `.env` file in the Backend directory:
```env
EMAIL_USER=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_SSL=false
EMAIL_USE_STARTTLS=true
RATE_LIMIT_SECONDS=2.0
```

**Note:** For Gmail, you'll need to use an App Password, not your regular password.

### 3. Start the Server
```bash
python start_server.py
```

The server will start on `http://localhost:5000`

## 🔌 API Endpoints

### Templates
- `GET /api/templates` - Get all templates
- `POST /api/templates` - Create a new template

### Mail Merge
- `POST /api/mail-merge` - Process CSV with template (preview mode)
- `POST /api/send-emails` - Send actual emails

### Health Check
- `GET /api/health` - Server health status

## 📁 Project Structure

```
Backend/
├── app.py              # Flask API server
├── start_server.py     # Startup script
├── mail_merge.py       # Core mail merge logic
├── email_logger.py     # Email logging functionality
├── contact_processor.py # Contact processing utilities
├── duplicate_tracker.py # Duplicate detection
├── requirements.txt    # Python dependencies
├── Templates/          # Email templates storage
├── data/              # Sample CSV files
└── logs/              # Application logs
```

## 🔧 Configuration

### Email Settings
The backend supports both SMTP and SendGrid for sending emails:

- **SMTP**: Configure via environment variables
- **SendGrid**: Install sendgrid package and configure API key

### Rate Limiting
Control email sending speed to avoid being blocked:
```env
RATE_LIMIT_SECONDS=2.0  # Wait 2 seconds between emails
```

## 🧪 Testing the API

### Test with curl

1. **Create a template:**
```bash
curl -X POST http://localhost:5000/api/templates \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Welcome Email",
    "subject": "Welcome to {{Company}}, {{Name}}!",
    "content": "Hi {{Name}},\n\nWelcome to {{Company}}!",
    "variables": ["Name", "Company"]
  }'
```

2. **Get all templates:**
```bash
curl http://localhost:5000/api/templates
```

3. **Health check:**
```bash
curl http://localhost:5000/api/health
```

## 🔗 Frontend Integration

The frontend automatically connects to this backend when running on `http://localhost:3000` (or 3001).

**Frontend → Backend Communication:**
- Templates are saved to and loaded from the backend
- CSV processing happens on the backend
- Email previews are generated server-side
- Actual email sending is handled by the backend

## 🚨 Troubleshooting

### Common Issues

1. **Port already in use:**
   ```bash
   # Find process using port 5000
   netstat -ano | findstr :5000
   # Kill the process
   taskkill /PID <PID> /F
   ```

2. **Import errors:**
   ```bash
   pip install -r requirements.txt
   ```

3. **CORS issues:**
   - The backend has CORS enabled for development
   - Make sure frontend is running on the expected port

4. **Email not working:**
   - Check environment variables
   - For Gmail, use App Password, not regular password
   - Verify SMTP settings

### Debug Mode
The server runs in debug mode by default. Check the console for detailed error messages.

## 🔒 Security Notes

- **Development only**: This setup is for development/testing
- **Production**: Use proper WSGI server (Gunicorn, uWSGI)
- **Environment variables**: Never commit `.env` files
- **CORS**: Configure properly for production domains

## 🚀 Production Deployment

For production deployment:

1. **Use WSGI server:**
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

2. **Set production environment:**
   ```bash
   export FLASK_ENV=production
   export FLASK_DEBUG=0
   ```

3. **Configure reverse proxy (nginx/Apache)**

4. **Use environment-specific settings**

## 📞 Support

If you encounter issues:
1. Check the console output for error messages
2. Verify all dependencies are installed
3. Check environment variable configuration
4. Ensure ports are not blocked by firewall

---

**Happy Email Marketing! 🚀**
