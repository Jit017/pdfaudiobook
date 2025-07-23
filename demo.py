#!/usr/bin/env python3
"""
Demo script for PDF to Audiobook Converter API functions.

This script demonstrates the main API functions with dummy data,
allowing you to test the pipeline at home without external dependencies.
"""

import tempfile
from pathlib import Path

# Add src to path for imports
import sys
sys.path.append(str(Path(__file__).parent / "src"))

from src.utils import log_event, sanitize_filename
from config.settings import get_config_summary


def demo_text_processing():
    """Demo the text processing function."""
    print("\n🔍 Demo: Text Processing")
    print("-" * 40)
    
    try:
        from src.text_processor import process_text
        
        # Sample text with SFX keywords
        sample_text = """
        John walked slowly down the dark hallway. Suddenly, the old door creaked loudly,
        making him jump. His footsteps echoed as he ran away from the mysterious sound.
        Thunder rumbled in the distance, and rain began to fall on the roof.
        """
        
        print(f"Processing text: {len(sample_text)} characters")
        
        # Process the text
        chunks = process_text(sample_text)
        
        print(f"✅ Generated {len(chunks)} text chunks")
        
        for i, chunk in enumerate(chunks):
            print(f"\nChunk {i+1}:")
            print(f"  Text: {chunk['text'][:60]}...")
            print(f"  SFX: {chunk['sfx']}")
            print(f"  Emotion: {chunk['emotion']}")
            
    except Exception as e:
        print(f"❌ Error in text processing: {e}")


def demo_emotion_detection():
    """Demo the emotion detection function."""
    print("\n🧠 Demo: Emotion Detection")
    print("-" * 40)
    
    try:
        from src.emotion_detector import detect_emotion
        
        test_texts = [
            "I am so happy and excited about this wonderful day!",
            "This is the worst thing that could happen to me.",
            "I'm really angry about this unfair situation!",
            "I'm terrified of what might happen next.",
            "What a shocking and unexpected surprise!",
            "The weather forecast shows partly cloudy skies."
        ]
        
        print("Testing emotion detection on sample texts:")
        
        for text in test_texts:
            emotion = detect_emotion(text)
            print(f"  '{text[:40]}...' → {emotion}")
            
    except Exception as e:
        print(f"❌ Error in emotion detection: {e}")


def demo_tts_synthesis():
    """Demo the TTS synthesis function."""
    print("\n🎙️ Demo: TTS Synthesis")
    print("-" * 40)
    
    try:
        from src.tts_engine import synthesize_speech
        
        sample_text = "Hello! This is a test of the text to speech system."
        
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
            output_path = tmp.name
        
        print(f"Synthesizing: '{sample_text}'")
        print(f"Output: {output_path}")
        
        # Note: This might fail if pyttsx3 isn't installed
        try:
            synthesize_speech(sample_text, output_path)
            
            if Path(output_path).exists():
                file_size = Path(output_path).stat().st_size
                print(f"✅ TTS synthesis completed! File size: {file_size} bytes")
            else:
                print("❌ TTS synthesis failed - no output file created")
                
        except ImportError as e:
            print(f"⚠️ TTS engine not available: {e}")
            print("   Install with: pip install pyttsx3")
        except Exception as e:
            print(f"❌ TTS synthesis failed: {e}")
            
        # Clean up
        Path(output_path).unlink(missing_ok=True)
        
    except Exception as e:
        print(f"❌ Error in TTS demo: {e}")


def demo_utils():
    """Demo the utility functions."""
    print("\n🧰 Demo: Utility Functions")
    print("-" * 40)
    
    try:
        # Test filename sanitization
        dirty_names = [
            "My Book: Chapter 1!",
            "File with <invalid> characters",
            "Normal_filename.txt",
            "../../dangerous/path",
            "a" * 150  # Very long name
        ]
        
        print("Testing filename sanitization:")
        for name in dirty_names:
            clean = sanitize_filename(name)
            print(f"  '{name[:30]}...' → '{clean}'")
        
        # Test logging
        print("\nTesting log events:")
        log_event("Demo log message 1")
        log_event("Demo log message 2")
        print("  ✅ Check console output for log messages")
        
    except Exception as e:
        print(f"❌ Error in utils demo: {e}")


def demo_full_pipeline():
    """Demo a simplified full pipeline."""
    print("\n🎬 Demo: Full Pipeline (Simplified)")
    print("-" * 50)
    
    try:
        from src.text_processor import process_text
        from src.emotion_detector import detect_emotion
        
        # Sample story text
        story = """
        Sarah opened the creaky door and stepped into the dark room. 
        Her heart was pounding with fear as she heard strange noises.
        Suddenly, she felt relieved when she realized it was just her cat.
        She laughed with joy at her own silly fears.
        """
        
        print("1. Processing text...")
        chunks = process_text(story)
        print(f"   ✅ Created {len(chunks)} chunks")
        
        print("2. Detecting emotions...")
        for chunk in chunks:
            emotion = detect_emotion(chunk['text'])
            chunk['emotion'] = emotion
            print(f"   Chunk: {chunk['text'][:40]}... → {emotion}")
        
        print("3. Would generate TTS for each chunk...")
        print("4. Would mix audio with BGM and SFX...")
        print("5. Would export final audiobook...")
        
        print(f"\n✅ Pipeline demo completed with {len(chunks)} chunks!")
        
    except Exception as e:
        print(f"❌ Error in full pipeline demo: {e}")


def main():
    """Run all demos."""
    print("🎧 PDF to Audiobook Converter - API Demo")
    print("=" * 50)
    
    # Show current configuration
    config = get_config_summary()
    print("\n⚙️ Current Configuration:")
    for key, value in config.items():
        print(f"  {key}: {value}")
    
    # Run demos
    demo_text_processing()
    demo_emotion_detection()
    demo_tts_synthesis()
    demo_utils()
    demo_full_pipeline()
    
    print("\n" + "=" * 50)
    print("🎉 Demo completed!")
    print("\nNext steps:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Test with real PDF: python app.py --pdf document.pdf --output audiobook.mp3")
    print("3. Switch to production mode by editing config/settings.py")


if __name__ == "__main__":
    main() 