# 🎧 PDF to Audiobook Converter

Convert PDF documents into immersive audiobooks with emotion-based background music and contextual sound effects.

## ✨ Features

- **📖 PDF Text Extraction**: Clean text extraction from PDF documents with header/footer removal
- **🧠 Emotion Detection**: AI-powered emotion analysis using transformer models (with CPU fallback)
- **🎵 Multiple TTS Engines**: Support for pyttsx3 (offline), Google TTS, and Coqui TTS (GPU-accelerated)
- **🎼 Dynamic Background Music**: Emotion-based background music selection
- **🔊 Sound Effects**: Contextual sound effects triggered by keywords
- **📱 Dual Interface**: Both command-line and web interfaces available
- **⚙️ Flexible Configuration**: Easy switching between development and production modes

## 🏗️ Project Structure

```
pdf_to_audiobook/
├── app.py                      # Main CLI or Streamlit app (entry point)
├── requirements.txt            # All dependencies
├── README.md                   # Project overview & instructions
├── config/
│   └── settings.py             # Paths, config flags (TTS model, use_gpu, etc.)
├── data/
│   ├── input/                  # User-uploaded PDFs
│   └── output/                 # Final MP3 audiobook files
├── assets/
│   ├── bg_music/               # Royalty-free emotion-based background tracks
│   └── sfx/                    # Sound effects (door creak, thunder, etc.)
├── src/
│   ├── __init__.py
│   ├── pdf_reader.py           # Extracts & cleans text from PDF
│   ├── text_processor.py       # Splits text, finds keywords, tags SFX
│   ├── emotion_detector.py     # Emotion detection using transformer models
│   ├── tts_engine.py           # Text-to-speech (basic and advanced models)
│   ├── audio_mixer.py          # Combines narration, BGM, and SFX
│   └── utils.py                # Shared utilities (logging, timing, etc.)
└── tests/
    ├── test_pdf_reader.py
    ├── test_emotion_detector.py
    └── test_audio_mixer.py
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10.13+ (recommended)
- macOS, Windows, or Linux

### Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd pdf_to_audiobook
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Verify setup**:
   ```bash
   python check_setup.py
   ```

4. **Configure for your environment**:
   Edit `config/settings.py` to match your setup:
   ```python
   # For development (no GPU)
   USE_GPU = False
   USE_REAL_EMOTION = False
   TTS_ENGINE = "pyttsx3"
   
   # For production (with GPU)
   USE_GPU = True
   USE_REAL_EMOTION = True
   TTS_ENGINE = "coqui"
   ```

### Basic Usage

#### Quick Start (No Dependencies)

```bash
# Test basic functionality without dependencies
python demo_basic.py

# Verify project setup
python check_setup.py
```

#### Command Line Interface

```bash
# Convert a PDF to audiobook
python app.py --pdf document.pdf --output audiobook.mp3

# Preview mode (first 2 minutes only)
python app.py --pdf document.pdf --output preview.mp3 --preview

# Show current configuration
python app.py --config
```

#### Web Interface

```bash
# Launch Streamlit web app
python app.py --streamlit
```

Then open your browser to `http://localhost:8501`

#### Demo & Testing

```bash
# Run basic demo without external dependencies (works immediately)
python demo_basic.py

# Install and test minimal dependencies for audiobook creation
python install_test_deps.py

# Verify project setup
python check_setup.py

# Run full demo with all features (requires dependencies)
python demo.py

# Test API functions (requires dependencies)
python test_api.py
```

#### 🎧 Real Audiobook Creation Demo

The enhanced `demo_basic.py` now creates **real audiobooks** with:

**✅ Sample Story with SFX:**
- "Sarah walked toward the old wooden **door**"
- "The **door creaked** loudly as she pushed it open"  
- "She let out a terrified **scream**"

**✅ Detected Elements:**
- **SFX Detection**: `door`, `scream` keywords → `door.mp3`, `scream.mp3`
- **Emotion Detection**: `fear` (scream), `joy` (relief), `sadness` (default)
- **Background Music**: `sadness.mp3`, `joy.mp3` based on emotions

**✅ Pipeline Output:**
- **Text Processing**: 4 chunks, 4 SFX events detected
- **TTS Synthesis**: Individual narration files per chunk  
- **Audio Mixing**: Final `demo_result.mp3` with BGM + SFX + narration
- **Clean Integration**: Uses actual `assets/bg_music/` and `assets/sfx/` files

## ⚙️ Configuration

The `config/settings.py` file controls all major features:

### Development Mode (Home - No GPU)
```python
USE_GPU = False                 # Use CPU for all processing
USE_REAL_EMOTION = False        # Use simple rule-based emotion detection
TTS_ENGINE = "pyttsx3"          # Use offline TTS engine
```

### Production Mode (College - With GPU)
```python
USE_GPU = True                  # Use GPU acceleration
USE_REAL_EMOTION = True         # Use transformer-based emotion detection
TTS_ENGINE = "coqui"            # Use high-quality Coqui TTS
```

### Key Configuration Options

| Setting | Development | Production | Description |
|---------|-------------|------------|-------------|
| `USE_GPU` | `False` | `True` | Enable GPU acceleration |
| `USE_REAL_EMOTION` | `False` | `True` | Use AI emotion detection |
| `TTS_ENGINE` | `"pyttsx3"` | `"coqui"` | Text-to-speech engine |
| `BGM_VOLUME` | `0.3` | `0.3` | Background music volume |
| `SFX_VOLUME` | `0.6` | `0.6` | Sound effects volume |

