from project.app import create_app


ADMIN_TOKEN = "test-admin-token"


def _client(monkeypatch):
    monkeypatch.setenv("ADMIN_TOKEN", ADMIN_TOKEN)
    app = create_app({
        "TESTING": True,
        "WTF_CSRF_ENABLED": False,
    })
    return app.test_client()


def test_admin_login_get_returns_login_page(monkeypatch):
    response = _client(monkeypatch).get("/admin/login")

    assert response.status_code == 200
    assert b"Admin Login" in response.data


def test_admin_login_rejects_incorrect_token(monkeypatch):
    response = _client(monkeypatch).post(
        "/admin/login",
        data={"token": "incorrect-token"},
    )

    assert response.status_code == 200
    assert b"Invalid token" in response.data
    set_cookie_headers = response.headers.getlist("Set-Cookie")
    assert not any(
        header.startswith("admin_session=")
        for header in set_cookie_headers
    )

def test_admin_login_sets_current_session_cookie_and_redirects(
    monkeypatch,
):
    client = _client(monkeypatch)

    response = client.post(
        "/admin/login",
        data={"token": ADMIN_TOKEN},
    )

    assert response.status_code == 302
    assert response.headers["Location"] == "/admin/dashboard"

    cookie = response.headers["Set-Cookie"]
    assert f"admin_session={ADMIN_TOKEN}" in cookie
    assert "HttpOnly" in cookie
    assert "SameSite=Lax" in cookie
    assert "Max-Age=3600" in cookie

    # The current contract accepts the login cookie for dashboard access.
    dashboard = client.get("/admin/dashboard")
    assert dashboard.status_code == 200


def test_admin_dashboard_requires_credentials(monkeypatch):
    response = _client(monkeypatch).get("/admin/dashboard")

    assert response.status_code == 401
    assert response.get_json() == {"error": "Unauthorized"}


def test_admin_dashboard_accepts_bearer_token(monkeypatch):
    response = _client(monkeypatch).get(
        "/admin/dashboard",
        headers={"Authorization": f"Bearer {ADMIN_TOKEN}"},
    )

    assert response.status_code == 200


def test_admin_dashboard_accepts_x_admin_token(monkeypatch):
    response = _client(monkeypatch).get(
        "/admin/dashboard",
        headers={"X-ADMIN-TOKEN": ADMIN_TOKEN},
    )

    assert response.status_code == 200

def test_create_app_requires_secret_key_outside_testing(monkeypatch):
    monkeypatch.delenv("SECRET_KEY", raising=False)

    try:
        create_app()
    except RuntimeError as exc:
        assert "SECRET_KEY must be configured through the environment." in str(exc)
    else:
        raise AssertionError("create_app() should require SECRET_KEY outside testing")


def test_create_app_accepts_secret_key_from_environment(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "test-secret-key")

    app = create_app({
        "TESTING": True,
    })

    assert app.config["SECRET_KEY"] == "test-secret-key"

def test_session_cookie_security_defaults_are_configured():
    app = create_app({
        "TESTING": True,
    })

    assert app.config["SESSION_COOKIE_HTTPONLY"] is True
    assert app.config["SESSION_COOKIE_SAMESITE"] == "Lax"
    assert app.config["SESSION_COOKIE_SECURE"] is False


def test_rate_limiter_uses_configured_storage():
    app = create_app({
        "TESTING": True,
        "RATELIMIT_STORAGE_URI": "memory://",
    })

    assert app.config["RATELIMIT_STORAGE_URI"] == "memory://"


def test_security_headers_are_applied():
    app = create_app({
        "TESTING": True,
    })

    response = app.test_client().get("/")

    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["Referrer-Policy"] == "strict-origin"
    assert response.headers["Cache-Control"] == "no-store"
