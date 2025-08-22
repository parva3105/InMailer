# InMailer (CSV → Personalized Emails)

A professional email automation tool that sends personalized emails with automatic resume attachments, HTML formatting, and professional styling.

## ✨ Features

- **📧 Personalized Emails**: Dynamic content substitution from CSV data
- **📎 Auto-Resume Attachment**: Automatically detects and attaches your resume
- **🎨 HTML Email Support**: Professional formatting with custom fonts and styling
- **🔗 LinkedIn Integration**: Clickable hyperlinks in your signature
- **⚡ Multiple Email Providers**: SMTP (Gmail) and SendGrid support
- **📊 Detailed Logging**: Track sent, failed, and skipped emails
- **🚀 Rate Limiting**: Prevent email provider throttling

## 📁 Files

- `mail_merge.py` - Main script with all features
- `sample_contacts.csv` - Example CSV with contact data
- `requirements.txt` - Python dependencies
- `Templates/` - Folder for email templates
- `Resume/` - Folder for resume attachments
- `logs/email_log.csv` - Email sending logs (auto-generated)
- `logs/sent_emails.json` - Email tracking database (auto-generated)

**Note**: Email templates are not included in this repository for privacy reasons. See the "Creating Your Own Template" section below.

## 🚀 Quick Start

### 1. Setup Environment Variables

Create a `.env` file or export these variables:

```bash
# For Gmail SMTP
export EMAIL_USER="yourgmail@gmail.com"
export EMAIL_PASSWORD="your-app-password"
export EMAIL_HOST="smtp.gmail.com"
export EMAIL_PORT="587"

# For SendGrid (optional)
export SENDGRID_API_KEY="your-sendgrid-api-key"
```

**Note**: For Gmail, use an App Password, not your regular password.

### 2. Prepare Your Files

- **CSV**: Update `sample_contacts.csv` with your contacts
- **Resume**: Place your resume PDF in the Resume/ folder (auto-detected)
- **Template**: Create your own email template in the Templates/ folder (see template creation guide below)

### 3. Test First (Dry Run)

```bash
python mail_merge.py --csv sample_contacts.csv --template your_template.txt --from "Your Name <yourgmail@gmail.com>" --mode smtp --dry-run
```

### 4. Send Real Emails

```bash
python mail_merge.py --csv sample_contacts.csv --template your_template.txt --from "Your Name <yourgmail@gmail.com>" --mode smtp
```

## 📝 Creating Your Own Template

### Template File Structure

Create a new text file (e.g., `my_template.txt`) with this structure:

```
Subject: Your Subject Line Here

<div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; font-size: 14px; line-height: 1.6; color: #333333; max-width: 600px; margin: 0 auto;">

<p style="margin-bottom: 16px;">Hello ${First_Name},</p>

<p style="margin-bottom: 16px;">Your email content here...</p>

<p style="margin-bottom: 16px;">More content with ${Company} placeholder...</p>

<p style="margin-top: 24px; margin-bottom: 8px;">Regards,</p>
<p style="margin-bottom: 4px;"><strong>Your Name</strong></p>
<p style="margin-bottom: 4px;">Your Title</p>
<p style="margin-bottom: 4px;">Your Company</p>
<p style="margin-top: 16px; color: #666666; font-size: 13px;">your.email@domain.com | <a href="https://linkedin.com/in/yourprofile" style="color: #0077b5; text-decoration: none;">LinkedIn</a> | Your Phone</p>

</div>
```

### Template Requirements

1. **First Line**: Must start with `Subject: ` followed by your subject template
2. **HTML Structure**: Use proper HTML tags for formatting
3. **Placeholders**: Use `${Column_Name}` syntax for dynamic content
4. **Styling**: Include CSS styles for professional appearance

### Template Examples

