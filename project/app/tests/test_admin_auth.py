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
