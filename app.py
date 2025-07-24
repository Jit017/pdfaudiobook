#!/usr/bin/env python3
"""
Streamlit Web UI for PDF to Audiobook Generator

A user-friendly interface for converting PDFs to audiobooks with 
narration, background music, and sound effects.
"""

import streamlit as st
import os
import time
from pathlib import Path
import tempfile
from typing import Optional

# Configure Streamlit page
st.set_page_config(
    page_title="PDF to Audiobook Generator",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

def check_dependencies() -> tuple[bool, list[str]]:
    """Check if required dependencies are available."""
    missing_deps = []
    
    try:
        import pyttsx3
    except ImportError:
        missing_deps.append("pyttsx3")
    
    try:
        import pydub
    except ImportError:
        missing_deps.append("pydub")
    
    # Check if audio assets exist
    required_files = [
        "assets/bg_music/joy.mp3",
        "assets/bg_music/sadness.mp3",
        "assets/sfx/door.mp3",
        "assets/sfx/scream.mp3"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    all_deps_available = len(missing_deps) == 0 and len(missing_files) == 0
    
    return all_deps_available, missing_deps + missing_files

def extract_text_from_pdf(pdf_path: str) -> Optional[str]:
    """Extract text from PDF file."""
    try:
        # Try to use PyMuPDF if available
        try:
            import fitz
            doc = fitz.open(pdf_path)
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            return text.strip()
        except ImportError:
            st.warning("PyMuPDF not available. Install with: pip install PyMuPDF")
            return None
    except Exception as e:
        st.error(f"Error extracting text from PDF: {e}")
        return None

def simple_text_processor(text: str) -> list[dict]:
    """
    Simple text processor that splits text into chunks and detects SFX keywords.
    """
    # SFX keywords matching our available assets
    SFX_KEYWORDS = {
        "door": ["door", "doorway", "opened", "closed", "creak", "creaked"],
        "footsteps": ["walked", "running", "footsteps", "steps", "walking"],
        "scream": ["scream", "screamed", "screaming", "yell", "shout", "shouted"]
    }
    
    # Split text into sentences/chunks
    import re
    sentences = re.split(r'[.!?]+', text)
    chunks = []
    
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence or len(sentence) < 10:  # Skip very short sentences
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
        
        # Simple emotion detection
        if any(word in text_lower for word in ['scream', 'terrified', 'scared', 'afraid', 'dark', 'shadow']):
            emotion = 'fear'
        elif any(word in text_lower for word in ['happy', 'laughing', 'joy', 'peaceful', 'wonderful', 'better']):
            emotion = 'joy'
        else:
            emotion = 'sadness'  # Default for dramatic effect
        
        chunk = {
            'text': sentence,
            'sfx': detected_sfx,
            'emotion': emotion
        }
        chunks.append(chunk)
    
    return chunks

def generate_single_audio_chunk(text: str, output_path: str) -> bool:
    """
    Generate a single audio chunk using TTS in a Streamlit-safe way.
    
    Args:
        text: Text to convert to speech
        output_path: Path where to save the audio file
        
    Returns:
        True if successful, False otherwise
    """
    import pyttsx3
    import time
    from pathlib import Path
    
    try:
        # Create a completely fresh engine instance
        engine = pyttsx3.init()
        
        # Configure the engine using config settings
        from config.settings import TTS_CONFIG
        tts_settings = TTS_CONFIG['pyttsx3']
        
        voices = engine.getProperty('voices')
        if voices and len(voices) > 0:
            # Find the best English voice using config keywords
            best_voice = None
            for voice in voices:
                for keyword in tts_settings['voice_selection']['preferred_keywords']:
                    if keyword in voice.name.lower() or keyword in voice.id.lower():
                        best_voice = voice.id
                        break
                if best_voice:
                    break
            
            if best_voice:
                engine.setProperty('voice', best_voice)
            else:
                fallback_index = tts_settings['voice_selection']['fallback_index']
                engine.setProperty('voice', voices[fallback_index].id)
        
        # Set optimal properties from config
        engine.setProperty('rate', tts_settings['rate'])
        engine.setProperty('volume', tts_settings['volume'])
        
        # Generate the audio
        engine.save_to_file(text, output_path)
        engine.runAndWait()
        
        # Give extra time for file to be written
        time.sleep(1.0)
        
        # Clean shutdown
        try:
            engine.stop()
        except:
            pass
        
        # Verify file was created
        if Path(output_path).exists():
            from config.settings import AUDIO_PROCESSING
            file_size = Path(output_path).stat().st_size
            return file_size > AUDIO_PROCESSING['minimum_file_size']
        
        return False
        
    except Exception as e:
        print(f"TTS generation error: {e}")
        return False
    
    finally:
        # Extra cleanup
        try:
            del engine
        except:
            pass

def generate_audiobook_from_text(text: str, output_path: str, tts_engine: str = "pyttsx3") -> bool:
    """
    Generate audiobook from text using the streamlined approach.
    """
    try:
        # Import audio processing
        from pydub import AudioSegment
        from pydub.effects import normalize
        import pyttsx3
        
        # Process text into chunks
        chunks = simple_text_processor(text)
        
        if not chunks:
            st.error("No valid text chunks found to process")
            return False
        
        # Create progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Step 1: Generate TTS for each chunk
        status_text.text("🎙️ Generating speech narration...")
        
        from config.settings import OUTPUT_FILES
        temp_dir = Path(OUTPUT_FILES['temp_narration_dir'])
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        narration_files = []
        successful_chunks = 0
        
        for i, chunk in enumerate(chunks):
            progress = (i + 1) / (len(chunks) + 1)  # +1 for mixing step
            progress_bar.progress(progress * 0.8)  # Reserve 20% for mixing
            
            status_text.text(f"🔊 Synthesizing chunk {i+1}/{len(chunks)}: '{chunk['text'][:40]}...'")
            
            # Try to create a proper TTS engine and generate audio
            audio_file = None
            try:
                # Test with a simple approach first
                test_file = temp_dir / f"narration_{i:02d}.aiff"
                
                # Clean approach: create new engine for each chunk
                success = generate_single_audio_chunk(chunk['text'], str(test_file))
                
                from config.settings import AUDIO_PROCESSING
                if success and test_file.exists() and test_file.stat().st_size > AUDIO_PROCESSING['minimum_file_size']:
                    # Verify audio content
                    try:
                        test_audio = AudioSegment.from_file(str(test_file))
                        if len(test_audio) > AUDIO_PROCESSING['minimum_duration']:
                            audio_file = test_file
                            chunk['audio_file'] = str(audio_file)
                            chunk['audio_format'] = 'aiff'
                            narration_files.append(audio_file)
                            st.text(f"      ✅ Generated: {audio_file.name} ({test_file.stat().st_size:,} bytes, {len(test_audio)}ms)")
                            successful_chunks += 1
                        else:
                            st.warning(f"Generated audio for chunk {i+1} is too short ({len(test_audio)}ms)")
                            test_file.unlink(missing_ok=True)
                    except Exception as e:
                        st.warning(f"Audio verification failed for chunk {i+1}: {e}")
                        test_file.unlink(missing_ok=True)
                else:
                    file_size = test_file.stat().st_size if test_file.exists() else 0
                    st.warning(f"TTS failed for chunk {i+1}: {file_size} bytes generated")
                    if test_file.exists():
                        test_file.unlink(missing_ok=True)
                        
            except Exception as e:
                st.warning(f"TTS error for chunk {i+1}: {e}")
                continue
            
            # Show status for failed generation
            if audio_file is None:
                st.warning(f"Failed to generate audio for chunk {i+1}")
        
        if not narration_files:
            st.error("No narration files were created")
            return False
        
        # Step 2: Mix audio with background music and SFX
        status_text.text("🎵 Mixing audio with background music and sound effects...")
        progress_bar.progress(0.9)
        
        # Import emotion to BGM mapping from config
        from config.settings import get_bgm_path
        
        final_audio = AudioSegment.empty()
        
        for i, chunk in enumerate(chunks):
            if not chunk.get('audio_file'):
                continue
                
            # Load narration with format detection
            try:
                audio_format = chunk.get('audio_format', 'wav')
                audio_file_path = chunk['audio_file']
                
                if audio_format == 'aiff':
                    narration = AudioSegment.from_file(audio_file_path, format='aiff')
                elif audio_format == 'wav':
                    narration = AudioSegment.from_wav(audio_file_path)
                elif audio_format == 'm4a':
                    narration = AudioSegment.from_file(audio_file_path, format='m4a')
                else:
                    # Try auto-detection
                    narration = AudioSegment.from_file(audio_file_path)
                
            except Exception as e:
                st.warning(f"Failed to load narration for chunk {i+1}: {e}")
                continue
            
            # Load and mix background music
            emotion = chunk['emotion']
            bgm_file = get_bgm_path(emotion)
            
            try:
                bgm = AudioSegment.from_mp3(bgm_file)
                # Loop BGM to match narration length
                if len(bgm) < len(narration):
                    repeats = (len(narration) // len(bgm)) + 1
                    bgm = bgm * repeats
                bgm = bgm[:len(narration)]
                bgm = bgm - AUDIO_PROCESSING['bgm_volume_reduction']  # Lower BGM volume
                
                segment_audio = narration.overlay(bgm)
            except Exception as e:
                st.warning(f"Failed to load BGM {bgm_file}: {e}")
                segment_audio = narration
            
            # Add sound effects
            for sfx_type in chunk['sfx']:
                from config.settings import get_sfx_path
                sfx_file = get_sfx_path(sfx_type)
                if sfx_file:
                    try:
                        sfx = AudioSegment.from_mp3(sfx_file)
                        if len(sfx) <= len(segment_audio):
                            segment_audio = segment_audio.overlay(sfx, position=0)
                    except Exception as e:
                        st.warning(f"Failed to load SFX {sfx_file}: {e}")
                else:
                    st.warning(f"SFX file not found for type: {sfx_type}")
            
            # Add to final audio with pause
            final_audio += segment_audio
            if i < len([c for c in chunks if c.get('audio_file')]) - 1:
                pause_duration = AUDIO_PROCESSING['mixing_pause_between_segments']
                final_audio += AudioSegment.silent(duration=pause_duration)
        
        # Normalize and export
        status_text.text("📁 Exporting final audiobook...")
        progress_bar.progress(0.95)
        
        final_audio = normalize(final_audio)
        
        # Create output directory
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Export final audiobook
        final_audio.export(output_path, format="mp3", bitrate="128k")
        
        # Cleanup
        for temp_file in narration_files:
            temp_file.unlink(missing_ok=True)
        if temp_dir.exists() and not list(temp_dir.iterdir()):
            temp_dir.rmdir()
        
        progress_bar.progress(1.0)
        status_text.text("✅ Audiobook generation complete!")
        
        return True
        
    except Exception as e:
        st.error(f"Audiobook generation failed: {e}")
        return False

def main():
    """Main Streamlit application."""
    
    # Header
    st.title("📚 PDF to Audiobook Generator")
    st.markdown("Convert your PDFs into immersive audiobooks with narration, background music, and sound effects!")
    
    # Check dependencies
    deps_ok, missing_items = check_dependencies()
    
    if not deps_ok:
        st.error("⚠️ Missing Dependencies")
        st.write("Please install the following:")
        for item in missing_items:
            if item.endswith('.mp3'):
                st.write(f"• Audio asset: `{item}`")
            else:
                st.write(f"• Python package: `{item}` (install with: `pip install {item}`)")
        st.stop()
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # TTS Engine selection
        tts_engine = st.selectbox(
            "TTS Engine",
            options=["pyttsx3", "gTTS", "coqui"],
            index=0,
            help="Text-to-speech engine (pyttsx3 is offline and works immediately)"
        )
        
        # GPU usage
        use_gpu = st.checkbox(
            "Use GPU",
            value=False,
            help="Enable GPU acceleration (requires compatible hardware)"
        )
        
        # Real emotion detection
        use_real_emotion = st.checkbox(
            "Use Real Emotion Detection",
            value=False,
            help="Use AI-powered emotion detection (requires transformers)"
        )
        
        # Show current config
        st.markdown("---")
        st.subheader("Current Settings")
        st.write(f"🎙️ TTS: {tts_engine}")
        st.write(f"⚡ GPU: {'Enabled' if use_gpu else 'Disabled'}")
        st.write(f"🧠 Emotion: {'AI' if use_real_emotion else 'Rule-based'}")
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("📄 PDF Upload")
        
        uploaded_file = st.file_uploader(
            "Choose a PDF file",
            type=['pdf'],
            help="Upload a PDF file to convert to audiobook"
        )
        
        # Sample text option
        st.markdown("---")
        st.subheader("📝 Or Use Sample Text")
        use_sample = st.checkbox("Use built-in sample story")
        
        if use_sample:
            from config.settings import SAMPLE_STORY
            st.text_area("Sample story:", SAMPLE_STORY, height=200, disabled=True)
    
    with col2:
        st.header("🎧 Generate Audiobook")
        
        # Text preview area
        extracted_text = None
        
        if uploaded_file is not None:
            # Save uploaded file
            input_dir = Path("data/input")
            input_dir.mkdir(parents=True, exist_ok=True)
            
            pdf_path = input_dir / uploaded_file.name
            with open(pdf_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            st.success(f"✅ PDF uploaded: {uploaded_file.name}")
            
            # Extract text
            with st.spinner("Extracting text from PDF..."):
                extracted_text = extract_text_from_pdf(str(pdf_path))
            
            if extracted_text:
                st.success(f"✅ Extracted {len(extracted_text)} characters")
                
                # Show text preview
                with st.expander("📖 Text Preview"):
                    preview = extracted_text[:1000] + "..." if len(extracted_text) > 1000 else extracted_text
                    st.text_area("Extracted text:", preview, height=200)
            else:
                st.error("❌ Failed to extract text from PDF")
        
        elif use_sample:
            from config.settings import SAMPLE_STORY
            extracted_text = SAMPLE_STORY
            st.info("✅ Using sample story")
        
        # Generation button
        if extracted_text:
            # Show processing preview
            with st.expander("🔍 Processing Preview"):
                chunks = simple_text_processor(extracted_text)
                
                st.write(f"**Text chunks:** {len(chunks)}")
                
                # Show SFX and emotions
                sfx_detected = []
                emotions_detected = []
                
                for i, chunk in enumerate(chunks):
                    if chunk['sfx']:
                        sfx_detected.extend(chunk['sfx'])
                    emotions_detected.append(chunk['emotion'])
                
                col_sfx, col_emotion = st.columns(2)
                
                with col_sfx:
                    st.write("**SFX Detected:**")
                    unique_sfx = list(set(sfx_detected))
                    if unique_sfx:
                        for sfx in unique_sfx:
                            st.write(f"🎭 {sfx}")
                    else:
                        st.write("None detected")
                
                with col_emotion:
                    st.write("**Emotions Detected:**")
                    unique_emotions = list(set(emotions_detected))
                    for emotion in unique_emotions:
                        count = emotions_detected.count(emotion)
                        st.write(f"😊 {emotion}: {count} chunks")
            
            # Generate button
            if st.button("🎬 Generate Audiobook", type="primary", use_container_width=True):
                from config.settings import get_output_path
                output_path = get_output_path('streamlit')
                
                with st.spinner("🎧 Generating audiobook... This may take a few minutes."):
                    success = generate_audiobook_from_text(extracted_text, output_path, tts_engine)
                
                if success and Path(output_path).exists():
                    st.success("🎉 Audiobook generated successfully!")
                    
                    # Show file info
                    file_size = Path(output_path).stat().st_size
                    st.write(f"📁 File: `{output_path}`")
                    st.write(f"📊 Size: {file_size:,} bytes ({file_size/1024/1024:.1f} MB)")
                    
                else:
                    st.error("❌ Failed to generate audiobook")
        
        else:
            st.info("👆 Please upload a PDF or select the sample story option")
    
    # Audio player section
    st.markdown("---")
    st.header("🎵 Generated Audiobook")
    
    from config.settings import get_output_path
    output_path = get_output_path('streamlit')
    if Path(output_path).exists():
        st.success("✅ Audiobook available!")
        
        # Display audio player
        try:
            with open(output_path, "rb") as audio_file:
                audio_bytes = audio_file.read()
                st.audio(audio_bytes, format='audio/mp3')
            
            # Download button
            st.download_button(
                label="📥 Download Audiobook",
                data=audio_bytes,
                file_name="audiobook.mp3",
                mime="audio/mp3"
            )
            
        except Exception as e:
            st.error(f"Error loading audio file: {e}")
    else:
        st.info("No audiobook generated yet. Upload a PDF and click 'Generate Audiobook' to create one.")
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666;'>
            📚 PDF to Audiobook Generator | Built with Streamlit | 
            Features: TTS Narration + Background Music + Sound Effects
        </div>
        """, 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main() 