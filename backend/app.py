"""
SignBridge Flask Application
Main application factory
"""

from flask import Flask, Response
import cv2
from backend.config import config
from backend.services import GestureRecognizer, VideoMatcher, TextToSpeechService
from backend.routes import main_bp, api_bp
from backend.routes.api import init_services


def create_app():
    """Create and configure Flask application"""

    app = Flask(
        __name__,
        template_folder=str(config.TEMPLATES_PATH),
        static_folder=str(config.STATIC_PATH)
    )

    app.config['SECRET_KEY']          = config.SECRET_KEY
    app.config['MAX_CONTENT_LENGTH']  = 16 * 1024 * 1024  # 16 MB
    app.config['DEPLOYMENT_MODE']     = config.DEPLOYMENT_MODE

    config.print_config()

    try:
        config.validate()
    except FileNotFoundError as e:
        print(f"❌ Configuration error: {e}")
        return None

    # ── Services ──────────────────────────────────────────────
    print("\n🔧 Initializing services...")

    gesture_recognizer = GestureRecognizer(
        models_path=config.MODELS_PATH,
        buffer_size=config.PREDICTION_BUFFER_SIZE,
        confidence_threshold=config.GESTURE_CONFIDENCE_THRESHOLD
    )

    video_matcher = VideoMatcher(videos_path=config.VIDEOS_PATH)
    tts_service   = TextToSpeechService(enabled=config.TTS_ENABLED)

    init_services(gesture_recognizer, video_matcher, tts_service)

    app.gesture_recognizer = gesture_recognizer
    app.video_matcher      = video_matcher
    app.tts_service        = tts_service

    # ── Blueprints ────────────────────────────────────────────
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp)

    # ── Camera stream (local only) ────────────────────────────
    if not config.is_cloud():
        @app.route('/video-feed')
        def video_feed():
            return Response(
                generate_frames(gesture_recognizer),
                mimetype='multipart/x-mixed-replace; boundary=frame'
            )

    # ── Security headers ──────────────────────────────────────
    @app.after_request
    def add_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options']        = 'SAMEORIGIN'
        response.headers['X-XSS-Protection']       = '1; mode=block'
        response.headers['Referrer-Policy']        = 'strict-origin-when-cross-origin'
        return response

    print("\n✅ SignBridge ready!")
    print(f"   Gestures : {gesture_recognizer.get_available_gestures()['total']}")
    print(f"   Videos   : {len(video_matcher.get_all_videos())}")
    print(f"   Mode     : {config.DEPLOYMENT_MODE}")

    return app


def generate_frames(gesture_recognizer):
    """MJPEG stream with gesture recognition overlay (local dev only)"""
    camera = cv2.VideoCapture(config.CAMERA_INDEX)

    if not camera.isOpened():
        print("❌ Cannot open camera!")
        return

    try:
        while True:
            success, frame = camera.read()
            if not success:
                break

            frame  = cv2.flip(frame, 1)
            result = gesture_recognizer.process_frame(frame)

            if result['hand_landmarks']:
                gesture_recognizer.draw_landmarks(frame, result['hand_landmarks'])

            _draw_gesture_info(frame, result)

            ret, buffer = cv2.imencode('.jpg', frame)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
    finally:
        camera.release()


def _draw_gesture_info(frame, result):
    gesture    = result['gesture']
    confidence = result['confidence']
    num_hands  = result['num_hands']

    cv2.rectangle(frame, (10, 10), (400, 120), (0, 0, 0), -1)
    cv2.rectangle(frame, (10, 10), (400, 120), (255, 255, 255), 2)

    color = (0, 255, 0) if gesture not in ['NO_HANDS', 'DETECTING...', 'UNCERTAIN'] else (0, 165, 255)
    cv2.putText(frame, f"Gesture: {gesture}",       (20, 40),  cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
    cv2.putText(frame, f"Confidence: {confidence:.1%}", (20, 70),  cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    cv2.putText(frame, f"Hands: {num_hands}",       (20, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                (0, 255, 0) if num_hands > 0 else (0, 0, 255), 1)
