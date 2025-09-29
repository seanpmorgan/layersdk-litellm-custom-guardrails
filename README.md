# Quickstart: LiteLLM + Layer SDK guardrail

Follow these steps to run the example guardrail and walk through the notebook integration.

1) Load secrets

If you keep secrets in the repository helper, source the helper script before starting. From the repo root run:

```zsh
source litellm-protectai-layersdk/load_secrets.sh
```

This script should export any required environment variables (for example `LAYER_OIDC_CLIENT_SECRET`). If you prefer, set environment variables manually instead of using the helper script.

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

