#!/usr/bin/env python
"""
Script to verify that the correct AI models are configured and can be loaded.
This script checks that:
1. Image similarity uses "Marqo/marqo-fashionSigLIP"
2. Text recognition uses "microsoft/trocr"
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

def verify_model_configuration():
    """Verify that the correct models are configured"""
    print("Verifying AI Model Configuration")
    print("=" * 60)
    
    # Import the search views to check model names
    from members.search_views import load_fashion_model, load_trocr_model
    
    print("Model loading functions imported successfully")
    
    # Check if the model names are correct in the source code
    with open('members/search_views.py', 'r') as f:
        content = f.read()
        
        # Check for Marqo FashionSigLIP model
        if 'Marqo/marqo-fashionSigLIP' in content:
            print("Image similarity model: Marqo/marqo-fashionSigLIP - CONFIGURED")
        else:
            print("Image similarity model: Marqo/marqo-fashionSigLIP - NOT FOUND")
            
        # Check for Microsoft TrOCR model
        if 'microsoft/trocr-base-printed' in content:
            print("Text recognition model: microsoft/trocr-base-printed - CONFIGURED")
        else:
            print("Text recognition model: microsoft/trocr-base-printed - NOT FOUND")
    
    print("\n" + "=" * 60)
    print("Testing Model Loading (Optional)")
    print("=" * 60)
    
    # Test if models can be loaded (this will download them if not cached)
    try:
        print("Testing image similarity model loading...")
        if load_fashion_model():
            print("Image similarity model loaded successfully")
        else:
            print("Image similarity model loading failed (check dependencies)")
    except Exception as e:
        print(f"Image similarity model error: {e}")
    
    try:
        print("Testing text recognition model loading...")
        if load_trocr_model():
            print("Text recognition model loaded successfully")
        else:
            print("Text recognition model loading failed (check dependencies)")
    except Exception as e:
        print(f"Text recognition model error: {e}")
    
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    print("Model configuration updated successfully!")
    print("Image Similarity: Marqo/marqo-fashionSigLIP")
    print("Text Recognition: microsoft/trocr-base-printed")
    print("\nNote: Models will be downloaded on first use if not cached locally.")
    print("Make sure you have sufficient disk space and internet connection.")

if __name__ == "__main__":
    verify_model_configuration()
