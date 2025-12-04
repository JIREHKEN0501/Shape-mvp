# HumanOS Tech – Deployment Notes (MVP)

## Environments

- **Dev**: Flask built-in server on port 5000
- **Prod-like / Demo**: Gunicorn on port 8000

## Starting the app (dev)

```bash
cd ~/shape-mvp-clean
source venv/bin/activate
flask run
# or: python app.py

