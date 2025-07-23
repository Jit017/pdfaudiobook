#!/usr/bin/env python3
"""
Basic demo script for PDF to Audiobook Converter - No External Dependencies.

This script demonstrates the core functionality without requiring external
dependencies like PyMuPDF, pydub, etc. Perfect for testing at home.
"""

import sys
from pathlib import Path

# Add config to path for imports
sys.path.append(str(Path(__file__).parent))

def demo_configuration():
    """Demo the configuration system."""
    print("\n⚙️ Demo: Configuration System")
    print("-" * 40)
    
    try:
        from config.settings import (
            get_config_summary, USE_GPU, USE_REAL_EMOTION, TTS_ENGINE,
            EMOTION_BGM_MAP, SFX_KEYWORDS, create_directories
        )
        
        print("Current configuration:")
        config = get_config_summary()
        for key, value in config.items():
            print(f"  {key}: {value}")
        
        print(f"\nKey settings:")
        print(f"  USE_GPU: {USE_GPU}")
        print(f"  USE_REAL_EMOTION: {USE_REAL_EMOTION}")
        print(f"  TTS_ENGINE: {TTS_ENGINE}")
        
        print(f"\nEmotion → BGM mapping:")
        for emotion, music in EMOTION_BGM_MAP.items():
            print(f"  {emotion}: {music}")
        
        print(f"\nSound effect keywords:")
        for sfx_type, keywords in SFX_KEYWORDS.items():
            print(f"  {sfx_type}: {keywords[:3]}...")  # Show first 3 keywords
        
        # Test directory creation
        print(f"\nTesting directory creation...")
        create_directories()
        print(f"  ✅ Directories created successfully")
        
    except Exception as e:
        print(f"❌ Error in configuration demo: {e}")


def demo_core_functions():
    """Demo core functions without external dependencies."""
    print("\n🧰 Demo: Core Functions (No External Deps)")
    print("-" * 50)
    
    try:
        # Test text cleaning and processing utilities
        import re
        
        def clean_text_demo(text):
            """Demo text cleaning function."""
            if not text:
                return ""
            # Remove extra whitespace
            text = re.sub(r'\s+', ' ', text)
            # Remove special characters that interfere with TTS
            text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\'\"]', '', text)
            return text.strip()
        
        def detect_sfx_keywords_demo(text, keywords):
            """Demo SFX keyword detection."""
            text_lower = text.lower()
            detected = []
            for sfx_type, word_list in keywords.items():
                for word in word_list:
                    if word in text_lower:
                        detected.append(sfx_type)
                        break
            return detected
        
        def detect_emotion_fallback_demo(text):
            """Demo fallback emotion detection."""
            text_lower = text.lower()
            emotion_keywords = {
                'joy': ['happy', 'joy', 'excited', 'wonderful', 'amazing', 'great'],
                'sadness': ['sad', 'cry', 'tears', 'sorrow', 'grief', 'lonely'],
                'anger': ['angry', 'mad', 'furious', 'rage', 'hate', 'annoyed'],
                'fear': ['afraid', 'scared', 'terrified', 'anxious', 'worried'],
                'surprise': ['surprised', 'shocked', 'amazed', 'astonished']
            }
            
            for emotion, keywords in emotion_keywords.items():
                if any(keyword in text_lower for keyword in keywords):
                    return emotion
            return 'neutral'
        
        # Test sample text
        sample_text = """
        John walked slowly down the dark hallway. Suddenly, the old door creaked loudly,
        making him jump with fear. His footsteps echoed as he ran away from the mysterious sound.
        Thunder rumbled in the distance, and rain began to fall on the roof.
        He felt so happy when he finally reached safety!
        """
        
        print("Testing text processing functions:")
        
        # Clean text
        cleaned = clean_text_demo(sample_text)
        print(f"✅ Text cleaned: {len(cleaned)} chars")
        
        # Detect SFX
        from config.settings import SFX_KEYWORDS
        sfx = detect_sfx_keywords_demo(sample_text, SFX_KEYWORDS)
        print(f"✅ SFX detected: {sfx}")
        
        # Detect emotions in sentences
        sentences = sample_text.split('.')
        for i, sentence in enumerate(sentences):
            if sentence.strip():
                emotion = detect_emotion_fallback_demo(sentence)
                print(f"  Sentence {i+1}: {emotion}")
        
    except Exception as e:
        print(f"❌ Error in core functions demo: {e}")


