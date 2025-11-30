# project/app/security/__init__.py

from flask import jsonify, request


def bot_tripwire():
    """
    Placeholder anti-bot hook.
    If suspicious traffic is detected, return a Flask response.
    Otherwise return None to allow the request.

    For now, always allow.
    """
    # Example future logic:
    # if request.headers.get("User-Agent", "").lower() in known_bad_agents:
    #     return jsonify({"error": "bot_blocked"}), 403

    return None

