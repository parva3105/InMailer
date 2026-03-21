# InMailer

InMailer is a full-stack mail merge platform for sending personalized outreach emails at scale. It combines a React frontend, a Flask backend, Google OAuth for authentication, Gmail API based sending, and a SQLAlchemy-backed database for templates, users, and email activity.

This repository is suitable for two use cases:

- Product use: sign in with Google, create templates, upload a CSV, preview personalized emails, and send them in bulk.
- Engineering/demo use: inspect a clean example of a React + Flask + SQLAlchemy application with OAuth, session auth, file uploads, and email workflow orchestration.

## Table of Contents

- [What the Project Does](#what-the-project-does)
- [Core Capabilities](#core-capabilities)
- [How the Product Works](#how-the-product-works)
- [Architecture Overview](#architecture-overview)
- [Tech Stack](#tech-stack)
- [Repository Structure](#repository-structure)
- [Frontend Overview](#frontend-overview)
- [Backend Overview](#backend-overview)
- [Database Model](#database-model)
- [API Overview](#api-overview)
- [Local Development Setup](#local-development-setup)
- [Environment Variables](#environment-variables)
- [Deployment Notes](#deployment-notes)
- [Presentation Notes](#presentation-notes)
- [Known Limitations and Risks](#known-limitations-and-risks)

## What the Project Does

InMailer helps a user send customized emails to many recipients without manually editing each message.

The user workflow is:

1. Sign in with Google.
2. Create an email template with placeholders such as `${First_Name}` or `${Company}`.
3. Optionally attach a file such as a resume or portfolio.
4. Upload a CSV file containing recipient data.
5. Preview how the subject and body render for each contact.
6. Send emails through the user’s Gmail account.
7. Track sent and failed emails through dashboard statistics and logs.

This makes the project especially useful for:

- Job outreach campaigns
- Sales or partnership outreach
- Event invitations
- Personalized follow-up emails
- Any workflow where message structure is fixed but recipient details vary

## Core Capabilities

- Google OAuth sign-in and cookie-based session authentication
- User-specific template management
- Dynamic variable insertion inside subjects and email bodies
- CSV upload and parsing for contact lists
- Email preview before sending
- Bulk send through Gmail API
- Single test email screen for configuration validation
- Optional file attachment support on templates
- Dashboard statistics for templates and sent emails
- Email activity logging in the database
- User limit control for gated/free access
- Legacy mail merge CLI utilities in `Backend/mail_merge.py`

## How the Product Works

### 1. Authentication

The app uses Google OAuth to authenticate users. When a user signs in:

- the backend starts an OAuth flow using Google credentials
- Google returns an authorization code to the backend callback
- the backend exchanges the code for tokens
- user identity is fetched from Google
- the session stores the authenticated user and OAuth credentials
- the user record is created or updated in the database

The frontend then uses session-based requests with credentials enabled, so protected pages can load user-specific data.

### 2. Template Creation

Users create templates from the frontend template editor. A template contains:

- a template name
- a subject line
- a body
- a list of dynamic variables
- an optional attachment

Variables are inserted using placeholder syntax such as:

```txt
Hi ${First_Name},

I wanted to reach out regarding opportunities at ${Company}.
```

The backend stores templates per user, so each user only sees and manages their own templates.

### 3. CSV Upload and Preview

In the mail merge screen, the user uploads a CSV file of contacts. The frontend parses the file for quick display, and the backend also processes it for preview generation.

The preview step is important because it lets the user verify:

- the correct template is selected
- variables are being substituted properly
- the resulting subject line looks correct
- the message body reads naturally for each contact
- an attachment is associated if expected

The backend contains flexible variable replacement logic that attempts to handle multiple naming styles, including:

- `First_Name`
- `first_name`
- `First Name`
- `firstName`
- `Company`
- `company_name`

That normalization logic reduces CSV formatting friction during demos and real usage.

### 4. Sending Emails

When the user confirms the bulk send:

- the frontend submits the selected template and contact data
- the backend rebuilds Gmail credentials from the session
- each contact receives a rendered subject and body
- the Gmail API sends the email
- attachment metadata from the template is included when available
- each send attempt is logged as sent or failed

There is also a separate test-email page for sending one email manually before a campaign.

### 5. Dashboard and Logging

The dashboard presents operational visibility:

- number of templates
- number of emails sent
- orphaned email count

Orphaned emails are emails that still exist in logs even if the original template has been deleted. The code preserves those logs intentionally so history is not lost.

## Architecture Overview

At a high level, the system is split into two layers.

### Frontend

The React frontend is responsible for:

- routing
- authentication state management
- template creation UI
- CSV upload UI
- preview rendering
- triggering email sends
- showing dashboard stats

### Backend

The Flask backend is responsible for:

- Google OAuth flow
- session management
- template CRUD APIs
- file upload handling
- CSV processing
- variable replacement
- Gmail API integration
- database persistence
- stats and email history endpoints

### Data Layer

SQLAlchemy models define and persist:

- users
- templates
- email logs

SQLite is used by default for local development, while PostgreSQL can be used in deployment via `DATABASE_URL`.

## Tech Stack

### Frontend

- React 19
- TypeScript
- React Router
- Axios
- Tailwind CSS
- Lucide React icons
- Vercel Analytics

### Backend

- Python
- Flask
- Flask-CORS
- SQLAlchemy
- Alembic
- python-dotenv
- Google Auth libraries
- Google Gmail API client
- Requests
- Gunicorn

### External Integrations

- Google OAuth
- Gmail API
- Render for backend deployment
- Vercel-oriented frontend config patterns

## Repository Structure

```txt
mail_merge_kit/
├── Backend/
│   ├── app_db.py                # Main Flask application with routes and business logic
│   ├── mail_merge.py            # CLI-style mail merge utilities and template rendering helpers
│   ├── start_server_db.py       # Backend startup entrypoint for local dev
│   ├── wsgi.py                  # WSGI entry for deployment
│   ├── requirements.txt         # Python dependencies
│   ├── render.yaml              # Render deployment config
│   ├── lib/
│   │   ├── app_factory.py       # Flask app configuration and CORS/session setup
│   │   └── oauth.py             # OAuth helper logic
│   └── db/
│       ├── config.py            # Database engine/session configuration
│       ├── init_db.py           # Database initialization helpers
│       ├── models.py            # SQLAlchemy models
│       └── services.py          # Service layer for users, templates, and email logs
├── frontend/
│   ├── package.json             # Frontend dependencies and scripts
│   ├── public/                  # Static assets and legal pages
│   └── src/
│       ├── App.tsx              # App routes
│       ├── config.ts            # Frontend API config
│       ├── contexts/
│       │   └── AuthContext.tsx  # Session-aware auth state
│       ├── components/
│       │   └── ProtectedRoute.tsx
│       └── pages/
│           ├── LandingPage.tsx
│           ├── SignIn.tsx
│           ├── SignUp.tsx
│           ├── AuthSuccess.tsx
│           ├── Dashboard.tsx
│           ├── TemplateCreator.tsx
│           ├── MailMerge.tsx
│           └── TestEmail.tsx
├── Templates/                   # Template/attachment storage support
├── start_local.bat              # Windows launcher for local setup
├── PRIVACY_POLICY.md
├── TERMS_OF_SERVICE.md
└── README.md
```

## Frontend Overview

### Routing

The frontend routes defined in `frontend/src/App.tsx` include:

- `/` - landing page
- `/signin` - sign-in page
- `/signup` - sign-up page
- `/auth/success` - OAuth success redirect landing
- `/dashboard` - protected dashboard
- `/templates` - protected template creator/editor
- `/merge` - protected mail merge workflow
- `/test-email` - protected test email screen

Protected pages are wrapped in `ProtectedRoute`, which relies on `AuthContext`.

### Auth State

`frontend/src/contexts/AuthContext.tsx`:

- stores the current user in React state
- checks `/auth/user` on startup
- enables `withCredentials` on Axios requests
- supports sign-out via `/auth/logout`

### Dashboard

The dashboard provides:

- template count
- sent email count
- orphaned email count
- links to the main actions in the app

### Template Creator

The template editor supports:

- create and edit modes
- dynamic variable management
- inline variable insertion into content
- optional attachment upload
- attachment preservation when editing

### Mail Merge Screen

The mail merge page supports:

- CSV upload
- sample CSV download
- template selection
- preview generation
- template edit/delete shortcuts
- bulk send trigger

### Test Email Screen

The test-email page supports:

- recipient input
- subject/body customization
- optional attachment path
- direct send request to the backend

## Backend Overview

The main backend implementation lives in `Backend/app_db.py`. It contains route handlers and much of the application business logic.

### Key Backend Responsibilities

- initialize database and migrate legacy templates
- configure OAuth scopes and credentials
- normalize and replace template variables
- handle template CRUD
- process CSVs for preview generation
- send emails via Gmail API
- store and retrieve email logs
- expose health and debug endpoints
- enforce a max free-user limit

### App Configuration

`Backend/lib/app_factory.py` configures:

- Flask app creation
- secret key and session lifetime
- secure cookie settings for production
- local cookie settings for development
- CORS for frontend origins

### Template Rendering Logic

There are two template-related paths in the backend:

- `Backend/mail_merge.py` contains generic parsing/rendering helpers based on Python `string.Template`
- `Backend/app_db.py` contains broader replacement logic used by the web app, including normalization and semantic alias matching

This dual approach reflects the project’s evolution from a script-based mail merge utility into a database-backed web application.

### Email Sending

The primary send path uses the Gmail API. The code also includes SMTP and optional SendGrid helpers in `Backend/mail_merge.py`, which are useful as legacy or alternate sending utilities.

## Database Model

The database has three core entities.

### User

- `id`
- `email`
- `name`
- `password_hash`
- `is_google_user`
- `oauth_credentials`
- timestamps

### Template

- `id`
- `user_id`
- `name`
- `subject`
- `content`
- `variables`
- `attachment_path`
- `attachment_name`
- timestamps

### EmailLog

- `id`
- `user_id`
- `template_id`
- `recipient_email`
- `subject`
- `status`
- `error_message`
- `gmail_message_id`
- `sent_at`

### Relationship Behavior

- A user owns many templates.
- A user owns many email logs.
- A template can have many email logs.
- When a template is deleted, related email logs are preserved and `template_id` is set to `NULL`.

That last rule is important because it preserves historical analytics even after cleanup.

## API Overview

The backend exposes both product endpoints and debug/admin-style endpoints.

### Authentication Routes

- `GET /auth/google` - start Google OAuth flow
- `GET /auth/google/callback` - Google OAuth callback
- `GET /auth/user` - fetch authenticated user from session
- `GET /auth/logout` - clear session
- `GET /auth/force-reauth` - force reauthentication flow
- `GET /auth/validate-credentials` - validate stored Gmail credentials
- `GET /auth/debug-session` - inspect session state for debugging

### Template Routes

- `GET /api/templates` - list current user templates
- `POST /api/templates` - create template
- `PUT /api/templates/<id>` - update template
- `DELETE /api/templates/<id>` - delete template
- `POST /api/template-attachment` - handle attachment-specific upload flow

### Mail Merge and Email Routes

- `POST /api/mail-merge` - generate preview output from template + CSV
- `POST /api/send-emails` - send bulk emails
- `POST /api/send-gmail` - send a single test email

### Stats and System Routes

- `GET /api/user/stats` - user-level email statistics
- `GET /api/dashboard/stats` - dashboard summary
- `GET /api/user-limit-status` - registration capacity info
- `GET /api/health` - application/database health check

### Debug/Admin Routes

- `GET /api/debug/database`
- `POST /api/debug-csv`
- `GET /api/debug/credentials`
- `GET /api/admin/users`

These are useful in development and demos, but some would need stricter access control before production hardening.

## Local Development Setup

### Prerequisites

- Python 3.10+ recommended
- Node.js 18+ recommended
- npm
- A Google Cloud OAuth client configured for the app

### Option A: Start Manually

#### 1. Start the backend

```bash
cd Backend
pip install -r requirements.txt
python start_server_db.py
```

The backend runs on:

- `http://localhost:5000`

Health check:

- `http://localhost:5000/api/health`

#### 2. Start the frontend

```bash
cd frontend
npm install
npm start
```

The frontend runs on:

- `http://localhost:3001`

### Option B: Use the Windows launcher

From the repository root:

```bat
start_local.bat
```

This script:

- installs backend dependencies
- runs a backend local test script
- starts the backend in a new command window
- installs frontend dependencies
- starts the frontend in a new command window

## Environment Variables

### Backend `.env`

Place a `.env` file inside `Backend/`.

Required for the main web app:

```env
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_REDIRECT_URI=http://localhost:5000/auth/google/callback
FRONTEND_URL=http://localhost:3001
SECRET_KEY=replace_with_a_real_secret
```

Database configuration:

```env
DATABASE_URL=sqlite:///inmailer.db
```

Optional application controls:

```env
FLASK_ENV=development
MAX_FREE_USERS=50
```

Optional SMTP-style settings used by legacy/alternate send helpers:

```env
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER=your_email@example.com
EMAIL_PASSWORD=your_app_password
EMAIL_USE_SSL=false
EMAIL_USE_STARTTLS=true
SENDGRID_API_KEY=optional
RATE_LIMIT_SECONDS=2.0
```

### Frontend `.env.local`

Place a `.env.local` file inside `frontend/`.

```env
REACT_APP_API_URL=http://localhost:5000
REACT_APP_GOOGLE_CLIENT_ID=your_google_client_id
```

## Deployment Notes

The repository already includes backend deployment hints.

### Backend

- WSGI entrypoint: `Backend/wsgi.py`
- Render config: `Backend/render.yaml`
- Start command:

```bash
gunicorn app_db:app --bind 0.0.0.0:$PORT --workers 1 --timeout 120
```

### Frontend

The frontend is configured in a way that fits deployment behind a public API URL such as:

- `https://inmailer.onrender.com` for backend
- a Vercel-hosted frontend origin

Production CORS and cookie behavior are handled in the Flask app factory.

## Presentation Notes

If you need to explain the project in a meeting, this is a strong structure to use.

### 1. Problem Statement

"Sending personalized emails manually is slow and error-prone. InMailer solves that by letting users define one template and automatically personalize it for many recipients from CSV data."

### 2. Product Value

- saves time on repetitive outreach
- keeps personalization at scale
- centralizes templates and send history
- allows users to review output before sending
- uses Google authentication and Gmail sending instead of asking users to trust a separate mail server

### 3. Technical Highlights

- full-stack architecture with React and Flask
- secure Google OAuth login
- session-based protected routes
- SQLAlchemy persistence layer
- attachment-aware email templates
- preview-before-send workflow
- Gmail API integration instead of only SMTP
- logging and dashboard analytics

### 4. End-to-End Flow to Demonstrate

1. Sign in with Google.
2. Open the dashboard.
3. Create a template with variables like `${First_Name}` and `${Company}`.
4. Attach a sample file.
5. Upload a CSV.
6. Generate previews to show real personalization.
7. Send a test email or a bulk set.
8. Return to the dashboard and show updated stats.

### 5. Engineering Maturity Talking Points

- clear separation between frontend, backend, and database layers
- reusable service layer in `Backend/db/services.py`
- environment-driven configuration
- deployment entrypoints already present
- health and debug endpoints for troubleshooting
- preserved audit trail through `EmailLog`

## Known Limitations and Risks

These are worth acknowledging if asked during the meeting.

- `Backend/app_db.py` is large and centralizes many responsibilities; future refactoring into blueprints/services would improve maintainability.
- Several debug/admin endpoints appear intended for development and would need stronger access control for production.
- Some frontend text and console output suggest the project is still in active refinement rather than fully product-polished.
- CSV parsing on the frontend is basic and may not handle every quoting/escaping edge case.
- Gmail/API credential handling is functional, but OAuth/session behavior is an area that typically needs careful production testing.
- Attachment handling and file storage strategy may need hardening depending on deployment scale.

## Summary

InMailer is a practical, end-to-end personalized email automation platform. From a presentation perspective, its strength is that it is not just a UI prototype: it includes real authentication, persistent storage, template management, CSV-driven personalization, Gmail-based sending, and measurable activity tracking.

That makes it a strong project to present both as a usable product and as a full-stack engineering build.
