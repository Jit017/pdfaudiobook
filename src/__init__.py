"""
PDF to Audiobook Converter Package

A modular system for converting PDF documents to immersive audiobooks
with emotion-based background music and sound effects.
"""

__version__ = "1.0.0"
__author__ = "Your Name"

from .pdf_reader import PDFReader
from .text_processor import TextProcessor
from .emotion_detector import EmotionDetector
from .tts_engine import TTSEngine
from .audio_mixer import AudioMixer
from .utils import setup_logging, timing_decorator

__all__ = [
    "PDFReader",
    "TextProcessor", 
    "EmotionDetector",
    "TTSEngine",
    "AudioMixer",
    "setup_logging",
    "timing_decorator"
] 