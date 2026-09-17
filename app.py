"""Generic Streamlit starter for Aiven Runtime."""
import hmac
import os
from datetime import timedelta

import streamlit as st

from starter import database_status, sample_data, validate_password

st.set_page_config(page_title="Streamlit starter", page_icon="◈", layout="wide")

password = os.environ.get("APP_PASSWORD", "")
try:
    validate_password(password)
except ValueError as exc:
    st.error(str(exc))
    st.stop()

# Demo-only shared-password gate. Data and queries are below the guard.
if not st.session_state.get("authenticated", False):
    st.title("Streamlit starter")
    st.caption("Sign in to explore the demo.")
    with st.form("login"):
        entered = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Sign in")
    if submitted:
        if hmac.compare_digest(entered.encode(), password.encode()):
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Incorrect password.")
    st.stop()

with st.sidebar:
    st.header("Explore")
    selected = st.multiselect("Series", ["Alpha", "Beta", "Gamma"], default=["Alpha", "Beta", "Gamma"])
    days = st.slider("Days to display", 1, 30, 14)
    if st.button("Sign out"):
        st.session_state.clear()
        st.rerun()

st.title("Streamlit starter")
st.write("A small starting point for your next app. Explore sample data, try the controls, or connect PostgreSQL.")
st.caption("All chart and table values are synthetic. They reset when the app reruns.")

data = sample_data()
filtered = data[data["series"].isin(selected) & (data["date"] < data["date"].min() + timedelta(days=days))]
first, second, third = st.columns(3)
first.metric("Rows", len(filtered))
second.metric("Series", len(selected))
third.metric("Average value", f"{filtered['value'].mean():.1f}" if not filtered.empty else "—")

charts, table, database = st.tabs(["Charts", "Table", "PostgreSQL"])
with charts:
    if filtered.empty:
        st.info("Select at least one series to display a chart.")
    else:
        st.line_chart(filtered, x="date", y="value", color="series")
        st.bar_chart(filtered.groupby("series", as_index=False)["value"].mean(), x="series", y="value")
with table:
    st.write("Sort columns and search the table, or download the filtered sample.")
    st.dataframe(filtered, hide_index=True)
    st.download_button("Download CSV", filtered.to_csv(index=False), "sample.csv", "text/csv")
with database:
    st.subheader("Optional PostgreSQL connection")
    st.write("The sample charts work without a database. This example runs a read-only query against your configured PostgreSQL service.")
    if not os.environ.get("DATABASE_URL"):
        st.info("PostgreSQL is not configured. Follow the README to connect an Aiven service.")
    elif st.button("Test connection"):
        try:
            status = database_status()
        except Exception:
            # Do not render driver exceptions: connection details may contain secrets.
            st.error("Connection failed. Check DATABASE_URL, PG_CA_CERT_BASE64, service availability, and network access.")
        else:
            st.success("Connected using verified TLS.")
            st.json(status)

st.divider()
st.caption("Make it yours: replace the sample data in starter.py and the interface in app.py.")
