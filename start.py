"""Validate demo authentication before starting the web server."""
import os
import sys

from starter import validate_password

if __name__ == "__main__":
    try:
        validate_password(os.environ.get("APP_PASSWORD", ""))
    except ValueError as exc:
        sys.exit(str(exc))
    os.execv(sys.executable, [sys.executable, "-m", "streamlit", "run", "app.py"])
