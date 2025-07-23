#!/usr/bin/env python3
"""
Streamlined Audiobook Maker

Creates complete audiobooks with narration, background music, and sound effects.
Bypasses PDF dependencies for direct text-to-audiobook conversion.
"""

import sys
import time
from pathlib import Path
from typing import List, Dict

def check_minimal_dependencies() -> bool:
    """Check if minimal required dependencies are available."""
    print("🔍 Checking minimal dependencies...")
    
    missing_deps = []
    
    # Check TTS dependency
    try:
        import pyttsx3
        print("  ✅ pyttsx3 (TTS) available")
    except ImportError:
        missing_deps.append("pyttsx3")
        print("  ❌ pyttsx3 not found")
    
    # Check audio mixing dependency
    try:
        import pydub
        print("  ✅ pydub (audio mixing) available")
    except ImportError:
        missing_deps.append("pydub")
        print("  ❌ pydub not found")
    
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

def simple_text_processor(story: str) -> List[Dict]:
    """
    Simple text processor that doesn't require external dependencies.
    Splits text into chunks and detects SFX keywords.
    """
    
    # SFX keywords matching our available assets
    SFX_KEYWORDS = {
        "door": ["door", "doorway", "opened", "closed", "creak"],
        "footsteps": ["walked", "running", "footsteps", "steps"],
        "scream": ["scream", "screamed", "screaming", "yell", "shout"]
    }
    
    # Split story into sentences/chunks
    import re
    sentences = re.split(r'[.!?]+', story)
    chunks = []
    
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
            
        # Add punctuation back
        if not sentence.endswith(('.', '!', '?')):
            sentence += '.'
        
        # Detect SFX keywords
        detected_sfx = []
        text_lower = sentence.lower()
        
        for sfx_type, keywords in SFX_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text_lower:
                    detected_sfx.append(sfx_type)
                    break  # Only add each SFX type once per chunk
        
        chunk = {
            'text': sentence,
            'sfx': detected_sfx,
            'emotion': 'neutral'  # Will be set later
        }
        chunks.append(chunk)
    
    return chunks

def simple_emotion_detector(text: str) -> str:
    """
    Simple emotion detector based on keyword analysis.
    """
    text_lower = text.lower()
    
    # Fear/negative emotions
    if any(word in text_lower for word in ['scream', 'terrified', 'scared', 'afraid', 'dark', 'shadow']):
        return 'fear'
    
    # Joy/positive emotions  
    elif any(word in text_lower for word in ['happy', 'laughing', 'joy', 'peaceful', 'wonderful', 'better']):
        return 'joy'
    
    # Default to sadness for dramatic effect
    else:
        return 'sadness'

def synthesize_speech_simple(text: str, output_path: str) -> bool:
    """
    Simple TTS synthesis using pyttsx3.
    """
    try:
        import pyttsx3
        
        # Initialize TTS engine
        engine = pyttsx3.init()
        
        # Configure voice settings for better quality
        voices = engine.getProperty('voices')
        if voices:
            # Use first available voice
            engine.setProperty('voice', voices[0].id)
        
        # Set speech rate (words per minute)
        engine.setProperty('rate', 150)  # Slower for better clarity
        
        # Set volume
        engine.setProperty('volume', 0.9)
        
        # Save speech to file
        engine.save_to_file(text, output_path)
        engine.runAndWait()
        
        return Path(output_path).exists()
        
    except Exception as e:
        print(f"      TTS Error: {e}")
        return False

