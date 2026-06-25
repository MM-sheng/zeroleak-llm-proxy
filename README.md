# ZeroLeak LLM Proxy

OpenAI-compatible privacy proxy for LLM API calls. It redacts secrets and personal data before prompts leave your machine, forwards the sanitized request to a model provider, then restores placeholders in the response.

This project is an MVP for developers who want to use cloud LLM APIs without accidentally sending API keys, tokens, emails, phone numbers, database URLs, or private keys to the model provider.

## Repository Map

This GitHub repository currently has two separate project lines:

| Branch | Project | Purpose |
|---|---|---|
| `main` | ZeroLeak LLM Proxy | OpenAI-compatible privacy/redaction proxy for LLM API calls |
| `btc-pm-strategy` | BTC Polymarket research system | Paper-only BTC/Polymarket research, backtesting, and reports |

The default branch is `main`, and this README describes ZeroLeak only. See
`REPOSITORY.md` for the full repository-level map and branch cleanup notes.

## What It Does

- Accepts OpenAI-compatible `POST /v1/chat/completions` requests.
- Redacts sensitive values in `messages`, `tools`, and common string fields.
- Forwards the sanitized request to an OpenAI-compatible upstream API.
- Restores placeholders in the model response before returning it.
- Avoids writing prompts or responses to disk.
- Includes a local CLI redaction demo.

## Why

Developers increasingly paste source code, logs, `.env` files, stack traces, and customer data into AI tools. A small proxy layer can reduce accidental leakage while keeping the normal OpenAI API workflow.

This is not a replacement for confidential computing or true encrypted inference. The goal is narrower and immediately useful:

> Prevent sensitive strings from being sent to third-party LLM providers.

## Quick Start

```bash
npm test
cp .env.example .env
npm start
```

In another terminal:

```bash
curl http://localhost:8787/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer local-dev-key" \
  -d '{
    "model": "gpt-4o-mini",
    "messages": [
      {
        "role": "user",
        "content": "Review this config: OPENAI_API_KEY=sk-proj-example123 and email me at alice@example.com"
      }
    ]
  }'
```

## Environment

```bash
UPSTREAM_API_KEY=your_provider_key
UPSTREAM_BASE_URL=https://api.openai.com
PORT=8787
```

Any OpenAI-compatible provider can be used by changing `UPSTREAM_BASE_URL`.

## CLI Demo

```bash
npm run redact -- "Email alice@example.com and use token sk-proj-secret123"
```

Example output:

```json
{
  "redacted": "Email [EMAIL_1] and use token [OPENAI_KEY_1]",
  "replacements": {
    "[EMAIL_1]": "alice@example.com",
    "[OPENAI_KEY_1]": "sk-proj-secret123"
  }
}
```

## API Compatibility

Implemented:

- `POST /v1/chat/completions`
- `GET /health`

Not implemented yet:

- Streaming responses
- Embeddings
- Image/audio endpoints
- User/team policy engine
- Browser or IDE integrations

## Security Model

This MVP protects against accidental disclosure to the upstream LLM provider.

It does not claim:

- End-to-end encrypted inference.
- Protection from a malicious local machine.
- Protection from a malicious proxy operator if deployed remotely.
- Perfect detection of every sensitive value.

For the strongest privacy posture, run the proxy locally or inside infrastructure you control.

## Roadmap

- Streaming support.
- Python and TypeScript SDKs.
- VS Code extension.
- Team policy file.
- Risk scoring per request.
- Audit logs with hashes only.
- Optional TEE-backed worker integration.

## License

MIT
