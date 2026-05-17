"""
Gesture Recognition Service
Refactored from predict_gestures.py for web application use
"""

import cv2
import mediapipe as mp
import numpy as np
import joblib
import json
from collections import deque
from pathlib import Path


class GestureRecognizer:
    """Real-time ISL gesture recognition service"""
    
    def __init__(self, models_path, config_path=None, buffer_size=10, confidence_threshold=0.6):
        """
        Initialize gesture recognizer
        
        Args:
            models_path: Path to models directory
            config_path: Path to gesture config JSON (optional)
            buffer_size: Size of prediction smoothing buffer
            confidence_threshold: Minimum confidence for predictions
        """
        self.models_path = Path(models_path)
        self.buffer_size = buffer_size
        self.confidence_threshold = confidence_threshold
        
        # Load models
        self.one_handed_model = None
        self.two_handed_model = None
        self.one_handed_gestures = []
        self.two_handed_gestures = []
        self.load_models(config_path)
        
        # MediaPipe setup
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            max_num_hands=2,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )
        self.mp_draw = mp.solutions.drawing_utils
        
        # Prediction smoothing
        self.prediction_buffer = deque(maxlen=buffer_size)
        
        # Current state
        self.current_gesture = "NO_HANDS"
        self.current_confidence = 0.0
        self.current_gesture_type = "none"
        self.num_hands_detected = 0
    
    def load_models(self, config_path=None):
        """Load ML models and configuration"""
        
        # Load one-handed model
        one_handed_path = self.models_path / "one_handed_model.pkl"
        if one_handed_path.exists():
            try:
                self.one_handed_model = joblib.load(one_handed_path)
                print(f"✅ One-handed model loaded")
            except Exception as e:
                print(f"⚠️  Error loading one-handed model: {e}")
        
        # Load two-handed model
        two_handed_path = self.models_path / "two_handed_model.pkl"
        if two_handed_path.exists():
            try:
                self.two_handed_model = joblib.load(two_handed_path)
                print(f"✅ Two-handed model loaded")
            except Exception as e:
                print(f"⚠️  Error loading two-handed model: {e}")
        
        # Load configuration
        if config_path is None:
            config_path = self.models_path / "gesture_config.json"
        
        if Path(config_path).exists():
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                self.one_handed_gestures = config.get('one_handed', [])
                self.two_handed_gestures = config.get('two_handed', [])
                print(f"✅ Gestures loaded: {len(self.one_handed_gestures)} one-handed, {len(self.two_handed_gestures)} two-handed")
            except Exception as e:
                print(f"⚠️  Error loading configuration: {e}")
    
    def extract_landmarks(self, results):
        """Extract hand landmarks from MediaPipe results"""
        if not results.multi_hand_landmarks:
            return None, None, 0
        
        num_hands = len(results.multi_hand_landmarks)
        all_landmarks = []
        
        for hand_landmarks in results.multi_hand_landmarks:
            for lm in hand_landmarks.landmark:
                all_landmarks.extend([lm.x, lm.y, lm.z])
        
        # One-handed features
        one_handed_features = None
        if num_hands == 1 and len(all_landmarks) >= 63:
            one_handed_features = np.array(all_landmarks[:63]).reshape(1, -1)
        elif num_hands == 2 and len(all_landmarks) == 126:
            one_handed_features = np.array(all_landmarks[63:126]).reshape(1, -1)
        
        # Two-handed features
        two_handed_features = None
        if num_hands == 2 and len(all_landmarks) == 126:
            two_handed_features = np.array(all_landmarks).reshape(1, -1)
        
        return one_handed_features, two_handed_features, num_hands
    
    def predict_gesture(self, one_handed_features, two_handed_features, num_hands):
        """Predict gesture from features"""
        predictions = []
        
        if self.one_handed_model and one_handed_features is not None and num_hands == 1:
            try:
                pred = self.one_handed_model.predict(one_handed_features)[0]
                prob = np.max(self.one_handed_model.predict_proba(one_handed_features)[0])
                predictions.append((pred, prob, "one_handed"))
            except:
                pass
        
        if self.two_handed_model and two_handed_features is not None and num_hands == 2:
            try:
                pred = self.two_handed_model.predict(two_handed_features)[0]
                prob = np.max(self.two_handed_model.predict_proba(two_handed_features)[0])
                predictions.append((pred, prob, "two_handed"))
            except:
                pass
        
        if predictions:
            best_pred = max(predictions, key=lambda x: x[1])
            return best_pred[0], best_pred[1], best_pred[2]
        
        return None, 0.0, "none"
    
    def smooth_prediction(self, prediction):
        """Smooth predictions using temporal filtering"""
        if prediction is None:
            return "NO_PREDICTION"
        
        self.prediction_buffer.append(prediction)
        
        if len(self.prediction_buffer) < 5:
            return "DETECTING..."
        
        predictions = list(self.prediction_buffer)
        unique, counts = np.unique(predictions, return_counts=True)
        most_common_idx = np.argmax(counts)
        most_common = unique[most_common_idx]
        confidence = counts[most_common_idx] / len(predictions)
        
        return most_common if confidence >= self.confidence_threshold else "UNCERTAIN"
    
    def process_frame(self, frame):
        """Process a single frame and recognize gesture"""
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb)
        
        one_handed_features, two_handed_features, num_hands = self.extract_landmarks(results)
        self.num_hands_detected = num_hands
        
        if num_hands > 0:
            gesture, confidence, gesture_type = self.predict_gesture(
                one_handed_features, two_handed_features, num_hands)
            
            if gesture:
                smoothed_gesture = self.smooth_prediction(gesture)
                self.current_gesture = smoothed_gesture
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
            'gesture': self.current_gesture,
            'confidence': float(self.current_confidence),
            'gesture_type': self.current_gesture_type,
            'num_hands': num_hands,
            'hand_landmarks': results.multi_hand_landmarks
        }
    
    def draw_landmarks(self, frame, hand_landmarks):
        """Draw hand landmarks on frame"""
        if hand_landmarks:
            for landmarks in hand_landmarks:
                self.mp_draw.draw_landmarks(
                    frame, landmarks, self.mp_hands.HAND_CONNECTIONS)
    
    def reset_buffer(self):
        """Reset prediction buffer"""
        self.prediction_buffer.clear()
    
    def get_available_gestures(self):
        """Get list of available gestures"""
        return {
            'one_handed': self.one_handed_gestures,
            'two_handed': self.two_handed_gestures,
            'total': len(self.one_handed_gestures) + len(self.two_handed_gestures)
        }
    
    def get_current_state(self):
        """Get current recognition state"""
        return {
            'gesture': self.current_gesture,
            'confidence': float(self.current_confidence),
            'gesture_type': self.current_gesture_type,
            'num_hands': self.num_hands_detected
        }
    
    def cleanup(self):
        """Cleanup resources"""
        if self.hands:
            self.hands.close()
