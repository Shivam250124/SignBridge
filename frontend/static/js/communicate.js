// SignBridge - Main Communication Page Logic

class SignBridgeApp {
    constructor() {
        this.conversation = new ConversationManager(50);
        this.camera = new CameraHandler();
        this.speech = new SpeechHandler();
        this.ttsEnabled = true;
        this.lastSpokenGesture = null;
        this.synth = window.speechSynthesis || null;
    }
    
    init() {
        console.log('🌉 Initializing SignBridge App...');
        
        // Initialize conversation
        if (!this.conversation.init('conversationHistory')) {
            console.error('Failed to initialize conversation');
            return;
        }
        
        // Initialize camera
        this.camera.init();
        
        // Setup event handlers
        this.setupEventHandlers();
        
        // Setup speech recognition callbacks
        this.setupSpeechCallbacks();
        
        // Setup camera callbacks
        this.setupCameraCallbacks();
        
        // Start gesture polling
        this.camera.startGesturePolling(600);
        
        // Load available gestures and videos info
        this.loadAvailableGestures();
        this.loadAvailableVideos();

        // Show browser TTS status
        if (!this.synth) {
            console.warn('Browser TTS not available');
        }

        // Check server health and update status indicator
        this.checkServerHealth();
        setInterval(() => this.checkServerHealth(), 10000);
        
        console.log('✅ SignBridge App initialized');
    }
    
