"""
MotoVision Main Entry Point
Only starts the application.
"""
import sys
from core.app import App

def main():
    """Main function to launch the MotoVision application."""
    print("Initializing MotoVision...")
    app = App()
    app.run()

if __name__ == "__main__":
    sys.exit(main())
