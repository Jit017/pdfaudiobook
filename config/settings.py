"""
Configuration settings for PDF to Audiobook converter.

This file controls all major features and can be modified to switch between
local development (no GPU) and production (with GPU) environments.
"""

import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
ASSETS_DIR = BASE_DIR / "assets"

# Input/Output directories
INPUT_DIR = DATA_DIR / "input"
OUTPUT_DIR = DATA_DIR / "output"
BG_MUSIC_DIR = ASSETS_DIR / "bg_music"
SFX_DIR = ASSETS_DIR / "sfx"

# Hardware and model configuration
USE_GPU = False  # Set to True when running on GPU-enabled machine
USE_REAL_EMOTION = False  # Set to True to use actual emotion detection models
DEVICE = "cuda" if USE_GPU else "cpu"

# TTS Engine Configuration
# Options: "pyttsx3" (local), "gtts" (Google), "coqui" (GPU required)
TTS_ENGINE = "pyttsx3"

# Emotion Detection Configuration
EMOTION_MODEL = "j-hartmann/emotion-english-distilroberta-base"  # HuggingFace model
EMOTION_FALLBACK = "neutral"  # Default emotion when USE_REAL_EMOTION=False

# Audio Configuration
AUDIO_FORMAT = "mp3"
SAMPLE_RATE = 22050
CHANNELS = 2  # Stereo

# TTS Voice Settings
VOICE_SPEED = 150  # Words per minute for pyttsx3
VOICE_VOLUME = 0.8

# Background Music Settings
BGM_VOLUME = 0.3  # Background music volume (0.0 to 1.0)
SFX_VOLUME = 0.6  # Sound effects volume (0.0 to 1.0)

# Text Processing Settings
MAX_CHUNK_SIZE = 1000  # Maximum characters per TTS chunk
SENTENCE_PAUSE = 0.5  # Seconds of pause between sentences
PARAGRAPH_PAUSE = 1.0  # Seconds of pause between paragraphs

# File Paths Configuration
AUDIO_ASSETS = {
    'bg_music': {
        'joy': BG_MUSIC_DIR / "joy.mp3",
        'sadness': BG_MUSIC_DIR / "sadness.mp3",
        'anger': BG_MUSIC_DIR / "sadness.mp3",  # Fallback
        'fear': BG_MUSIC_DIR / "sadness.mp3",   # Fallback
        'surprise': BG_MUSIC_DIR / "joy.mp3",   # Fallback
        'neutral': BG_MUSIC_DIR / "sadness.mp3" # Fallback
    },
    'sfx': {
        'door': SFX_DIR / "door.mp3",
        'scream': SFX_DIR / "scream.mp3",
        'footsteps': SFX_DIR / "footsteps.mp3",  # For future expansion
        'thunder': SFX_DIR / "thunder.mp3",      # For future expansion
        'water': SFX_DIR / "water.mp3",          # For future expansion
        'fire': SFX_DIR / "fire.mp3"             # For future expansion
    }
}

# Output File Paths
OUTPUT_FILES = {
    'demo_basic': OUTPUT_DIR / "demo_result.mp3",
    'streamlit': OUTPUT_DIR / "streamlit_result.mp3",
    'audiobook_maker': OUTPUT_DIR / "audiobook_result.mp3",
    'temp_narration_dir': OUTPUT_DIR / "temp_narration"
}

# Emotion to Background Music Mapping (using file references)
EMOTION_BGM_MAP = {
    "joy": "joy.mp3",
    "sadness": "sadness.mp3", 
    "anger": "sadness.mp3",  # Fallback to sadness.mp3
    "fear": "sadness.mp3",   # Fallback to sadness.mp3
    "surprise": "joy.mp3",   # Fallback to joy.mp3
    "neutral": "sadness.mp3" # Fallback to sadness.mp3
}

# Sound Effect Keywords
SFX_KEYWORDS = {
    "door": ["door", "doorway", "opened", "closed", "creak"],
    "footsteps": ["walked", "running", "footsteps", "steps"],
    "thunder": ["thunder", "lightning", "storm"],
    "water": ["rain", "water", "splash", "drip"],
    "fire": ["fire", "flames", "crackling", "burning"],
    "scream": ["scream", "screamed", "screaming", "yell", "shout"]
}

# Sample Content Configuration
SAMPLE_STORY = """
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
""".strip()

# TTS Configuration
TTS_CONFIG = {
    'pyttsx3': {
        'rate': 160,
        'volume': 1.0,
        'voice_selection': {
            'preferred_keywords': ['english', 'en_', 'en-'],
            'fallback_index': 0
        }
    },
    'gtts': {
        'lang': 'en',
        'slow': False
    },
    'coqui': {
        'model_name': 'tts_models/en/ljspeech/tacotron2-DDC',
        'gpu': USE_GPU
    }
}

# Audio Processing Configuration
AUDIO_PROCESSING = {
    'minimum_file_size': 1000,  # Minimum bytes for valid audio file
    'minimum_duration': 100,    # Minimum milliseconds for valid audio
    'generation_timeout': 10.0, # Seconds to wait for TTS generation
    'mixing_pause_between_segments': 500,  # Milliseconds pause between segments
    'bgm_volume_reduction': 20   # dB reduction for background music
}

# Logging Configuration
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Helper functions
def get_bgm_path(emotion: str) -> str:
    """Get background music file path for given emotion."""
    bgm_file = EMOTION_BGM_MAP.get(emotion, "sadness.mp3")
    return str(AUDIO_ASSETS['bg_music'][emotion.replace('.mp3', '')])

def get_sfx_path(sfx_type: str) -> str:
    """Get sound effect file path for given SFX type."""
    if sfx_type in AUDIO_ASSETS['sfx']:
        return str(AUDIO_ASSETS['sfx'][sfx_type])
    return None

def get_output_path(output_type: str = 'demo_basic') -> str:
    """Get output file path for given type."""
    return str(OUTPUT_FILES.get(output_type, OUTPUT_FILES['demo_basic']))

def create_directories():
    """Create necessary directories if they don't exist."""
    directories = [INPUT_DIR, OUTPUT_DIR, BG_MUSIC_DIR, SFX_DIR, OUTPUT_FILES['temp_narration_dir']]
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)

def get_config_summary():
    """Return a summary of current configuration."""
    return {
        "use_gpu": USE_GPU,
        "use_real_emotion": USE_REAL_EMOTION,
        "tts_engine": TTS_ENGINE,
        "device": DEVICE,
        "audio_format": AUDIO_FORMAT
    } 