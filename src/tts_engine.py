"""
Text-to-Speech Engine module supporting multiple TTS backends.

Provides flexible TTS functionality with support for pyttsx3 (offline),
gTTS (online), and Coqui TTS (GPU-accelerated), controlled by configuration.
"""

import os
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any, List
import time

from .utils import setup_logging, timing_decorator, ensure_file_extension, log_event
from config.settings import (
    TTS_ENGINE, USE_GPU, VOICE_SPEED, VOICE_VOLUME, 
    SAMPLE_RATE, OUTPUT_DIR, AUDIO_FORMAT
)

# Module-level logger
logger = setup_logging(__name__)


class TTSEngine:
    """
    Text-to-Speech engine with multiple backend support.
    
    Supports:
    - pyttsx3: Offline TTS (good for development)
    - gtts: Google Text-to-Speech (requires internet)
    - coqui: Coqui TTS (GPU-accelerated, high quality)
    """
    
    def __init__(self, engine_type: Optional[str] = None):
        self.logger = setup_logging(__name__)
        self.engine_type = engine_type or TTS_ENGINE
        self.engine = None
        self.voice_settings = {
            'rate': VOICE_SPEED,
            'volume': VOICE_VOLUME
        }
        
        # Initialize the specified engine
        self._initialize_engine()
    
    def _initialize_engine(self):
        """Initialize the TTS engine based on configuration."""
        try:
            if self.engine_type == "pyttsx3":
                self._initialize_pyttsx3()
            elif self.engine_type == "gtts":
                self._initialize_gtts()
            elif self.engine_type == "coqui":
                self._initialize_coqui()
            else:
                self.logger.warning(f"Unknown TTS engine: {self.engine_type}, falling back to pyttsx3")
                self.engine_type = "pyttsx3"
                self._initialize_pyttsx3()
                
        except Exception as e:
            self.logger.error(f"Failed to initialize {self.engine_type} engine: {e}")
            if self.engine_type != "pyttsx3":
                self.logger.info("Falling back to pyttsx3")
                self.engine_type = "pyttsx3"
                self._initialize_pyttsx3()
            else:
                raise
    
    def _initialize_pyttsx3(self):
        """Initialize pyttsx3 TTS engine."""
        try:
            import pyttsx3
            
            self.engine = pyttsx3.init()
            
            # Configure voice settings
            self.engine.setProperty('rate', self.voice_settings['rate'])
            self.engine.setProperty('volume', self.voice_settings['volume'])
            
            # List available voices
            voices = self.engine.getProperty('voices')
            if voices:
                self.logger.info(f"pyttsx3 initialized with {len(voices)} voices available")
                # Use the first available voice (can be made configurable)
                self.engine.setProperty('voice', voices[0].id)
            
        except ImportError:
            raise ImportError("pyttsx3 not installed. Run: pip install pyttsx3")
    
    def _initialize_gtts(self):
        """Initialize Google Text-to-Speech."""
        try:
            from gtts import gTTS
            # gTTS doesn't need initialization, just import check
            self.logger.info("Google TTS initialized")
            
        except ImportError:
            raise ImportError("gTTS not installed. Run: pip install gtts")
    
    def _initialize_coqui(self):
        """Initialize Coqui TTS (GPU-accelerated)."""
        try:
            from TTS.api import TTS
            import torch
            
            if not USE_GPU or not torch.cuda.is_available():
                self.logger.warning("Coqui TTS requested but GPU not available")
                raise RuntimeError("GPU required for Coqui TTS")
            
            # Initialize with a good quality model
            model_name = "tts_models/en/ljspeech/tacotron2-DDC"
            self.engine = TTS(model_name=model_name, gpu=True)
            
            self.logger.info(f"Coqui TTS initialized with model: {model_name}")
            
        except ImportError:
            raise ImportError("Coqui TTS not installed. Run: pip install TTS")
    
    @timing_decorator
    def synthesize_speech(self, text: str, output_path: Path) -> bool:
        """
        Convert text to speech and save to file.
        
        Args:
            text: Text to convert to speech
            output_path: Path where audio file will be saved
            
        Returns:
            True if successful, False otherwise
        """
        if not text.strip():
            self.logger.warning("Empty text provided for TTS")
            return False
        
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Ensure correct file extension
        output_path = ensure_file_extension(output_path, AUDIO_FORMAT)
        
        try:
            if self.engine_type == "pyttsx3":
                return self._synthesize_pyttsx3(text, output_path)
            elif self.engine_type == "gtts":
                return self._synthesize_gtts(text, output_path)
            elif self.engine_type == "coqui":
                return self._synthesize_coqui(text, output_path)
            else:
                self.logger.error(f"Unknown engine type: {self.engine_type}")
                return False
                
        except Exception as e:
            self.logger.error(f"TTS synthesis failed: {e}")
            return False
    
    def _synthesize_pyttsx3(self, text: str, output_path: Path) -> bool:
        """Synthesize speech using pyttsx3."""
        try:
            # pyttsx3 saves to WAV, we might need to convert
            temp_wav = output_path.with_suffix('.wav')
            
            self.engine.save_to_file(text, str(temp_wav))
            self.engine.runAndWait()
            
            # Convert to desired format if needed
            if output_path.suffix.lower() != '.wav':
                success = self._convert_audio_format(temp_wav, output_path)
                if temp_wav.exists():
                    temp_wav.unlink()  # Clean up temp file
                return success
            else:
                if temp_wav != output_path:
                    temp_wav.rename(output_path)
                return True
                
        except Exception as e:
            self.logger.error(f"pyttsx3 synthesis error: {e}")
            return False
    
    def _synthesize_gtts(self, text: str, output_path: Path) -> bool:
        """Synthesize speech using Google TTS."""
        try:
            from gtts import gTTS
            
            tts = gTTS(text=text, lang='en', slow=False)
            
            # gTTS saves to MP3 by default
            if output_path.suffix.lower() == '.mp3':
                tts.save(str(output_path))
                return True
            else:
                # Save to temp MP3 then convert
                temp_mp3 = output_path.with_suffix('.mp3')
                tts.save(str(temp_mp3))
                
                success = self._convert_audio_format(temp_mp3, output_path)
                if temp_mp3.exists():
                    temp_mp3.unlink()
                return success
                
        except Exception as e:
            self.logger.error(f"gTTS synthesis error: {e}")
            return False
    
    def _synthesize_coqui(self, text: str, output_path: Path) -> bool:
        """Synthesize speech using Coqui TTS."""
        try:
            if not self.engine:
                raise RuntimeError("Coqui TTS engine not initialized")
            
            # Coqui generates WAV by default
            temp_wav = output_path.with_suffix('.wav')
            
            self.engine.tts_to_file(text=text, file_path=str(temp_wav))
            
            # Convert if needed
            if output_path.suffix.lower() != '.wav':
                success = self._convert_audio_format(temp_wav, output_path)
                if temp_wav.exists():
                    temp_wav.unlink()
                return success
            else:
                if temp_wav != output_path:
                    temp_wav.rename(output_path)
                return True
                
        except Exception as e:
            self.logger.error(f"Coqui TTS synthesis error: {e}")
            return False
    
    def _convert_audio_format(self, input_path: Path, output_path: Path) -> bool:
        """Convert audio from one format to another using pydub."""
        try:
            from pydub import AudioSegment
            
            # Load audio file
            if input_path.suffix.lower() == '.wav':
                audio = AudioSegment.from_wav(str(input_path))
            elif input_path.suffix.lower() == '.mp3':
                audio = AudioSegment.from_mp3(str(input_path))
            else:
                audio = AudioSegment.from_file(str(input_path))
            
            # Export in desired format
            output_format = output_path.suffix.lower()[1:]  # Remove the dot
            audio.export(str(output_path), format=output_format)
            
            return True
            
        except ImportError:
            self.logger.error("pydub not installed. Cannot convert audio formats.")
            return False
        except Exception as e:
            self.logger.error(f"Audio conversion error: {e}")
            return False
    
    def synthesize_batch(self, text_chunks: List[str], output_dir: Path, 
                        filename_prefix: str = "chunk") -> List[Path]:
        """
        Synthesize multiple text chunks to separate audio files.
        
        Args:
            text_chunks: List of text strings to synthesize
            output_dir: Directory to save audio files
            filename_prefix: Prefix for generated filenames
            
        Returns:
            List of paths to generated audio files
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        generated_files = []
        
        for i, text in enumerate(text_chunks):
            if not text.strip():
                continue
                
            filename = f"{filename_prefix}_{i:03d}.{AUDIO_FORMAT}"
            output_path = output_dir / filename
            
            if self.synthesize_speech(text, output_path):
                generated_files.append(output_path)
                self.logger.info(f"Generated audio: {filename}")
            else:
                self.logger.error(f"Failed to generate audio for chunk {i}")
        
        return generated_files
    
    def get_voice_list(self) -> List[Dict[str, Any]]:
        """
        Get list of available voices for the current engine.
        
        Returns:
            List of voice information dictionaries
        """
        voices = []
        
        if self.engine_type == "pyttsx3" and self.engine:
            try:
                pyttsx3_voices = self.engine.getProperty('voices')
                for voice in pyttsx3_voices:
                    voices.append({
                        'id': voice.id,
                        'name': voice.name,
                        'languages': getattr(voice, 'languages', []),
                        'gender': getattr(voice, 'gender', 'unknown')
                    })
            except Exception as e:
                self.logger.error(f"Error getting pyttsx3 voices: {e}")
        
        elif self.engine_type == "gtts":
            # gTTS supports many languages but limited voice variety
            voices.append({
                'id': 'gtts_en',
                'name': 'Google TTS English',
                'languages': ['en'],
                'gender': 'neutral'
            })
        
        elif self.engine_type == "coqui":
            # Coqui models vary, this is a placeholder
            voices.append({
                'id': 'coqui_ljspeech',
                'name': 'Coqui LJSpeech',
                'languages': ['en'],
                'gender': 'female'
            })
        
        return voices
    
    def set_voice(self, voice_id: str) -> bool:
        """
        Set the voice to use for TTS.
        
        Args:
            voice_id: Voice identifier
            
        Returns:
            True if voice was set successfully
        """
        try:
            if self.engine_type == "pyttsx3" and self.engine:
                voices = self.engine.getProperty('voices')
                for voice in voices:
                    if voice.id == voice_id:
                        self.engine.setProperty('voice', voice_id)
                        self.logger.info(f"Voice set to: {voice.name}")
                        return True
                self.logger.warning(f"Voice not found: {voice_id}")
                return False
            
            # For other engines, voice setting might be limited
            self.logger.info(f"Voice setting not supported for {self.engine_type}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error setting voice: {e}")
            return False
    
    def adjust_speech_rate(self, rate: int):
        """
        Adjust speech rate (words per minute).
        
        Args:
            rate: Speech rate in words per minute
        """
        self.voice_settings['rate'] = rate
        
        if self.engine_type == "pyttsx3" and self.engine:
            self.engine.setProperty('rate', rate)
            self.logger.info(f"Speech rate set to {rate} WPM")
    
    def adjust_volume(self, volume: float):
        """
        Adjust speech volume.
        
        Args:
            volume: Volume level (0.0 to 1.0)
        """
        volume = max(0.0, min(1.0, volume))  # Clamp to valid range
        self.voice_settings['volume'] = volume
        
        if self.engine_type == "pyttsx3" and self.engine:
            self.engine.setProperty('volume', volume)
            self.logger.info(f"Volume set to {volume}")
    
    def get_engine_info(self) -> Dict[str, Any]:
        """
        Get information about the current TTS engine.
        
        Returns:
            Dictionary with engine information
        """
        return {
            'engine_type': self.engine_type,
            'voice_settings': self.voice_settings.copy(),
            'available_voices': len(self.get_voice_list()),
                         'gpu_support': self.engine_type == "coqui" and USE_GPU,
             'online_required': self.engine_type == "gtts"
         }


# Main API function requested by user
@timing_decorator  
def synthesize_speech(text: str, output_path: str) -> None:
    """
    Convert text to speech and save to file using configured TTS engine.
    
    This is the main API function for text-to-speech synthesis. It uses
    the TTS engine specified in config/settings.py and handles all the
    engine-specific logic internally.
    
    Args:
        text: Text string to convert to speech
        output_path: Path where the audio file should be saved
        
    Raises:
        ValueError: If text is empty or output path is invalid
        RuntimeError: If TTS synthesis fails
        ImportError: If required TTS engine is not installed
        
    Example:
        >>> synthesize_speech("Hello world", "output.mp3")
        >>> # Creates output.mp3 with spoken text
    """
    log_event(f"Starting TTS synthesis: {len(text)} chars -> {output_path}")
    log_event(f"Using TTS engine: {TTS_ENGINE}")
    
    # Validate inputs
    if not text or not text.strip():
        error_msg = "Empty text provided for TTS synthesis"
        log_event(error_msg)
        raise ValueError(error_msg)
    
    if not output_path:
        error_msg = "Empty output path provided"
        log_event(error_msg)
        raise ValueError(error_msg)
    
    try:
        # Initialize TTS engine based on config
        tts_engine = TTSEngine()
        output_path_obj = Path(output_path)
        
        # Perform synthesis
        success = tts_engine.synthesize_speech(text, output_path_obj)
        
        if success:
            log_event(f"TTS synthesis completed successfully: {output_path}")
        else:
            error_msg = f"TTS synthesis failed for: {output_path}"
            log_event(error_msg)
            raise RuntimeError(error_msg)
            
    except ImportError as e:
        error_msg = f"TTS engine {TTS_ENGINE} not available: {e}"
        log_event(error_msg)
        raise ImportError(error_msg)
        
    except Exception as e:
        error_msg = f"Error during TTS synthesis: {e}"
        log_event(error_msg)
        raise RuntimeError(error_msg) 