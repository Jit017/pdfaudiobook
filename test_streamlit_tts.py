#!/usr/bin/env python3
"""
Test the new TTS function that's designed to work in Streamlit.
"""

import sys
from pathlib import Path

# Add current directory to path so we can import from app.py
sys.path.append('.')

def test_streamlit_tts():
    """Test the new generate_single_audio_chunk function."""
    print("🧪 Testing Streamlit-compatible TTS function...")
    
    # Import the function from app.py
    try:
        from app import generate_single_audio_chunk
    except ImportError as e:
        print(f"❌ Cannot import function: {e}")
        return False
    
    test_text = "This is a test of the streamlit compatible TTS function."
    output_file = Path("test_streamlit_tts.aiff")
    
    try:
        # Clean up any existing file
        if output_file.exists():
            output_file.unlink()
        
        print(f"🔊 Generating audio: '{test_text}'")
        
        # Test the function
        success = generate_single_audio_chunk(test_text, str(output_file))
        
        if success:
            print("✅ Function returned success")
            
            if output_file.exists():
                file_size = output_file.stat().st_size
                print(f"✅ File created: {file_size:,} bytes")
                
                if file_size > 1000:
                    print("🎉 TTS function is working correctly!")
                    return True
                else:
                    print(f"⚠️ File too small: {file_size} bytes")
                    return False
            else:
                print("❌ No file created despite success return")
                return False
        else:
            print("❌ Function returned failure")
            return False
    
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    
    finally:
        # Cleanup
        if output_file.exists():
            output_file.unlink()

if __name__ == "__main__":
    success = test_streamlit_tts()
    if success:
        print("\n🎉 Streamlit TTS test passed!")
        print("💡 Your audiobook generation should now work in the Streamlit app.")
    else:
        print("\n❌ Streamlit TTS test failed.")
        print("💡 There may still be issues with TTS in the Streamlit context.") 