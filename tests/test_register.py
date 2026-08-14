import database.db as db_module


def test_get_register_renders_form(client):
    response = client.get("/register")
    assert response.status_code == 200
    assert b'name="email"' in response.data


def test_post_register_creates_user(client):
    response = client.post(
        "/register",
        data={"name": "Test User", "email": "test1@example.com", "password": "password123"},
    )
    assert response.status_code == 302

    user = db_module.get_user_by_email("test1@example.com")
    assert user is not None
    assert user["password_hash"] != "password123"


def test_post_register_redirects_to_login(client):
    response = client.post(
        "/register",
        data={"name": "Test User", "email": "test2@example.com", "password": "password123"},
    )
    assert response.headers["Location"].endswith("/login")


def test_post_register_duplicate_email(client):
    conn = db_module.get_db()
    before = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    conn.close()

    response = client.post(
        "/register",
        data={"name": "Demo Duplicate", "email": "demo@spendly.com", "password": "password123"},
    )
    assert response.status_code == 200
    assert b"auth-error" in response.data

    conn = db_module.get_db()
    after = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    conn.close()
    assert after == before


def test_post_register_missing_field(client):
    response = client.post(
        "/register",
        data={"name": "Foo", "email": "foo@example.com", "password": ""},
    )
    assert response.status_code == 200
    assert b"auth-error" in response.data
    assert db_module.get_user_by_email("foo@example.com") is None


def test_post_register_short_password(client):
    response = client.post(
        "/register",
        data={"name": "Foo", "email": "shortpw@example.com", "password": "short"},
    )
    assert response.status_code == 200
    assert b"auth-error" in response.data
    assert db_module.get_user_by_email("shortpw@example.com") is None


def test_post_register_invalid_email_format(client):
    response = client.post(
        "/register",
        data={"name": "Foo", "email": "notanemail", "password": "password123"},
    )
    assert response.status_code == 200
    assert b"auth-error" in response.data
    assert db_module.get_user_by_email("notanemail") is None
