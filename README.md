# LiteLLM + Layer SDK Integration

🚀 A production-ready integration between LiteLLM and Layer SDK that provides comprehensive AI safety guardrails, real-time monitoring, and session tracking for any LLM provider.

## Features

- **AI Safety Guardrails**: Pre and post-call monitoring with Layer SDK
- **Session Tracking**: Automatic conversation grouping and context management
- **Multi-Provider Support**: Works with OpenAI, Anthropic, Google, and other LLM providers (has only been tested with Google Gemini Flash 2.0
- **Security First**: Secure credential management with template files
- **Easy Setup**: Simple configuration with environment variables or JSON

## Prerequisites

- Python 3.9+
- Layer SDK account and API credentials
- Model provider API keys (OpenAI, Google Gemini, etc.)

## Quick Start

### 1. Clone and Setup

```bash
git clone https://github.com/protectai/layersdk-litellm-custom-guardrails.git
cd layersdk-litellm-custom-guardrails

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r litellm-protectai-layersdk/requirements.txt
```

### 2. Configure Credentials

**⚠️ SECURITY**: Never commit actual API keys to version control!

**Environment File (Recommended)**
```bash
cp litellm-protectai-layersdk/.env.example litellm-protectai-layersdk/.env
# Edit .env with your actual credentials
```

#### Required Credentials

Get these from your respective accounts:
- **GEMINI_API_KEY**: From [Google AI Studio](https://aistudio.google.com/app/apikey)
- **LAYER_APPLICATION_ID**: From your Layer dashboard
- **LAYER_OIDC_CLIENT_SECRET**: From your Layer OIDC configuration
- **LAYER_BASE_URL**: Your Layer instance URL
- **LAYER_FIREWALL_URL**: Your Layer instance URL

### 3. Start LiteLLM with Layer Integration

```bash
cd litellm-protectai-layersdk
python start.py
```

This will:
- Load your credentials from `.env`
- Start LiteLLM proxy on `http://localhost:4000`
- Enable Layer SDK guardrails for all requests

### 4. Test the Integration

Check that the service is running:
```bash
curl -sSf http://localhost:4000/health || echo "LiteLLM not responding"
```

### 5. Explore with Jupyter Notebook

Open `litellm-protectai-layersdk/layer_integration.ipynb` to see:
- Example API requests with guardrails
- Session tracking demonstrations
- Permission gate configuration
- Real-time monitoring examples

## Configuration

### LiteLLM Config (`config.yaml`)

The integration uses a pre-configured LiteLLM setup with:

```yaml
model_list:
  - model_name: gemini-2-flash
    litellm_params:
      model: gemini/gemini-2.0-flash-exp
      api_key: "os.environ//GEMINI_API_KEY"

guardrails:
  - guardrail_name: "layer-pre-guard"
    litellm_params:
      guardrail: layer_guardrail.myCustomGuardrail
      mode: "pre_call,post_call"

general_settings:
  master_key: sk-1234  # Change this for production!
```

### Layer SDK Configuration

The guardrail automatically configures Layer SDK with:
- Session tracking for conversation grouping
- Pre-call and post-call monitoring
- Firewall integration for content filtering
- Permission-based API access control

## Permission Control

The guardrail includes a permission gate that controls when Layer APIs are called. Grant permissions using any of these methods:

1. **Environment Variable** (for testing):
   ```bash
   export LAYER_ALLOW_SYNC=1
   ```

2. **API Key Permissions**: Include `sync` or `augment` in the `user_api_key_dict` permissions

3. **Request Header**:
   ```bash
   curl -H "x-allow-sync: true" http://localhost:4000/v1/chat/completions
   ```

## Project Structure

```
litellm-protectai-layersdk/
├── layer_guardrail.py          # Main guardrail implementation
├── start.py                    # Application launcher
├── config.yaml                 # LiteLLM configuration
├── requirements.txt            # Python dependencies
├── layer_integration.ipynb     # Interactive examples
├── .env.example               # Environment template
└── secrets.json.example       # JSON credentials template
```

## Security

🔒 **Security Features:**
- All sensitive files automatically ignored by `.gitignore`
- Template files provided for safe credential management
- No hardcoded secrets in tracked files
- Production-ready environment variable support

See [SECURITY.md](SECURITY.md) for detailed security guidelines.

## Troubleshooting

**LiteLLM not starting?**
- Check that all required credentials are set
- Verify API keys are valid
- Ensure port 4000 is available

**Layer SDK connection issues?**
- Verify `LAYER_BASE_URL` and `LAYER_APPLICATION_ID`
- Check OIDC credentials are correct
- Enable debug logging with `LAYER_ALLOW_SYNC=1`

**Permission denied errors?**
- Set `LAYER_ALLOW_SYNC=1` for testing
- Add `x-allow-sync: true` header to requests
- Check API key permissions include `sync` scope

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

See [LICENSE](LICENSE) for details.