def demo_file_operations():
    """Demo file operations."""
    print("\n📁 Demo: File Operations")
    print("-" * 40)
    
    try:
        import tempfile
        import re
        
        def sanitize_filename_demo(name):
            """Demo filename sanitization."""
            if not name:
                return "untitled"
            # Remove problematic characters
            sanitized = re.sub(r'[<>:"/\\|?*]', '_', name)
            sanitized = re.sub(r'[^\w\s\-_\.]', '', sanitized)
            sanitized = re.sub(r'\s+', '_', sanitized)
            sanitized = sanitized.strip('_.')
            if len(sanitized) > 100:
                sanitized = sanitized[:100]
            if not sanitized:
                sanitized = "untitled"
            return sanitized
        
        # Test filename sanitization
        test_names = [
            "My Book: Chapter 1!",
            "File with <invalid> characters",
            "../../dangerous/path",
            "a" * 150
        ]
        
        print("Testing filename sanitization:")
        for name in test_names:
            clean = sanitize_filename_demo(name)
            print(f"  '{name[:30]}...' → '{clean}'")
        
        # Test temporary file creation
        print("\nTesting temporary file operations:")
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp:
            tmp.write(b"Test content")
            temp_path = Path(tmp.name)
        
        print(f"  ✅ Created temp file: {temp_path.name}")
        print(f"  ✅ File exists: {temp_path.exists()}")
        
        # Clean up
        temp_path.unlink()
        print(f"  ✅ Cleaned up temp file")
        
    except Exception as e:
        print(f"❌ Error in file operations demo: {e}")


def demo_config_switching():
    """Demo configuration switching scenarios."""
    print("\n🔄 Demo: Configuration Switching")
    print("-" * 40)
    
    try:
        from config.settings import USE_GPU, USE_REAL_EMOTION, TTS_ENGINE
        
        print("Current mode:")
        if USE_GPU:
            print("  🎯 PRODUCTION MODE (College)")
            print("    - GPU acceleration enabled")
            print("    - Real AI emotion detection")
            print("    - High-quality TTS (Coqui)")
        else:
            print("  🏠 DEVELOPMENT MODE (Home)")
            print("    - CPU-only processing")
            print("    - Fallback emotion detection")
            print("    - Offline TTS (pyttsx3)")
        
        print(f"\nTo switch modes, edit config/settings.py:")
        print(f"  USE_GPU = {'False' if USE_GPU else 'True'}")
        print(f"  USE_REAL_EMOTION = {'False' if USE_REAL_EMOTION else 'True'}")
        print(f"  TTS_ENGINE = \"{'pyttsx3' if TTS_ENGINE == 'coqui' else 'coqui'}\"")
        
        print(f"\nFeature availability in current mode:")
        print(f"  ✅ PDF text extraction")
        print(f"  ✅ Text chunking & SFX detection")
        print(f"  {'✅' if USE_REAL_EMOTION else '⚠️ '} Emotion detection ({'AI' if USE_REAL_EMOTION else 'fallback'})")
        print(f"  ⚠️  TTS synthesis (requires: pip install {TTS_ENGINE})")
        print(f"  ⚠️  Audio mixing (requires: pip install pydub)")
        
    except Exception as e:
        print(f"❌ Error in config switching demo: {e}")


