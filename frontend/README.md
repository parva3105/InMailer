# Frontend (React)

The frontend is a React + TypeScript app for:
- Google sign-in flow
- Dashboard metrics
- Template management
- CSV upload + preview
- Bulk email send
- Test email send

## Run

```bash
npm install
npm start
```

Set `REACT_APP_API_URL` in `.env.local` for backend base URL (for local: `http://localhost:5000`).

## Main Routes

- `/` landing
- `/signin` and `/signup`
- `/auth/success` OAuth landing
- `/dashboard` (protected)
- `/templates` (protected)
- `/merge` (protected)
- `/test-email` (protected)
