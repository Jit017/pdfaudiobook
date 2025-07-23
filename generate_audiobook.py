#!/usr/bin/env python3
"""
Production Audiobook Generator

Creates complete audiobooks with narration, background music, and sound effects
using the integrated PDF to Audiobook system.
"""

import sys
import time
from pathlib import Path
from typing import List, Dict, Optional

def setup_logging():
    """Setup basic logging for the audiobook generator."""
    import logging
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    return logging.getLogger(__name__)

def check_dependencies() -> bool:
    """Check if required dependencies are available."""
    print("🔍 Checking dependencies...")
    
    missing_deps = []
    
    # Check core modules
    try:
        from src.text_processor import process_text
        from src.emotion_detector import detect_emotion
        from src.tts_engine import synthesize_speech
        from src.audio_mixer import mix_audio
        print("  ✅ Core modules available")
    except ImportError as e:
        print(f"  ❌ Core modules missing: {e}")
        return False
    
    # Check TTS dependency
    try:
        import pyttsx3
        print("  ✅ pyttsx3 (TTS) available")
    except ImportError:
        missing_deps.append("pyttsx3")
    
    # Check audio mixing dependency
    try:
        import pydub
        print("  ✅ pydub (audio mixing) available")
    except ImportError:
        missing_deps.append("pydub")
    
    if missing_deps:
        print(f"  ❌ Missing dependencies: {missing_deps}")
        print(f"  💡 Install with: pip install {' '.join(missing_deps)}")
        return False
    
    return True

def check_audio_assets() -> bool:
    """Check if required audio assets are available."""
    print("🎵 Checking audio assets...")
    
    required_files = [
        "assets/bg_music/joy.mp3",
        "assets/bg_music/sadness.mp3",
        "assets/sfx/door.mp3",
        "assets/sfx/scream.mp3"
    ]
    
    missing_files = []
    for file_path in required_files:
        if Path(file_path).exists():
            file_size = Path(file_path).stat().st_size
            print(f"  ✅ {file_path} ({file_size:,} bytes)")
        else:
            missing_files.append(file_path)
            print(f"  ❌ {file_path} - not found")
    
    if missing_files:
        print(f"  ❌ Missing {len(missing_files)} audio files")
        return False
    
    print(f"  ✅ All {len(required_files)} audio assets available")
    return True

def load_sample_story() -> str:
    """Load a sample story for audiobook generation."""
    story = """
    Sarah had always been curious about the old mansion at the end of her street. 
    Today, she finally decided to explore it. She walked slowly up the cracked pathway, 
    her footsteps echoing in the quiet afternoon.
    
    When she reached the front entrance, Sarah hesitated for a moment before pushing 
    open the heavy wooden door. The door creaked loudly as it swung open, revealing 
    a dusty hallway filled with shadows.
    
    As she stepped inside, something moved in the darkness ahead. Sarah let out a 
    terrified scream when a dark figure suddenly appeared before her, thinking it 
    was some kind of ghost or intruder.
    
    But then she started laughing when she realized it was just her own reflection 
    in an old mirror. She felt much better and even a bit silly for being so scared. 
    The mansion wasn't haunted after all - it was just full of memories and old furniture.
    
    Sarah spent the rest of the afternoon exploring the beautiful old rooms, discovering 
    family photographs and antique books. She left feeling peaceful and happy, 
    having conquered her fears and found something wonderful instead.
    """
    
    return story.strip()

