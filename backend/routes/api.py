"""
API Routes - REST API endpoints
"""

from flask import Blueprint, request, jsonify, Response
import cv2
import base64
import numpy as np
from backend.config import config

api_bp = Blueprint('api', __name__, url_prefix='/api')

# Global services (will be initialized in app.py)
gesture_recognizer = None
video_matcher = None
tts_service = None


def init_services(gr, vm, tts):
    """Initialize services from app.py"""
    global gesture_recognizer, video_matcher, tts_service
    gesture_recognizer = gr
    video_matcher = vm
    tts_service = tts


@api_bp.route('/available-gestures', methods=['GET'])
def get_available_gestures():
    """Get list of supported gestures"""
    if not gesture_recognizer:
        return jsonify({'error': 'Gesture recognizer not initialized'}), 500
    
    gestures = gesture_recognizer.get_available_gestures()
    return jsonify({
        'success': True,
        'gestures': gestures
    })


@api_bp.route('/available-videos', methods=['GET'])
def get_available_videos():
    """Get list of available sign language videos"""
    if not video_matcher:
        return jsonify({'error': 'Video matcher not initialized'}), 500
    
    videos = video_matcher.get_all_videos()
    return jsonify({
        'success': True,
        'videos': videos,
        'total': len(videos)
    })


@api_bp.route('/process-speech', methods=['POST'])
def process_speech():
    """Process speech input and find matching sign video"""
    if not video_matcher:
        return jsonify({'error': 'Video matcher not initialized'}), 500
    
    data = request.get_json()
    text = data.get('text', '').strip()
    
    if not text:
        return jsonify({
            'success': False,
            'error': 'No text provided'
        }), 400
    
    # Find matching video
    video_info = video_matcher.find_video(text)
    
    if video_info:
        return jsonify({
            'success': True,
            'video': video_info['filename'],
            'video_url': f'/videos/{video_info["filename"]}',
            'normalized_name': video_info['normalized_name'],
            'match_type': video_info['match_type']
        })
    else:
        return jsonify({
            'success': False,
            'error': f'No matching video found for: {text}'
        }), 404


@api_bp.route('/recognize-gesture', methods=['POST'])
def recognize_gesture():
    """Recognize gesture from image frame"""
    if not gesture_recognizer:
        return jsonify({'error': 'Gesture recognizer not initialized'}), 500
    
    try:
        data = request.get_json()
        image_data = data.get('image', '')
        
        if not image_data:
            return jsonify({
                'success': False,
                'error': 'No image data provided'
            }), 400
        
        # Decode base64 image
        image_bytes = base64.b64decode(image_data.split(',')[1])
        nparr = np.frombuffer(image_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Process frame
        result = gesture_recognizer.process_frame(frame)
        
        return jsonify({
            'success': True,
            'gesture': result['gesture'],
            'confidence': result['confidence'],
            'gesture_type': result['gesture_type'],
            'num_hands': result['num_hands']
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route('/current-gesture', methods=['GET'])
def get_current_gesture():
    """Get current recognized gesture state"""
    if not gesture_recognizer:
        return jsonify({'error': 'Gesture recognizer not initialized'}), 500
    
    state = gesture_recognizer.get_current_state()
    return jsonify({
        'success': True,
        **state
    })


@api_bp.route('/reset-gesture-buffer', methods=['POST'])
def reset_gesture_buffer():
    """Reset gesture prediction buffer"""
    if not gesture_recognizer:
        return jsonify({'error': 'Gesture recognizer not initialized'}), 500
    
    gesture_recognizer.reset_buffer()
    return jsonify({
        'success': True,
        'message': 'Gesture buffer reset'
    })


@api_bp.route('/text-to-speech', methods=['POST'])
def text_to_speech():
    """Convert text to speech"""
    if not tts_service:
        return jsonify({'error': 'TTS service not initialized'}), 500
    
    if not tts_service.is_available():
        return jsonify({
            'success': False,
            'error': 'Text-to-speech not available'
        }), 503
    
    data = request.get_json()
    text = data.get('text', '').strip()
    
    if not text:
        return jsonify({
            'success': False,
            'error': 'No text provided'
        }), 400
    
    success = tts_service.speak(text)
    
    return jsonify({
        'success': success,
        'message': 'Text spoken' if success else 'Failed to speak text'
    })


@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'services': {
            'gesture_recognizer': gesture_recognizer is not None,
            'video_matcher': video_matcher is not None,
            'tts_service': tts_service is not None and tts_service.is_available()
        }
    })
