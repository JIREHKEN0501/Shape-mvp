# run.py (at repo root)
import os
from project.app import create_app

if __name__ == "__main__":
    cfg = {}
    # optionally read some env vars to override
    if os.environ.get("LIMITER_STORAGE_URI"):
        cfg["LIMITER_STORAGE_URI"] = os.environ.get("LIMITER_STORAGE_URI")
    app = create_app(cfg)
    # for dev only: run with Flask debug server
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", "5000")), debug=False)

