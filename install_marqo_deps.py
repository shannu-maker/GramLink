#!/usr/bin/env python
"""
Script to install additional dependencies required for the Marqo FashionSigLIP model.
Run this script to install the missing packages: open_clip and ftfy
"""

import subprocess
import sys
import os

def install_package(package):
    """Install a package using pip"""
    try:
        print(f"Installing {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ {package} installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install {package}: {e}")
        return False

def main():
    """Install required dependencies for Marqo FashionSigLIP model"""
    print("Installing dependencies for Marqo FashionSigLIP model...")
    print("=" * 60)
    
    # Required packages for Marqo FashionSigLIP
    packages = [
        "open_clip_torch",
        "ftfy"
    ]
    
    success_count = 0
    for package in packages:
        if install_package(package):
            success_count += 1
    
    print("\n" + "=" * 60)
    print("Installation Summary")
    print("=" * 60)
    print(f"Successfully installed: {success_count}/{len(packages)} packages")
    
    if success_count == len(packages):
        print("✅ All dependencies installed successfully!")
        print("The Marqo FashionSigLIP model should now work properly.")
    else:
        print("⚠️  Some dependencies failed to install.")
        print("You may need to install them manually:")
        for package in packages:
            print(f"  pip install {package}")
    
    print("\nNote: You may need to restart your Django server after installing these packages.")

if __name__ == "__main__":
    main()
