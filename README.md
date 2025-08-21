# InMailer - Complete Email Automation Solution

A professional email automation tool with a modern React frontend and powerful Python backend, designed for personalized email campaigns, job applications, and business outreach.

## 🏗️ **Project Structure**

```
mail_merge_kit/
├── Backend/                 # Python backend with all original functionality
│   ├── *.py                # Python modules (mail_merge.py, contact_processor.py, etc.)
│   ├── data/               # Contact CSV files
│   ├── Templates/          # Email templates
│   ├── Resume/             # Resume attachments
│   ├── logs/               # Email logs and tracking
│   ├── duplicates/         # Duplicate contact exports
│   └── requirements.txt    # Python dependencies
├── frontend/               # React + TypeScript frontend
│   ├── src/
│   │   ├── components/     # Reusable UI components
│   │   ├── pages/          # Page components
│   │   └── App.tsx         # Main application
│   ├── tailwind.config.js  # Tailwind CSS configuration
│   └── package.json        # Node.js dependencies
└── README.md               # This file
```

## ✨ **Features**

### 🎯 **Core Email Automation**
- **Personalized Emails**: Dynamic content substitution from CSV data
- **Auto-Resume Attachment**: Automatically detects and attaches resumes
- **HTML Email Support**: Professional formatting with custom styling
- **Multiple Providers**: SMTP (Gmail) and SendGrid support
- **Rate Limiting**: Prevent email provider throttling
- **Duplicate Prevention**: Smart detection and management

### 🖥️ **Modern Web Interface**
- **Beautiful Dashboard**: Real-time statistics and quick actions
- **Campaign Builder**: Step-by-step wizard for creating campaigns
- **Template Management**: Visual editor with preview functionality
- **Contact Management**: Import, organize, and manage contact lists
- **Settings Panel**: Comprehensive configuration and user preferences
- **Responsive Design**: Works perfectly on all devices

### 🔧 **Advanced Backend**
- **Modular Architecture**: Clean, maintainable Python code
- **Comprehensive Logging**: Track all email operations
- **Data Validation**: Robust CSV and template validation
- **Error Handling**: Graceful error handling and reporting
- **Performance Optimization**: Efficient processing and memory management

## 🚀 **Quick Start**

### **Option 1: Web Interface (Recommended)**

1. **Start the Frontend**
   ```bash
   cd frontend
   npm install
   npm start
   ```
   Open `http://localhost:3000` in your browser

2. **Configure Backend**
   ```bash
   cd Backend
   pip install -r requirements.txt
   # Set up environment variables (see Backend/README.md)
   ```

3. **Use the Web Interface**
   - Create campaigns through the intuitive wizard
   - Manage templates with the visual editor
   - Upload contacts and monitor campaigns
   - Configure email settings

### **Option 2: Command Line (Original)**

1. **Navigate to Backend**
   ```bash
   cd Backend
   ```

2. **Set up environment variables**
   ```bash
   export EMAIL_USER="yourgmail@gmail.com"
   export EMAIL_PASSWORD="your-app-password"
   ```

3. **Run campaigns**
   ```bash
   python mail_merge.py --csv data/contacts.csv --template Templates/template.txt --from "Your Name <your@email.com>"
   ```

## 🛠️ **Technology Stack**

### **Frontend**
- **React 18** with TypeScript for type safety
- **Tailwind CSS** for beautiful, responsive design
- **React Router** for navigation and routing
- **Lucide React** for consistent, beautiful icons
- **Axios** for HTTP communication

### **Backend**
- **Python 3.8+** for robust email processing
- **SMTP/SendGrid** for email delivery
- **CSV Processing** for contact management
- **HTML Templating** for dynamic content
- **Logging & Tracking** for campaign monitoring

## 📱 **User Experience**

### **Dashboard**
- **Real-time Statistics**: Campaign counts, success rates, and performance metrics
- **Quick Actions**: One-click access to common tasks
- **Recent Activity**: Monitor ongoing campaigns and system status
- **Visual Feedback**: Beautiful charts and progress indicators

