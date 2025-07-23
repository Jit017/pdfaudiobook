"""
Emotion Detection module for analyzing text sentiment and emotion.

Provides both GPU-accelerated transformer models and CPU fallback methods
for emotion detection, controlled by configuration settings.
"""

from typing import List, Dict, Optional, Union
import re

from .utils import setup_logging, timing_decorator, log_event
from config.settings import USE_REAL_EMOTION, USE_GPU, EMOTION_MODEL, EMOTION_FALLBACK, DEVICE

# Module-level logger
logger = setup_logging(__name__)


class EmotionDetector:
    """
    Detects emotions in text using either transformer models or rule-based fallbacks.
    
    When USE_REAL_EMOTION=True: Uses HuggingFace transformer models for accurate detection
    When USE_REAL_EMOTION=False: Uses simple rule-based detection for development
    """
    
    def __init__(self):
        self.logger = setup_logging(__name__)
        self.model = None
        self.tokenizer = None
        self.use_real_emotion = USE_REAL_EMOTION
        self.device = DEVICE
        
        # Initialize the appropriate detection method
        if self.use_real_emotion:
            self._initialize_transformer_model()
        else:
            self.logger.info("Using fallback emotion detection (development mode)")
    
    def _initialize_transformer_model(self):
        """
        Initialize the transformer model for emotion detection.
        Only runs when USE_REAL_EMOTION=True.
        """
        try:
            from transformers import AutoTokenizer, AutoModelForSequenceClassification
            import torch
            
            self.logger.info(f"Loading emotion model: {EMOTION_MODEL}")
            self.logger.info(f"Using device: {self.device}")
            
            # Load tokenizer and model
            self.tokenizer = AutoTokenizer.from_pretrained(EMOTION_MODEL)
            self.model = AutoModelForSequenceClassification.from_pretrained(EMOTION_MODEL)
            
            # Move model to appropriate device
            if USE_GPU and torch.cuda.is_available():
                self.model = self.model.to(self.device)
                self.logger.info("Model loaded on GPU")
            else:
                self.logger.info("Model loaded on CPU")
            
            self.model.eval()  # Set to evaluation mode
            
            # Get emotion labels from model config
            self.emotion_labels = self.model.config.id2label
            
        except ImportError as e:
            self.logger.error(f"Required packages not installed for transformer model: {e}")
            self.logger.info("Falling back to rule-based emotion detection")
            self.use_real_emotion = False
        except Exception as e:
            self.logger.error(f"Failed to load emotion model: {e}")
            self.logger.info("Falling back to rule-based emotion detection")
            self.use_real_emotion = False
    
    @timing_decorator
    def detect_emotion(self, text: str) -> str:
        """
        Detect the primary emotion in a text passage.
        
        Args:
            text: Text to analyze
            
        Returns:
            Detected emotion as string (e.g., 'joy', 'sadness', 'anger')
        """
        if not text.strip():
            return EMOTION_FALLBACK
        
        if self.use_real_emotion and self.model is not None:
            return self._detect_emotion_transformer(text)
        else:
            return self._detect_emotion_fallback(text)
    
    def _detect_emotion_transformer(self, text: str) -> str:
        """
        Detect emotion using transformer model.
        
        Args:
            text: Text to analyze
            
        Returns:
            Detected emotion
        """
        try:
            import torch
            
            # Tokenize input
            inputs = self.tokenizer(
                text, 
                return_tensors="pt", 
                truncation=True, 
                padding=True, 
                max_length=512
            )
            
            # Move inputs to device
            if USE_GPU and torch.cuda.is_available():
                inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Get predictions
            with torch.no_grad():
                outputs = self.model(**inputs)
                predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
                predicted_id = torch.argmax(predictions, dim=-1).item()
            
            # Convert to emotion label
            emotion = self.emotion_labels.get(predicted_id, EMOTION_FALLBACK)
            
            # Map model-specific labels to our standard set
            emotion = self._normalize_emotion_label(emotion)
            
            self.logger.debug(f"Detected emotion: {emotion} for text: {text[:50]}...")
            return emotion
            
        except Exception as e:
            self.logger.error(f"Error in transformer emotion detection: {e}")
            return self._detect_emotion_fallback(text)
    
    def _detect_emotion_fallback(self, text: str) -> str:
        """
        Simple rule-based emotion detection for development/fallback.
        
        Args:
            text: Text to analyze
            
        Returns:
            Detected emotion
        """
        text_lower = text.lower()
        
        # Define emotion keywords
        emotion_keywords = {
            'joy': ['happy', 'joy', 'excited', 'wonderful', 'amazing', 'great', 'fantastic', 
                   'love', 'smile', 'laugh', 'cheerful', 'delighted', 'pleased'],
            'sadness': ['sad', 'cry', 'tears', 'sorrow', 'grief', 'melancholy', 'depressed',
                       'lonely', 'empty', 'lost', 'hopeless', 'despair', 'mourn'],
            'anger': ['angry', 'mad', 'furious', 'rage', 'hate', 'annoyed', 'frustrated',
                     'irritated', 'outraged', 'livid', 'hostile', 'aggressive'],
            'fear': ['afraid', 'scared', 'terrified', 'anxious', 'worried', 'nervous',
                    'panic', 'frightened', 'alarmed', 'uneasy', 'dread', 'horror'],
            'surprise': ['surprised', 'shocked', 'amazed', 'astonished', 'stunned',
                        'bewildered', 'astounded', 'startled', 'unexpected']
        }
        
        # Count emotion indicators
        emotion_scores = {}
        for emotion, keywords in emotion_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                emotion_scores[emotion] = score
        
        # Return the emotion with highest score, or neutral if none found
        if emotion_scores:
            dominant_emotion = max(emotion_scores, key=emotion_scores.get)
            self.logger.debug(f"Fallback detected emotion: {dominant_emotion} for text: {text[:50]}...")
            return dominant_emotion
        else:
            return 'neutral'
    
    def _normalize_emotion_label(self, emotion: str) -> str:
        """
        Normalize emotion labels from different models to our standard set.
        
        Args:
            emotion: Raw emotion label from model
            
        Returns:
            Normalized emotion label
        """
        emotion_lower = emotion.lower()
        
        # Map common variations to our standard emotions
        emotion_mapping = {
            'happiness': 'joy',
            'joy': 'joy',
            'love': 'joy',
            'optimism': 'joy',
            
            'sadness': 'sadness',
            'grief': 'sadness',
            'disappointment': 'sadness',
            
            'anger': 'anger',
            'rage': 'anger',
            'annoyance': 'anger',
            'irritation': 'anger',
            
            'fear': 'fear',
            'anxiety': 'fear',
            'worry': 'fear',
            'nervousness': 'fear',
            
            'surprise': 'surprise',
            'amazement': 'surprise',
            'confusion': 'surprise',
            
            'neutral': 'neutral',
            'calm': 'neutral',
            'peace': 'neutral'
        }
        
        return emotion_mapping.get(emotion_lower, 'neutral')
    
    @timing_decorator
    def detect_emotions_batch(self, texts: List[str]) -> List[str]:
        """
        Detect emotions for a batch of texts.
        
        Args:
            texts: List of texts to analyze
            
        Returns:
            List of detected emotions
        """
        if self.use_real_emotion and self.model is not None:
            return self._detect_emotions_batch_transformer(texts)
        else:
            return [self._detect_emotion_fallback(text) for text in texts]
    
    def _detect_emotions_batch_transformer(self, texts: List[str]) -> List[str]:
        """
        Batch emotion detection using transformer model.
        
        Args:
            texts: List of texts to analyze
            
        Returns:
            List of detected emotions
        """
        try:
            import torch
            
            # Tokenize all texts
            inputs = self.tokenizer(
                texts,
                return_tensors="pt",
                truncation=True,
                padding=True,
                max_length=512
            )
            
            # Move to device
            if USE_GPU and torch.cuda.is_available():
                inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Get predictions
            with torch.no_grad():
                outputs = self.model(**inputs)
                predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
                predicted_ids = torch.argmax(predictions, dim=-1).cpu().numpy()
            
            # Convert to emotion labels
            emotions = []
            for pred_id in predicted_ids:
                emotion = self.emotion_labels.get(pred_id, EMOTION_FALLBACK)
                emotion = self._normalize_emotion_label(emotion)
                emotions.append(emotion)
            
            return emotions
            
        except Exception as e:
            self.logger.error(f"Error in batch transformer emotion detection: {e}")
            return [self._detect_emotion_fallback(text) for text in texts]
    
    def get_emotion_confidence(self, text: str) -> Dict[str, float]:
        """
        Get confidence scores for all emotions.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary mapping emotions to confidence scores
        """
        if not self.use_real_emotion or self.model is None:
            # For fallback, return simple binary confidence
            detected = self._detect_emotion_fallback(text)
            return {emotion: (1.0 if emotion == detected else 0.0) 
                   for emotion in ['joy', 'sadness', 'anger', 'fear', 'surprise', 'neutral']}
        
        try:
            import torch
            
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                padding=True,
                max_length=512
            )
            
            if USE_GPU and torch.cuda.is_available():
                inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            with torch.no_grad():
                outputs = self.model(**inputs)
                probabilities = torch.nn.functional.softmax(outputs.logits, dim=-1)[0]
            
            # Create confidence dictionary
            confidence_dict = {}
            for i, prob in enumerate(probabilities.cpu().numpy()):
                emotion_label = self.emotion_labels.get(i, 'unknown')
                normalized_emotion = self._normalize_emotion_label(emotion_label)
                if normalized_emotion in confidence_dict:
                    confidence_dict[normalized_emotion] += float(prob)
                else:
                    confidence_dict[normalized_emotion] = float(prob)
            
            return confidence_dict
            
        except Exception as e:
            self.logger.error(f"Error getting emotion confidence: {e}")
            detected = self._detect_emotion_fallback(text)
            return {emotion: (1.0 if emotion == detected else 0.0) 
                   for emotion in ['joy', 'sadness', 'anger', 'fear', 'surprise', 'neutral']}
    
    def analyze_text_emotions(self, text: str, chunk_size: int = 1000) -> Dict:
        """
        Analyze emotions throughout a longer text.
        
        Args:
            text: Full text to analyze
            chunk_size: Size of chunks for analysis
            
        Returns:
            Dictionary with emotion analysis results
        """
        from .utils import chunk_text
        
        chunks = chunk_text(text, chunk_size)
        emotions = self.detect_emotions_batch(chunks)
        
        # Calculate emotion distribution
        emotion_counts = {}
        for emotion in emotions:
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
        
        total_chunks = len(emotions)
        emotion_percentages = {
            emotion: (count / total_chunks) * 100 
            for emotion, count in emotion_counts.items()
        }
        
        # Find dominant emotion
        dominant_emotion = max(emotion_counts, key=emotion_counts.get) if emotion_counts else 'neutral'
        
        return {
                         'dominant_emotion': dominant_emotion,
             'emotion_distribution': emotion_percentages,
             'chunk_emotions': emotions,
             'total_chunks': total_chunks
         }


# Main API function requested by user
def detect_emotion(text: str) -> str:
    """
    Detect emotion from text using config-based logic.
    
    This is the main API function for emotion detection. It uses either
    real AI models or fallback logic based on the USE_REAL_EMOTION config flag.
    
    Args:
        text: Text string to analyze for emotion
        
    Returns:
        Detected emotion as string (one of: 'joy', 'sadness', 'anger', 'fear', 'surprise', 'neutral')
        
    Example:
        >>> emotion = detect_emotion("I am so happy today!")
        >>> print(emotion)  # 'joy' (if real AI) or 'sadness' (if fallback)
    """
    log_event(f"Detecting emotion for text: {text[:50]}...")
    
    if not text or not text.strip():
        log_event("Warning: Empty text provided for emotion detection")
        return EMOTION_FALLBACK
    
    try:
        # Initialize detector and get emotion
        detector = EmotionDetector()
        emotion = detector.detect_emotion(text)
        
        log_event(f"Detected emotion: {emotion} ({'AI model' if USE_REAL_EMOTION else 'fallback logic'})")
        return emotion
        
    except Exception as e:
        error_msg = f"Error detecting emotion: {e}"
        log_event(error_msg)
        # Return fallback emotion on error
        return EMOTION_FALLBACK 