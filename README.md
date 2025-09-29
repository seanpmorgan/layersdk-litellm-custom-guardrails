# Quickstart: LiteLLM + Layer SDK guardrail

🚀 A quickstart integration between LiteLLM and Layer SDK that provides comprehensive AI safety guardrails, real-time monitoring, and session tracking for any LLM provider.
Follow these steps to run the example guardrail and walk through the notebook integration.

## Prerequisites

* Python 3.9+
* Layer SDK account and API credentials
* LiteLLM proxy setup
* Model provider API keys (OpenAI, Anthropic, etc.)

## Steps

1) CLone the repository

```zsh
git clone https://github.com/protectai/layersdk-litellm-custom-guardrails.git
```

2) Create a virtual environment and install dependencies

```zsh
python3 -m venv litellm-layer-env
source litellm-layer-env/bin/activate
pip install -r litellm-protectai-layersdk/requirements.txt
```

3) Configure Layer SDK credentials
You'll need these values from your Layer account:

* LAYER_APPLICATION_ID: Your Layer application ID
* LAYER_BASE_URL: Your Layer instance URL
* LAYER_OIDC_CLIENT_ID: OIDC client identifier
* LAYER_OIDC_CLIENT_SECRET: OIDC client secret (stored in secrets.json)

4) Update & Load secrets
Update secrets.json with your API keys:

```json
{
  "GEMINI_API_KEY": "your_gemini_api_key_here",
  "OPENAI_API_KEY": "your_openai_api_key_here", 
  "LAYER_DEMO2_AUTH_CLIENT_SECRET": "your_layer_client_secret_here"
}
```

If you keep secrets in the repository helper, source the helper script before starting. From the repo root run:

```zsh
source litellm-protectai-layersdk/load_secrets.sh
```

This script should export any required environment variables (for example `LAYER_OIDC_CLIENT_SECRET`). If you prefer, set environment variables manually instead of using the helper script.

5) LiteLLM configuration (config.yaml)
```yaml
model_list:
  - model_name: gemini-2-flash
    litellm_params:
      model: gemini/gemini-2.0-flash-exp
      api_key: env/GEMINI_API_KEY

  - model_name: gpt-4
    litellm_params:
      model: openai/gpt-4o
      api_key: env/OPENAI_API_KEY

# Single guardrail entry for both pre and post call hooks  
guardrails:
  - guardrail_name: "layer-tracking"
    litellm_params:
      guardrail: layer_guardrail.myCustomGuardrail
      mode: "pre_call,post_call"

general_settings:
  master_key: sk-1234
  
litellm_settings:
  drop_params: true
  set_verbose: true


2) Start the example application

From the repo root run the example runner:

```zsh
python litellm-protectai-layersdk/start.py
```

The runner uses the local virtual environment in `litellm-layer-env` if you activate it, but you can run with any Python environment that has the project's dependencies installed.

3) Ensure LiteLLM is listening on localhost:4000

The example integration expects LiteLLM to be available at `http://localhost:4000`.
Check that the service is up with a quick request:

```zsh
curl -sSf http://localhost:4000/ || echo "LiteLLM not responding on localhost:4000"
```

If LiteLLM is not running locally, start it according to your LiteLLM setup. This repository assumes you already have LiteLLM configured; `start.py` will integrate with it.

4) Open and follow the notebook

Open the notebook `litellm-protectai-layersdk/layer_integration.ipynb` in Jupyter or VS Code and follow the cells step-by-step. The notebook demonstrates example requests, how the guardrail attaches sessions, and how to exercise the permission gate.

Quick notes and tips
- Permission gate: the guardrail will only call Layer APIs when a sync permission is present. You can grant permission in one of three ways:
  - Set `LAYER_ALLOW_SYNC=1` (env) to allow syncing for all requests (useful for testing).
  - Provide `permissions` or `scopes` on the `user_api_key_dict` that include `sync` or `augment`.
  - Add a metadata header on a request: `x-allow-sync: true`.

- If you used `load_secrets.sh` it should have exported necessary OIDC secrets; otherwise set `LAYER_OIDC_CLIENT_SECRET` and related env vars manually.

- To debug, watch the stdout printed by `start.py` and `layer_guardrail.py` — the guardrail prints diagnostic messages about initialization, permission checks, and firewall decisions.

Where to look in the code
- `litellm-protectai-layersdk/layer_guardrail.py` — main guardrail implementation; exported as `myCustomGuardrail`.
- `litellm-protectai-layersdk/start.py` — example runner that integrates the guardrail.
- `litellm-protectai-layersdk/layer_integration.ipynb` — walkthrough notebook to exercise the integration.

