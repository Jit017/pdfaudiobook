#!/usr/bin/env python3
"""
Quick launcher for the Streamlit PDF to Audiobook Generator UI.
"""

import subprocess
import sys
from pathlib import Path

def check_streamlit():
    """Check if Streamlit is installed."""
    try:
        import streamlit
        return True
    except ImportError:
        return False

def main():
    """Launch the Streamlit app."""
    
    print("🚀 PDF to Audiobook Generator - Streamlit UI Launcher")
    print("=" * 55)
    
    # Check if Streamlit is installed
    if not check_streamlit():
        print("❌ Streamlit not found!")
        print("💡 Install with: pip install streamlit")
        response = input("\n🤔 Install Streamlit now? (y/N): ").strip().lower()
        
        if response in ['y', 'yes']:
            try:
                print("📦 Installing Streamlit...")
                subprocess.check_call([sys.executable, "-m", "pip", "install", "streamlit"])
                print("✅ Streamlit installed successfully!")
            except subprocess.CalledProcessError:
                print("❌ Failed to install Streamlit")
                return
        else:
            return
    
    # Check if app.py exists
    if not Path("app.py").exists():
        print("❌ app.py not found in current directory")
        return
    
    print("✅ Starting Streamlit app...")
    print("🌐 The app will open in your browser automatically")
    print("🔗 URL: http://localhost:8501")
    print("\n💡 Press Ctrl+C to stop the server")
    print("-" * 55)
    
    try:
        # Run Streamlit app
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start Streamlit: {e}")
    except KeyboardInterrupt:
        print("\n👋 Streamlit app stopped by user")

if __name__ == "__main__":
    main() 