# 🚀 SignBridge Deployment Guide

This guide covers deploying SignBridge to **Render** (recommended), **Railway**, or **Heroku**.

---

## Prerequisites

- Git repository with all files committed (including `models/*.pkl` and videos)
- GitHub account
- Account on your chosen platform

---

## Option 1: Render (Recommended — Free Tier Available)

### 1. Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit — SignBridge"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/signbridge.git
git push -u origin main
```

### 2. Deploy on Render

1. Go to [https://render.com](https://render.com) and sign in with GitHub
2. Click **New +** → **Web Service**
3. Connect your `signbridge` repository
4. Render will auto-detect `render.yaml` — click **Apply**
5. Or configure manually:
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn "backend.app:create_app()" --bind 0.0.0.0:$PORT --workers 1 --threads 4 --timeout 120 --preload`

### 3. Set Environment Variables on Render

In the Render dashboard → your service → **Environment**:

| Key | Value |
|-----|-------|
| `DEPLOYMENT_MODE` | `cloud` |
| `DEBUG` | `False` |
| `SECRET_KEY` | *(generate: `python3 -c "import secrets; print(secrets.token_hex(32))"`)* |
| `TTS_ENABLED` | `False` |

> `PORT` is set automatically by Render — do not add it manually.

### 4. Deploy

Click **Create Web Service**. Render will build and deploy in ~5 minutes.

Your app will be live at: `https://signbridge.onrender.com`

---

## Option 2: Railway

### 1. Push to GitHub (same as above)

### 2. Deploy on Railway

1. Go to [https://railway.app](https://railway.app) and sign in with GitHub
2. Click **New Project** → **Deploy from GitHub repo**
3. Select your `signbridge` repository
4. Railway auto-detects the `Procfile` and deploys

### 3. Set Environment Variables on Railway

In the Railway dashboard → your service → **Variables**:

| Key | Value |
|-----|-------|
| `DEPLOYMENT_MODE` | `cloud` |
| `DEBUG` | `False` |
| `SECRET_KEY` | *(generate a random hex string)* |
| `TTS_ENABLED` | `False` |

### 4. Get Your URL

Railway assigns a URL like: `https://signbridge.up.railway.app`

---

## Option 3: Heroku

### 1. Install Heroku CLI

```bash
brew tap heroku/brew && brew install heroku
```

### 2. Login and Create App

```bash
heroku login
heroku create signbridge-app
```

### 3. Set Environment Variables

```bash
heroku config:set DEPLOYMENT_MODE=cloud
heroku config:set DEBUG=False
heroku config:set SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
heroku config:set TTS_ENABLED=False
```

### 4. Push and Deploy

```bash
git push heroku main
heroku open
```

---

## Post-Deployment Checklist

- [ ] App loads at the public URL
- [ ] Landing page renders correctly
- [ ] `/api/health` returns `{"status": "healthy"}`
- [ ] Gesture recognition works (browser sends frames via WebRTC)
- [ ] Speech input finds matching videos
- [ ] Videos play correctly
- [ ] HTTPS is active (required for camera/microphone access)

---

## Troubleshooting

### Build fails with `libGL` error
Make sure `requirements.txt` uses `opencv-python-headless` (not `opencv-python`). ✅ Already fixed.

### App crashes on startup — models not found
Ensure `models/one_handed_model.pkl` and `models/two_handed_model.pkl` are committed to git.
Check `.gitignore` — the `models/*.pkl` line must be commented out. ✅ Already fixed.

### Videos not found
The `Speech to Sign  /videos1/` folder (note the two trailing spaces) must be committed.
Verify with: `git ls-files | grep videos`

### Camera/microphone not working
Cloud deployments require **HTTPS**. Render, Railway, and Heroku all provide free SSL — ensure you're accessing via `https://`.

### App sleeps after inactivity (Render free tier)
Free tier services spin down after 15 minutes of inactivity. First request after sleep takes ~30 seconds.
Use [UptimeRobot](https://uptimerobot.com) (free) to ping your app every 10 minutes to keep it awake.

---

## Architecture in Cloud Mode

In `DEPLOYMENT_MODE=cloud`:
- The server-side MJPEG camera stream (`/video-feed`) is **disabled**
- Gesture recognition uses the `/api/recognize-gesture` endpoint
- The browser captures webcam frames via WebRTC and sends them as base64 to the API
- All other features (speech input, video playback, conversation history) work identically

---

## Monitoring (Optional)

### Uptime Monitoring — UptimeRobot (Free)
1. Sign up at [https://uptimerobot.com](https://uptimerobot.com)
2. Add a new HTTP monitor pointing to `https://your-app.onrender.com/api/health`
3. Get email alerts if the app goes down

### Error Tracking — Sentry (Free Tier)
```bash
pip install sentry-sdk[flask]==1.39.1
```

Add to `backend/app.py` after imports:
```python
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

sentry_sdk.init(
    dsn=os.getenv('SENTRY_DSN', ''),
    integrations=[FlaskIntegration()],
    traces_sample_rate=0.1
)
```

Set `SENTRY_DSN` as an environment variable on your platform.
