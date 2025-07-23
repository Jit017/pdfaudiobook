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

# Emotion to Background Music Mapping
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

# Logging Configuration
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

def create_directories():
    """Create necessary directories if they don't exist."""
    directories = [INPUT_DIR, OUTPUT_DIR, BG_MUSIC_DIR, SFX_DIR]
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