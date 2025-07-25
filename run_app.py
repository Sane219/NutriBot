#!/usr/bin/env python3
"""
NutriBot Application Launcher
Run this script to start the Streamlit app
"""

import subprocess
import sys
import os

def main():
    # Ensure we're in the right directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Check if we're in a virtual environment
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("Warning: You're not in a virtual environment!")
        print("Consider activating the nutribot_env virtual environment first:")
        print("  Windows: nutribot_env\\Scripts\\Activate")
        print("  Unix/macOS: source nutribot_env/bin/activate")
        print()
    
    # Run the Streamlit app
    try:
        print("Starting NutriBot application...")
        print("Once the app loads, you can access it at http://localhost:8501")
        print("Press Ctrl+C to stop the app")
        print("-" * 50)
        
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "app/main.py",
            "--server.headless", "false",
            "--server.fileWatcherType", "none",
            "--browser.gatherUsageStats", "false"
        ])
    except KeyboardInterrupt:
        print("\nApplication stopped by user")
    except Exception as e:
        print(f"Error starting application: {e}")
        print("Make sure you have installed all requirements with:")
        print("  pip install -r requirements.txt")

if __name__ == "__main__":
    main()
