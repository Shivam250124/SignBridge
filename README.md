# 🌉 SignBridge

**Bridging the communication gap between the hearing and deaf/hard-of-hearing communities using real-time Indian Sign Language (ISL) recognition and speech-to-sign translation.**

🔗 **Live Demo:** [https://signbridge-zouc.onrender.com](https://signbridge-zouc.onrender.com)

---

## What is SignBridge?

SignBridge is a two-way communication tool that works entirely in your browser — no app install, no plugins required.

It solves a real problem: most sign language tools only go one direction. SignBridge does both:

- **Sign → Text:** Point your webcam at your hands. The app recognizes your ISL gesture in real time and displays the word.
- **Speech → Sign:** Speak or type a word/phrase. The app plays the matching ISL sign language video instantly.

This makes it useful for both deaf/hard-of-hearing users signing to hearing people, and hearing people trying to communicate back.

---

## What Makes It Different

| Feature | SignBridge | Typical tools |
|---|---|---|
| Two-way communication | ✅ Both directions | ❌ Usually one-way |
| Works in browser | ✅ No install needed | ❌ Often requires app |
| Real-time gesture recognition | ✅ Live webcam feed | ❌ Often image upload |
| Speech to sign video | ✅ Speaks and matches video | ❌ Rarely included |
| Cloud + local mode | ✅ Dual deployment support | ❌ Usually local only |
| Conversation history | ✅ Tracks full session | ❌ Usually single query |

The gesture recognition uses a **dual ML model system** — separate models for one-handed and two-handed signs — which improves accuracy compared to a single combined model.

---

## How to Test It

Visit the live app: [https://signbridge-zouc.onrender.com](https://signbridge-zouc.onrender.com)

> ⚠️ The free tier sleeps after 15 minutes of inactivity. First load may take ~30 seconds to wake up.

### Test Gesture Recognition (Sign → Text)
1. Click **Start Camera** and allow webcam access (requires HTTPS — already handled)
2. Show one of the supported ISL gestures to your camera
3. The recognized gesture and confidence score appear in real time

### Test Speech to Sign (Speech → Sign)
1. Click the **microphone button** or type in the text box
2. Say or type one of the supported phrases (see list below)
3. The matching ISL sign language video plays automatically

### Check API Health
```
GET https://signbridge-zouc.onrender.com/api/health
```

---

## Supported Gestures (15 total)

The ML models are trained on ISL hand landmarks captured via MediaPipe.

**One-handed gestures (10):**

| Gesture | Type |
|---|---|
| HELLO | Greeting |
| THANK YOU | Courtesy |
| BYE | Farewell |
| WELCOME | Courtesy |
| GOOD | Expression |
| I | Pronoun |
| C | Alphabet |
| 1 | Number |
| 2 | Number |
| 3 | Number |

**Two-handed gestures (5):**

| Gesture | Type |
|---|---|
| A | Alphabet |
| B | Alphabet |
| D | Alphabet |
| T | Alphabet |
| X | Alphabet |

---

## Sign Language Videos (9 total)

These play when you speak or type the matching phrase:

| Phrase | Video |
|---|---|
| Hello | Hello.mp4 |
| Thank You | Thank You.mp4 |
| Sorry | Sorry.mp4 |
| Bad | Bad.mp4 |
| Big | Big.mp4 |
| Angry | Angry.mp4 |
| I am fine | I am fine.mp4 |
| Hello how are you | Hello how are you.mp4 |
| What is your name | What Is Your Name.mp4 |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11, Flask 3.0 |
| ML / Hand Tracking | MediaPipe 0.10.21, scikit-learn |
| Computer Vision | OpenCV (headless) |
| Frontend | HTML, CSS, Vanilla JS |
| Camera (cloud) | WebRTC — browser captures frames, sends as base64 |
| Camera (local) | OpenCV server-side MJPEG stream |
| Deployment | Render (free tier) |
| Server | Gunicorn |

---

## Run Locally

```bash
# Clone
git clone https://github.com/Shivam250124/SignBridge.git
cd SignBridge

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy env file
cp .env.example .env

# Run
python run.py
```

App runs at `http://localhost:8000`

In local mode the server opens your webcam directly. In cloud mode the browser handles the webcam via WebRTC.

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/health` | Health check |
| GET | `/api/available-gestures` | List all supported gestures |
| GET | `/api/available-videos` | List all sign videos |
| POST | `/api/recognize-gesture` | Recognize gesture from base64 image frame |
| POST | `/api/process-speech` | Find sign video matching text input |
| GET | `/api/current-gesture` | Get current gesture state |
| POST | `/api/reset-gesture-buffer` | Reset prediction smoothing buffer |

---

## Project Structure

```
SignBridge/
├── backend/
│   ├── app.py                  # Flask app factory
│   ├── config.py               # Configuration
│   ├── routes/
│   │   ├── api.py              # REST API endpoints
│   │   └── main.py             # Page routes
│   └── services/
│       ├── gesture_recognizer.py  # MediaPipe + ML inference
│       ├── video_matcher.py       # Speech-to-sign matching
│       └── text_to_speech.py      # TTS service
├── frontend/
│   ├── static/                 # CSS, JS, images
│   └── templates/              # HTML templates
├── models/
│   ├── one_handed_model.pkl    # One-handed gesture classifier
│   ├── two_handed_model.pkl    # Two-handed gesture classifier
│   └── gesture_config.json     # Gesture labels config
├── Speech to Sign  /
│   └── videos1/                # ISL sign videos (.mp4)
├── requirements.txt
├── render.yaml
└── Procfile
```

---

## License

MIT License — free to use, modify, and distribute.
