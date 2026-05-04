<div align="center">
  <img src="docs/cover.png" alt="Prospect Audit" width="100%">
  <p><strong>Offline checks for saved website evidence and phone-line intelligence.</strong></p>
  <p>
    <a href="#why-prospect-audit">Why</a> ·
    <a href="#how-it-works">How it works</a> ·
    <a href="#quick-start">Quick start</a> ·
    <a href="#verification">Verification</a> ·
    <a href="#project-boundaries">Boundaries</a>
  </p>
  <p>
    <img alt="Status: pre-1.0" src="https://img.shields.io/badge/status-pre--1.0-64748b">
    <img alt="Python 3.11 or newer" src="https://img.shields.io/badge/python-3.11%2B-3776AB">
    <img alt="Runtime: standard library" src="https://img.shields.io/badge/runtime-standard_library-475569">
    <img alt="License: MIT" src="https://img.shields.io/badge/license-MIT-16a34a">
  </p>
</div>

Prospect Audit turns data you already hold into small, reviewable observations. It inspects saved HTML, interprets supplied phone-line intelligence, and emits structured JSON suitable for a qualification pipeline or a human review queue.

The package is deliberately offline at the command line. It does not crawl websites, call a phone provider, store a lead list, or decide whether a prospect should be contacted. Network access, provider cost, authorization, and retention remain with the calling application.

## Why Prospect Audit

Prospect research often mixes collection, analysis, sales judgment, and personal data in one script. That makes results difficult to reproduce and gives a local utility more authority than it should have.

Prospect Audit separates those concerns. A collector may save an HTML response or a provider payload; this package then evaluates that supplied evidence without changing it. The result records what was observed and preserves uncertainty where the evidence cannot support a stronger conclusion.

Use it when you need repeatable local checks before a broader workflow decides what to do next.

## How it works

| Stage | Input | Output | Deliberate limit |
| --- | --- | --- | --- |
| HTML inspection | Saved HTML plus caller-supplied URL, status, and timing | Title, viewport, phone pattern, visible-text count, findings, verdict, and score | No fetch, browser rendering, or JavaScript execution |
| Line classification | E.164 number plus a saved provider response | Normalized line type, status, carrier, and textability hint | No provider call or deliverability claim |
| Row enrichment | Rows plus a caller-owned lookup function | Copies of rows with normalized classification fields | No mutation of input rows or campaign routing |
| URL validation | Public HTTP or HTTPS URL | Normalized URL or a typed rejection | No connection is opened |

The HTML score is a compact review aid. It starts from observable characteristics such as HTTPS, viewport metadata, page title, visible text, a phone pattern, and caller-supplied response time. Placeholder and error responses are reported separately. The score is not a conversion estimate or a judgment about the business.

Phone results follow the same rule. `yes`, `likely`, `no`, and `unknown` describe the supplied line-type response; they do not establish ownership, current reachability, consent, or permission to send a message.

## Implemented capabilities

- Offline HTML inspection with bounded, machine-readable findings.
- Placeholder and parked-page marker detection.
- E.164 normalization with an explicit international prefix requirement.
- Provider-neutral line-type and carrier normalization.
- Conservative textability hints that preserve unknown states.
- Batch row enrichment through a dependency supplied by the caller.
- Public-address validation for applications preparing to build their own network client.
- JSON command output for scripting and review pipelines.
- Synthetic fixtures and tests with no live prospect data.

## Quick start

Prospect Audit requires Python 3.11 or newer and has no runtime dependencies outside the standard library.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install .

prospect-audit html tests/fixtures/sample_site.html \
  --url https://example.test/ \
  --status 200 \
  --elapsed-ms 120

prospect-audit line +12025550123 tests/fixtures/mobile_line.json
```

The HTML command reads the local file. URL, status, and elapsed time are request metadata supplied by the caller. The line command expects a local JSON object containing `line_type_intelligence`.

## Practical usage

The public API has three focused entry points and one network-safety helper:

| Entry point | Use |
| --- | --- |
| `analyse_html` | Produce a `SiteObservation` from one saved HTML response |
| `classify_provider_payload` | Convert one provider payload into a small, provider-neutral result |
| `enrich_rows` | Apply a caller-owned lookup function across a collection without mutating it |
| `validate_public_url` | Reject unsafe or non-public destinations before a separate client is built |

For a pipeline, keep collection and analysis as separate steps. Save the response and its request metadata, run the local inspection, retain the structured result, and let a later policy layer decide whether further review is justified. That boundary makes test fixtures useful and keeps network behavior visible.

Detailed field meanings, score bands, and uncertainty semantics are documented in [Output semantics](docs/OUTPUTS.md).

## Verification

```bash
python -m unittest discover -s tests -v
python -m compileall -q src tests
prospect-audit html tests/fixtures/sample_site.html --elapsed-ms 120
```

The test suite covers command output, observable HTML signals, placeholder handling, E.164 normalization, provider-response classification, non-mutating row enrichment, and URL rejection for private, local, mixed, credentialed, or non-HTTP destinations. The repository CI installs the package on Python 3.12, runs the suite, and exercises the HTML command.

## Repository map

| Path | Responsibility |
| --- | --- |
| `src/prospect_audit/site_health.py` | HTML observations, score construction, and public URL validation |
| `src/prospect_audit/line_type.py` | Phone normalization, payload classification, and row enrichment |
| `src/prospect_audit/cli.py` | Offline command-line interface and JSON serialization |
| `tests/` | Unit tests and synthetic fixtures |
| `docs/OUTPUTS.md` | Stable interpretation of output fields and score bands |

## Project boundaries

Prospect Audit does not fetch a page, follow redirects, execute JavaScript, inspect layout, test a booking flow, confirm a business identity, or recommend a sales action. A page that passes its checks can still be outdated or unusable; a page that scores poorly may still serve its owner well.

`validate_public_url` resolves and rejects non-global addresses, but it is not a network client and does not prevent DNS rebinding after validation. A caller adding network access must pin validated addresses, re-check redirects, enforce timeouts and response limits, and apply its own authorization policy.

Use only data you are authorized to process. Keep provider credentials, raw lead lists, and personal information out of repositories, examples, and issue reports.

## Documentation and support

- [Output semantics](docs/OUTPUTS.md) — field meanings, score bands, and uncertainty.
- [Security](SECURITY.md) — trust boundaries and sensitive-data guidance.
- [Contributing](CONTRIBUTING.md) — local checks and contribution expectations.

This is a pre-1.0 utility. Interfaces may change while the output contract is refined.

## Contributing, security, and license

Changes should stay offline-first, preserve uncertainty, and include focused synthetic tests. Security reports should use a private repository advisory and must not include live contact data or provider credentials.

Prospect Audit is available under the [MIT License](LICENSE).
