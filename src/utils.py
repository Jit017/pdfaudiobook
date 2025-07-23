"""
Shared utility functions for the PDF to Audiobook converter.

Contains logging setup, timing decorators, string cleaning, and other
common helper functions used across the project.
"""

import logging
import time
import re
import functools
from pathlib import Path
from typing import Any, Callable, Optional

from config.settings import LOG_LEVEL, LOG_FORMAT


def setup_logging(name: str, level: Optional[str] = None) -> logging.Logger:
    """
    Set up logging for the application.
    
    Args:
        name: Logger name (usually __name__)
        level: Logging level override (defaults to config setting)
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level or LOG_LEVEL))
    
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(LOG_FORMAT)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger


def timing_decorator(func: Callable) -> Callable:
    """
    Decorator to measure and log function execution time.
    
    Args:
        func: Function to time
        
    Returns:
        Wrapped function with timing
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        logger = setup_logging(func.__module__)
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(f"{func.__name__} completed in {execution_time:.2f} seconds")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"{func.__name__} failed after {execution_time:.2f} seconds: {e}")
            raise
    
    return wrapper


def clean_text(text: str) -> str:
    """
    Clean and normalize text for processing.
    
    Args:
        text: Raw text to clean
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters that interfere with TTS
    text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\'\"]', '', text)
    
    # Fix common PDF extraction issues
    text = text.replace('fi', 'fi').replace('fl', 'fl')  # Fix ligatures
    text = re.sub(r'(\w)-\s+(\w)', r'\1\2', text)  # Fix hyphenated words
    
    return text.strip()


def split_into_sentences(text: str) -> list[str]:
    """
    Split text into sentences for better TTS processing.
    
    Args:
        text: Text to split
        
    Returns:
        List of sentences
    """
    # Simple sentence splitting (can be enhanced with NLTK)
    sentences = re.split(r'[.!?]+', text)
    return [s.strip() for s in sentences if s.strip()]


def milliseconds_to_timecode(ms: int) -> str:
    """
    Convert milliseconds to human-readable timecode.
    
    Args:
        ms: Milliseconds
        
    Returns:
        Timecode in format "MM:SS.mmm"
    """
    seconds = ms // 1000
    milliseconds = ms % 1000
    minutes = seconds // 60
    seconds = seconds % 60
    
    return f"{minutes:02d}:{seconds:02d}.{milliseconds:03d}"


def ensure_file_extension(filepath: Path, extension: str) -> Path:
    """
    Ensure file has the correct extension.
    
    Args:
        filepath: Path to check
        extension: Required extension (with or without dot)
        
    Returns:
        Path with correct extension
    """
    if not extension.startswith('.'):
        extension = '.' + extension
    
    if filepath.suffix.lower() != extension.lower():
        return filepath.with_suffix(extension)
    
    return filepath


def safe_filename(filename: str) -> str:
    """
    Create a safe filename by removing problematic characters.
    
    Args:
        filename: Original filename
        
    Returns:
        Safe filename
    """
    # Remove problematic characters
    safe_name = re.sub(r'[<>:"/\\|?*]', '_', filename)
    safe_name = re.sub(r'\s+', '_', safe_name)
    
    # Limit length
    if len(safe_name) > 100:
        name, ext = safe_name.rsplit('.', 1) if '.' in safe_name else (safe_name, '')
        safe_name = name[:95] + ('.' + ext if ext else '')
    
    return safe_name


def chunk_text(text: str, max_length: int = 1000) -> list[str]:
    """
    Split text into chunks suitable for TTS processing.
    
    Args:
        text: Text to chunk
        max_length: Maximum characters per chunk
        
    Returns:
        List of text chunks
    """
    if len(text) <= max_length:
        return [text]
    
    chunks = []
    sentences = split_into_sentences(text)
    current_chunk = ""
    
    for sentence in sentences:
        if len(current_chunk) + len(sentence) <= max_length:
            current_chunk += sentence + ". "
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = sentence + ". "
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks


def validate_audio_file(filepath: Path) -> bool:
    """
    Validate that a file is a supported audio format.
    
    Args:
        filepath: Path to audio file
        
    Returns:
        True if valid audio file
    """
    if not filepath.exists():
        return False
    
    supported_extensions = {'.mp3', '.wav', '.ogg', '.m4a', '.flac'}
    return filepath.suffix.lower() in supported_extensions


class ProgressTracker:
    """Simple progress tracking utility."""
    
    def __init__(self, total: int, description: str = "Processing"):
        self.total = total
        self.current = 0
        self.description = description
        self.logger = setup_logging(__name__)
    
    def update(self, increment: int = 1):
        """Update progress by increment."""
        self.current += increment
        percentage = (self.current / self.total) * 100
        self.logger.info(f"{self.description}: {self.current}/{self.total} ({percentage:.1f}%)")
    
    def finish(self):
        """Mark progress as complete."""
        self.logger.info(f"{self.description}: Complete!")


# Additional helper functions requested by user
def load_audio(path: str):
    """
    Load an audio file using pydub.
    
    This helper function loads an audio file and returns an AudioSegment
    object. It handles different audio formats and provides error handling.
    
    Args:
        path: Path to the audio file
        
    Returns:
        AudioSegment object or None if loading fails
        
    Example:
        >>> audio = load_audio("music.mp3")
        >>> if audio:
        ...     print(f"Loaded audio: {len(audio)}ms")
    """
    try:
        from pydub import AudioSegment
        
        audio_path = Path(path)
        if not audio_path.exists():
            logger = setup_logging(__name__)
            logger.warning(f"Audio file not found: {path}")
            return None
        
        # Load based on file extension
        if audio_path.suffix.lower() == '.mp3':
            return AudioSegment.from_mp3(str(audio_path))
        elif audio_path.suffix.lower() == '.wav':
            return AudioSegment.from_wav(str(audio_path))
        else:
            return AudioSegment.from_file(str(audio_path))
            
    except ImportError:
        logger = setup_logging(__name__)
        logger.error("pydub not installed. Cannot load audio.")
        return None
    except Exception as e:
        logger = setup_logging(__name__)
        logger.error(f"Error loading audio file {path}: {e}")
        return None


def log_event(msg: str) -> None:
    """
    Log an event message.
    
    This helper function provides a simple way to log events throughout
    the application with consistent formatting.
    
    Args:
        msg: Message to log
        
    Example:
        >>> log_event("Starting PDF processing")
        >>> log_event("Completed TTS synthesis")
    """
    logger = setup_logging(__name__)
    logger.info(msg)


def sanitize_filename(name: str) -> str:
    """
    Sanitize a filename by removing problematic characters.
    
    This helper function takes a string and makes it safe to use as
    a filename by removing or replacing problematic characters.
    
    Args:
        name: Original filename or string
        
    Returns:
        Sanitized filename safe for filesystem use
        
    Example:
        >>> clean_name = sanitize_filename("My Book: Chapter 1!")
        >>> print(clean_name)  # "My_Book_Chapter_1"
    """
    if not name:
        return "untitled"
    
    # Remove problematic characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', name)
    sanitized = re.sub(r'[^\w\s\-_\.]', '', sanitized)
    sanitized = re.sub(r'\s+', '_', sanitized)
    
    # Remove leading/trailing underscores and dots
    sanitized = sanitized.strip('_.')
    
    # Limit length
    if len(sanitized) > 100:
        sanitized = sanitized[:100]
    
    # Ensure we have something
    if not sanitized:
        sanitized = "untitled"
    
    return sanitized 