#!/usr/bin/env bash
# Simple production entrypoint for HumanOS Tech MVP

# Activate virtualenv if needed (uncomment if using from plain shell)
# source venv/bin/activate

# Bind to all interfaces on port 8000 with 3 workers
exec gunicorn -w 3 -b 0.0.0.0:8000 "app:create_app()"

