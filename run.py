#!/usr/bin/env python3
"""
SignBridge Application Launcher
Run this file to start the SignBridge web application
"""

import sys
from backend.app import create_app
from backend.config import config


def main():
    """Main entry point"""
    
    print("=" * 60)
    print("🌉 SignBridge - 2-Way Communication Platform")
    print("=" * 60)
    print()
    
    # Create Flask app
    app = create_app()
    
    if app is None:
        print("\n❌ Failed to create application. Please check configuration.")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("🚀 Starting SignBridge server...")
    print("=" * 60)
    print(f"\n🌐 Access the application at: http://localhost:{config.PORT}")
    print(f"🌐 Or from network: http://{config.HOST}:{config.PORT}")
    print("\n💡 Press Ctrl+C to stop the server")
    print("=" * 60)
    print()
    
    try:
        # Run Flask app
        app.run(
            host=config.HOST,
            port=config.PORT,
            debug=config.DEBUG,
            threaded=True
        )
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down SignBridge...")
        print("✅ Server stopped successfully")
    except Exception as e:
        print(f"\n❌ Error running server: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
