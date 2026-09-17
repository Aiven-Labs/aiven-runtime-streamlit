"""Replace these examples with your own data and queries."""
import base64
import os
import random
import ssl
import tempfile
from datetime import date, timedelta

import pandas as pd
import psycopg
from psycopg.conninfo import conninfo_to_dict


def validate_password(password):
    if len(password) < 16:
        raise ValueError("Set APP_PASSWORD to a unique password of at least 16 characters.")


def sample_data():
    """Deterministic synthetic data: no customer information or remote downloads."""
    rng = random.Random(42)
    return pd.DataFrame([
        {"date": date(2026, 1, 1) + timedelta(days=day),
         "series": series, "value": round(rng.uniform(20, 100), 2)}
        for day in range(30) for series in ("Alpha", "Beta", "Gamma")
    ])


def connection_options(uri, ca_path):
    # Ignore URI options: callers cannot weaken TLS or override our query timeout.
    parsed = conninfo_to_dict(uri)
    options = {key: parsed[key] for key in ("host", "port", "dbname", "user", "password") if key in parsed}
    if not options.get("host") or options["host"].startswith("/"):
        raise ValueError("DATABASE_URL must specify a PostgreSQL network hostname.")
    return dict(options, sslmode="verify-full", sslrootcert=ca_path,
                connect_timeout=5, options="-c default_transaction_read_only=on -c statement_timeout=5000")


def database_status():
    """Read-only example query over verified TLS; never initialize or mutate a database."""
    uri = os.environ.get("DATABASE_URL", "")
    encoded_ca = os.environ.get("PG_CA_CERT_BASE64", "")
    if not uri or not encoded_ca:
        raise ValueError("DATABASE_URL and PG_CA_CERT_BASE64 are both required.")
    certificate = base64.b64decode(encoded_ca, validate=True).decode("ascii")
    ssl.create_default_context(cadata=certificate)
    with tempfile.NamedTemporaryFile(mode="w", suffix=".pem") as ca:
        ca.write(certificate)
        ca.flush()
        with psycopg.connect(**connection_options(uri, ca.name)) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT current_database(), CURRENT_TIMESTAMP")
                name, timestamp = cursor.fetchone()
                cursor.execute("SELECT ssl FROM pg_stat_ssl WHERE pid = pg_backend_pid()")
                tls = cursor.fetchone()[0]
    return {"Database": name, "Database time (UTC)": str(timestamp), "TLS active": tls}
