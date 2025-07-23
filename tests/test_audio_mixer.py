"""
Tests for the Audio Mixer module.
"""

import pytest
from pathlib import Path
import tempfile
import sys

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))
from src.audio_mixer import AudioMixer


class TestAudioMixer:
    """Test cases for AudioMixer class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mixer = AudioMixer()
    
    def test_audio_mixer_initialization(self):
        """Test AudioMixer initializes correctly."""
        assert self.mixer is not None
        assert hasattr(self.mixer, 'logger')
        assert hasattr(self.mixer, 'bgm_volume')
        assert hasattr(self.mixer, 'sfx_volume')
        assert hasattr(self.mixer, '_audio_cache')
    
    def test_initial_volume_settings(self):
        """Test initial volume settings are within valid range."""
        assert 0.0 <= self.mixer.bgm_volume <= 1.0
        assert 0.0 <= self.mixer.sfx_volume <= 1.0
    
    def test_adjust_volumes(self):
        """Test volume adjustment functionality."""
        # Test valid volumes
        self.mixer.adjust_volumes(0.5, 0.7)
        assert self.mixer.bgm_volume == 0.5
        assert self.mixer.sfx_volume == 0.7
        
        # Test volume clamping
        self.mixer.adjust_volumes(-0.1, 1.5)
        assert self.mixer.bgm_volume == 0.0  # Clamped to minimum
        assert self.mixer.sfx_volume == 1.0  # Clamped to maximum
    
    def test_load_audio_nonexistent_file(self):
        """Test loading non-existent audio file."""
        fake_path = Path("nonexistent.mp3")
        result = self.mixer._load_audio(fake_path)
        assert result is None
    
    def test_get_audio_info_nonexistent_file(self):
        """Test getting info for non-existent audio file."""
        fake_path = Path("nonexistent.mp3")
        info = self.mixer.get_audio_info(fake_path)
        assert info == {}
    
    def test_get_sfx_for_timerange(self):
        """Test SFX filtering by time range."""
        sfx_timeline = [
            {'sfx_type': 'door', 'time_offset': 5.0},
            {'sfx_type': 'footsteps', 'time_offset': 15.0},
            {'sfx_type': 'thunder', 'time_offset': 25.0}
        ]
        
        # Test time range that includes middle event
        events = self.mixer._get_sfx_for_timerange(sfx_timeline, 10000, 20000)
        assert len(events) == 1
        assert events[0]['sfx_type'] == 'footsteps'
        
        # Test time range that includes no events
        events = self.mixer._get_sfx_for_timerange(sfx_timeline, 30000, 40000)
        assert len(events) == 0
    
    def test_get_sound_effect_nonexistent(self):
        """Test getting non-existent sound effect."""
        result = self.mixer._get_sound_effect("nonexistent_sfx")
        assert result is None
    
    def test_find_fallback_bgm_empty_directory(self):
        """Test fallback BGM when directory is empty or doesn't exist."""
        result = self.mixer._find_fallback_bgm()
        # Should return None if no BGM directory or files exist
        # This is expected in test environment
        assert result is None
    
    def test_clear_cache(self):
        """Test audio cache clearing functionality."""
        # Add something to cache
        self.mixer._audio_cache['test'] = "dummy_audio"
        assert len(self.mixer._audio_cache) > 0
        
        # Clear cache
        self.mixer.clear_cache()
        assert len(self.mixer._audio_cache) == 0
    
    def test_create_audiobook_empty_narration_files(self):
        """Test audiobook creation with empty narration files list."""
        with tempfile.NamedTemporaryFile(suffix=".mp3") as tmp:
            output_path = Path(tmp.name)
            
            result = self.mixer.create_audiobook(
                narration_files=[],
                emotions=[],
                sfx_timeline=[],
                output_path=output_path
            )
            
            assert result is False
    
    def test_get_background_music_unknown_emotion(self):
        """Test background music selection for unknown emotion."""
        # Should fall back to neutral or return None if no files exist
        bgm = self.mixer._get_background_music("unknown_emotion", 5000)
        # In test environment without actual audio files, this should be None
        assert bgm is None
    
    def test_create_chapter_audiobook_empty_chapters(self):
        """Test chapter audiobook creation with empty chapters."""
        with tempfile.NamedTemporaryFile(suffix=".mp3") as tmp:
            output_path = Path(tmp.name)
            
            result = self.mixer.create_chapter_audiobook([], output_path)
            # Should handle empty chapters gracefully
            assert isinstance(result, bool)
    
    def test_preview_mix_nonexistent_narration(self):
        """Test preview creation with non-existent narration file."""
        fake_path = Path("nonexistent.mp3")
        
        result = self.mixer.preview_mix(
            narration_file=fake_path,
            emotion="neutral",
            sfx_events=[],
            duration_seconds=10
        )
        
        assert result is None
    
    @pytest.mark.integration
    def test_audio_mixer_with_real_files(self):
        """Integration test with real audio files (if available)."""
        # This test would run only if sample audio files are available
        sample_audio = Path("tests/sample_audio.mp3")
        
        if sample_audio.exists():
            # Test audio loading
            audio = self.mixer._load_audio(sample_audio)
            assert audio is not None
            
            # Test audio info
            info = self.mixer.get_audio_info(sample_audio)
            assert 'duration_ms' in info
            assert 'sample_rate' in info
            assert 'channels' in info
        else:
            pytest.skip("No sample audio files available for integration testing")
    
    def test_audio_mixer_error_handling(self):
        """Test error handling in audio mixer operations."""
        # The mixer should handle missing dependencies gracefully
        # and log appropriate error messages
        
        # This test mainly ensures no exceptions are raised
        # during initialization when optional dependencies might be missing
        assert self.mixer is not None
        
    def test_volume_range_validation(self):
        """Test that volume values stay within valid ranges."""
        # Test extreme values
        self.mixer.adjust_volumes(-999, 999)
        assert 0.0 <= self.mixer.bgm_volume <= 1.0
        assert 0.0 <= self.mixer.sfx_volume <= 1.0
        
        # Test edge cases
        self.mixer.adjust_volumes(0.0, 1.0)
        assert self.mixer.bgm_volume == 0.0
        assert self.mixer.sfx_volume == 1.0


if __name__ == "__main__":
    pytest.main([__file__]) 