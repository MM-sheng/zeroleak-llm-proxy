# Repository Map

This repository currently contains two different project lines on separate branches.

GitHub repository:

```text
https://github.com/MM-sheng/zeroleak-llm-proxy
```

## Branches

| Branch | Project | Status | Notes |
|---|---|---|---|
| `main` | ZeroLeak LLM Proxy | Public MVP | Default branch. Keep this branch focused on the privacy proxy. |
| `btc-pm-strategy` | BTC Polymarket research system | Paper-only research branch | Separate project uploaded here temporarily. Should move to its own repo if it continues. |

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

## Secondary Branch: BTC Polymarket Research

The `btc-pm-strategy` branch is not part of the ZeroLeak product. It contains a
paper-only BTC/Polymarket strategy research system with backtests, reports, and
governance files.

Branch URL:

```text
https://github.com/MM-sheng/zeroleak-llm-proxy/tree/btc-pm-strategy
```

Recommended future cleanup:

1. Create a dedicated repository, for example `MM-sheng/btc-pm-strategy`.
2. Push the `btc-pm-strategy` branch contents there as `main`.
3. Keep this repository's `main` branch only for ZeroLeak.
4. Delete or archive the temporary BTC branch only after confirming the new repo is complete.

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

