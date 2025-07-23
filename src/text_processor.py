"""
Text Processor module for preparing text for TTS and audio enhancement.

Handles text chunking, keyword detection for sound effects, and text preprocessing
to create an immersive audiobook experience.
"""

import re
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

from .utils import setup_logging, timing_decorator, chunk_text, split_into_sentences, log_event
from config.settings import SFX_KEYWORDS, MAX_CHUNK_SIZE

# Module-level logger
logger = setup_logging(__name__)


@dataclass
class TextChunk:
    """
    Represents a chunk of text with associated metadata.
    """
    text: str
    start_position: int
    end_position: int
    chunk_id: int
    sfx_triggers: List[str]
    estimated_duration: float = 0.0  # Estimated speaking time in seconds
    
    def __post_init__(self):
        # Estimate speaking duration (roughly 200 words per minute)
        word_count = len(self.text.split())
        self.estimated_duration = (word_count / 200) * 60


@dataclass
class SFXEvent:
    """
    Represents a sound effect event with timing information.
    """
    sfx_type: str
    trigger_word: str
    position: int
    context: str
    confidence: float = 1.0


class TextProcessor:
    """
    Processes text for audiobook conversion.
    
    Handles text chunking, sound effect detection, and preparation
    for TTS conversion with timing metadata.
    """
    
    def __init__(self):
        self.logger = setup_logging(__name__)
        self.sfx_keywords = SFX_KEYWORDS
        self.processed_chunks: List[TextChunk] = []
        self.sfx_events: List[SFXEvent] = []
    
    @timing_decorator
    def process_text(self, text: str, chunk_size: Optional[int] = None) -> List[TextChunk]:
        """
        Process text into chunks with SFX detection.
        
        Args:
            text: Input text to process
            chunk_size: Maximum characters per chunk (defaults to config setting)
            
        Returns:
            List of TextChunk objects with metadata
        """
        if not text.strip():
            self.logger.warning("Empty text provided for processing")
            return []
        
        chunk_size = chunk_size or MAX_CHUNK_SIZE
        
        # Split text into manageable chunks
        raw_chunks = chunk_text(text, chunk_size)
        
        self.processed_chunks = []
        self.sfx_events = []
        current_position = 0
        
        for i, chunk_text in enumerate(raw_chunks):
            # Create chunk with metadata
            chunk = TextChunk(
                text=chunk_text,
                start_position=current_position,
                end_position=current_position + len(chunk_text),
                chunk_id=i,
                sfx_triggers=[]
            )
            
            # Detect SFX keywords in this chunk
            sfx_events = self._detect_sfx_keywords(chunk_text, current_position)
            chunk.sfx_triggers = [event.sfx_type for event in sfx_events]
            
            self.processed_chunks.append(chunk)
            self.sfx_events.extend(sfx_events)
            
            current_position += len(chunk_text) + 2  # +2 for spacing between chunks
        
        self.logger.info(f"Processed text into {len(self.processed_chunks)} chunks")
        self.logger.info(f"Detected {len(self.sfx_events)} sound effect triggers")
        
        return self.processed_chunks
    
    def _detect_sfx_keywords(self, text: str, start_position: int) -> List[SFXEvent]:
        """
        Detect sound effect keywords in text.
        
        Args:
            text: Text to analyze
            start_position: Starting position in the full text
            
        Returns:
            List of SFXEvent objects
        """
        events = []
        text_lower = text.lower()
        
        for sfx_type, keywords in self.sfx_keywords.items():
            for keyword in keywords:
                # Find all occurrences of this keyword
                pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
                matches = re.finditer(pattern, text_lower)
                
                for match in matches:
                    # Get context around the keyword
                    context_start = max(0, match.start() - 20)
                    context_end = min(len(text), match.end() + 20)
                    context = text[context_start:context_end].strip()
                    
                    # Calculate confidence based on context
                    confidence = self._calculate_sfx_confidence(keyword, context)
                    
                    if confidence > 0.3:  # Only include reasonably confident matches
                        event = SFXEvent(
                            sfx_type=sfx_type,
                            trigger_word=keyword,
                            position=start_position + match.start(),
                            context=context,
                            confidence=confidence
                        )
                        events.append(event)
        
        return events
    
    def _calculate_sfx_confidence(self, keyword: str, context: str) -> float:
        """
        Calculate confidence score for SFX detection.
        
        Args:
            keyword: The detected keyword
            context: Surrounding text context
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        confidence = 0.5  # Base confidence
        context_lower = context.lower()
        
        # Boost confidence for action words
        action_words = ['suddenly', 'loudly', 'slowly', 'quickly', 'heard', 'sound']
        for word in action_words:
            if word in context_lower:
                confidence += 0.1
        
        # Boost confidence for descriptive words
        descriptive_words = ['creaking', 'slamming', 'echoing', 'crackling']
        for word in descriptive_words:
            if word in context_lower:
                confidence += 0.2
        
        # Reduce confidence if it seems like a metaphor
        metaphor_indicators = ['like', 'as if', 'seemed', 'appeared']
        for indicator in metaphor_indicators:
            if indicator in context_lower:
                confidence -= 0.2
        
        return max(0.0, min(1.0, confidence))
    
    def get_chunks_by_emotion(self, emotion_data: Dict[int, str]) -> Dict[str, List[TextChunk]]:
        """
        Group chunks by their detected emotion.
        
        Args:
            emotion_data: Dictionary mapping chunk_id to emotion
            
        Returns:
            Dictionary mapping emotion to list of chunks
        """
        emotion_groups = {}
        
        for chunk in self.processed_chunks:
            emotion = emotion_data.get(chunk.chunk_id, 'neutral')
            if emotion not in emotion_groups:
                emotion_groups[emotion] = []
            emotion_groups[emotion].append(chunk)
        
        return emotion_groups
    
    def get_sfx_timeline(self) -> List[Dict]:
        """
        Get a timeline of sound effects with timing information.
        
        Returns:
            List of SFX events with timing data
        """
        timeline = []
        
        for event in self.sfx_events:
            # Find which chunk this event belongs to
            chunk = self._find_chunk_for_position(event.position)
            
            if chunk:
                # Estimate time offset within the chunk
                relative_pos = event.position - chunk.start_position
                char_ratio = relative_pos / len(chunk.text) if chunk.text else 0
                time_offset = chunk.estimated_duration * char_ratio
                
                timeline.append({
                    'sfx_type': event.sfx_type,
                    'trigger_word': event.trigger_word,
                    'chunk_id': chunk.chunk_id,
                    'time_offset': time_offset,
                    'context': event.context,
                    'confidence': event.confidence
                })
        
        return sorted(timeline, key=lambda x: (x['chunk_id'], x['time_offset']))
    
    def _find_chunk_for_position(self, position: int) -> Optional[TextChunk]:
        """
        Find the chunk that contains a specific text position.
        
        Args:
            position: Character position in the full text
            
        Returns:
            TextChunk containing the position, or None
        """
        for chunk in self.processed_chunks:
            if chunk.start_position <= position < chunk.end_position:
                return chunk
        return None
    
    def split_by_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences for fine-grained processing.
        
        Args:
            text: Text to split
            
        Returns:
            List of sentences
        """
        return split_into_sentences(text)
    
    def prepare_for_tts(self, chunk: TextChunk) -> str:
        """
        Prepare a text chunk for TTS processing.
        
        Args:
            chunk: TextChunk to prepare
            
        Returns:
            TTS-ready text
        """
        text = chunk.text
        
        # Add pauses for better speech rhythm
        # Add short pause after commas and semicolons
        text = re.sub(r'([,;])', r'\1<break time="0.3s"/>', text)
        
        # Add longer pause after periods and exclamation marks
        text = re.sub(r'([.!])', r'\1<break time="0.7s"/>', text)
        
        # Add pause after question marks
        text = re.sub(r'([?])', r'\1<break time="0.5s"/>', text)
        
        return text
    
    def get_processing_stats(self) -> Dict:
        """
        Get statistics about the processed text.
        
        Returns:
            Dictionary with processing statistics
        """
        if not self.processed_chunks:
            return {}
        
        total_chars = sum(len(chunk.text) for chunk in self.processed_chunks)
        total_words = sum(len(chunk.text.split()) for chunk in self.processed_chunks)
        total_duration = sum(chunk.estimated_duration for chunk in self.processed_chunks)
        
        sfx_by_type = {}
        for event in self.sfx_events:
            sfx_by_type[event.sfx_type] = sfx_by_type.get(event.sfx_type, 0) + 1
        
        return {
            'total_chunks': len(self.processed_chunks),
            'total_characters': total_chars,
            'total_words': total_words,
            'estimated_duration_minutes': total_duration / 60,
            'sfx_events_total': len(self.sfx_events),
            'sfx_by_type': sfx_by_type,
            'average_chunk_size': total_chars / len(self.processed_chunks)
        }
    
    def export_chunks_for_tts(self) -> List[Dict]:
        """
        Export chunks in a format suitable for TTS processing.
        
        Returns:
            List of dictionaries with chunk data for TTS
        """
        return [
            {
                'chunk_id': chunk.chunk_id,
                'text': self.prepare_for_tts(chunk),
                'raw_text': chunk.text,
                'estimated_duration': chunk.estimated_duration,
                'sfx_triggers': chunk.sfx_triggers
            }
            for chunk in self.processed_chunks
        ]


