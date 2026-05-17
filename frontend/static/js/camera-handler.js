// SignBridge - Camera & Gesture Recognition Handler
// Supports two modes:
//   local → polls /api/current-gesture (server processes MJPEG stream)
//   cloud → captures WebRTC frame, sends to /api/recognize-gesture

class CameraHandler {
    constructor() {
        this.updateInterval      = null;
        this.isActive            = false;
        this.onGestureDetected   = null;
        this.lastGesture         = null;
        this.lastConfirmedGesture = null;
        this.sameGestureCount    = 0;
        this.CONFIRM_THRESHOLD   = 3;

        this.mode   = (window.DEPLOYMENT_MODE === 'cloud') ? 'cloud' : 'local';
        this.stream = null; // WebRTC stream (cloud only)
    }

    init() {
        console.log(`Camera handler init — mode: ${this.mode}`);
        if (this.mode === 'cloud') {
            this._startWebRTC();
        }
        return true;
    }

    // ── WebRTC (cloud mode) ───────────────────────────────────────────────────

    async _startWebRTC() {
        const video  = document.getElementById('webrtcFeed');
        const canvas = document.getElementById('webrtcCanvas');
        if (!video || !canvas) return;

        try {
            this.stream = await navigator.mediaDevices.getUserMedia({
                video: { width: 640, height: 480, facingMode: 'user' },
                audio: false
            });
            video.srcObject = this.stream;
            console.log('✅ WebRTC camera started');
        } catch (err) {
            console.error('Camera access denied:', err);
            SignBridge.showNotification('Camera access denied. Please allow camera permission.', 'error');
        }
    }

    async _captureAndRecognize() {
        const video  = document.getElementById('webrtcFeed');
        const canvas = document.getElementById('webrtcCanvas');
        if (!video || !canvas || !video.srcObject) return null;

        canvas.width  = video.videoWidth  || 640;
        canvas.height = video.videoHeight || 480;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

        const imageData = canvas.toDataURL('image/jpeg', 0.7);

        try {
            const data = await SignBridge.apiRequest('/api/recognize-gesture', {
                method: 'POST',
                body: JSON.stringify({ image: imageData })
            });
            if (data.success) {
                return { gesture: data.gesture, confidence: data.confidence, num_hands: data.num_hands };
            }
        } catch (e) {
            console.error('Recognize gesture failed:', e);
        }
        return null;
    }

    // ── Polling ───────────────────────────────────────────────────────────────

    startGesturePolling(intervalMs = 600) {
        if (this.isActive) return;
        this.isActive = true;

        this.updateInterval = setInterval(async () => {
            let result = null;

            if (this.mode === 'cloud') {
                result = await this._captureAndRecognize();
            } else {
                try {
                    const data = await SignBridge.apiRequest('/api/current-gesture');
                    if (data.success) {
                        result = { gesture: data.gesture, confidence: data.confidence, num_hands: data.num_hands };
                    }
                } catch (e) {
                    console.error('Failed to fetch gesture:', e);
                }
            }

            if (result) this._processResult(result);
        }, intervalMs);

        console.log('Gesture polling started');
    }

    stopGesturePolling() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
        }
        this.isActive = false;
        if (this.stream) {
            this.stream.getTracks().forEach(t => t.stop());
            this.stream = null;
        }
    }

    _processResult({ gesture, confidence, num_hands }) {
        // Always update the live overlay
        this.updateOverlay(gesture, confidence, num_hands);

        const invalid = ['NO_HANDS', 'DETECTING...', 'UNCERTAIN', 'NO_PREDICTION'];
        if (invalid.includes(gesture)) {
            this.sameGestureCount = 0;
            return;
        }

        if (gesture === this.lastGesture) {
            this.sameGestureCount++;
        } else {
            this.lastGesture      = gesture;
            this.sameGestureCount = 1;
        }

        // Fire callback only when confirmed AND changed
        if (this.sameGestureCount === this.CONFIRM_THRESHOLD &&
            gesture !== this.lastConfirmedGesture) {

            this.lastConfirmedGesture = gesture;

            if (this.onGestureDetected) {
                this.onGestureDetected({ gesture, confidence, timestamp: new Date() });
            }
        }
    }

    updateOverlay(gesture, confidence, numHands) {
        const gestureEl    = document.getElementById('detectedGesture');
        const confidenceEl = document.getElementById('gestureConfidence');
        if (!gestureEl) return;

        const invalid = ['NO_HANDS', 'DETECTING...', 'UNCERTAIN', 'NO_PREDICTION'];

        if (gesture === 'NO_HANDS' || numHands === 0) {
            gestureEl.textContent = 'Show your hands';
            gestureEl.style.color = '#aaa';
            if (confidenceEl) confidenceEl.textContent = '';
        } else if (gesture === 'DETECTING...') {
            gestureEl.textContent = 'Detecting…';
            gestureEl.style.color = '#ffd700';
            if (confidenceEl) confidenceEl.textContent = '';
        } else if (invalid.includes(gesture)) {
            gestureEl.textContent = gesture;
            gestureEl.style.color = '#ff9800';
            if (confidenceEl) confidenceEl.textContent = '';
        } else {
            gestureEl.textContent = gesture;
            gestureEl.style.color = '#4ade80';
            if (confidenceEl && typeof confidence === 'number' && confidence > 0) {
                confidenceEl.textContent = `Confidence: ${(confidence * 100).toFixed(1)}%`;
            }
        }
    }

    async resetGestureBuffer() {
        try {
            const data = await SignBridge.apiRequest('/api/reset-gesture-buffer', { method: 'POST' });
            if (data.success) {
                this.lastGesture          = null;
                this.lastConfirmedGesture = null;
                this.sameGestureCount     = 0;
                this.updateOverlay('NO_HANDS', 0, 0);
                return true;
            }
        } catch (e) {
            console.error('Failed to reset gesture buffer:', e);
        }
        return false;
    }
}

window.CameraHandler = CameraHandler;
