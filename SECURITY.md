# Security

## Scope

This is a **portfolio demonstration project**. It is not a production system and
should not be deployed as one without adding real authentication, input limits,
and hardened provider integrations.

## What this repo deliberately does not contain

- No credentials, API keys, tokens, cookies, or `.env` files with real values.
- No real supplier, customer, employee, or pricing data.
- No production URLs, hostnames, internal IPs, or database connection strings.
- No proprietary business logic — supplier parsing rules and pricing are
  simplified, illustrative examples on invented data.

All external integrations (LLM, image generation, object storage, shop API) are
mock implementations that make no network calls. The application runs fully
offline with no configuration.

## Reporting

If you believe you have found sensitive information that was published by
mistake, or a security issue in the demo code, please open a GitHub issue
without including the sensitive value itself, or contact the repository owner
directly.

## Notes for anyone extending this

- The sample `SessionAuth` pattern is not wired in and is not a substitute for a
  real auth layer.
- Uploads are capped at 5 MB and restricted by the adapter parsers, but there is
  no malware scanning or sandboxing.
- CORS defaults to `http://localhost:5173` only.
