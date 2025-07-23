#!/usr/bin/env python3
"""
Setup verification script for PDF to Audiobook Converter.

This script checks that the project structure is correct and
all modules can be imported (without external dependencies).
"""

import sys
from pathlib import Path

def check_project_structure():
    """Check that all required directories and files exist."""
    print("🔍 Checking project structure...")
    
    required_files = [
        "app.py",
        "requirements.txt", 
        "README.md",
        "config/settings.py",
        "src/__init__.py",
        "src/utils.py",
        "src/pdf_reader.py",
        "src/text_processor.py", 
        "src/emotion_detector.py",
        "src/tts_engine.py",
        "src/audio_mixer.py"
    ]
    
    required_dirs = [
        "config",
        "src",
        "tests",
        "data/input",
        "data/output", 
        "assets/bg_music",
        "assets/sfx"
    ]
    
    missing_files = []
    missing_dirs = []
    
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    for dir_path in required_dirs:
        if not Path(dir_path).exists():
            missing_dirs.append(dir_path)
    
    if missing_files:
        print("❌ Missing files:")
        for file in missing_files:
            print(f"   - {file}")
    
    if missing_dirs:
        print("❌ Missing directories:")
        for dir in missing_dirs:
            print(f"   - {dir}")
    
    if not missing_files and not missing_dirs:
        print("✅ All required files and directories exist")
        return True
    
    return False

def check_basic_imports():
    """Check that basic configuration can be imported."""
    print("\n🔍 Checking basic imports...")
    
    try:
        from config.settings import get_config_summary, USE_GPU, USE_REAL_EMOTION, TTS_ENGINE
        print("✅ Configuration imports successful")
        
        config = get_config_summary()
        print(f"✅ Configuration loaded: {config}")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def check_python_version():
    """Check Python version."""
    print("🔍 Checking Python version...")
    
    version = sys.version_info
    print(f"Python {version.major}.{version.minor}.{version.micro}")
    
    if version >= (3, 8):
        print("✅ Python version is compatible")
        return True
    else:
        print("❌ Python 3.8+ required")
        return False

def main():
    """Run all checks."""
    print("🎧 PDF to Audiobook Converter - Setup Verification")
    print("=" * 50)
    
    checks = [
        check_python_version(),
        check_project_structure(),
        check_basic_imports()
    ]
    
    print("\n" + "=" * 50)
    
    if all(checks):
        print("🎉 Setup verification completed successfully!")
        print("\nNext steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Test basic functionality: python app.py --config")
        print("3. Run tests: pytest tests/")
        return 0
    else:
        print("❌ Setup verification failed!")
        print("Please fix the issues above before proceeding.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 