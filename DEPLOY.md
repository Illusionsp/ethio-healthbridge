# Ethio-HealthBridge — Deployment Guide

## Quick Start (Local — for teammates)

### 1. Clone the repo
```bash
git clone <your-repo-url>
cd ethio-healthbridge
```

### 2. Backend setup
```bash
cd backend
pip install -r requirements.txt
```

Create `backend/.env`:
```
GEMINI_API_KEY=your_gemini_api_key_here
```
Get a free key at: https://aistudio.google.com/app/apikey

Ingest the MoH guidelines (one-time, takes ~15 min):
```bash
python scripts/ingest.py
```

Start the backend:
```bash
uvicorn main:app --port 8000 --reload
```

### 3. Frontend setup
```bash
cd ../frontend
npm install
npm run dev
```

Open http://localhost:3000

---

## Production Deployment

### Backend → Railway (free)

1. Go to https://railway.app and sign up
2. Click **New Project → Deploy from GitHub repo**
3. Select this repo, set **Root Directory** to `backend`
4. Add environment variable: `GEMINI_API_KEY=your_key`
5. Railway auto-detects the `Procfile` and deploys
6. Copy your Railway URL (e.g. `https://ethio-healthbridge.railway.app`)

> **Important:** The vector DB is not persisted on Railway free tier.
> You need to run `python scripts/ingest.py` locally and commit the
> `backend/data/vector_db/` folder, OR use Railway's persistent volume.

### Frontend → Vercel (free)

1. Go to https://vercel.com and sign up
2. Click **New Project → Import Git Repository**
3. Select this repo, set **Root Directory** to `frontend`
4. Add environment variable:
   ```
   NEXT_PUBLIC_API_URL=https://your-railway-url.railway.app
   ```
5. Click **Deploy**
6. Your app is live at `https://your-project.vercel.app`

---

## Environment Variables Summary

| Variable | Where | Value |
|---|---|---|
| `GEMINI_API_KEY` | backend `.env` / Railway | Your Gemini API key |
| `NEXT_PUBLIC_API_URL` | frontend `.env.local` / Vercel | Your Railway backend URL |

---

## Features to Evaluate

- Voice chat in Amharic, Afaan Oromoo, Tigrinya
- Text chat grounded in Ethiopian MoH Clinical Guidelines
- Medicine label scanner (upload a photo)
- Emergency red-flag detection (try saying "ደረት ህመም")
- Nearby health facility finder (uses your GPS)
- Child health mode (toggle in header)
- Symptom history (History page)
- Profile page
- Works offline (PWA — install from browser)

## Emergency Test
Type: `ደረት ህመም` — should trigger red flag with 912 call button.

## Voice Test
Click the mic button and say: `ራስ ምታት አለኝ` (I have a headache)
