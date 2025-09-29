#!/bin/bash
echo "Loading secrets from secrets.json..."

# Read API key more carefully
export GEMINI_API_KEY=$(python3 -c "
import json
try:
    with open('secrets.json') as f:
        secrets = json.load(f)
    key = secrets.get('GEMINI_API_KEY', '')
    if key:
        print(key)
    else:
        print('ERROR: GEMINI_API_KEY not found in secrets.json', file=__import__('sys').stderr)
        exit(1)
except Exception as e:
    print(f'ERROR loading secrets: {e}', file=__import__('sys').stderr)
    exit(1)
")

if [ -z "$GEMINI_API_KEY" ]; then
    echo "ERROR: Failed to load GEMINI_API_KEY"
    exit 1
fi

echo "GEMINI_API_KEY loaded (length: ${#GEMINI_API_KEY})"

# Load other variables
export LAYER_APPLICATION_ID="42b1a5ce-584e-4c22-ba4d-080134599acc"
export LAYER_OIDC_CLIENT_ID="demo02/layer-sdk"
export LAYER_OIDC_CLIENT_SECRET=$(python3 -c "
import json
with open('secrets.json') as f:
    secrets = json.load(f)
print(secrets.get('LAYER_DEMO2_AUTH_CLIENT_SECRET', ''))
")
export LAYER_BASE_URL="https://layer.demo02.protectai.cloud/"
export LAYER_ENVIRONMENT="demo02"
export LAYER_OIDC_TOKEN_URL="https://auth.protectai.cloud/realms/demo02/protocol/openid-connect/token"
export LAYER_FIREWALL_BASE_URL="https://layer-firewall.demo02.protectai.cloud"
echo "All environment variables loaded successfully"