def mix_audio_simple(segments: List[Dict], output_path: str) -> bool:
    """
    Simple audio mixer using pydub.
    """
    try:
        from pydub import AudioSegment
        from pydub.effects import normalize
        
        print(f"   🎛️ Starting audio mixing...")
        
        # Emotion to BGM mapping
        EMOTION_BGM_MAP = {
            "joy": "assets/bg_music/joy.mp3",
            "sadness": "assets/bg_music/sadness.mp3", 
            "anger": "assets/bg_music/sadness.mp3",
            "fear": "assets/bg_music/sadness.mp3",
            "surprise": "assets/bg_music/joy.mp3",
            "neutral": "assets/bg_music/sadness.mp3"
        }
        
        # Create final audio track
        final_audio = AudioSegment.empty()
        
        for i, segment in enumerate(segments):
            print(f"      Processing segment {i+1}/{len(segments)}...")
            
            # Load narration audio
            try:
                narration = AudioSegment.from_wav(segment['audio_file'])
                print(f"        ✅ Loaded narration: {len(narration)}ms")
            except Exception as e:
                print(f"        ❌ Failed to load narration: {e}")
                continue
            
            # Load background music
            emotion = segment['emotion']
            bgm_file = EMOTION_BGM_MAP.get(emotion, "assets/bg_music/sadness.mp3")
            
            try:
                bgm = AudioSegment.from_mp3(bgm_file)
                # Loop BGM to match narration length
                if len(bgm) < len(narration):
                    repeats = (len(narration) // len(bgm)) + 1
                    bgm = bgm * repeats
                bgm = bgm[:len(narration)]  # Trim to exact length
                
                # Lower BGM volume
                bgm = bgm - 20  # Reduce by 20dB
                print(f"        ✅ Loaded BGM: {bgm_file}")
            except Exception as e:
                print(f"        ⚠️ BGM load failed: {e}")
                bgm = AudioSegment.silent(duration=len(narration))
            
            # Mix narration and BGM
            segment_audio = narration.overlay(bgm)
            
            # Add sound effects
            for sfx_type in segment['sfx']:
                sfx_file = f"assets/sfx/{sfx_type}.mp3"
                try:
                    sfx = AudioSegment.from_mp3(sfx_file)
                    # Add SFX at the beginning of the segment
                    if len(sfx) <= len(segment_audio):
                        segment_audio = segment_audio.overlay(sfx, position=0)
                        print(f"        ✅ Added SFX: {sfx_file}")
                    else:
                        print(f"        ⚠️ SFX too long: {sfx_file}")
                except Exception as e:
                    print(f"        ⚠️ SFX load failed {sfx_file}: {e}")
            
            # Add to final audio with small pause
            final_audio += segment_audio
            if i < len(segments) - 1:  # Add pause between segments (except last)
                final_audio += AudioSegment.silent(duration=500)  # 0.5 second pause
        
        # Normalize final audio
        final_audio = normalize(final_audio)
        
        # Export final audiobook
        print(f"   📁 Exporting to: {output_path}")
        final_audio.export(output_path, format="mp3", bitrate="128k")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Audio mixing failed: {e}")
        return False

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
    """
    
    print("\n🎧 Starting Audiobook Generation")
    print("=" * 50)
    
    start_time = time.time()
    
    # Step 1: Process text into chunks and detect SFX
    print("\n📝 Step 1: Processing text and detecting SFX...")
    
    try:
        chunks = simple_text_processor(story)
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
            emotion = simple_emotion_detector(chunk['text'])
            chunk['emotion'] = emotion
            print(f"   Chunk {i+1}: emotion = {emotion}")
            
            # Show which background music will be used
            bgm_files = {
                "joy": "joy.mp3",
                "sadness": "sadness.mp3", 
                "fear": "sadness.mp3",
                "neutral": "sadness.mp3"
            }
            bgm_file = bgm_files.get(emotion, 'sadness.mp3')
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
                success = synthesize_speech_simple(chunk['text'], str(audio_file))
                
                if success and audio_file.exists() and audio_file.stat().st_size > 0:
                    chunk['audio_file'] = str(audio_file)
                    narration_files.append(audio_file)
                    file_size = audio_file.stat().st_size
                    print(f"      ✅ Generated: {audio_file.name} ({file_size:,} bytes)")
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
                segments.append(chunk)
        
        print(f"   🎛️ Mixing {len(segments)} segments with audio...")
        
        # Show what will be mixed
        for i, segment in enumerate(segments):
            bgm_files = {
                "joy": "joy.mp3",
                "sadness": "sadness.mp3", 
                "fear": "sadness.mp3",
                "neutral": "sadness.mp3"
            }
            bgm_file = bgm_files.get(segment['emotion'], 'sadness.mp3')
            sfx_info = f" + {segment['sfx']}" if segment['sfx'] else ""
            print(f"      Segment {i+1}: {bgm_file}{sfx_info}")
        
        # Create output directory
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        print(f"   📁 Output file: {output_path}")
        
        # Perform the mixing
        success = mix_audio_simple(segments, output_path)
        
        if success and Path(output_path).exists():
            file_size = Path(output_path).stat().st_size
            print(f"   ✅ Final audiobook created successfully!")
            print(f"   📊 File size: {file_size:,} bytes ({file_size/1024/1024:.1f} MB)")
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
    
    print("🎧 Streamlined Audiobook Maker")
    print("=" * 40)
    print("Creating complete audiobook with narration + BGM + SFX...")
    
    # Check system requirements
    if not check_minimal_dependencies():
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