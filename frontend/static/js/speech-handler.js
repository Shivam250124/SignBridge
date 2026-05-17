// SignBridge - Speech Recognition Handler

class SpeechHandler {
    constructor() {
        this.recognition = null;
        this.isListening = false;
        this._shouldRestart = false; // user intent: keep listening
        this.onResult = null;
        this.onError = null;
        this.onStatusChange = null;
        
        this.initRecognition();
    }
    
    initRecognition() {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        
        if (!SpeechRecognition) {
            console.error('Speech recognition not supported');
            return false;
        }
        
        this.recognition = new SpeechRecognition();
        this.recognition.lang = 'en-IN';
        this.recognition.continuous = true;
        this.recognition.interimResults = true;
        
        this.recognition.onstart = () => {
            this.isListening = true;
            this.updateStatus('🎙️ Listening... Speak clearly');
            console.log('Speech recognition started');
        };
        
        this.recognition.onend = () => {
            this.isListening = false;
            console.log('Speech recognition ended');

            // Auto-restart if user hasn't clicked Stop
            if (this._shouldRestart) {
                this.updateStatus('🔄 Restarting listener...');
                setTimeout(() => {
                    if (this._shouldRestart) {
                        try {
                            this.recognition.start();
                        } catch (e) {
                            console.warn('Auto-restart failed:', e);
                        }
                    }
                }, 300);
            } else {
                this.updateStatus('Stopped. Click "Start Speaking" to continue');
            }
        };
        
        this.recognition.onerror = (event) => {
            console.error('Speech recognition error:', event.error);

            // 'no-speech' is normal — don't show as error
            if (event.error === 'no-speech') {
                this.updateStatus('🎙️ Listening... (no speech detected)');
                return;
            }

            // 'aborted' happens on manual stop — ignore
            if (event.error === 'aborted') return;

            this.updateStatus(`⚠️ Error: ${event.error}`);
            if (this.onError) {
                this.onError(event.error);
            }
        };
        
        this.recognition.onresult = (event) => {
            let interimTranscript = '';
            let finalTranscript = '';
            
            for (let i = event.resultIndex; i < event.results.length; i++) {
                const transcript = event.results[i][0].transcript;
                if (event.results[i].isFinal) {
                    finalTranscript += transcript + ' ';
                } else {
                    interimTranscript += transcript;
                }
            }
            
            if (this.onResult) {
                this.onResult({
                    final: finalTranscript.trim(),
                    interim: interimTranscript.trim(),
                    isFinal: finalTranscript.length > 0
                });
            }
        };
        
        return true;
    }
    
    start() {
        if (!this.recognition) {
            console.error('Speech recognition not initialized');
            return false;
        }
        
        if (this.isListening) {
            console.warn('Already listening');
            return false;
        }
        
        try {
            this._shouldRestart = true;
            this.recognition.start();
            return true;
        } catch (error) {
            console.error('Failed to start recognition:', error);
            return false;
        }
    }
    
    stop() {
        this._shouldRestart = false;

        if (!this.recognition) return false;
        
        try {
            this.recognition.stop();
            this.isListening = false;
            return true;
        } catch (error) {
            console.error('Failed to stop recognition:', error);
            return false;
        }
    }
    
    updateStatus(message) {
        if (this.onStatusChange) {
            this.onStatusChange(message);
        }
    }
    
    isSupported() {
        return !!(window.SpeechRecognition || window.webkitSpeechRecognition);
    }
}

// Make globally available
window.SpeechHandler = SpeechHandler;
