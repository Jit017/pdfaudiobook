"""
Tests for the Emotion Detector module.
"""

import pytest
from pathlib import Path
import sys

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))
from src.emotion_detector import EmotionDetector


class TestEmotionDetector:
    """Test cases for EmotionDetector class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.detector = EmotionDetector()
    
    def test_emotion_detector_initialization(self):
        """Test EmotionDetector initializes correctly."""
        assert self.detector is not None
        assert hasattr(self.detector, 'logger')
        assert hasattr(self.detector, 'use_real_emotion')
    
    def test_detect_emotion_empty_text(self):
        """Test emotion detection with empty text."""
        emotion = self.detector.detect_emotion("")
        assert emotion in ['neutral', 'joy', 'sadness', 'anger', 'fear', 'surprise']
    
    def test_detect_emotion_fallback_joy(self):
        """Test fallback emotion detection for joyful text."""
        joyful_text = "I am so happy and excited about this wonderful news!"
        emotion = self.detector._detect_emotion_fallback(joyful_text)
        assert emotion == 'joy'
    
    def test_detect_emotion_fallback_sadness(self):
        """Test fallback emotion detection for sad text."""
        sad_text = "I feel so sad and lonely, tears are falling down my face."
        emotion = self.detector._detect_emotion_fallback(sad_text)
        assert emotion == 'sadness'
    
    def test_detect_emotion_fallback_anger(self):
        """Test fallback emotion detection for angry text."""
        angry_text = "I am furious and mad about this outrageous situation!"
        emotion = self.detector._detect_emotion_fallback(angry_text)
        assert emotion == 'anger'
    
    def test_detect_emotion_fallback_fear(self):
        """Test fallback emotion detection for fearful text."""
        fearful_text = "I am terrified and scared of the dark shadows ahead."
        emotion = self.detector._detect_emotion_fallback(fearful_text)
        assert emotion == 'fear'
    
    def test_detect_emotion_fallback_surprise(self):
        """Test fallback emotion detection for surprised text."""
        surprised_text = "I was shocked and amazed by the unexpected turn of events!"
        emotion = self.detector._detect_emotion_fallback(surprised_text)
        assert emotion == 'surprise'
    
    def test_detect_emotion_fallback_neutral(self):
        """Test fallback emotion detection for neutral text."""
        neutral_text = "The weather today is partly cloudy with temperatures around 20 degrees."
        emotion = self.detector._detect_emotion_fallback(neutral_text)
        assert emotion == 'neutral'
    
    def test_normalize_emotion_label(self):
        """Test emotion label normalization."""
        # Test standard emotions
        assert self.detector._normalize_emotion_label('happiness') == 'joy'
        assert self.detector._normalize_emotion_label('sadness') == 'sadness'
        assert self.detector._normalize_emotion_label('anger') == 'anger'
        assert self.detector._normalize_emotion_label('fear') == 'fear'
        assert self.detector._normalize_emotion_label('surprise') == 'surprise'
        
        # Test variations
        assert self.detector._normalize_emotion_label('rage') == 'anger'
        assert self.detector._normalize_emotion_label('anxiety') == 'fear'
        assert self.detector._normalize_emotion_label('amazement') == 'surprise'
        
        # Test unknown emotion
        assert self.detector._normalize_emotion_label('unknown') == 'neutral'
    
    def test_detect_emotions_batch(self):
        """Test batch emotion detection."""
        texts = [
            "I am happy!",
            "This is terrible.",
            "The cat sits on the mat."
        ]
        emotions = self.detector.detect_emotions_batch(texts)
        
        assert len(emotions) == 3
        assert all(emotion in ['neutral', 'joy', 'sadness', 'anger', 'fear', 'surprise'] 
                  for emotion in emotions)
    
    def test_get_emotion_confidence(self):
        """Test emotion confidence scoring."""
        text = "I am very happy today!"
        confidence = self.detector.get_emotion_confidence(text)
        
        assert isinstance(confidence, dict)
        assert all(0.0 <= score <= 1.0 for score in confidence.values())
        assert sum(confidence.values()) > 0  # At least one emotion should have confidence
    
    def test_analyze_text_emotions(self):
        """Test full text emotion analysis."""
        long_text = """
        I was so excited when I got the news! It made me incredibly happy.
        But then I realized the implications and became worried and anxious.
        The whole situation made me feel sad and disappointed.
        However, I was surprised by how well everything turned out in the end.
        """
        
        analysis = self.detector.analyze_text_emotions(long_text)
        
        assert isinstance(analysis, dict)
        assert 'dominant_emotion' in analysis
        assert 'emotion_distribution' in analysis
        assert 'chunk_emotions' in analysis
        assert 'total_chunks' in analysis
        
        assert analysis['dominant_emotion'] in ['neutral', 'joy', 'sadness', 'anger', 'fear', 'surprise']
        assert isinstance(analysis['emotion_distribution'], dict)
        assert isinstance(analysis['chunk_emotions'], list)
        assert isinstance(analysis['total_chunks'], int)
    
    def test_emotion_detection_consistency(self):
        """Test that emotion detection is consistent for the same text."""
        text = "I am absolutely thrilled and delighted!"
        
        emotion1 = self.detector.detect_emotion(text)
        emotion2 = self.detector.detect_emotion(text)
        
        # Should get the same result for the same input
        assert emotion1 == emotion2
    
    @pytest.mark.parametrize("text,expected_emotion", [
        ("I love this amazing book!", "joy"),
        ("This is the worst day ever.", "sadness"),
        ("I hate this stupid thing!", "anger"),
        ("I'm scared of the dark.", "fear"),
        ("What a shocking revelation!", "surprise"),
        ("The temperature is 25 degrees.", "neutral"),
    ])
    def test_emotion_detection_examples(self, text, expected_emotion):
        """Test emotion detection with specific examples."""
        detected = self.detector._detect_emotion_fallback(text)
        # Note: Using fallback method to ensure deterministic results
        assert detected == expected_emotion
    
    def test_configuration_awareness(self):
        """Test that detector respects configuration settings."""
        # The detector should know whether it's using real emotion or fallback
        assert hasattr(self.detector, 'use_real_emotion')
        
        # Should use the configured detection method
        if self.detector.use_real_emotion:
            assert self.detector.model is not None
            assert self.detector.tokenizer is not None
        else:
            # In fallback mode, transformer components may be None
            pass  # This is acceptable in development mode


if __name__ == "__main__":
    pytest.main([__file__]) 