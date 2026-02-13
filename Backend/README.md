# Backend (Flask API)

Main app file: `app_db.py`

## What it exposes

- `GET /api/health`
- `GET /api/templates`
- `POST /api/templates`
- `PUT /api/templates/<id>`
- `DELETE /api/templates/<id>`
- `POST /api/mail-merge` (CSV preview)
- `POST /api/send-emails` (bulk send)
- `POST /api/send-gmail` (single test email)
- `GET /api/user/stats`
- `GET /api/dashboard/stats`
- Auth routes:
  - `GET /auth/google`
  - `GET /auth/google/callback`
  - `GET /auth/user`
  - `GET /auth/logout`

## Local Run

```bash
pip install -r requirements.txt
python start_server_db.py
```

## Notes

- DB defaults to `sqlite:///inmailer.db` if `DATABASE_URL` is not set.
- OAuth and Gmail sending require valid Google credentials in environment variables.
- Sessions are cookie-based and CORS is configured for local + production frontend origins.
