"""
Gesture Recognition Service
Uses mediapipe Hands via the legacy solutions API (0.10.x compatible shim)
or falls back to the new Tasks API for mediapipe >= 0.10.30.
"""

import cv2
import numpy as np
import joblib
import json
from collections import deque
from pathlib import Path


def _build_hands():
    """
    Return a hands detector using mediapipe 0.10.21 solutions API.
    """
    import mediapipe as mp

    hands = mp.solutions.hands.Hands(
        max_num_hands=2,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.7,
    )
    draw_utils = mp.solutions.drawing_utils
    hand_connections = mp.solutions.hands.HAND_CONNECTIONS
    return hands, draw_utils, hand_connections, "solutions"


class GestureRecognizer:
    """Real-time ISL gesture recognition service"""

    def __init__(self, models_path, config_path=None,
                 buffer_size=10, confidence_threshold=0.6):
        self.models_path = Path(models_path)
        self.buffer_size = buffer_size
        self.confidence_threshold = confidence_threshold

        # Load ML models
        self.one_handed_model = None
        self.two_handed_model = None
        self.one_handed_gestures = []
        self.two_handed_gestures = []
        self.load_models(config_path)

        # MediaPipe setup (version-agnostic)
        self.hands, self._draw_utils, self._hand_connections, self._api = \
            _build_hands()

        # Prediction smoothing
        self.prediction_buffer = deque(maxlen=buffer_size)

        # Current state
        self.current_gesture = "NO_HANDS"
        self.current_confidence = 0.0
        self.current_gesture_type = "none"
        self.num_hands_detected = 0

    # ------------------------------------------------------------------
    # Model loading
    # ------------------------------------------------------------------

    def load_models(self, config_path=None):
        """Load ML models and gesture configuration."""
        one_handed_path = self.models_path / "one_handed_model.pkl"
        if one_handed_path.exists():
            try:
                self.one_handed_model = joblib.load(one_handed_path)
                print("✅ One-handed model loaded")
            except Exception as e:
                print(f"⚠️  Error loading one-handed model: {e}")

        two_handed_path = self.models_path / "two_handed_model.pkl"
        if two_handed_path.exists():
            try:
                self.two_handed_model = joblib.load(two_handed_path)
                print("✅ Two-handed model loaded")
            except Exception as e:
                print(f"⚠️  Error loading two-handed model: {e}")

        if config_path is None:
            config_path = self.models_path / "gesture_config.json"

        if Path(config_path).exists():
            try:
                with open(config_path, "r") as f:
                    cfg = json.load(f)
                self.one_handed_gestures = cfg.get("one_handed", [])
                self.two_handed_gestures = cfg.get("two_handed", [])
                print(
                    f"✅ Gestures loaded: {len(self.one_handed_gestures)} "
                    f"one-handed, {len(self.two_handed_gestures)} two-handed"
                )
            except Exception as e:
                print(f"⚠️  Error loading configuration: {e}")

    # ------------------------------------------------------------------
    # Landmark extraction
    # ------------------------------------------------------------------

    def extract_landmarks(self, results):
        """Extract hand landmarks from MediaPipe results."""
        multi = getattr(results, "multi_hand_landmarks", None)
        if not multi:
            return None, None, 0

        num_hands = len(multi)
        all_landmarks = []
        for hand_landmarks in multi:
            for lm in hand_landmarks.landmark:
                all_landmarks.extend([lm.x, lm.y, lm.z])

        one_handed_features = None
        if num_hands == 1 and len(all_landmarks) >= 63:
            one_handed_features = np.array(all_landmarks[:63]).reshape(1, -1)
        elif num_hands == 2 and len(all_landmarks) == 126:
            one_handed_features = np.array(all_landmarks[63:126]).reshape(1, -1)

        two_handed_features = None
        if num_hands == 2 and len(all_landmarks) == 126:
            two_handed_features = np.array(all_landmarks).reshape(1, -1)

        return one_handed_features, two_handed_features, num_hands

    # ------------------------------------------------------------------
    # Prediction
    # ------------------------------------------------------------------

    def predict_gesture(self, one_handed_features, two_handed_features, num_hands):
        """Predict gesture from extracted features."""
        predictions = []

        if self.one_handed_model and one_handed_features is not None and num_hands == 1:
            try:
                pred = self.one_handed_model.predict(one_handed_features)[0]
                prob = np.max(
                    self.one_handed_model.predict_proba(one_handed_features)[0]
                )
                predictions.append((pred, prob, "one_handed"))
            except Exception:
                pass

        if self.two_handed_model and two_handed_features is not None and num_hands == 2:
            try:
                pred = self.two_handed_model.predict(two_handed_features)[0]
                prob = np.max(
                    self.two_handed_model.predict_proba(two_handed_features)[0]
                )
                predictions.append((pred, prob, "two_handed"))
            except Exception:
                pass

        if predictions:
            best = max(predictions, key=lambda x: x[1])
            return best[0], best[1], best[2]

        return None, 0.0, "none"

    def smooth_prediction(self, prediction):
        """Temporal smoothing of predictions."""
        if prediction is None:
            return "NO_PREDICTION"

        self.prediction_buffer.append(prediction)

        if len(self.prediction_buffer) < 5:
            return "DETECTING..."

        preds = list(self.prediction_buffer)
        unique, counts = np.unique(preds, return_counts=True)
        idx = np.argmax(counts)
        confidence = counts[idx] / len(preds)
        return unique[idx] if confidence >= self.confidence_threshold else "UNCERTAIN"

    # ------------------------------------------------------------------
    # Frame processing
    # ------------------------------------------------------------------

    def process_frame(self, frame):
        """Process a single BGR frame and return gesture info."""
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb)

        one_handed_features, two_handed_features, num_hands = \
            self.extract_landmarks(results)
        self.num_hands_detected = num_hands

        if num_hands > 0:
            gesture, confidence, gesture_type = self.predict_gesture(
                one_handed_features, two_handed_features, num_hands
            )
            if gesture:
                self.current_gesture = self.smooth_prediction(gesture)
                self.current_confidence = confidence
                self.current_gesture_type = gesture_type
            else:
                self.current_gesture = "NO_PREDICTION"
                self.current_confidence = 0.0
                self.current_gesture_type = "none"
        else:
            self.current_gesture = "NO_HANDS"
            self.current_confidence = 0.0
            self.current_gesture_type = "none"

        return {
            "gesture": self.current_gesture,
            "confidence": float(self.current_confidence),
            "gesture_type": self.current_gesture_type,
            "num_hands": num_hands,
            "hand_landmarks": getattr(results, "multi_hand_landmarks", None),
        }

    def draw_landmarks(self, frame, hand_landmarks):
        """Draw hand landmarks on frame (local dev only)."""
        if hand_landmarks and self._draw_utils:
            for landmarks in hand_landmarks:
                self._draw_utils.draw_landmarks(
                    frame, landmarks, self._hand_connections
                )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def reset_buffer(self):
        self.prediction_buffer.clear()

    def get_available_gestures(self):
        return {
            "one_handed": self.one_handed_gestures,
            "two_handed": self.two_handed_gestures,
            "total": len(self.one_handed_gestures) + len(self.two_handed_gestures),
        }

    def get_current_state(self):
        return {
            "gesture": self.current_gesture,
            "confidence": float(self.current_confidence),
            "gesture_type": self.current_gesture_type,
            "num_hands": self.num_hands_detected,
        }

    def cleanup(self):
        if self.hands:
            try:
                self.hands.close()
            except Exception:
                pass
