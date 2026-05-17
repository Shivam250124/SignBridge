# SignBridge

Real-time 2-way communication platform for deaf and hearing individuals.

## What It Does

- **Deaf → Hearing** — Show ISL hand gestures to the camera. They're recognised instantly and spoken aloud.
- **Hearing → Deaf** — Speak or type a phrase. A matching sign language video plays immediately.

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start the server
python3 run.py

# 3. Open in browser (Chrome recommended)
open http://localhost:8000
```

## Features

| Feature | Detail |
|---|---|
| Gesture recognition | 99%+ accuracy, 15 ISL gestures |
| Speech-to-sign | 9 sign language videos |
| Text-to-speech | Browser Web Speech API |
| Conversation history | Save as .txt file |
| Live camera stream | 30+ FPS |

## Supported Gestures

**One-handed (10):** C, I, 1, 2, 3, HELLO, BYE, GOOD, THANK YOU, WELCOME

**Two-handed (5):** A, B, D, T, X

## Project Structure

```
SignBridge/
├── backend/                  # Flask application
│   ├── app.py                # App factory
│   ├── config.py             # Configuration
│   ├── routes/
│   │   ├── main.py           # Page routes
│   │   └── api.py            # REST API (8 endpoints)
│   └── services/
│       ├── gesture_recognizer.py   # MediaPipe + ML inference
│       ├── video_matcher.py        # Speech-to-video matching
│       └── text_to_speech.py       # TTS service
├── frontend/
│   ├── templates/            # Jinja2 HTML templates
│   │   ├── base.html
│   │   ├── index.html
│   │   └── communicate.html
│   └── static/
│       ├── css/              # Styles
│       ├── js/               # Client-side logic
│       └── img/              # Favicon & assets
├── models/                   # Trained ML models
│   ├── one_handed_model.pkl
│   ├── two_handed_model.pkl
│   └── gesture_config.json
├── dataset/csv/              # Training data CSVs
├── Speech to Sign  /videos1/ # Sign language video files
├── run.py                    # Entry point
├── .env                      # Local config (not in git)
└── requirements.txt
```

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/health` | Server health check |
| GET | `/api/available-gestures` | List all 15 gestures |
| GET | `/api/available-videos` | List all 9 videos |
| POST | `/api/process-speech` | Match text to sign video |
| GET | `/api/current-gesture` | Get live gesture state |
| POST | `/api/reset-gesture-buffer` | Reset prediction buffer |
| GET | `/video-feed` | MJPEG camera stream |
| GET | `/videos/<filename>` | Serve sign video file |

## Configuration

Copy `.env.example` to `.env` and adjust:

```bash
DEBUG=True
PORT=8000
HOST=0.0.0.0
GESTURE_CONFIDENCE_THRESHOLD=0.6
```

## Browser Support

| Browser | Gesture Recognition | Speech Recognition |
|---|---|---|
| Chrome | ✅ | ✅ |
| Edge | ✅ | ✅ |
| Safari | ✅ | ⚠️ Limited |
| Firefox | ✅ | ❌ |

## ML Model Details

- **Algorithm:** Random Forest (150 estimators, max depth 12)
- **Training data:** 2,387 samples across 15 gestures
- **One-handed model:** 63 features (21 landmarks × 3 axes)
- **Two-handed model:** 126 features (42 landmarks × 3 axes)
- **Accuracy:** 99%+ on test set

## Deployment

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for full step-by-step instructions.

**Quick deploy to Render:**
1. Push this repo to GitHub
2. Connect repo on [render.com](https://render.com) — `render.yaml` handles the rest
3. Set `DEPLOYMENT_MODE=cloud`, `DEBUG=False`, and a strong `SECRET_KEY` in the dashboard
4. Done — your app is live at `https://signbridge.onrender.com`

> **Note:** In cloud mode the server-side camera stream is disabled. Gesture recognition runs via the `/api/recognize-gesture` endpoint, with the browser sending webcam frames over WebRTC.
