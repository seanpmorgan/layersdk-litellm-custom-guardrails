#!/usr/bin/env python3
import json
import os
import subprocess
import sys
import time
from dotenv import load_dotenv

def load_secrets():
    """Load secrets from .env or secrets.json into environment variables"""
    # Try loading from .env file first
    if os.path.exists('.env'):
        print("📄 Loading credentials from .env file...")
        load_dotenv('.env')

        # Check if key variables are loaded
        required_vars = ['GEMINI_API_KEY', 'LAYER_APPLICATION_ID']
        loaded_vars = []
        for var in required_vars:
            if os.getenv(var):
                loaded_vars.append(var)
                masked_value = f"{os.getenv(var)[:8]}...{os.getenv(var)[-4:]}" if len(os.getenv(var)) > 12 else "****"
                print(f"✅ Loaded {var}: {masked_value}")

        if loaded_vars:
            print(f"✅ Successfully loaded {len(loaded_vars)} variables from .env")
            return

    # Fallback to secrets.json
    try:
        print("📄 Loading credentials from secrets.json...")
        with open('secrets.json', 'r') as f:
            secrets = json.load(f)

        for key, value in secrets.items():
            if value:  # Only set non-empty values
                os.environ[key] = str(value)
                masked_value = f"{str(value)[:8]}...{str(value)[-4:]}" if len(str(value)) > 12 else "****"
                print(f"✅ Loaded {key}: {masked_value}")

    except FileNotFoundError:
        print("❌ Neither .env nor secrets.json found!")
        print("💡 Copy .env.example to .env or secrets.json.example to secrets.json")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error loading secrets: {e}")
        sys.exit(1)

def start_litellm_simple():
    """Start LiteLLM with existing config"""
    print("🚀 Starting LiteLLM...")
    
    # Check if config exists
    if not os.path.exists('config.yaml'):
        print("❌ config.yaml not found!")
        sys.exit(1)
    
    cmd = [
        "litellm",
        "--config", "config.yaml",
        "--port", "4000"
    ]
    
    print(f"🔧 Command: {' '.join(cmd)}")
    
    try:
        # Start LiteLLM and let it run in foreground
        print("📡 Starting LiteLLM...")
        print("💡 Environment variables will be passed to subprocess")
        print("⏳ This will run in foreground - press Ctrl+C to stop")
        print("📍 Once started, proxy will be at: http://localhost:4000")
        print("🔑 Master key: sk-1234")
        print("-" * 50)
        
        # Pass the current environment (which includes loaded secrets)
        subprocess.run(cmd, check=True, env=os.environ.copy())
        
    except KeyboardInterrupt:
        print("\n👋 Stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ LiteLLM failed: {e}")
    except FileNotFoundError:
        print("❌ litellm command not found!")
        print("Install with: pip install 'litellm[proxy]'")

def main():
    print("🚀 LiteLLM Startup")
    print("=" * 30)
    
    # Load secrets
    load_secrets()
    
    print("\n💡 Using existing config.yaml")
    
    # Start LiteLLM
    start_litellm_simple()

if __name__ == "__main__":
    main()