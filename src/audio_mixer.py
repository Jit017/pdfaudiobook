"""
Audio Mixer module for combining narration, background music, and sound effects.

Creates immersive audiobooks by layering voice narration with emotion-based
background music and contextual sound effects.
"""

from pathlib import Path
from typing import List, Dict, Optional, Tuple
import random

from .utils import setup_logging, timing_decorator, validate_audio_file, milliseconds_to_timecode, log_event
from config.settings import (
    BGM_VOLUME, SFX_VOLUME, BG_MUSIC_DIR, SFX_DIR, 
    EMOTION_BGM_MAP, AUDIO_FORMAT, SAMPLE_RATE, CHANNELS
)

# Module-level logger  
logger = setup_logging(__name__)


class AudioMixer:
    """
    Handles mixing of narration audio with background music and sound effects.
    
    Creates layered audio experiences by combining:
    - Voice narration (primary audio)
    - Emotion-based background music (continuous, low volume)
    - Sound effects (triggered by keywords, higher volume)
    """
    
    def __init__(self):
        self.logger = setup_logging(__name__)
        self.bgm_volume = BGM_VOLUME
        self.sfx_volume = SFX_VOLUME
        self.sample_rate = SAMPLE_RATE
        self.channels = CHANNELS
        
        # Cache for loaded audio files
        self._audio_cache = {}
    
    @timing_decorator
    def create_audiobook(self, narration_files: List[Path], 
                        emotions: List[str],
                        sfx_timeline: List[Dict],
                        output_path: Path) -> bool:
        """
        Create complete audiobook by mixing all audio elements.
        
        Args:
            narration_files: List of paths to narration audio files
            emotions: List of emotions corresponding to each narration file
            sfx_timeline: Timeline of sound effects with timing data
            output_path: Path for final audiobook file
            
        Returns:
            True if successful, False otherwise
        """
        if not narration_files:
            self.logger.error("No narration files provided")
            return False
        
        try:
            from pydub import AudioSegment
            
            self.logger.info(f"Creating audiobook with {len(narration_files)} segments")
            
            # Start with silence
            final_audio = AudioSegment.silent(duration=0)
            current_time = 0
            
            for i, narration_file in enumerate(narration_files):
                if not narration_file.exists():
                    self.logger.warning(f"Narration file not found: {narration_file}")
                    continue
                
                # Load narration audio
                narration = self._load_audio(narration_file)
                if narration is None:
                    continue
                
                # Get emotion for this segment
                emotion = emotions[i] if i < len(emotions) else 'neutral'
                
                # Create mixed segment
                segment = self._create_mixed_segment(
                    narration=narration,
                    emotion=emotion,
                    segment_start_time=current_time,
                    sfx_events=self._get_sfx_for_timerange(
                        sfx_timeline, current_time, current_time + len(narration)
                    )
                )
                
                # Add to final audio
                final_audio += segment
                current_time += len(segment)
                
                # Add brief pause between segments
                final_audio += AudioSegment.silent(duration=500)  # 0.5 second pause
                current_time += 500
            
            # Export final audiobook
            self._export_audio(final_audio, output_path)
            
            duration_minutes = len(final_audio) / (1000 * 60)
            self.logger.info(f"Audiobook created: {output_path.name} ({duration_minutes:.1f} minutes)")
            
            return True
            
        except ImportError:
            self.logger.error("pydub not installed. Cannot create audiobook.")
            return False
        except Exception as e:
            self.logger.error(f"Error creating audiobook: {e}")
            return False
    
    def _create_mixed_segment(self, narration, emotion: str, 
                             segment_start_time: int, sfx_events: List[Dict]):
        """
        Create a mixed audio segment with narration, BGM, and SFX.
        
        Args:
            narration: AudioSegment with voice narration
            emotion: Emotion for this segment
            segment_start_time: Start time in milliseconds
            sfx_events: Sound effects for this segment
            
        Returns:
            Mixed AudioSegment
        """
        from pydub import AudioSegment
        
        # Start with the narration
        mixed_audio = narration
        
        # Add background music based on emotion
        bgm = self._get_background_music(emotion, len(narration))
        if bgm:
            # Lower the volume and overlay
            bgm = bgm - (60 - int(self.bgm_volume * 60))  # Convert to dB reduction
            mixed_audio = mixed_audio.overlay(bgm)
        
        # Add sound effects
        for sfx_event in sfx_events:
            sfx_audio = self._get_sound_effect(sfx_event['sfx_type'])
            if sfx_audio:
                # Calculate timing within this segment
                relative_time = sfx_event.get('time_offset', 0) * 1000  # Convert to ms
                relative_time = max(0, min(relative_time, len(mixed_audio) - len(sfx_audio)))
                
                # Adjust volume and overlay
                sfx_audio = sfx_audio - (60 - int(self.sfx_volume * 60))
                mixed_audio = mixed_audio.overlay(sfx_audio, position=int(relative_time))
        
        return mixed_audio
    
    def _get_background_music(self, emotion: str, duration_ms: int):
        """
        Get background music for the specified emotion and duration.
        
        Args:
            emotion: Emotion to get music for
            duration_ms: Required duration in milliseconds
            
        Returns:
            AudioSegment or None
        """
        bgm_filename = EMOTION_BGM_MAP.get(emotion, EMOTION_BGM_MAP.get('neutral'))
        if not bgm_filename:
            return None
        
        bgm_path = BG_MUSIC_DIR / bgm_filename
        
        # Try to load the BGM file
        bgm_audio = self._load_audio(bgm_path)
        if bgm_audio is None:
            # Try to find any audio file in the bg_music directory
            bgm_audio = self._find_fallback_bgm()
        
        if bgm_audio is None:
            return None
        
        # Adjust duration to match narration
        if len(bgm_audio) < duration_ms:
            # Loop the BGM if it's shorter than needed
            loops_needed = (duration_ms // len(bgm_audio)) + 1
            bgm_audio = bgm_audio * loops_needed
        
        # Trim to exact duration
        return bgm_audio[:duration_ms]
    
    def _get_sound_effect(self, sfx_type: str):
        """
        Get sound effect audio for the specified type.
        
        Args:
            sfx_type: Type of sound effect (e.g., 'door', 'footsteps')
            
        Returns:
            AudioSegment or None
        """
        # Look for sound effect files
        possible_names = [
            f"{sfx_type}.mp3",
            f"{sfx_type}.wav",
            f"{sfx_type}_001.mp3",
            f"{sfx_type}_1.mp3"
        ]
        
        for name in possible_names:
            sfx_path = SFX_DIR / name
            if sfx_path.exists():
                return self._load_audio(sfx_path)
        
        # If no specific file found, try to find any file with the sfx_type in name
        if SFX_DIR.exists():
            for file_path in SFX_DIR.glob(f"*{sfx_type}*"):
                if validate_audio_file(file_path):
                    return self._load_audio(file_path)
        
        self.logger.debug(f"No sound effect found for: {sfx_type}")
        return None
    
    def _find_fallback_bgm(self):
        """Find any available background music file as fallback."""
        if not BG_MUSIC_DIR.exists():
            return None
        
        for file_path in BG_MUSIC_DIR.glob("*"):
            if validate_audio_file(file_path):
                return self._load_audio(file_path)
        
        return None
    
    def _load_audio(self, file_path: Path):
        """
        Load audio file with caching.
        
        Args:
            file_path: Path to audio file
            
        Returns:
            AudioSegment or None
        """
        if not file_path.exists():
            return None
        
        # Check cache first
        cache_key = str(file_path)
        if cache_key in self._audio_cache:
            return self._audio_cache[cache_key]
        
        try:
            from pydub import AudioSegment
            
            if file_path.suffix.lower() == '.mp3':
                audio = AudioSegment.from_mp3(str(file_path))
            elif file_path.suffix.lower() == '.wav':
                audio = AudioSegment.from_wav(str(file_path))
            else:
                audio = AudioSegment.from_file(str(file_path))
            
            # Normalize audio properties
            audio = audio.set_frame_rate(self.sample_rate)
            audio = audio.set_channels(self.channels)
            
            # Cache for future use
            self._audio_cache[cache_key] = audio
            
            return audio
            
        except Exception as e:
            self.logger.error(f"Error loading audio file {file_path}: {e}")
            return None
    
    def _export_audio(self, audio, output_path: Path):
        """Export audio to file."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        export_format = output_path.suffix.lower()[1:]  # Remove dot
        audio.export(str(output_path), format=export_format)
    
    def _get_sfx_for_timerange(self, sfx_timeline: List[Dict], 
                              start_time: int, end_time: int) -> List[Dict]:
        """
        Get sound effects that occur within a time range.
        
        Args:
            sfx_timeline: Complete SFX timeline
            start_time: Start time in milliseconds
            end_time: End time in milliseconds
            
        Returns:
            List of SFX events in the time range
        """
        events_in_range = []
        
        for event in sfx_timeline:
            # Calculate absolute time of the event
            event_time = start_time + (event.get('time_offset', 0) * 1000)
            
            if start_time <= event_time <= end_time:
                # Adjust time offset to be relative to segment start
                adjusted_event = event.copy()
                adjusted_event['time_offset'] = (event_time - start_time) / 1000
                events_in_range.append(adjusted_event)
        
        return events_in_range
    
    def create_chapter_audiobook(self, chapters: List[Dict], output_path: Path) -> bool:
        """
        Create audiobook with chapter structure.
        
        Args:
            chapters: List of chapter dictionaries with audio and metadata
            output_path: Path for final audiobook
            
        Returns:
            True if successful
        """
        try:
            from pydub import AudioSegment
            
            final_audio = AudioSegment.silent(duration=0)
            
            for i, chapter in enumerate(chapters):
                self.logger.info(f"Processing chapter {i + 1}: {chapter.get('title', 'Untitled')}")
                
                # Add chapter announcement if title provided
                if chapter.get('title'):
                    chapter_pause = AudioSegment.silent(duration=2000)  # 2 second pause
                    final_audio += chapter_pause
                
                # Process chapter content
                chapter_audio = self.create_audiobook(
                    narration_files=chapter['narration_files'],
                    emotions=chapter['emotions'],
                    sfx_timeline=chapter.get('sfx_timeline', []),
                    output_path=Path(f"temp_chapter_{i}.mp3")
                )
                
                if chapter_audio and Path(f"temp_chapter_{i}.mp3").exists():
                    chapter_segment = self._load_audio(Path(f"temp_chapter_{i}.mp3"))
                    if chapter_segment:
                        final_audio += chapter_segment
                    
                    # Clean up temp file
                    Path(f"temp_chapter_{i}.mp3").unlink(missing_ok=True)
                
                # Add pause between chapters
                if i < len(chapters) - 1:
                    final_audio += AudioSegment.silent(duration=3000)  # 3 second pause
            
            self._export_audio(final_audio, output_path)
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating chapter audiobook: {e}")
            return False
    
    def adjust_volumes(self, bgm_volume: float, sfx_volume: float):
        """
        Adjust volume levels for BGM and SFX.
        
        Args:
            bgm_volume: Background music volume (0.0 to 1.0)
            sfx_volume: Sound effects volume (0.0 to 1.0)
        """
        self.bgm_volume = max(0.0, min(1.0, bgm_volume))
        self.sfx_volume = max(0.0, min(1.0, sfx_volume))
        
        self.logger.info(f"Volume adjusted - BGM: {self.bgm_volume}, SFX: {self.sfx_volume}")
    
    def get_audio_info(self, file_path: Path) -> Dict:
        """
        Get information about an audio file.
        
        Args:
            file_path: Path to audio file
            
        Returns:
            Dictionary with audio information
        """
        audio = self._load_audio(file_path)
        if audio is None:
            return {}
        
        return {
            'duration_ms': len(audio),
            'duration_readable': milliseconds_to_timecode(len(audio)),
            'sample_rate': audio.frame_rate,
            'channels': audio.channels,
            'file_size_mb': file_path.stat().st_size / (1024 * 1024) if file_path.exists() else 0
        }
    
    def preview_mix(self, narration_file: Path, emotion: str, 
                   sfx_events: List[Dict], duration_seconds: int = 30) -> Optional[Path]:
        """
        Create a preview of the mixed audio.
        
        Args:
            narration_file: Path to narration file
            emotion: Emotion for background music
            sfx_events: Sound effects to include
            duration_seconds: Length of preview in seconds
            
        Returns:
            Path to preview file or None
        """
        try:
            narration = self._load_audio(narration_file)
            if narration is None:
                return None
            
            # Limit to preview duration
            preview_duration = duration_seconds * 1000
            narration = narration[:preview_duration]
            
            # Create mixed segment
            preview = self._create_mixed_segment(
                narration=narration,
                emotion=emotion,
                segment_start_time=0,
                sfx_events=sfx_events
            )
            
            # Save preview
            preview_path = Path("temp_preview.mp3")
            self._export_audio(preview, preview_path)
            
            return preview_path
            
        except Exception as e:
            self.logger.error(f"Error creating preview: {e}")
            return None
    
    def clear_cache(self):
        """Clear the audio file cache."""
        self._audio_cache.clear()
        self.logger.info("Audio cache cleared")


# Main API function requested by user
@timing_decorator
def mix_audio(segments: List[Dict], output_path: str) -> None:
    """
    Mix audio segments with background music and sound effects.
    
    This is the main API function for audio mixing. It takes a list of
    segments with narration, emotions, and SFX, then creates a final
    mixed audiobook with background music and sound effects.
    
    Args:
        segments: List of dictionaries with structure:
                 [
                     {
                         "text": "text content...",
                         "emotion": "joy",  # or "sadness", "anger", etc.
                         "sfx": ["door", "footsteps"],  # list of SFX types
                         "audio_file": "path/to/narration.mp3"  # generated TTS file
                     },
                     ...
                 ]
        output_path: Path where final mixed audiobook should be saved
        
    Raises:
        ValueError: If segments list is empty or invalid
        ImportError: If pydub is not available
        RuntimeError: If audio mixing fails
        
    Example:
        >>> segments = [
        ...     {
        ...         "text": "The door creaked loudly.",
        ...         "emotion": "fear", 
        ...         "sfx": ["door"],
        ...         "audio_file": "narration_01.mp3"
        ...     }
        ... ]
        >>> mix_audio(segments, "final_audiobook.mp3")
    """
    log_event(f"Starting audio mixing: {len(segments)} segments -> {output_path}")
    
    # Validate inputs
    if not segments:
        error_msg = "Empty segments list provided for audio mixing"
        log_event(error_msg)
        raise ValueError(error_msg)
    
    if not output_path:
        error_msg = "Empty output path provided"
        log_event(error_msg)
        raise ValueError(error_msg)
    
    try:
        # Check for pydub availability
        try:
            from pydub import AudioSegment
        except ImportError:
            error_msg = "pydub not installed. Cannot mix audio."
            log_event(error_msg)
            raise ImportError(error_msg)
        
        # Initialize mixer
        mixer = AudioMixer()
        
        # Extract narration files and emotions from segments
        narration_files = []
        emotions = []
        sfx_timeline = []
        
        current_time = 0
        for i, segment in enumerate(segments):
            # Validate segment structure
            if "audio_file" not in segment:
                log_event(f"Warning: Segment {i} missing audio_file, skipping")
                continue
                
            audio_file = Path(segment["audio_file"])
            if not audio_file.exists():
                log_event(f"Warning: Audio file not found: {audio_file}, skipping")
                continue
            
            narration_files.append(audio_file)
            emotions.append(segment.get("emotion", "neutral"))
            
            # Add SFX events for this segment
            sfx_list = segment.get("sfx", [])
            for sfx_type in sfx_list:
                sfx_event = {
                    "sfx_type": sfx_type,
                    "chunk_id": i,
                    "time_offset": 0,  # Beginning of segment for simplicity
                    "trigger_word": sfx_type,
                    "context": segment.get("text", "")[:50] + "...",
                    "confidence": 1.0
                }
                sfx_timeline.append(sfx_event)
        
        if not narration_files:
            error_msg = "No valid narration files found in segments"
            log_event(error_msg)
            raise ValueError(error_msg)
        
        # Create the mixed audiobook
        output_path_obj = Path(output_path)
        success = mixer.create_audiobook(
            narration_files=narration_files,
            emotions=emotions,
            sfx_timeline=sfx_timeline,
            output_path=output_path_obj
        )
        
        if success:
            log_event(f"Audio mixing completed successfully: {output_path}")
        else:
            error_msg = f"Audio mixing failed for: {output_path}"
            log_event(error_msg)
            raise RuntimeError(error_msg)
            
    except Exception as e:
        error_msg = f"Error during audio mixing: {e}"
        log_event(error_msg)
        raise RuntimeError(error_msg) 