def generate_audiobook(story: str, output_path: str = "data/output/demo_result.mp3") -> bool:
    """
    Generate a complete audiobook with narration, background music, and sound effects.
    
    Args:
        story: Text content to convert to audiobook
        output_path: Where to save the final audiobook file
        
    Returns:
        True if successful, False otherwise
    """
    
    logger = setup_logging()
    
    print("\n🎧 Starting Audiobook Generation")
    print("=" * 50)
    
    start_time = time.time()
    
    # Import required modules
    try:
        from src.text_processor import process_text
        from src.emotion_detector import detect_emotion
        from src.tts_engine import synthesize_speech
        from src.audio_mixer import mix_audio
    except ImportError as e:
        print(f"❌ Failed to import modules: {e}")
        return False
    
    # Step 1: Process text into chunks and detect SFX
    print("\n📝 Step 1: Processing text and detecting SFX...")
    
    try:
        chunks = process_text(story)
        print(f"   ✅ Created {len(chunks)} text chunks")
        
        # Show detected SFX
        total_sfx_events = 0
        for i, chunk in enumerate(chunks):
            chunk_preview = chunk['text'][:50] + "..." if len(chunk['text']) > 50 else chunk['text']
            if chunk['sfx']:
                print(f"   📢 Chunk {i+1}: {chunk['sfx']} detected")
                print(f"      Text: \"{chunk_preview}\"")
                total_sfx_events += len(chunk['sfx'])
            else:
                print(f"   📝 Chunk {i+1}: No SFX detected")
                print(f"      Text: \"{chunk_preview}\"")
        
        print(f"   🎯 Total SFX events: {total_sfx_events}")
        
    except Exception as e:
        print(f"   ❌ Text processing failed: {e}")
        return False
    
    # Step 2: Detect emotions for each chunk
    print(f"\n🧠 Step 2: Detecting emotions...")
    
    try:
        for i, chunk in enumerate(chunks):
            emotion = detect_emotion(chunk['text'])
            chunk['emotion'] = emotion
            print(f"   Chunk {i+1}: emotion = {emotion}")
            
            # Show which background music will be used
            from config.settings import EMOTION_BGM_MAP
            bgm_file = EMOTION_BGM_MAP.get(emotion, 'sadness.mp3')
            print(f"      → Background music: {bgm_file}")
        
    except Exception as e:
        print(f"   ❌ Emotion detection failed: {e}")
        return False
    
    # Step 3: Generate speech for each chunk
    print(f"\n🎙️ Step 3: Generating speech narration...")
    
    temp_dir = Path("data/output/temp_narration")
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    narration_files = []
    successful_chunks = 0
    
    try:
        for i, chunk in enumerate(chunks):
            print(f"   🔊 Synthesizing chunk {i+1}/{len(chunks)}...")
            
            # Create temporary audio file
            audio_file = temp_dir / f"narration_{i:02d}.wav"
            
            try:
                # Generate speech
                synthesize_speech(chunk['text'], str(audio_file))
                
                if audio_file.exists() and audio_file.stat().st_size > 0:
                    chunk['audio_file'] = str(audio_file)
                    narration_files.append(audio_file)
                    file_size = audio_file.stat().st_size
                    duration = file_size / (16000 * 2)  # Rough duration estimate
                    print(f"      ✅ Generated: {audio_file.name} ({file_size:,} bytes, ~{duration:.1f}s)")
                    successful_chunks += 1
                else:
                    print(f"      ❌ Failed to create audio file")
                    chunk['audio_file'] = None
                    
            except Exception as e:
                print(f"      ⚠️ TTS failed for chunk {i+1}: {e}")
                chunk['audio_file'] = None
        
        print(f"   📊 Successfully generated {successful_chunks}/{len(chunks)} narration files")
        
        if successful_chunks == 0:
            print("   ❌ No narration files created - cannot proceed")
            return False
            
    except Exception as e:
        print(f"   ❌ Speech synthesis failed: {e}")
        return False
    
    # Step 4: Mix audio with background music and sound effects
    print(f"\n🎵 Step 4: Mixing audio with background music and SFX...")
    
    try:
        # Prepare segments for mixing (only include chunks with audio files)
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
        
        print(f"   🎛️ Mixing {len(segments)} segments with audio...")
        
        # Show what will be mixed
        for i, segment in enumerate(segments):
            from config.settings import EMOTION_BGM_MAP
            bgm_file = EMOTION_BGM_MAP.get(segment['emotion'], 'sadness.mp3')
            sfx_info = f" + {segment['sfx']}" if segment['sfx'] else ""
            print(f"      Segment {i+1}: {bgm_file}{sfx_info}")
        
        # Create output directory
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        print(f"   📁 Output file: {output_path}")
        
        # Perform the mixing
        mix_audio(segments, output_path)
        
        # Check if output was created
        if Path(output_path).exists():
            file_size = Path(output_path).stat().st_size
            duration_estimate = len(segments) * 3  # Rough estimate
            print(f"   ✅ Final audiobook created successfully!")
            print(f"   📊 File size: {file_size:,} bytes ({file_size/1024/1024:.1f} MB)")
            print(f"   ⏱️ Estimated duration: ~{duration_estimate} seconds")
        else:
            print(f"   ❌ Failed to create final audiobook")
            return False
            
    except Exception as e:
        print(f"   ❌ Audio mixing failed: {e}")
        return False
    
    # Step 5: Cleanup and summary
    print(f"\n🧹 Step 5: Cleanup and summary...")
    
    try:
        # Clean up temporary files
        print(f"   🗑️ Cleaning up {len(narration_files)} temporary files...")
        for temp_file in narration_files:
            temp_file.unlink(missing_ok=True)
        
        if temp_dir.exists() and not list(temp_dir.iterdir()):
            temp_dir.rmdir()
            print(f"   ✅ Temporary directory cleaned up")
            
    except Exception as e:
        print(f"   ⚠️ Cleanup warning: {e}")
    
    # Final summary
    elapsed_time = time.time() - start_time
    
    print(f"\n🎉 AUDIOBOOK GENERATION COMPLETE!")
    print("=" * 50)
    print(f"📖 Story: {len(story)} characters, {len(chunks)} chunks")
    print(f"🎵 Audio: {successful_chunks} narrated segments")
    print(f"📢 SFX: {total_sfx_events} sound effect events")
    print(f"⏱️ Time: {elapsed_time:.1f} seconds")
    print(f"📁 Output: {output_path}")
    print(f"\n🎧 Your audiobook is ready to play!")
    
    return True

def main():
    """Main function to run the audiobook generator."""
    
    print("🎧 PDF to Audiobook Converter - Production Generator")
    print("=" * 55)
    print("Creating complete audiobook with narration + BGM + SFX...")
    
    # Check system requirements
    if not check_dependencies():
        print("\n❌ Missing dependencies. Please install required packages:")
        print("   pip install pyttsx3 pydub")
        sys.exit(1)
    
    if not check_audio_assets():
        print("\n❌ Missing audio assets. Please ensure all BGM and SFX files are present.")
        sys.exit(1)
    
    # Load story content
    print("\n📚 Loading sample story...")
    story = load_sample_story()
    word_count = len(story.split())
    print(f"   ✅ Loaded story: {len(story)} characters, {word_count} words")
    
    # Generate the audiobook
    output_file = "data/output/demo_result.mp3"
    success = generate_audiobook(story, output_file)
    
    if success:
        print(f"\n🎉 SUCCESS! Audiobook created: {output_file}")
        print(f"💡 Play with: open {output_file}")
        
        # Offer to play the file
        try:
            import platform
            if platform.system() == "Darwin":  # macOS
                response = input("\n🎵 Play the audiobook now? (y/N): ").strip().lower()
                if response in ['y', 'yes']:
                    import subprocess
                    subprocess.run(["open", output_file])
        except:
            pass
            
    else:
        print(f"\n❌ Failed to generate audiobook")
        sys.exit(1)

if __name__ == "__main__":
    main() 