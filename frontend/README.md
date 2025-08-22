# InMailer - Frontend

A simple, streamlined mail merge application built with React and TypeScript.

## Features

- **Google Authentication**: Sign in with your Google account
- **Template Creation**: Create email templates with dynamic variables like `{{Name}}` and `{{Company}}`
- **CSV Upload**: Upload contact lists in CSV format
- **Mail Merge**: Select a template and send personalized emails to all contacts

## Getting Started

### Prerequisites

- Node.js (v14 or higher)
- npm or yarn

### Installation

1. Install dependencies:
   ```bash
   npm install
   ```

2. Set up Google OAuth:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one
   - Enable Google+ API
   - Create OAuth 2.0 credentials
   - Replace `YOUR_GOOGLE_CLIENT_ID` in `src/App.tsx` with your actual client ID

3. Start the development server:
   ```bash
   npm start
   ```

4. Open [http://localhost:3000](http://localhost:3000) in your browser

## Usage

### 1. Sign In
- Land on the homepage and click "Sign in with Google"
- Authorize the application with your Google account

### 2. Create Templates
- Click "Create Template" to build email templates
- Add dynamic variables like `{{Name}}`, `{{Company}}`, etc.
- Write your email subject and content
- Use the variable buttons to insert dynamic content

### 3. Mail Merge
- Click "Start Mail Merge"
- Upload your CSV file with contact information
- Select a template to use
- Preview how emails will look for each contact
- Send personalized emails to all contacts

## CSV Format

Your CSV should have headers that match your template variables. For example:

```csv
Name,Company,Email
John Doe,Acme Corp,john@acme.com
Jane Smith,Tech Inc,jane@tech.com
```

## Development

- Built with React 19 and TypeScript
- Styled with Tailwind CSS
- Uses React Router for navigation
- Google OAuth integration with @react-oauth/google

## Build for Production

```bash
npm run build
```

This creates a `build` folder with optimized production files.

## Project Structure

```
src/
├── App.tsx              # Main app with routing
├── pages/
│   ├── LandingPage.tsx  # Homepage with Google sign-in
│   ├── TemplateCreator.tsx # Template creation interface
│   └── MailMerge.tsx    # CSV upload and mail merge
└── index.tsx            # App entry point
```

## Notes

- This is a frontend-only implementation
- Templates and email sending are simulated
- In production, you'll need to connect to your backend API
- Google OAuth client ID must be configured before use