    setupEventHandlers() {
        // Speech controls
        const startSpeechBtn = document.getElementById('startSpeechBtn');
        const stopSpeechBtn  = document.getElementById('stopSpeechBtn');
        const sendTextBtn    = document.getElementById('sendTextBtn');
        const textInput      = document.getElementById('textInput');
        
        if (startSpeechBtn) {
            startSpeechBtn.addEventListener('click', () => this.startSpeech());
        }
        if (stopSpeechBtn) {
            stopSpeechBtn.addEventListener('click', () => this.stopSpeech());
        }
        if (sendTextBtn) {
            sendTextBtn.addEventListener('click', () => this.sendText());
        }
        if (textInput) {
            textInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') this.sendText();
            });
        }
        
        // Gesture controls
        const resetGestureBtn = document.getElementById('resetGestureBtn');
        if (resetGestureBtn) {
            resetGestureBtn.addEventListener('click', () => this.resetGesture());
        }
        
        const ttsToggleBtn = document.getElementById('ttsToggleBtn');
        if (ttsToggleBtn) {
            ttsToggleBtn.addEventListener('click', () => this.toggleTTS());
        }
        
        // Conversation controls
        const clearHistoryBtn = document.getElementById('clearHistoryBtn');
        if (clearHistoryBtn) {
            clearHistoryBtn.addEventListener('click', () => this.clearHistory());
        }
        const saveHistoryBtn = document.getElementById('saveHistoryBtn');
        if (saveHistoryBtn) {
            saveHistoryBtn.addEventListener('click', () => this.saveHistory());
        }
        
        // Help modal
        const helpBtn   = document.getElementById('helpBtn');
        const helpModal = document.getElementById('helpModal');
        const modalClose = helpModal?.querySelector('.modal-close');
        
        if (helpBtn && helpModal) {
            helpBtn.addEventListener('click', () => helpModal.classList.add('active'));
        }
        if (modalClose && helpModal) {
            modalClose.addEventListener('click', () => helpModal.classList.remove('active'));
        }
        if (helpModal) {
            helpModal.addEventListener('click', (e) => {
                if (e.target === helpModal) helpModal.classList.remove('active');
            });
        }

        // Video ended → reset placeholder
        const videoPlayer = document.getElementById('signVideoPlayer');
        if (videoPlayer) {
            videoPlayer.addEventListener('ended', () => {
                const videoTitle = document.getElementById('videoTitle');
                if (videoTitle) videoTitle.textContent = 'Video finished';
            });
        }
    }
    
    setupSpeechCallbacks() {
        this.speech.onResult = (result) => {
            const recognizedText = document.getElementById('recognizedText');
            if (recognizedText) {
                recognizedText.textContent = result.final || result.interim || 'Listening...';
            }
            
            // Process final result
            if (result.isFinal && result.final) {
                this.processSpeech(result.final);
            }
        };
        
        this.speech.onStatusChange = (status) => {
            const speechStatus = document.getElementById('speechStatus');
            if (speechStatus) speechStatus.textContent = status;
        };
        
        this.speech.onError = (error) => {
            SignBridge.showNotification(`Speech error: ${error}`, 'error');
        };
    }
    
    setupCameraCallbacks() {
        this.camera.onGestureDetected = (data) => {
            console.log('✅ Confirmed gesture:', data.gesture, data.confidence);
            
            // Add to conversation
            this.conversation.addMessage('deaf', data.gesture);
            
            // Speak gesture using browser TTS if enabled
            if (this.ttsEnabled && data.gesture !== this.lastSpokenGesture) {
                this.speakText(data.gesture);
                this.lastSpokenGesture = data.gesture;
            }

            SignBridge.showNotification(`Gesture: ${data.gesture}`, 'success');
        };
    }
    
    startSpeech() {
        if (!this.speech.isSupported()) {
            SignBridge.showNotification(
                'Speech recognition requires Chrome or Edge browser.', 'warning');
            return;
        }
        
        if (this.speech.start()) {
            const startBtn = document.getElementById('startSpeechBtn');
            const stopBtn  = document.getElementById('stopSpeechBtn');
            if (startBtn) startBtn.disabled = true;
            if (stopBtn)  stopBtn.disabled  = false;
        }
    }
    
    stopSpeech() {
        if (this.speech.stop()) {
            const startBtn = document.getElementById('startSpeechBtn');
            const stopBtn  = document.getElementById('stopSpeechBtn');
            if (startBtn) startBtn.disabled = false;
            if (stopBtn)  stopBtn.disabled  = true;
        }
    }
    
    async sendText() {
        const textInput = document.getElementById('textInput');
        const text = textInput ? textInput.value.trim() : '';
        
        if (!text) return;
        
        // Show in recognized text area
        const recognizedText = document.getElementById('recognizedText');
        if (recognizedText) recognizedText.textContent = text;
        
        await this.processSpeech(text);
        
        if (textInput) textInput.value = '';
    }
    
    async processSpeech(text) {
        console.log('Processing speech:', text);
        
        // Add to conversation
        this.conversation.addMessage('hearing', text);
        
        // Find matching sign video
        try {
            const data = await SignBridge.apiRequest('/api/process-speech', {
                method: 'POST',
                body: JSON.stringify({ text: text })
            });
            
            if (data.success) {
                this.playSignVideo(data.video, data.video_url, text);
                SignBridge.showNotification(`Playing sign for: "${text}"`, 'success');
            } else {
                SignBridge.showNotification(`No sign video found for: "${text}"`, 'warning');
            }
        } catch (error) {
            console.error('Failed to process speech:', error);
            SignBridge.showNotification('Failed to process speech. Is the server running?', 'error');
        }
    }
    
    playSignVideo(filename, url, title) {
        const videoPlayer      = document.getElementById('signVideoPlayer');
        const videoPlaceholder = document.getElementById('videoPlaceholder');
        const videoTitle       = document.getElementById('videoTitle');
        
        if (videoPlayer) {
            videoPlayer.src = url;
            videoPlayer.classList.add('active');
            if (videoPlaceholder) videoPlaceholder.classList.add('hidden');
            if (videoTitle) videoTitle.textContent = `▶ Playing: ${title}`;
            
            videoPlayer.play().catch(e => {
                console.error('Failed to play video:', e);
                SignBridge.showNotification('Video playback failed.', 'error');
            });
        }
    }
    
    // Use browser's built-in Web Speech API for TTS (no backend dependency)
    speakText(text) {
        if (!this.synth) return;

        // Cancel any ongoing speech
        this.synth.cancel();

        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = 'en-US';
        utterance.rate = 0.9;
        utterance.pitch = 1;
        utterance.volume = 1;
        this.synth.speak(utterance);
    }
    
    async resetGesture() {
        await this.camera.resetGestureBuffer();
        this.lastSpokenGesture = null;
        SignBridge.showNotification('Gesture buffer reset', 'info');
    }
    
    toggleTTS() {
        this.ttsEnabled = !this.ttsEnabled;
        const btn = document.getElementById('ttsToggleBtn');
        if (btn) {
            btn.innerHTML = this.ttsEnabled
                ? '<i class="fas fa-volume-up"></i> TTS: ON'
                : '<i class="fas fa-volume-mute"></i> TTS: OFF';
            btn.classList.toggle('btn-secondary', !this.ttsEnabled);
            btn.classList.toggle('btn-primary',   this.ttsEnabled);
        }
        SignBridge.showNotification(`TTS ${this.ttsEnabled ? 'enabled' : 'disabled'}`, 'info');
    }
    
    clearHistory() {
        if (confirm('Clear conversation history?')) {
            this.conversation.clear();
            SignBridge.showNotification('Conversation cleared', 'info');
        }
    }
    
    saveHistory() {
        this.conversation.save();
    }
    
    async loadAvailableGestures() {
        try {
            const data = await SignBridge.apiRequest('/api/available-gestures');
            if (data.success) {
                console.log(`📋 Gestures loaded: ${data.gestures.total} total`);
            }
        } catch (error) {
            console.error('Failed to load gestures:', error);
        }
    }
    
    async loadAvailableVideos() {
        try {
            const data = await SignBridge.apiRequest('/api/available-videos');
            if (data.success) {
                console.log(`📹 Videos loaded: ${data.total} total`);
            }
        } catch (error) {
            console.error('Failed to load videos:', error);
        }
    }

    async checkServerHealth() {
        const dot  = document.getElementById('statusDot');
        const text = document.getElementById('statusText');
        try {
            const data = await SignBridge.apiRequest('/api/health');
            if (data.status === 'healthy') {
                if (dot)  { dot.className  = 'status-indicator active'; }
                if (text) { text.textContent = 'Server Online'; }
            }
        } catch (e) {
            if (dot)  { dot.className  = 'status-indicator inactive'; }
            if (text) { text.textContent = 'Server Offline'; }
        }
    }
}

// Initialize app when page loads
document.addEventListener('DOMContentLoaded', () => {
    const app = new SignBridgeApp();
    app.init();
    
    // Make app globally available for debugging
    window.signBridgeApp = app;
});