def demo_real_audiobook_creation():
    """Demo creating a real audiobook with actual audio assets."""
    print("\n🎬 Demo: Real Audiobook Creation")
    print("-" * 50)
    
    try:
        # Sample story with SFX keywords that match our assets
        story = """
        Sarah walked slowly toward the old wooden door. The door creaked loudly as she pushed it open.
        She let out a terrified scream when she saw the dark figure inside.
        But then she realized it was just her coat hanging on a hook, and she felt much better.
        """
        
        print("🔍 Step 1: Processing text and detecting SFX...")
        
        # Check if we can import the API functions
        try:
            from src.text_processor import process_text
            from src.emotion_detector import detect_emotion
        except ImportError as e:
            print(f"   ❌ Cannot import API functions: {e}")
            print("   💡 Install dependencies: pip install -r requirements.txt")
            demo_simplified_audiobook()
            return
        
        # Process text into chunks
        chunks = process_text(story)
        print(f"   ✅ Created {len(chunks)} text chunks")
        
        # Show detected SFX
        total_sfx = 0
        for i, chunk in enumerate(chunks):
            if chunk['sfx']:
                print(f"   📢 Chunk {i+1} detected SFX: {chunk['sfx']}")
                total_sfx += len(chunk['sfx'])
            else:
                print(f"   📝 Chunk {i+1}: No SFX detected")
        
        print(f"   🎯 Total SFX events detected: {total_sfx}")
        
        print(f"\n🧠 Step 2: Detecting emotions...")
        
        # Detect emotions for each chunk
        for i, chunk in enumerate(chunks):
            emotion = detect_emotion(chunk['text'])
            chunk['emotion'] = emotion
            print(f"   Chunk {i+1}: '{chunk['text'][:40]}...' → {emotion}")
        
        print(f"\n🎙️ Step 3: Generating speech narration...")
        
        # Check if we can actually do TTS
        try:
            from src.tts_engine import synthesize_speech
            
            # Create temporary narration files
            narration_files = []
            temp_dir = Path("data/output/temp_narration")
            temp_dir.mkdir(parents=True, exist_ok=True)
            
            success_count = 0
            for i, chunk in enumerate(chunks):
                audio_file = temp_dir / f"narration_{i:02d}.wav"
                
                try:
                    print(f"   🔊 Synthesizing chunk {i+1}: '{chunk['text'][:30]}...'")
                    synthesize_speech(chunk['text'], str(audio_file))
                    
                    if audio_file.exists():
                        chunk['audio_file'] = str(audio_file)
                        narration_files.append(audio_file)
                        file_size = audio_file.stat().st_size
                        print(f"      ✅ Created: {audio_file.name} ({file_size} bytes)")
                        success_count += 1
                    else:
                        print(f"      ❌ Failed to create audio file")
                        chunk['audio_file'] = None
                        
                except Exception as e:
                    print(f"      ⚠️ TTS failed for chunk {i+1}: {e}")
                    chunk['audio_file'] = None
            
            print(f"   📊 Successfully created {success_count}/{len(chunks)} narration files")
            
            if success_count == 0:
                print("   ❌ No narration files created - TTS engine may not be available")
                print("   💡 Install pyttsx3: pip install pyttsx3")
                return
                
        except ImportError as e:
            print(f"   ❌ TTS not available: {e}")
            print("   💡 Install pyttsx3: pip install pyttsx3")
            return
        
        print(f"\n🎵 Step 4: Mixing audio with background music and SFX...")
        
        # Check audio assets
        bg_music_files = list(Path("assets/bg_music").glob("*.mp3"))
        sfx_files = list(Path("assets/sfx").glob("*.mp3"))
        
        print(f"   📁 Available background music: {[f.name for f in bg_music_files]}")
        print(f"   📁 Available sound effects: {[f.name for f in sfx_files]}")
        
        try:
            from src.audio_mixer import mix_audio
            
            # Prepare segments for mixing - only include chunks with audio files
            segments = []
            for chunk in chunks:
                if chunk.get('audio_file'):
                    segment = {
                        'text': chunk['text'],
                        'emotion': chunk['emotion'],
                        'sfx': chunk['sfx'],
                        'audio_file': chunk['audio_file']
                    }
                    segments.append(segment)
                    print(f"   🎯 Segment: emotion={segment['emotion']}, sfx={segment['sfx']}")
            
            if not segments:
                print("   ❌ No segments available for mixing")
                return
            
            # Create final audiobook
            output_path = "data/output/demo_result.mp3"
            print(f"   🎛️ Mixing {len(segments)} segments...")
            print(f"   📁 Output: {output_path}")
            
            mix_audio(segments, output_path)
            
            if Path(output_path).exists():
                file_size = Path(output_path).stat().st_size
                print(f"   ✅ Final audiobook created: {output_path}")
                print(f"   📊 File size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
                
                # Show what was mixed
                print(f"   🎼 Mixed content:")
                for i, segment in enumerate(segments):
                    from config.settings import EMOTION_BGM_MAP
                    bgm_file = EMOTION_BGM_MAP.get(segment['emotion'], 'neutral.mp3')
                    print(f"      - Segment {i+1}: {bgm_file} + {segment['sfx'] if segment['sfx'] else 'no SFX'}")
                
                # Clean up temporary files
                print(f"   🧹 Cleaning up {len(narration_files)} temporary files...")
                for temp_file in narration_files:
                    temp_file.unlink(missing_ok=True)
                if temp_dir.exists():
                    temp_dir.rmdir()
                
                print(f"\n🎉 SUCCESS! Real audiobook created with narration + BGM + SFX!")
                return True
            else:
                print(f"   ❌ Failed to create final audiobook")
                return False
                
        except ImportError as e:
            print(f"   ❌ Audio mixing not available: {e}")
            print("   💡 Install pydub: pip install pydub")
            return False
        except Exception as e:
            print(f"   ❌ Audio mixing failed: {e}")
            return False
        
    except Exception as e:
        print(f"❌ Error in audiobook creation: {e}")
        return False


def demo_simplified_audiobook():
    """Demo a simplified audiobook pipeline when dependencies aren't available."""
    print("\n🎬 Demo: Simplified Audiobook Pipeline")
    print("-" * 50)
    
    try:
        # Test the core logic without external dependencies
        story = """
        Sarah walked slowly toward the old wooden door. The door creaked loudly as she pushed it open.
        She let out a terrified scream when she saw the dark figure inside.
        But then she realized it was just her coat hanging on a hook, and she felt much better.
        """
        
        print("🔍 Step 1: Text processing (simulated)...")
        
        # Simulate text processing
        import re
        from config.settings import SFX_KEYWORDS
        
        # Basic text chunking
        sentences = [s.strip() + '.' for s in story.split('.') if s.strip()]
        
        chunks = []
        for i, sentence in enumerate(sentences):
            # Detect SFX keywords
            detected_sfx = []
            text_lower = sentence.lower()
            for sfx_type, keywords in SFX_KEYWORDS.items():
                for keyword in keywords:
                    if keyword in text_lower:
                        detected_sfx.append(sfx_type)
                        break
            
            chunk = {
                'text': sentence,
                'sfx': detected_sfx,
                'emotion': 'neutral'  # Default emotion in fallback mode
            }
            chunks.append(chunk)
            
            print(f"   Chunk {i+1}: '{sentence[:40]}...'")
            print(f"      SFX detected: {detected_sfx}")
        
        print(f"\n🧠 Step 2: Emotion detection (simulated)...")
        for i, chunk in enumerate(chunks):
            # Simulate emotion detection based on keywords
            text_lower = chunk['text'].lower()
            if any(word in text_lower for word in ['scream', 'terrified', 'scared']):
                emotion = 'fear'
            elif any(word in text_lower for word in ['better', 'relieved', 'realized']):
                emotion = 'joy'
            else:
                emotion = 'sadness'  # Default fallback emotion
            
            chunk['emotion'] = emotion
            print(f"   Chunk {i+1}: emotion = {emotion}")
        
        print(f"\n🎙️ Step 3: TTS synthesis (simulated)...")
        print(f"   Would generate {len(chunks)} narration files with pyttsx3")
        
        print(f"\n🎵 Step 4: Audio mixing (simulated)...")
        print(f"   Would mix with background music and sound effects:")
        
        from config.settings import EMOTION_BGM_MAP
        for i, chunk in enumerate(chunks):
            bgm_file = EMOTION_BGM_MAP.get(chunk['emotion'], 'neutral.mp3')
            print(f"   Segment {i+1}:")
            print(f"      Background: {bgm_file}")
            if chunk['sfx']:
                sfx_files = [f"{sfx}.mp3" for sfx in chunk['sfx']]
                print(f"      Sound effects: {sfx_files}")
            else:
                print(f"      Sound effects: none")
        
        print(f"\n✅ Simulated audiobook pipeline completed!")
        print(f"📊 Stats: {len(chunks)} chunks, {sum(len(c['sfx']) for c in chunks)} SFX events")
        print("💡 Install dependencies to run the real pipeline:")
        print("   pip install -r requirements.txt")
        
    except Exception as e:
        print(f"❌ Error in simplified audiobook demo: {e}")


def main():
    """Run all basic demos."""
    print("🎧 PDF to Audiobook Converter - Enhanced Basic Demo")
    print("=" * 55)
    print("Testing core functionality and real audiobook creation...")
    
    demo_configuration()
    demo_core_functions()
    demo_file_operations()
    demo_config_switching()
    demo_real_audiobook_creation()
    
    print("\n" + "=" * 55)
    print("🎉 Enhanced demo completed!")
    print("\nNext steps:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Run full demo: python demo.py")
    print("3. Test with real data: python app.py --config")


if __name__ == "__main__":
    main() 