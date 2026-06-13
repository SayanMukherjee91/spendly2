import database.db as db_module
from werkzeug.security import check_password_hash


class TestProfile:
    def test_unauthenticated_redirects_to_login(self, client):
        rv = client.get("/profile")
        assert rv.status_code == 302
        assert "/login" in rv.location

    def test_authenticated_returns_200(self, auth_client):
        rv = auth_client.get("/profile")
        assert rv.status_code == 200

    def test_shows_user_name(self, auth_client):
        rv = auth_client.get("/profile")
        assert b"Alice" in rv.data

    def test_update_name_success(self, auth_client):
        rv = auth_client.post("/profile", data={
            "action": "update_name", "name": "Alicia"
        }, follow_redirects=True)
        assert rv.status_code == 200
        assert b"Alicia" in rv.data

    def test_update_name_persists_in_db(self, app, auth_client):
        with auth_client.session_transaction() as sess:
            user_id = sess["user_id"]
        auth_client.post("/profile", data={"action": "update_name", "name": "Alicia"})
        db = db_module.get_db()
        row = db.execute("SELECT name FROM users WHERE id = ?", (user_id,)).fetchone()
        db.close()
        assert row["name"] == "Alicia"

    def test_update_name_blank_shows_error(self, auth_client):
        rv = auth_client.post("/profile", data={"action": "update_name", "name": ""})
        assert rv.status_code == 200
        assert b"blank" in rv.data.lower() or b"cannot" in rv.data.lower()

    def test_change_password_success(self, auth_client):
        rv = auth_client.post("/profile", data={
            "action": "change_password",
            "current_password": "password123",
            "new_password": "newpassword456",
        }, follow_redirects=True)
        assert rv.status_code == 200

    def test_change_password_persists_in_db(self, app, auth_client):
        with auth_client.session_transaction() as sess:
            user_id = sess["user_id"]
        auth_client.post("/profile", data={
            "action": "change_password",
            "current_password": "password123",
            "new_password": "newpassword456",
        })
        db = db_module.get_db()
        row = db.execute("SELECT password_hash FROM users WHERE id = ?", (user_id,)).fetchone()
        db.close()
        assert check_password_hash(row["password_hash"], "newpassword456")

    def test_change_password_wrong_current(self, auth_client):
        rv = auth_client.post("/profile", data={
            "action": "change_password",
            "current_password": "wrongpass",
            "new_password": "newpassword456",
        })
        assert rv.status_code == 200
        assert b"incorrect" in rv.data.lower()

    def test_change_password_too_short(self, auth_client):
        rv = auth_client.post("/profile", data={
            "action": "change_password",
            "current_password": "password123",
            "new_password": "short",
        })
        assert rv.status_code == 200
        assert b"8" in rv.data
