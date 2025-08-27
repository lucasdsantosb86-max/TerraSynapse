#!/usr/bin/env bash
set -e
streamlit run frontend/streamlit_app.py --server.port ${PORT:-8501} --server.address 0.0.0.0