# Main API function requested by user
@timing_decorator
def process_text(raw_text: str) -> List[Dict]:
    """
    Process raw text into structured chunks with SFX detection.
    
    This is the main API function for text processing. It takes raw text
    and returns a list of dictionaries containing text chunks, detected
    sound effects, and placeholders for emotions.
    
    Args:
        raw_text: Raw text string extracted from PDF
        
    Returns:
        List of dictionaries with structure:
        [
            {
                "text": "chunk of text...",
                "sfx": ["door", "footsteps"] or [],
                "emotion": None  # To be filled later by emotion detector
            },
            ...
        ]
        
    Example:
        >>> chunks = process_text("The door creaked as John walked slowly.")
        >>> print(chunks[0]["sfx"])  # ["door", "footsteps"]
    """
    log_event(f"Starting text processing: {len(raw_text)} characters")
    
    if not raw_text or not raw_text.strip():
        log_event("Warning: Empty text provided for processing")
        return []
    
    try:
        # Initialize processor and process text
        processor = TextProcessor()
        processed_chunks = processor.process_text(raw_text)
        
        # Convert to the requested format
        result = []
        for chunk in processed_chunks:
            chunk_dict = {
                "text": chunk.text,
                "sfx": chunk.sfx_triggers,  # List of detected SFX types
                "emotion": None  # Placeholder - will be filled by emotion detector
            }
            result.append(chunk_dict)
        
        log_event(f"Successfully processed text into {len(result)} chunks")
        log_event(f"Total SFX triggers detected: {sum(len(chunk['sfx']) for chunk in result)}")
        
        return result
        
    except Exception as e:
        error_msg = f"Error processing text: {e}"
        log_event(error_msg)
        raise 