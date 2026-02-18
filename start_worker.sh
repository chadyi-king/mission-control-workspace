#!/bin/bash
# Render Background Worker start script

echo "Starting Helios Background Worker..."
cd /app

# Install dependencies if needed
pip install redis -q

# Start the worker
exec python3 render_worker.py