## 🎵 Audio Assets

### Background Music (assets/bg_music/)
Place emotion-based background music files:
- `upbeat_ambient.mp3` (for joy)
- `melancholy_piano.mp3` (for sadness)
- `tense_strings.mp3` (for anger)
- `dark_ambient.mp3` (for fear)
- `soft_instrumental.mp3` (for neutral)

### Sound Effects (assets/sfx/)
Place sound effect files:
- `door.mp3` (triggered by "door", "creak", etc.)
- `footsteps.mp3` (triggered by "walk", "steps", etc.)
- `thunder.mp3` (triggered by "thunder", "storm", etc.)

## 🔧 Advanced Usage

### Main API Functions

The core functionality is exposed through clean API functions:

#### PDF Text Extraction
```python
from src.pdf_reader import extract_text_from_pdf

# Extract clean text from PDF
text = extract_text_from_pdf("document.pdf")
print(f"Extracted {len(text)} characters")
```

#### Text Processing & SFX Detection
```python
from src.text_processor import process_text

# Process text into chunks with SFX detection
chunks = process_text(raw_text)
for chunk in chunks:
    print(f"Text: {chunk['text']}")
    print(f"SFX: {chunk['sfx']}")
    print(f"Emotion: {chunk['emotion']}")  # None initially
```

#### Emotion Detection
```python
from src.emotion_detector import detect_emotion

# Detect emotion (AI or fallback based on config)
emotion = detect_emotion("I am so happy today!")
print(f"Detected emotion: {emotion}")
```

#### Text-to-Speech Synthesis
```python
from src.tts_engine import synthesize_speech

# Convert text to speech
synthesize_speech("Hello world", "output.mp3")
```

#### Audio Mixing
```python
from src.audio_mixer import mix_audio

# Mix segments with BGM and SFX
segments = [
    {
        "text": "The door creaked loudly.",
        "emotion": "fear",
        "sfx": ["door"],
        "audio_file": "narration_01.mp3"
    }
]
mix_audio(segments, "final_audiobook.mp3")
```

### Advanced Class-Based Usage

For more control, use the underlying classes:

#### Custom Text Processing
```python
from src import TextProcessor

processor = TextProcessor()
chunks = processor.process_text(text)
sfx_timeline = processor.get_sfx_timeline()
stats = processor.get_processing_stats()
```

#### Custom Emotion Detection
```python
from src import EmotionDetector

detector = EmotionDetector()
emotion = detector.detect_emotion("This is a happy sentence!")
emotions = detector.detect_emotions_batch(text_list)
```

#### Custom TTS Generation
```python
from src import TTSEngine

tts = TTSEngine("pyttsx3")  # or "gtts", "coqui"
success = tts.synthesize_speech("Hello world", output_path)
```

#### Custom Audio Mixing
```python
from src import AudioMixer

mixer = AudioMixer()
success = mixer.create_audiobook(
    narration_files=audio_files,
    emotions=emotions,
    sfx_timeline=sfx_events,
    output_path=output_path
)
```

## 🧪 Testing

Run the test suite:
```bash
pytest tests/
```

Run specific tests:
```bash
pytest tests/test_pdf_reader.py -v
```

## 🐛 Troubleshooting

### Common Issues

**1. Import errors**
```bash
# Make sure all dependencies are installed
pip install -r requirements.txt
```

**2. GPU not detected**
```bash
# Check PyTorch CUDA support
python -c "import torch; print(torch.cuda.is_available())"
```

**3. Audio format issues**
```bash
# Install additional audio codecs
pip install pydub[all]
```

**4. pyttsx3 voice issues**
```python
# List available voices
python -c "import pyttsx3; engine = pyttsx3.init(); voices = engine.getProperty('voices'); [print(v.id, v.name) for v in voices]"
```

### Platform-Specific Notes

**macOS**:
- pyttsx3 uses system TTS voices
- May need to install additional system voices

**Windows**:
- pyttsx3 uses SAPI voices
- Install additional SAPI voices for variety

**Linux**:
- May need to install espeak: `sudo apt-get install espeak`

## 📈 Performance Tips

### For Development (No GPU)
- Use smaller text chunks (`MAX_CHUNK_SIZE = 500`)
- Enable preview mode for testing
- Use pyttsx3 for fastest TTS generation

### For Production (With GPU)
- Use larger chunks (`MAX_CHUNK_SIZE = 1000`)
- Enable real emotion detection
- Use Coqui TTS for best quality

### Memory Optimization
- Clear audio cache periodically: `mixer.clear_cache()`
- Process large documents in chapters
- Use lower sample rates for longer documents

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and add tests
4. Commit your changes: `git commit -am 'Add feature'`
5. Push to the branch: `git push origin feature-name`
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **PyMuPDF** for PDF text extraction
- **Transformers** for emotion detection models
- **Coqui TTS** for high-quality speech synthesis
- **pydub** for audio processing
- **Streamlit** for the web interface

## 📞 Support

If you encounter any issues or have questions:

1. Check the troubleshooting section above
2. Search existing issues on GitHub
3. Create a new issue with detailed information about your problem

---

**Happy audiobook creation! 🎧📚** 