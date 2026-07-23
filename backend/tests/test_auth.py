def test_login_success(client, seeded_admin, admin_credentials):
    resp = client.post("/api/admin/auth/login", json=admin_credentials)
    assert resp.status_code == 200
    body = resp.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"


def test_login_wrong_password(client, seeded_admin, admin_credentials):
    resp = client.post(
        "/api/admin/auth/login",
        json={"username": admin_credentials["username"], "password": "wrong"},
    )
    assert resp.status_code == 401


def test_login_unknown_username(client, seeded_admin):
    resp = client.post("/api/admin/auth/login", json={"username": "nope", "password": "x"})
    assert resp.status_code == 401


def test_protected_endpoint_requires_token(client, seeded_admin):
    resp = client.get("/api/admin/auth/me")
    assert resp.status_code == 401


def test_me_with_valid_token(client, auth_headers, admin_credentials):
    resp = client.get("/api/admin/auth/me", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["username"] == admin_credentials["username"]


def test_update_profile_wrong_current_password(client, auth_headers):
    resp = client.put(
        "/api/admin/auth/me",
        headers=auth_headers,
        json={"current_password": "wrong", "new_password": "NewPass123!"},
    )
    assert resp.status_code == 403


def test_update_profile_changes_username_and_password_then_relogin(client, auth_headers, admin_credentials):
    resp = client.put(
        "/api/admin/auth/me",
        headers=auth_headers,
        json={
            "current_password": admin_credentials["password"],
            "new_username": "new_admin",
            "new_password": "BrandNewPass456!",
        },
    )
    assert resp.status_code == 200
    assert resp.json()["username"] == "new_admin"

    old_login = client.post("/api/admin/auth/login", json=admin_credentials)
    assert old_login.status_code == 401

    new_login = client.post(
        "/api/admin/auth/login",
        json={"username": "new_admin", "password": "BrandNewPass456!"},
    )
    assert new_login.status_code == 200
