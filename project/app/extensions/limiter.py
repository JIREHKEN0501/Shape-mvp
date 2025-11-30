# project/app/extensions/limiter.py

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address


# We instantiate the Limiter here without attaching it to the app.
# create_app() will call limiter.init_app(app) to finish setup.
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["120 per minute"],
    storage_uri="memory://",
    headers_enabled=True,
)

