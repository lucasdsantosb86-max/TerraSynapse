#!/usr/bin/env bash
set -e
export STREAMLIT_SERVER_PORT=${PORT:-8501}
streamlit run frontend/streamlit_app.py --server.address 0.0.0.0