### **Campaign Creation**
- **Step-by-Step Wizard**: Guided campaign creation process
- **Template Selection**: Choose from pre-built or custom templates
- **Contact Management**: Easy CSV upload and validation
- **Preview & Testing**: See exactly how emails will look
- **Dry Run Mode**: Test without sending actual emails

### **Template Management**
- **Visual Editor**: Create templates with HTML support
- **Variable System**: Use placeholders like `${First_Name}`, `${Company}`
- **Category Organization**: Organize templates by purpose
- **Preview Mode**: See templates with sample data
- **Import/Export**: Share templates across projects

### **Contact Management**
- **Bulk Import**: Upload large contact lists via CSV
- **Smart Validation**: Automatic email format checking
- **Deduplication**: Prevent duplicate contacts
- **Advanced Filtering**: Search and organize contacts
- **Status Tracking**: Monitor engagement and email status

## 🔧 **Configuration**

### **Email Setup**
- **Gmail**: Use App Passwords for enhanced security
- **Outlook**: Configure SMTP settings
- **SendGrid**: API key-based authentication
- **Custom SMTP**: Any SMTP server support

### **Security Features**
- **Environment Variables**: Secure credential management
- **SSL/TLS Support**: Encrypted email transmission
- **Input Validation**: Prevent injection attacks
- **Rate Limiting**: Protect against abuse

## 📊 **Monitoring & Analytics**

### **Campaign Tracking**
- **Real-time Progress**: Monitor email sending progress
- **Success Rates**: Track delivery and open rates
- **Error Reporting**: Detailed error logs and troubleshooting
- **Performance Metrics**: Campaign effectiveness analysis

### **System Health**
- **Service Status**: Monitor email provider connectivity
- **Resource Usage**: Track system performance
- **Error Logs**: Comprehensive error tracking
- **Audit Trail**: Complete operation history

## 🌟 **Use Cases**

### **Job Applications**
- **Personalized Outreach**: Target specific companies and roles
- **Resume Attachments**: Automatic resume inclusion
- **Follow-up Campaigns**: Track and manage responses
- **Professional Templates**: Industry-specific email formats

### **Business Development**
- **Lead Generation**: Reach potential clients and partners
- **Product Launches**: Announce new products and features
- **Customer Outreach**: Engage existing customers
- **Networking**: Connect with industry professionals

### **Marketing Campaigns**
- **Newsletter Distribution**: Regular content delivery
- **Event Promotion**: Conference and webinar announcements
- **Product Updates**: Feature releases and improvements
- **Customer Feedback**: Survey and feedback collection

## 🚀 **Deployment**

### **Frontend Deployment**
```bash
cd frontend
npm run build
# Deploy build/ folder to your hosting provider
```

### **Backend Deployment**
```bash
cd Backend
# Deploy to your preferred Python hosting service
# Set environment variables for production
```

### **Docker Support**
Both frontend and backend include Docker configurations for easy containerization.

## 🔒 **Best Practices**

### **Email Compliance**
- ✅ Include unsubscribe options
- ✅ Use real business addresses
- ✅ Respect recipient preferences
- ✅ Follow local email laws

### **Data Management**
- ✅ Regular backups of contact lists
- ✅ Secure storage of credentials
- ✅ Regular cleanup of old data
- ✅ Monitor system performance

### **Campaign Optimization**
- ✅ Test templates before sending
- ✅ Use appropriate rate limits
- ✅ Monitor delivery rates
- ✅ A/B test subject lines

## 🆘 **Support & Documentation**

- **Frontend Docs**: See `frontend/README.md` for detailed frontend documentation
- **Backend Docs**: See `Backend/README.md` for backend usage and API details
- **Issues**: Report bugs and request features through GitHub issues
- **Contributing**: See CONTRIBUTING.md for development guidelines

## 🤝 **Contributing**

We welcome contributions! Please see our contributing guidelines for:
- Code style and standards
- Testing requirements
- Pull request process
- Development setup

## 📄 **License**

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 **Acknowledgments**

- **React Team** for the amazing frontend framework
- **Tailwind CSS** for the beautiful styling system
- **Python Community** for robust backend tools
- **Email Service Providers** for reliable delivery infrastructure

---

**Transform your email outreach with InMailer! 🚀**

*Professional email automation with a beautiful, modern interface*