#### Job Application Template
```
Subject: Hi ${First_Name} – Application for ${Position} Role

<div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; font-size: 14px; line-height: 1.6; color: #333333; max-width: 600px; margin: 0 auto;">

<p style="margin-bottom: 16px;">Hello ${First_Name},</p>

<p style="margin-bottom: 16px;">My name is [Your Name], and I'm reaching out about the ${Position} role at ${Company}.</p>

<p style="margin-bottom: 16px;">[Your background and experience...]</p>

<p style="margin-bottom: 16px;">I've attached my resume for your reference. Would you be available for a brief conversation?</p>

<p style="margin-top: 24px; margin-bottom: 8px;">Best regards,</p>
<p style="margin-bottom: 4px;"><strong>[Your Name]</strong></p>
<p style="margin-bottom: 4px;">[Your Title]</p>
<p style="margin-top: 16px; color: #666666; font-size: 13px;">[Your Contact Info]</p>

</div>
```

#### Networking Template
```
Subject: Hi ${First_Name} – Coffee Chat Request

<div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; font-size: 14px; line-height: 1.6; color: #333333; max-width: 600px; margin: 0 auto;">

<p style="margin-bottom: 16px;">Hi ${First_Name},</p>

<p style="margin-bottom: 16px;">I came across your work at ${Company} and was impressed by [specific project/achievement].</p>

<p style="margin-bottom: 16px;">[Your introduction and why you want to connect...]</p>

<p style="margin-bottom: 16px;">Would you be open to a 15-minute coffee chat to discuss [topic]?</p>

<p style="margin-top: 24px; margin-bottom: 8px;">Thanks,</p>
<p style="margin-bottom: 4px;"><strong>[Your Name]</strong></p>
<p style="margin-top: 16px; color: #666666; font-size: 13px;">[Your Contact Info]</p>

</div>
```

## 📊 CSV Format

Your CSV must have these columns:

```csv
Email,First Name,Company
john@company.com,John,Acme Corp
jane@startup.com,Jane,Startup Inc
```

**Column Names**:
- `Email` - Recipient's email address
- `First Name` - Recipient's first name
- `Company` - Company name

**Custom Columns**: You can add more columns like `Position`, `Department`, etc., and use them in your template as `${Position}`, `${Department}`.

## 🔧 Command Line Options

```bash
python mail_merge.py [OPTIONS]

Required:
  --csv PATH          Path to contacts CSV file
  --template PATH     Path to your email template file
  --from EMAIL        From email address

Optional:
  --mode {smtp,sendgrid}  Email provider (default: smtp)
  --dry-run               Test mode (no emails sent)
  --limit N               Max emails to process (0 = all)
  --rate SECONDS          Delay between sends (default: 2.0)
  --log PATH              Log file path (default: logs/email_log.csv)
  --attachment PATH       Manual attachment path (optional)
```

## 📎 Resume Attachment

### Auto-Detection
The script automatically finds your resume in the Resume/ folder (preferred) or template directory:

**Supported Filenames**:
- `resume.pdf`, `Resume.pdf`
- `cv.pdf`, `CV.pdf`
- Word documents: `.docx`, `.doc`
- Custom names: `your_name_resume.pdf`

**Priority Order**:
1. **Resume/ folder** (recommended location)
2. Template directory (fallback)

### Manual Override
If you want to use a different file:

```bash
python mail_merge.py --csv contacts.csv --template template.txt --from "you@email.com" --attachment "path/to/resume.pdf"
```

## 🎨 HTML Email Features

### Font Customization
Change fonts by modifying the template:

```html
<div style="font-family: 'Arial', sans-serif; font-size: 14px;">
  <!-- Your content -->
</div>
```

