#!/usr/bin/env python3
"""
Dependency installer and tester for PDF to Audiobook Converter.

This script checks which dependencies are available and helps install missing ones.
"""

import subprocess
import sys
from pathlib import Path

def check_dependency(module_name, package_name=None, import_name=None):
    """Check if a dependency is available."""
    if import_name is None:
        import_name = module_name
    if package_name is None:
        package_name = module_name
    
    try:
        __import__(import_name)
        return True, f"✅ {module_name} is available"
    except ImportError:
        return False, f"❌ {module_name} not found (install: pip install {package_name})"

def install_basic_deps():
    """Install basic dependencies for testing."""
    basic_deps = [
        ("pyttsx3", "pyttsx3"),
        ("pydub", "pydub"),
    ]
    
    print("🔧 Installing basic dependencies for audiobook creation...")
    
    for dep_name, pip_name in basic_deps:
        available, status = check_dependency(dep_name, pip_name)
        print(f"  {status}")
        
        if not available:
            try:
                print(f"  📦 Installing {pip_name}...")
                subprocess.check_call([sys.executable, "-m", "pip", "install", pip_name])
                print(f"  ✅ {pip_name} installed successfully")
            except subprocess.CalledProcessError as e:
                print(f"  ❌ Failed to install {pip_name}: {e}")
                return False
    
    return True

def test_tts_only():
    """Test just the TTS functionality."""
    print("\n🎙️ Testing TTS functionality...")
    
    try:
        from src.tts_engine import synthesize_speech
        import tempfile
        
        # Test TTS with a simple phrase
        test_text = "Hello! This is a test of the text to speech system."
        
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            output_path = tmp.name
        
        print(f"  🔊 Synthesizing: '{test_text}'")
        print(f"  📁 Output: {output_path}")
        
        synthesize_speech(test_text, output_path)
        
        if Path(output_path).exists():
            file_size = Path(output_path).stat().st_size
            print(f"  ✅ TTS working! Generated {file_size} bytes")
            
            # Clean up
            Path(output_path).unlink()
            return True
        else:
            print(f"  ❌ TTS failed - no output file")
            return False
            
    except ImportError as e:
        print(f"  ❌ Cannot test TTS: {e}")
        return False
    except Exception as e:
        print(f"  ❌ TTS test failed: {e}")
        return False

def test_real_audiobook():
    """Test the complete audiobook creation pipeline."""
    print("\n🎬 Testing Complete Audiobook Pipeline...")
    
    try:
        # Run our demo function
        import sys
        import os
        
        # Add current directory to path
        sys.path.append(os.getcwd())
        
        from demo_basic import demo_real_audiobook_creation
        
        print("  🚀 Running real audiobook creation demo...")
        success = demo_real_audiobook_creation()
        
        if success:
            print("  🎉 Complete pipeline test successful!")
            return True
        else:
            print("  ⚠️ Pipeline test completed with some issues")
            return False
            
    except Exception as e:
        print(f"  ❌ Pipeline test failed: {e}")
        return False

def main():
    """Main test and installation script."""
    print("🎧 PDF to Audiobook Converter - Dependency Manager")
    print("=" * 55)
    
    # Check current status
    print("\n🔍 Checking current dependencies...")
    
    deps_to_check = [
        ("PyMuPDF", "PyMuPDF", "fitz"),
        ("pyttsx3", "pyttsx3"),
        ("pydub", "pydub"),
        ("transformers", "transformers"),
        ("torch", "torch"),
        ("streamlit", "streamlit"),
    ]
    
    missing_deps = []
    for dep_name, pip_name, import_name in deps_to_check:
        available, status = check_dependency(dep_name, pip_name, import_name)
        print(f"  {status}")
        if not available:
            missing_deps.append((dep_name, pip_name))
    
    print(f"\n📊 Status: {len(deps_to_check) - len(missing_deps)}/{len(deps_to_check)} dependencies available")
    
    if missing_deps:
        print(f"\n💡 To install all dependencies:")
        print(f"   pip install -r requirements.txt")
        print(f"\n💡 To install minimal dependencies for testing:")
        print(f"   pip install pyttsx3 pydub")
        
        response = input("\n🤔 Install minimal dependencies now? (y/N): ").strip().lower()
        if response in ['y', 'yes']:
            if install_basic_deps():
                print("✅ Basic dependencies installed!")
            else:
                print("❌ Failed to install basic dependencies")
                return False
    
    # Test what we can
    print(f"\n🧪 Running available tests...")
    
    # Test TTS if available
    if all(check_dependency(dep)[0] for dep in ["pyttsx3"]):
        test_tts_only()
    
    # Test complete pipeline if enough deps available
    if all(check_dependency(dep)[0] for dep in ["pyttsx3", "pydub"]):
        test_real_audiobook()
    
    print(f"\n✅ Testing completed!")
    print(f"\n💡 Next steps:")
    print(f"   1. Run: python demo_basic.py")
    print(f"   2. Check output: ls -la data/output/")
    print(f"   3. Install full deps: pip install -r requirements.txt")

if __name__ == "__main__":
    main() 