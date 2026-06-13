import pytest


class TestRegister:
    def test_get_register_returns_200(self, client):
        rv = client.get("/register")
        assert rv.status_code == 200

    def test_register_success_redirects_to_dashboard(self, client):
        rv = client.post("/register", data={
            "name": "Bob", "email": "bob@test.com", "password": "password123"
        }, follow_redirects=True)
        assert rv.status_code == 200
        assert b"/dashboard" in rv.request.path.encode() or b"dashboard" in rv.data.lower()

    def test_register_sets_session(self, app):
        c = app.test_client()
        c.post("/register", data={
            "name": "Bob", "email": "bob@test.com", "password": "password123"
        })
        with c.session_transaction() as sess:
            assert "user_id" in sess

    def test_register_missing_name(self, client):
        rv = client.post("/register", data={
            "name": "", "email": "bob@test.com", "password": "password123"
        })
        assert rv.status_code == 200
        assert b"required" in rv.data.lower()

    def test_register_missing_email(self, client):
        rv = client.post("/register", data={
            "name": "Bob", "email": "", "password": "password123"
        })
        assert rv.status_code == 200
        assert b"required" in rv.data.lower()

    def test_register_missing_password(self, client):
        rv = client.post("/register", data={
            "name": "Bob", "email": "bob@test.com", "password": ""
        })
        assert rv.status_code == 200
        assert b"required" in rv.data.lower()

    def test_register_password_too_short(self, client):
        rv = client.post("/register", data={
            "name": "Bob", "email": "bob@test.com", "password": "short"
        })
        assert rv.status_code == 200
        assert b"8" in rv.data

    def test_register_duplicate_email(self, client):
        data = {"name": "Bob", "email": "bob@test.com", "password": "password123"}
        client.post("/register", data=data)
        rv = client.post("/register", data=data)
        assert rv.status_code == 200
        assert b"already exists" in rv.data.lower()


class TestLogin:
    def test_get_login_returns_200(self, client):
        rv = client.get("/login")
        assert rv.status_code == 200

    def test_login_valid_credentials(self, client):
        client.post("/register", data={
            "name": "Bob", "email": "bob@test.com", "password": "password123"
        })
        with client.session_transaction() as sess:
            sess.clear()
        rv = client.post("/login", data={
            "email": "bob@test.com", "password": "password123"
        }, follow_redirects=True)
        assert rv.status_code == 200

    def test_login_sets_session(self, app):
        c = app.test_client()
        c.post("/register", data={
            "name": "Bob", "email": "bob@test.com", "password": "password123"
        })
        with c.session_transaction() as sess:
            sess.clear()
        c.post("/login", data={"email": "bob@test.com", "password": "password123"})
        with c.session_transaction() as sess:
            assert "user_id" in sess

    def test_login_wrong_password(self, client):
        client.post("/register", data={
            "name": "Bob", "email": "bob@test.com", "password": "password123"
        })
        rv = client.post("/login", data={
            "email": "bob@test.com", "password": "wrongpass"
        })
        assert rv.status_code == 200
        assert b"invalid" in rv.data.lower()

    def test_login_unknown_email(self, client):
        rv = client.post("/login", data={
            "email": "nobody@test.com", "password": "password123"
        })
        assert rv.status_code == 200
        assert b"invalid" in rv.data.lower()

    def test_login_empty_email(self, client):
        rv = client.post("/login", data={"email": "", "password": "password123"})
        assert rv.status_code == 200
        assert b"invalid" in rv.data.lower()


class TestLogout:
    def test_logout_redirects(self, auth_client):
        rv = auth_client.get("/logout")
        assert rv.status_code == 302

    def test_logout_redirects_to_landing(self, auth_client):
        rv = auth_client.get("/logout", follow_redirects=False)
        assert rv.location.endswith("/") or rv.location == "/"

    def test_logout_clears_session(self, auth_client):
        auth_client.get("/logout")
        with auth_client.session_transaction() as sess:
            assert "user_id" not in sess

    def test_logout_then_dashboard_redirects(self, auth_client):
        auth_client.get("/logout")
        rv = auth_client.get("/dashboard")
        assert rv.status_code == 302
        assert "/login" in rv.location
