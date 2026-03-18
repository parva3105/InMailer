# InMailer

A full-stack mail merge SaaS app. Create email templates with variable placeholders, upload a CSV of contacts, preview the merge, and send personalized bulk emails via the Gmail API.

**Live:** [inmailer.vercel.app](https://inmailer.vercel.app) — Backend on [Render](https://inmailer.onrender.com)

---

## Project Structure

```
mail_merge_kit/
├── Backend/              # Flask API (deployed on Render)
│   ├── app_db.py         # Main application + all routes
│   ├── db/               # SQLAlchemy models & services
│   ├── lib/              # OAuth helpers, app factory
│   ├── mail_merge.py     # Template variable substitution
│   ├── contact_processor.py  # CSV parsing
│   ├── render.yaml       # Render.com deployment config
│   ├── wsgi.py           # Gunicorn entry point
│   └── requirements.txt
├── frontend/             # React + TypeScript (deployed on Vercel)
│   └── src/
│       ├── pages/        # Dashboard, Templates, Merge, TestEmail, etc.
│       ├── components/   # ProtectedRoute, shared UI
│       └── contexts/     # Auth context
├── inmailer.db           # Local SQLite (dev only)
└── start_local.bat       # One-click local dev launcher (Windows)
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 19, TypeScript, TailwindCSS, React Router 7 |
| Backend | Flask 3, SQLAlchemy 2, Google OAuth 2.0 + Gmail API |
| Database | SQLite (dev) / PostgreSQL via Neon (prod) |
| Auth | Google OAuth 2.0 — session-based cookies |
| Deploy | Frontend → Vercel, Backend → Render.com |

---

## Core Features

- Google OAuth sign-in (Gmail API scopes for sending)
- User-scoped template CRUD with optional file attachments
- Variable placeholders: `${FirstName}`, `$company`, `$First-Name` — case-insensitive, normalized matching
- CSV upload → merge preview (first 5 contacts)
- Bulk send via Gmail API with per-recipient personalization
- Email send history and dashboard stats
- User registration limit (`MAX_FREE_USERS` env var)

---

## Run Locally

**1. Backend**
```bash
cd Backend
pip install -r requirements.txt
python start_server_db.py
```

**2. Frontend**
```bash
cd frontend
npm install
npm start
```

**3. Open**
- Frontend: `http://localhost:3001`
- Backend health: `http://localhost:5000/api/health`

Or on Windows, double-click `start_local.bat` to launch both.

---

## Environment Variables

### Backend — `Backend/.env`

| Variable | Description |
|----------|-------------|
| `GOOGLE_CLIENT_ID` | Google Cloud Console OAuth client ID |
| `GOOGLE_CLIENT_SECRET` | Google Cloud Console OAuth client secret |
| `GOOGLE_REDIRECT_URI` | `http://localhost:5000/auth/google/callback` (local) |
| `FRONTEND_URL` | `http://localhost:3001` (local) |
| `SECRET_KEY` | Flask session encryption key |
| `DATABASE_URL` | Optional — defaults to `sqlite:///inmailer.db` |
| `MAX_FREE_USERS` | Max allowed registrations (default: 50) |

### Frontend — `frontend/.env.local`

| Variable | Description |
|----------|-------------|
| `REACT_APP_API_URL` | `http://localhost:5000` (local) |
| `REACT_APP_GOOGLE_CLIENT_ID` | Same Google OAuth client ID |

---

## Deployment

### Backend (Render)
- Config: `Backend/render.yaml`
- Entry: `Backend/wsgi.py`
- Start command: `gunicorn app_db:app --bind 0.0.0.0:$PORT --workers 1 --timeout 120`
- Database: PostgreSQL via Neon (`DATABASE_URL` env var)

### Frontend (Vercel)
- Root directory: `frontend/`
- Production API URL set via `REACT_APP_API_URL` env var in Vercel dashboard

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/auth/google` | Initiate Google OAuth |
| GET | `/auth/google/callback` | OAuth callback |
| GET | `/auth/user` | Current user info |
| GET | `/auth/logout` | Clear session |
| GET | `/api/templates` | List user templates |
| POST | `/api/templates` | Create template |
| PUT | `/api/templates/<id>` | Update template |
| DELETE | `/api/templates/<id>` | Delete template |
| POST | `/api/mail-merge` | Preview merge (first 5 contacts) |
| POST | `/api/send-emails` | Send bulk emails |
| GET | `/api/dashboard/stats` | Dashboard overview |
| GET | `/api/health` | Health check |

---

## Known Limitations

- **Bulk sends are synchronous** — large CSVs (500+ rows) may hit the 120s Gunicorn timeout
- **No token auto-refresh** — Gmail access tokens expire ~1 hour; re-login required
- **Single Gunicorn worker** — not horizontally scalable in current config
- **No async job queue** — a Celery/RQ worker would be needed for high-volume sending
