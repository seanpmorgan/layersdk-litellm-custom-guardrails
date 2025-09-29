#!/usr/bin/env python3
import json
import os
import subprocess
import sys
import time

def load_secrets():
    """Load secrets from secrets.json into environment variables"""
    try:
        with open('secrets.json', 'r') as f:
            secrets = json.load(f)
        
        for key, value in secrets.items():
            os.environ[key] = str(value)
            masked_value = f"{str(value)[:8]}...{str(value)[-4:]}" if len(str(value)) > 12 else "****"
            print(f"✅ Loaded {key}: {masked_value}")
            
    except FileNotFoundError:
        print("❌ secrets.json not found!")
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