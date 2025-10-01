# Security Guidelines

## Overview

This document outlines the security measures implemented in this repository to protect sensitive information such as API keys, secrets, and credentials.

## Files Protected by .gitignore

### Sensitive Files (Never Committed)
- `.env` - Environment variables with actual secrets
- `secrets.json` - JSON file containing API keys and secrets
- `*.key`, `*.pem` - Private keys and certificates
- `credentials.json`, `auth.json` - Authentication files
- `__pycache__/` - Python bytecode files
- `.DS_Store` - macOS system files

### Template Files (Safe to Commit)
- `.env.example` - Template for environment variables
- `secrets.json.example` - Template for secrets configuration

## Security Best Practices

### 1. Never Commit Secrets
- All actual API keys, tokens, and secrets are automatically ignored by `.gitignore`
- Use template files (`.example` suffix) to document required configuration
- Copy template files and remove the `.example` suffix for local development

### 2. Environment Variable Management
Choose one of these methods for managing secrets:

**Method A: .env file (Recommended for development)**
```bash
cp litellm-protectai-layersdk/.env.example litellm-protectai-layersdk/.env
# Edit .env with your actual values
```

**Method B: secrets.json file**
```bash
cp litellm-protectai-layersdk/secrets.json.example litellm-protectai-layersdk/secrets.json
# Edit secrets.json with your actual values
```

**Method C: System environment variables (Recommended for production)**
```bash
export GEMINI_API_KEY="your_actual_key"
export LAYER_OIDC_CLIENT_SECRET="your_actual_secret"
```

### 3. Production Security
- Change default master key (`sk-1234`) in `config.yaml`
- Use strong, randomly generated keys
- Rotate API keys and secrets regularly
- Use environment variables instead of files in production
- Enable proper access controls and monitoring

### 4. Development Security
- Never share your actual `.env` or `secrets.json` files
- Use separate API keys for development and production
- Regularly audit and rotate development keys
- Be cautious when sharing screen recordings or logs

## Files Requiring Security Review

The following files contain configuration that may need security attention:

1. `litellm-protectai-layersdk/config.yaml` - Contains master key configuration
2. `litellm-protectai-layersdk/load_secrets.sh` - Script that loads secrets
3. `litellm-protectai-layersdk/start.py` - Application startup script

## Security Audit Checklist

- [ ] All sensitive files are listed in `.gitignore`
- [ ] Template files are provided for all configuration
- [ ] No hardcoded secrets in tracked files
- [ ] Production uses environment variables
- [ ] Default passwords/keys are changed
- [ ] API keys are rotated regularly
- [ ] Access logs are monitored

## Incident Response

If sensitive information is accidentally committed:

1. **Immediately rotate** all exposed keys/secrets
2. Remove the sensitive data from git history using `git filter-branch` or BFG Repo-Cleaner
3. Force push the cleaned history
4. Notify team members to re-clone the repository
5. Review and update security practices

## Contact

For security concerns or questions, please contact the repository maintainers.
