# Streamlit starter for Aiven Runtime

A generic starting point for a Streamlit app: synthetic sample charts, filters, a searchable table, CSV export, and optional Aiven PostgreSQL connectivity. Replace the examples with your own use case.

Uses Streamlit **1.64.0**, Python **3.12.14**, pandas **3.0.5**, and Psycopg **3.3.5**. Direct dependencies are pinned; transitive dependencies are resolved during installation.

## How it works

```text
Browser --HTTPS / WebSocket--> Aiven Runtime ingress --> :8080 Streamlit
                                                              |
                                                   optional verified TLS
                                                              |
                                                      Aiven PostgreSQL
```

One non-root container, one HTTP port, no persistent application disk required. A password form inside the app guards the sample content and database query. You do not need a username or browser Basic authentication prompt.

The default mode needs **only Runtime**. The PostgreSQL example runs a read-only query for the database name, time, and TLS status. Sample charts remain synthetic in both modes; they are not loaded from PostgreSQL. This starter does not create tables, seed data, or store edits.

## Run locally

With Docker Compose v2:

1. Copy `.env.example` to `.env` and set `APP_PASSWORD` to a unique password of at least 16 characters.
2. Run `docker compose up --build -d`.
3. Open <http://localhost:8080> and enter your password.
4. Stop with `docker compose down`.

Or use Python 3.12:

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Set `APP_PASSWORD` in your environment, then run `python start.py`. The Python command does **not** load `.env` automatically. To limit the direct Python server to your own machine, also set `STREAMLIT_SERVER_ADDRESS=127.0.0.1`.

## Deploy on Aiven Runtime

1. Review, commit, and push the repository to GitHub. Runtime builds from the selected remote branch, so staged local files cannot be deployed yet.
2. In your Aiven project, select **Runtime > Deploy application**, choose the repository and branch, and scan **compose.aiven.yaml**. You can also deploy the root **Dockerfile** through Aiven MCP/API.
3. Choose one replica, your region, and a suitable Runtime plan. Start around 1 GiB RAM for the small example and monitor actual usage; this is an estimate, not a tested minimum. Check available free/internal plans and displayed costs before creating resources.
4. Set **APP_PASSWORD** as a Runtime secret/environment variable before deployment. Never put it in Git. An absent or short password causes startup to fail closed.
5. Publish **HTTP port 8080** and open the generated HTTPS URL. Runtime handles public TLS. Streamlit also requires WebSocket traffic on the same port for interaction.
6. Sign in, change a filter, inspect the table, and download a CSV. A successful HTML response alone does not verify Streamlit's WebSocket session.

Keep Streamlit's CORS and XSRF protections enabled. If deploying under a custom hostname causes an origin error, configure `STREAMLIT_BROWSER_SERVER_ADDRESS` to that hostname and verify proxy/WebSocket settings rather than disabling protections.

## Optional Aiven PostgreSQL

Use **compose.aiven-postgres.yaml** instead of the sample-only manifest to request a managed PostgreSQL integration, or connect an existing service through Runtime. Review the detected service and plan before creating it. The database image in the manifest is a discovery hint, not a local database running inside the Runtime container.

Map the integration's PostgreSQL connection URI to `DATABASE_URL`. Supply the project's CA certificate encoded as one line:

```sh
openssl base64 -A -in ca.pem
```

Store that output in `PG_CA_CERT_BASE64`. Aiven Runtime environment values cannot contain literal newlines; base64 transports the PEM certificate without weakening TLS verification.

| Variable | Purpose |
| --- | --- |
| `APP_PASSWORD` | Required shared demo password, at least 16 characters |
| `DATABASE_URL` | Optional PostgreSQL URI, with URL-encoded credentials and the actual Aiven port |
| `PG_CA_CERT_BASE64` | Required when testing PostgreSQL; base64 project CA certificate |

Open the **PostgreSQL** tab and select **Test connection**. The server verifies both the certificate and hostname, enforces a five-second connection/query timeout, and opens read-only transactions. URI options cannot disable these protections. Failures show a generic message without exposing driver errors or connection credentials.

Use an account with only the permissions your app needs. Keep database credentials and CA files outside Git. Connecting to PostgreSQL is optional and no database resources need to be created for the default demo.

## Make it yours

- `app.py`: page layout, login form, widgets, charts, and table.
- `starter.py`: sample data and the read-only database query. Replace these functions with your own data source.
- `.streamlit/config.toml`: theme and server settings.
- `requirements.txt`: add and pin the packages your app requires.

Keep private data access below the authentication guard. For a real application, replace the shared demo password with Streamlit OIDC or your organization's authentication and authorization. The demo has no per-user roles, persistent login, or brute-force rate limiting. Health and static UI resources are public; the Python content is gated per WebSocket session. Reloading starts a new session and may require signing in again.

Use one replica initially. Multiple replicas need an explicit session-affinity strategy for Streamlit WebSockets and media/download requests. Session state and generated files are ephemeral; use a managed database/object store for durable data. Never rely on container disk or in-memory state for persistence.

## Validation

```sh
python -m unittest discover -s tests -v
```

See [VALIDATION.md](VALIDATION.md) for completed checks and outstanding deployment tests. The Docker health check requests `/_stcore/health`; Runtime's OCI builder may ignore Dockerfile HEALTHCHECK, so also check deployment status and an actual browser session.

## References

- [Aiven Runtime deployment](https://aiven.io/docs/products/runtime/deploy-apps)
- [Aiven Runtime Compose manifests](https://aiven.io/docs/products/runtime/manifest-files/compose-files)
- [Streamlit Docker deployment](https://docs.streamlit.io/deploy/tutorials/docker)
- [Streamlit configuration](https://docs.streamlit.io/develop/api-reference/configuration/config.toml)
