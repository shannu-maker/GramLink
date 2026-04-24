#!/usr/bin/env python
"""
Installation script for AI models and dependencies.
Run this script to install all required packages and download models.
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed!")
        print(f"Error: {e.stderr}")
        return False

def install_dependencies():
    """Install Python dependencies"""
    print("Installing Python dependencies...")
    print("=" * 50)
    
    # Install basic requirements
    if not run_command("pip install -r requirements.txt", "Installing requirements.txt"):
        print("⚠️  Some packages failed to install. Trying individual packages...")
        
        # Install packages individually
        packages = [
            "torch==2.1.0",
            "transformers==4.35.0", 
            "Pillow==10.0.0",
            "numpy==1.24.3",
            "opencv-python==4.8.1.78",
            "easyocr==1.7.0",
            "torchvision==0.16.0",
            "accelerate==0.24.0"
        ]
        
        for package in packages:
            run_command(f"pip install {package}", f"Installing {package}")

def test_installation():
    """Test if the installation worked"""
    print("\nTesting installation...")
    print("=" * 50)
    
    try:
        # Test imports
        import torch
        print(f"✅ PyTorch {torch.__version__} imported successfully")
        
        import transformers
        print(f"✅ Transformers {transformers.__version__} imported successfully")
        
        import PIL
        print(f"✅ Pillow {PIL.__version__} imported successfully")
        
        import cv2
        print(f"✅ OpenCV {cv2.__version__} imported successfully")
        
        import easyocr
        print(f"✅ EasyOCR imported successfully")
        
        print("\n🎉 All dependencies installed successfully!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def download_models():
    """Download AI models"""
    print("\nDownloading AI models...")
    print("=" * 50)
    
    try:
        from transformers import AutoProcessor, AutoModel
        
        # Download FashionSigLIP
        print("🔄 Downloading FashionSigLIP model...")
        try:
            processor = AutoProcessor.from_pretrained("microsoft/FashionSigLIP", trust_remote_code=True)
            model = AutoModel.from_pretrained("microsoft/FashionSigLIP", trust_remote_code=True)
            print("✅ FashionSigLIP model downloaded!")
        except Exception as e:
            print(f"⚠️  FashionSigLIP failed, trying fallback...")
            processor = AutoProcessor.from_pretrained("microsoft/CLIP-ViT-B-32")
            model = AutoModel.from_pretrained("microsoft/CLIP-ViT-B-32")
            print("✅ Fallback model downloaded!")
        
        # Download TrOCR
        print("🔄 Downloading TrOCR model...")
        try:
            processor = AutoProcessor.from_pretrained("microsoft/trocr-base-handwritten")
            model = AutoModel.from_pretrained("microsoft/trocr-base-handwritten")
            print("✅ TrOCR model downloaded!")
        except Exception as e:
            print(f"⚠️  TrOCR failed, trying fallback...")
            processor = AutoProcessor.from_pretrained("microsoft/trocr-base-printed")
            model = AutoModel.from_pretrained("microsoft/trocr-base-printed")
            print("✅ Fallback TrOCR model downloaded!")
        
        # Download EasyOCR
        print("🔄 Downloading EasyOCR models...")
        import easyocr
        reader = easyocr.Reader(['en'])
        print("✅ EasyOCR models downloaded!")
        
        print("\n🎉 All models downloaded successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Model download failed: {e}")
        return False

def main():
    """Main installation function"""
    print("🚀 AI Models Installation Script")
    print("=" * 50)
    print("This script will install all required dependencies and download AI models.")
    print("Make sure you have a stable internet connection.")
    print()
    
    # Install dependencies
    install_dependencies()
    
    # Test installation
    if not test_installation():
        print("\n❌ Installation test failed. Please check the errors above.")
        return
    
    # Download models
    if not download_models():
        print("\n⚠️  Model download failed, but basic functionality should work.")
        print("You can try running the search functionality - it will use fallback methods.")
    
    print("\n🎉 Installation completed!")
    print("\nNext steps:")
    print("1. Run the Django server: python manage.py runserver")
    print("2. Visit /api/debug/models/ to check model status")
    print("3. Try the search functionality at /search/")

if __name__ == "__main__":
    main()
