"""
Text-to-Speech Service
Converts recognized gestures to speech
"""

try:
    import pyttsx3
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False
    print("⚠️  pyttsx3 not available. Text-to-speech will be disabled.")


class TextToSpeechService:
    """Convert text to speech"""
    
    def __init__(self, enabled=True, rate=150, volume=1.0):
        """Initialize TTS service"""
        self.enabled = enabled and TTS_AVAILABLE
        self.rate = rate
        self.volume = volume
        self.engine = None
        
        if self.enabled:
            try:
                self.engine = pyttsx3.init()
                self.engine.setProperty('rate', rate)
                self.engine.setProperty('volume', volume)
                print(f"✅ Text-to-Speech initialized")
            except Exception as e:
                print(f"⚠️  Error initializing TTS: {e}")
                self.enabled = False
    
    def speak(self, text: str) -> bool:
        """Speak text aloud"""
        if not self.enabled or not text:
            return False
        
        try:
            self.engine.say(text)
            self.engine.runAndWait()
            return True
        except Exception as e:
            print(f"⚠️  Error speaking text: {e}")
            return False
    
    def is_available(self) -> bool:
        """Check if TTS is available"""
        return self.enabled
    
    def cleanup(self):
        """Cleanup resources"""
        if self.engine:
            try:
                self.engine.stop()
            except:
                pass
