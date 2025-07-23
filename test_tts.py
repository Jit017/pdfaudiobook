#!/usr/bin/env python3
"""
Quick TTS test to verify audio generation is working.
"""

import pyttsx3
from pathlib import Path
from pydub import AudioSegment
import time

def test_tts():
    """Test TTS functionality."""
    print("🎙️ Testing TTS functionality...")
    
    test_text = "Hello! This is a test of the text to speech system."
    output_file = Path("test_audio.aiff")
    
    try:
        # Initialize TTS engine
        engine = pyttsx3.init()
        
        # Get available voices
        voices = engine.getProperty('voices')
        print(f"📋 Available voices: {len(voices) if voices else 0}")
        
        if voices:
            for i, voice in enumerate(voices[:3]):  # Show first 3
                print(f"   {i+1}. {voice.name} ({voice.id})")
            
            # Set voice
            engine.setProperty('voice', voices[0].id)
        
        # Set properties
        engine.setProperty('rate', 160)
        engine.setProperty('volume', 1.0)
        
        print(f"🔊 Generating audio: '{test_text}'")
        
        # Generate audio
        engine.save_to_file(test_text, str(output_file))
        engine.runAndWait()
        time.sleep(0.5)  # Give it time to finish
        
        try:
            engine.stop()
        except:
            pass
        
        # Verify the file
        if output_file.exists():
            file_size = output_file.stat().st_size
            print(f"✅ File created: {file_size:,} bytes")
            
            if file_size > 100:
                # Try to load with pydub
                try:
                    audio = AudioSegment.from_file(str(output_file))
                    duration = len(audio)
                    print(f"✅ Audio loaded successfully: {duration}ms duration")
                    
                    if duration > 100:
                        print("🎉 TTS is working correctly!")
                        return True
                    else:
                        print("⚠️ Audio is too short")
                        return False
                        
                except Exception as e:
                    print(f"❌ Cannot load audio: {e}")
                    return False
            else:
                print("❌ File is too small")
                return False
        else:
            print("❌ No file created")
            return False
            
    except Exception as e:
        print(f"❌ TTS test failed: {e}")
        return False
    
    finally:
        # Cleanup
        if output_file.exists():
            output_file.unlink()

if __name__ == "__main__":
    success = test_tts()
    if success:
        print("\n🎉 TTS test passed! Your audiobook generation should work.")
    else:
        print("\n❌ TTS test failed. There may be issues with audio generation.") 