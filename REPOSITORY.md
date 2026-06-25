# Repository Map

This repository is the canonical home for ZeroLeak LLM Proxy.

GitHub repository:

```text
https://github.com/MM-sheng/zeroleak-llm-proxy
```

## Current Branches

| Branch | Project | Status | Notes |
|---|---|---|---|
| `main` | ZeroLeak LLM Proxy | Public MVP | Default branch. Keep this branch focused on the privacy proxy. |
| `btc-pm-strategy` | BTC Polymarket research system | Migrated | Historical temporary branch. Canonical repo is now `MM-sheng/btc-pm-strategy`. |

## Main Project: ZeroLeak LLM Proxy

ZeroLeak is an OpenAI-compatible privacy proxy. It accepts normal
`/v1/chat/completions` requests, redacts sensitive strings before forwarding the
request to an upstream OpenAI-compatible provider, then restores placeholders in
the response.

Current MVP includes:

- `POST /v1/chat/completions`
- `GET /health`
- local CLI redaction demo
- tests for redaction and restore behavior

Sensitive strings currently detected include:

- private keys
- OpenAI API keys
- AWS access keys
- JWTs
- database URLs
- emails
- phone numbers
- US SSNs
- China ID numbers

## Migrated Project: BTC Polymarket Research

The BTC/Polymarket strategy research system is not part of the ZeroLeak product.
It has been moved to a dedicated repository:

Canonical repository:

```text
https://github.com/MM-sheng/btc-pm-strategy
```

The old `btc-pm-strategy` branch in this repository should be treated as a
historical migration source only. Do not continue development there.

Recommended future cleanup:

1. Confirm `https://github.com/MM-sheng/btc-pm-strategy` has all expected files.
2. Update any bookmarks or Codex references to the dedicated repository.
3. Delete the temporary `btc-pm-strategy` branch from this repository only after
   confirming no active workflow depends on it.

## Local History

ZeroLeak was created locally on this machine under:

```text
/Users/m/Documents/Codex/2026-06-03/api-2
```

The initial local Git commit is:

```text
8e91ec5 Initial open source MVP
```

The GitHub repository was created on 2026-06-04.

## Maintenance Rules

- Do not mix trading research files into `main`.
- Do not add secrets, `.env`, API keys, or local publish scripts.
- Keep ZeroLeak docs and code focused on privacy proxy behavior.
- Add tests when changing redaction patterns, restore behavior, or API handling.
- Run `npm test` before pushing changes to `main`.
