# Validation

Checked locally on 2026-09-17 using Python 3.12.14 and the pinned dependencies.

## Passed

- Six automated checks using Streamlit AppTest and unittest: missing-password fail-closed behavior, rejected login, successful login/logout, filters and empty selections, TLS/read-only query settings that cannot be overridden by URI options, sanitized database failures, and missing-CA rejection.
- `pip check`: no incompatible installed dependencies.
- Actual local server and browser session: form login, charts rendered, filter interaction updated row counts from 42 to 28, and table/CSV control rendered. This exercised Streamlit's WebSocket session as well as HTTP.
- The shared-password form works in the Codex in-app browser without a browser authentication dialog.

## Still to validate

- Docker image build and Docker Compose execution: no local Docker engine is available.
- Aiven Runtime deployment, ingress WebSocket handling, and memory sizing: requires the user to commit and push the staged source first.
- Live optional Aiven PostgreSQL connection and TLS query: not run yet. No database was created for this starter.
- CSV download contents in a real browser: export control rendered; end-to-end download not yet checked.
- Console discovery of either Runtime Compose manifest.

No production suitability, high availability, multi-replica behavior, or load testing is claimed. No existing Temporal services were changed or deleted for these local checks.
