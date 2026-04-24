#!/usr/bin/env python
"""
Test script to check if the AI models can be loaded properly.
Run this script to diagnose model loading issues.
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

def test_model_loading():
    """Test loading of all AI models"""
    print("Testing AI model loading...")
    print("=" * 50)
    
    # Test Marqo FashionSigLIP model
    print("1. Testing Marqo FashionSigLIP model...")
    try:
        from transformers import AutoProcessor, AutoModel, VisionEncoderDecoderModel
        model_name = "Marqo/marqo-fashionSigLIP"
        print(f"Loading {model_name}...")
        processor = AutoProcessor.from_pretrained(model_name, trust_remote_code=True)
        model = AutoModel.from_pretrained(model_name, trust_remote_code=True)
        model.eval()
        print("✅ Marqo FashionSigLIP model loaded successfully!")
    except Exception as e:
        print(f"❌ Marqo FashionSigLIP model failed: {e}")
        
        # Try fallback to Microsoft's FashionSigLIP
        try:
            model_name = "microsoft/FashionSigLIP"
            print(f"Trying fallback model: {model_name}")
            processor = AutoProcessor.from_pretrained(model_name, trust_remote_code=True)
            model = AutoModel.from_pretrained(model_name, trust_remote_code=True)
            model.eval()
            print("✅ Fallback Microsoft FashionSigLIP model loaded successfully!")
        except Exception as e2:
            print(f"❌ Fallback model also failed: {e2}")
    
    print("\n" + "=" * 50)
    
    # Test TrOCR model
    print("2. Testing TrOCR model...")
    try:
        model_name = "microsoft/trocr-base-printed"
        print(f"Loading {model_name}...")
        processor = AutoProcessor.from_pretrained(model_name)
        model = VisionEncoderDecoderModel.from_pretrained(model_name)
        model.eval()
        print("✅ TrOCR model loaded successfully!")
    except Exception as e:
        print(f"❌ TrOCR model failed: {e}")
        
        # Try fallback to handwritten-specific model
        try:
            model_name = "microsoft/trocr-base-handwritten"
            print(f"Trying fallback TrOCR model: {model_name}")
            processor = AutoProcessor.from_pretrained(model_name)
            model = VisionEncoderDecoderModel.from_pretrained(model_name)
            model.eval()
            print("✅ Fallback TrOCR handwritten model loaded successfully!")
        except Exception as e2:
            print(f"❌ Fallback TrOCR model also failed: {e2}")
    
    print("\n" + "=" * 50)
    
    # Test EasyOCR
    print("3. Testing EasyOCR...")
    try:
        import easyocr
        reader = easyocr.Reader(['en'])
        print("✅ EasyOCR loaded successfully!")
    except Exception as e:
        print(f"❌ EasyOCR failed: {e}")
    
    print("\n" + "=" * 50)
    print("Model loading test completed!")
    print("\nIf models failed to load, try:")
    print("1. Install missing dependencies: pip install -r requirements.txt")
    print("2. Check internet connection (models download from Hugging Face)")
    print("3. Try running: pip install --upgrade transformers torch")

if __name__ == "__main__":
    test_model_loading()
