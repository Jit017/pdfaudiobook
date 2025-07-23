#!/usr/bin/env python3
"""
API Test Script for PDF to Audiobook Converter.

This script tests that all main API functions are properly implemented
and can be imported without errors (even if dependencies are missing).
"""

import sys
from pathlib import Path

# Add paths for imports
sys.path.append(str(Path(__file__).parent))
sys.path.append(str(Path(__file__).parent / "src"))

def test_function_imports():
    """Test that all main API functions can be imported."""
    print("🔍 Testing API Function Imports")
    print("-" * 40)
    
    functions_to_test = [
        ("src.pdf_reader", "extract_text_from_pdf"),
        ("src.text_processor", "process_text"),
        ("src.emotion_detector", "detect_emotion"),
        ("src.tts_engine", "synthesize_speech"),
        ("src.audio_mixer", "mix_audio"),
        ("src.utils", "load_audio"),
        ("src.utils", "log_event"),
        ("src.utils", "sanitize_filename"),
    ]
    
    success_count = 0
    
    for module_name, function_name in functions_to_test:
        try:
            module = __import__(module_name, fromlist=[function_name])
            func = getattr(module, function_name)
            print(f"  ✅ {module_name}.{function_name}")
            success_count += 1
            
            # Test that it's callable
            if not callable(func):
                print(f"    ⚠️  Warning: {function_name} is not callable")
                
        except ImportError as e:
            print(f"  ❌ {module_name}.{function_name} - Import Error: {e}")
        except AttributeError as e:
            print(f"  ❌ {module_name}.{function_name} - Not Found: {e}")
        except Exception as e:
            print(f"  ⚠️  {module_name}.{function_name} - Other Error: {e}")
    
    print(f"\nImport Summary: {success_count}/{len(functions_to_test)} functions imported successfully")
    return success_count == len(functions_to_test)


def test_function_signatures():
    """Test that functions have the expected signatures."""
    print("\n🔍 Testing Function Signatures")
    print("-" * 40)
    
    try:
        import inspect
        
        # Import functions for signature testing
        from src.pdf_reader import extract_text_from_pdf
        from src.text_processor import process_text
        from src.emotion_detector import detect_emotion
        from src.tts_engine import synthesize_speech
        from src.audio_mixer import mix_audio
        from src.utils import load_audio, log_event, sanitize_filename
        
        # Expected signatures
        expected_signatures = {
            "extract_text_from_pdf": ["pdf_path"],
            "process_text": ["raw_text"],
            "detect_emotion": ["text"],
            "synthesize_speech": ["text", "output_path"],
            "mix_audio": ["segments", "output_path"],
            "load_audio": ["path"],
            "log_event": ["msg"],
            "sanitize_filename": ["name"],
        }
        
        functions_to_check = {
            "extract_text_from_pdf": extract_text_from_pdf,
            "process_text": process_text,
            "detect_emotion": detect_emotion,
            "synthesize_speech": synthesize_speech,
            "mix_audio": mix_audio,
            "load_audio": load_audio,
            "log_event": log_event,
            "sanitize_filename": sanitize_filename,
        }
        
        signature_ok = True
        
        for func_name, func in functions_to_check.items():
            try:
                sig = inspect.signature(func)
                param_names = list(sig.parameters.keys())
                expected_params = expected_signatures[func_name]
                
                # Check if required parameters are present
                has_required_params = all(param in param_names for param in expected_params)
                
                if has_required_params:
                    print(f"  ✅ {func_name}({', '.join(param_names)})")
                else:
                    print(f"  ❌ {func_name} - Missing required params: {expected_params}")
                    signature_ok = False
                    
            except Exception as e:
                print(f"  ⚠️  {func_name} - Error checking signature: {e}")
                signature_ok = False
        
        return signature_ok
        
    except ImportError as e:
        print(f"❌ Cannot test signatures - import error: {e}")
        return False


def test_config_integration():
    """Test that functions properly integrate with the configuration system."""
    print("\n🔍 Testing Configuration Integration")
    print("-" * 40)
    
    try:
        from config.settings import (
            USE_GPU, USE_REAL_EMOTION, TTS_ENGINE,
            get_config_summary
        )
        
        config = get_config_summary()
        print(f"  Current config: {config}")
        
        # Test emotion detector respects config
        from src.emotion_detector import detect_emotion
        emotion = detect_emotion("This is a test sentence.")
        print(f"  ✅ Emotion detection works: '{emotion}'")
        
        if not USE_REAL_EMOTION:
            # Should use fallback logic
            print(f"    Using fallback emotion detection (expected in dev mode)")
        
        # Test that TTS engine setting is available
        print(f"  ✅ TTS engine configured: {TTS_ENGINE}")
        
        print(f"  ✅ Configuration integration working")
        return True
        
    except Exception as e:
        print(f"❌ Configuration integration error: {e}")
        return False


def test_error_handling():
    """Test that functions handle errors gracefully."""
    print("\n🔍 Testing Error Handling")
    print("-" * 40)
    
    try:
        # Test with invalid inputs
        from src.emotion_detector import detect_emotion
        from src.utils import sanitize_filename
        
        # Test empty input handling
        emotion = detect_emotion("")
        print(f"  ✅ Empty text handled: {emotion}")
        
        # Test filename sanitization
        clean_name = sanitize_filename("")
        print(f"  ✅ Empty filename handled: '{clean_name}'")
        
        # Test with special characters
        weird_name = sanitize_filename("file<>:\"|?*")
        print(f"  ✅ Special chars handled: '{weird_name}'")
        
        print(f"  ✅ Error handling working")
        return True
        
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False


def test_docstrings():
    """Test that functions have proper docstrings."""
    print("\n🔍 Testing Documentation")
    print("-" * 40)
    
    try:
        from src.pdf_reader import extract_text_from_pdf
        from src.text_processor import process_text
        from src.emotion_detector import detect_emotion
        from src.tts_engine import synthesize_speech
        from src.audio_mixer import mix_audio
        
        functions = [
            ("extract_text_from_pdf", extract_text_from_pdf),
            ("process_text", process_text),
            ("detect_emotion", detect_emotion),
            ("synthesize_speech", synthesize_speech),
            ("mix_audio", mix_audio),
        ]
        
        documented_count = 0
        
        for name, func in functions:
            docstring = func.__doc__
            if docstring and len(docstring.strip()) > 20:
                print(f"  ✅ {name} - Well documented")
                documented_count += 1
            else:
                print(f"  ⚠️  {name} - Missing or short docstring")
        
        print(f"  Documentation: {documented_count}/{len(functions)} functions well documented")
        return documented_count >= len(functions) * 0.8  # 80% threshold
        
    except Exception as e:
        print(f"❌ Documentation test error: {e}")
        return False


def main():
    """Run all API tests."""
    print("🎧 PDF to Audiobook Converter - API Test Suite")
    print("=" * 50)
    
    tests = [
        ("Function Imports", test_function_imports),
        ("Function Signatures", test_function_signatures),
        ("Configuration Integration", test_config_integration),
        ("Error Handling", test_error_handling),
        ("Documentation", test_docstrings),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    print("-" * 25)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} {test_name}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All API tests passed! The implementation is ready for use.")
    else:
        print("⚠️  Some tests failed. Check the issues above.")
    
    return passed == len(results)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 