from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Create limiter WITHOUT attaching to app (factory pattern)
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["120 per minute"],
    storage_uri="memory://",
    headers_enabled=True,
)

