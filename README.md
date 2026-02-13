# InMailer

InMailer is a full-stack mail merge app:
- React frontend (`frontend/`)
- Flask backend (`Backend/`)
- SQLAlchemy database models/services (`Backend/db/`)

## Core Features

- Google OAuth sign-in
- User-scoped template CRUD
- CSV preview for personalized merge output
- Bulk send via Gmail API
- Email send logging and dashboard stats
- Optional attachment per template

## Run Locally

1. Backend
```bash
cd Backend
pip install -r requirements.txt
python start_server_db.py
```

2. Frontend
```bash
cd frontend
npm install
npm start
```

3. Open:
- Frontend: `http://localhost:3001`
- Backend health: `http://localhost:5000/api/health`

## Required Environment Variables

Backend (`Backend/.env`):
- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`
- `GOOGLE_REDIRECT_URI` (for local: `http://localhost:5000/auth/google/callback`)
- `FRONTEND_URL` (for local: `http://localhost:3001`)
- `SECRET_KEY`
- `DATABASE_URL` (optional; defaults to `sqlite:///inmailer.db`)

Frontend (`frontend/.env.local`):
- `REACT_APP_API_URL` (for local: `http://localhost:5000`)

## Deployment

- Backend WSGI entry: `Backend/wsgi.py`
- Render start command: `gunicorn app_db:app --bind 0.0.0.0:$PORT --workers 1 --timeout 120`