### Professional Styling
The template includes:
- **Fonts**: Segoe UI, Tahoma, Geneva, Verdana
- **Colors**: Dark gray text (#333333), blue links (#0077b5)
- **Layout**: 600px max-width, centered content
- **Spacing**: Consistent margins and line heights

### CSS Properties You Can Use
- `font-family` - Font selection
- `font-size` - Text size
- `color` - Text color
- `margin` - Spacing around elements
- `padding` - Internal spacing
- `text-align` - Text alignment
- `background-color` - Background colors

## 📈 Email Providers

### Gmail SMTP (Recommended)
```bash
export EMAIL_USER="yourgmail@gmail.com"
export EMAIL_PASSWORD="your-app-password"
python mail_merge.py --mode smtp [other-options]
```

### SendGrid
```bash
pip install -r requirements.txt
export SENDGRID_API_KEY="your-api-key"
python mail_merge.py --mode sendgrid [other-options]
```

## 📊 Logging & Monitoring

### Email Log File
`logs/email_log.csv` tracks:
- `email` - Recipient address
- `status` - sent, failed, dry_run, skipped
- `error` - Error message (if any)
- `subject` - Email subject line

### Rate Limiting
- **Default**: 2 seconds between emails
- **Custom**: Use `--rate 5` for 5-second delays
- **Purpose**: Prevent email provider throttling

## 🧪 Testing & Debugging

### Dry Run Mode
```bash
python mail_merge.py --csv contacts.csv --template template.txt --from "test@email.com" --dry-run
```

**What it shows**:
- Template rendering with real data
- Email content preview
- No actual emails sent

### Template Testing Tips
1. **Test with small CSV**: Use 2-3 contacts first
2. **Check placeholders**: Ensure `${Column_Name}` matches CSV headers
3. **Validate HTML**: Use online HTML validators
4. **Preview emails**: Check how they look in different email clients

### Common Issues
1. **Placeholders not replaced**: Check CSV column names match template variables
2. **Resume not attached**: Ensure resume file is in Resume/ folder or template directory
3. **Authentication failed**: Verify Gmail App Password or SendGrid API key
4. **HTML not rendering**: Ensure template has proper HTML structure

## 📋 Example Usage

### Job Application Campaign
```bash
# Test first
python mail_merge.py --csv job_contacts.csv --template job_template.txt --from "Your Name <your@email.com>" --dry-run

# Send real emails
python mail_merge.py --csv job_contacts.csv --template job_template.txt --from "Your Name <your@email.com>" --mode smtp --rate 3
```

### Networking Outreach
```bash
python mail_merge.py --csv networking.csv --template networking.txt --from "Your Name <your@email.com>" --mode smtp
```

### Custom Campaign
```bash
# Create your own template first, then:
python mail_merge.py --csv your_contacts.csv --template your_template.txt --from "Your Name <your@email.com>" --mode smtp --dry-run
```

## 🔒 Best Practices

### Email Compliance
- ✅ Include unsubscribe option for marketing emails
- ✅ Use real business address
- ✅ Respect recipient preferences
- ✅ Follow local email laws

### Professional Etiquette
- ✅ Personalize each email
- ✅ Keep content relevant and concise
- ✅ Include clear call-to-action
- ✅ Professional signature with contact info
- ✅ Test templates before sending

### Template Design
- ✅ Keep it under 600px width for mobile compatibility
- ✅ Use consistent spacing and margins
- ✅ Include your contact information
- ✅ Make it easy to read on all devices
- ✅ Test with different email clients

## 🆘 Troubleshooting

### Gmail Issues
- **"Username and Password not accepted"**: Use App Password, not regular password
- **"Less secure app access"**: Enable 2FA and create App Password

### Template Issues
- **HTML not rendering**: Ensure template has proper HTML structure
- **Placeholders not working**: Check CSV column names match template variables
- **Formatting lost**: Verify CSS styles are inline (not external)

### Attachment Issues
- **Resume not found**: Verify filename matches supported patterns
- **File too large**: Keep attachments under 25MB for most providers

## 📞 Support

For issues or questions:
1. Check the logs in `logs/email_log.csv`
2. Run with `--dry-run` to test template rendering
3. Verify environment variables are set correctly
4. Ensure all required files are in the correct locations
5. Test your template with a small CSV first

## 🎯 Getting Started Checklist

- [ ] Set up environment variables
- [ ] Create your email template
- [ ] Prepare your CSV with contacts
- [ ] Place your resume in the folder
- [ ] Test with `--dry-run` flag
- [ ] Send a test email to yourself
- [ ] Run your campaign

---

**Happy Email Marketing! 🚀**

*Remember: Create your own templates to match your personal brand and messaging style.*
