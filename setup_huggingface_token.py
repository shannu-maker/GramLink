#!/usr/bin/env python
"""
Setup script for Hugging Face token configuration.
This script helps you configure your Hugging Face token for the AI search functionality.
"""

import os
import sys

def setup_huggingface_token():
    """Setup Hugging Face token for the application"""
    
    print("🤗 Hugging Face Token Setup")
    print("=" * 50)
    print()
    print("To use the AI search functionality, you need a Hugging Face token.")
    print("This token allows you to download and use AI models from Hugging Face Hub.")
    print()
    print("Steps to get your token:")
    print("1. Go to: https://huggingface.co/settings/tokens")
    print("2. Sign up or log in to your Hugging Face account")
    print("3. Click 'New token'")
    print("4. Give it a name (e.g., 'Django App Token')")
    print("5. Select 'Read' access")
    print("6. Click 'Generate token'")
    print("7. Copy the token (it starts with 'hf_...')")
    print()
    
    # Get token from user
    token = input("Enter your Hugging Face token (or press Enter to skip): ").strip()
    
    if not token:
        print("\n⚠️  No token provided. You can set it later using one of these methods:")
        print("\nMethod 1: Environment Variable (Recommended)")
        print("Set the HUGGINGFACE_TOKEN environment variable:")
        print("Windows: set HUGGINGFACE_TOKEN=your_token_here")
        print("Linux/Mac: export HUGGINGFACE_TOKEN=your_token_here")
        print("\nMethod 2: Direct in settings.py")
        print("Edit capstone/mysite/settings.py and uncomment the line:")
        print("HUGGINGFACE_TOKEN = 'your_token_here'")
        return
    
    # Validate token format
    if not token.startswith('hf_'):
        print("⚠️  Warning: Hugging Face tokens usually start with 'hf_'. Please verify your token.")
        confirm = input("Continue anyway? (y/n): ").strip().lower()
        if confirm != 'y':
            print("Setup cancelled.")
            return
    
    print(f"\n✅ Token received: {token[:10]}...")
    
    # Ask how to store the token
    print("\nHow would you like to store the token?")
    print("1. Set as environment variable (recommended)")
    print("2. Add directly to settings.py")
    print("3. Just show me the instructions")
    
    choice = input("Enter your choice (1-3): ").strip()
    
    if choice == "1":
        print("\n🔧 Setting up environment variable...")
        print("\nFor Windows (Command Prompt):")
        print(f"set HUGGINGFACE_TOKEN={token}")
        print("\nFor Windows (PowerShell):")
        print(f"$env:HUGGINGFACE_TOKEN='{token}'")
        print("\nFor Linux/Mac:")
        print(f"export HUGGINGFACE_TOKEN='{token}'")
        print("\nTo make it permanent, add the export command to your ~/.bashrc or ~/.zshrc file")
        
    elif choice == "2":
        print("\n🔧 Adding token to settings.py...")
        try:
            settings_file = "mysite/settings.py"
            with open(settings_file, 'r') as f:
                content = f.read()
            
            # Replace the commented line with the actual token
            old_line = "# HUGGINGFACE_TOKEN = 'your_token_here'"
            new_line = f"HUGGINGFACE_TOKEN = '{token}'"
            
            if old_line in content:
                content = content.replace(old_line, new_line)
                with open(settings_file, 'w') as f:
                    f.write(content)
                print("✅ Token added to settings.py")
            else:
                print("⚠️  Could not find the token line in settings.py")
                print("Please manually add this line to mysite/settings.py:")
                print(f"HUGGINGFACE_TOKEN = '{token}'")
        except Exception as e:
            print(f"❌ Error updating settings.py: {e}")
            print("Please manually add this line to mysite/settings.py:")
            print(f"HUGGINGFACE_TOKEN = '{token}'")
    
    elif choice == "3":
        print("\n📋 Manual Setup Instructions:")
        print("\nOption 1: Environment Variable")
        print("Set the HUGGINGFACE_TOKEN environment variable before running Django:")
        print(f"Windows: set HUGGINGFACE_TOKEN={token}")
        print(f"Linux/Mac: export HUGGINGFACE_TOKEN={token}")
        print("\nOption 2: Direct in settings.py")
        print("Edit capstone/mysite/settings.py and change this line:")
        print(f"HUGGINGFACE_TOKEN = '{token}'")
    
    print("\n🎉 Setup complete!")
    print("\nNext steps:")
    print("1. Restart your Django server")
    print("2. Test the AI search functionality")
    print("3. Check the debug endpoint: /api/debug/models/")

if __name__ == "__main__":
    setup_huggingface_token()
