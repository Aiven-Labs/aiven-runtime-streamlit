# Validation

Checked locally on 2026-09-17 using Python 3.12.14 and the pinned dependencies.

## Passed

- Six automated checks using Streamlit AppTest and unittest: missing-password fail-closed behavior, rejected login, successful login/logout, filters and empty selections, TLS/read-only query settings that cannot be overridden by URI options, sanitized database failures, and missing-CA rejection.
- `pip check`: no incompatible installed dependencies.
- Actual local server and browser session: form login, charts rendered, filter interaction updated row counts from 42 to 28, and table/CSV control rendered. This exercised Streamlit's WebSocket session as well as HTTP.
- The shared-password form works in the Codex in-app browser without a browser authentication dialog.

## Aiven Runtime validation — passed

Deployed commit `160ecabb21ef20c598f8a8dab3f72a911a27572f` from GitHub main using the root Dockerfile through Aiven MCP on 2026-09-17.

- Service `streamlit-demo`, project `cara-test`, cloud `aws-eu-west-1`, plan `startup-50-1024` (1 GiB RAM).
- Build status SUCCESS, deployment COMPLETED, service RUNNING. No application code changes were needed.
- Live HTTPS browser test: unauthenticated visitors see only the login form; incorrect passwords are rejected; correct login renders both charts and the table.
- Runtime WebSocket interaction: removing Gamma updates the displayed row count from 42 to 28 and series count from 3 to 2.
- CSV export: clicking Download CSV emitted a browser download event. Downloaded file contents were not inspected.
- Optional PostgreSQL tab correctly shows its unconfigured state; default deployment needs no database.
- Sign out returns to the login form and removes the sample content.
- Public `/_stcore/health` responds HTTP 200 with `ok`. Recent runtime logs show successful startup with no application errors.
- Service remains running at the observed plan price of $0.03836/hour (approximately $0.92/day), excluding other project services.

## Still to validate

- Local Docker Compose execution: no local Docker engine is available. The Linux image build passed on Runtime.
- Load testing and memory sizing beyond this small single-user test.
- Live optional Aiven PostgreSQL connection and TLS query: not run yet. No database was created for this starter.
- Downloaded CSV contents: browser download event observed; file contents not inspected.
- Console discovery of either Runtime Compose manifest.

No production suitability, high availability, multi-replica behavior, or load testing is claimed. No existing Temporal services were changed or deleted during validation.
