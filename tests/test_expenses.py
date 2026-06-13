import database.db as db_module
from werkzeug.security import generate_password_hash


class TestExpensesList:
    def test_unauthenticated_redirects_to_login(self, client):
        rv = client.get("/expenses")
        assert rv.status_code == 302
        assert "/login" in rv.location

    def test_authenticated_returns_200(self, auth_client):
        rv = auth_client.get("/expenses")
        assert rv.status_code == 200

    def test_empty_list_for_new_user(self, auth_client):
        rv = auth_client.get("/expenses")
        assert rv.status_code == 200

    def test_seeded_expenses_shown(self, seeded_client):
        rv = seeded_client.get("/expenses")
        assert rv.status_code == 200
        assert b"Food" in rv.data or b"Bills" in rv.data

    def test_no_cross_user_data_leakage(self, app):
        db = db_module.get_db()
        db.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            ("User1", "u1@test.com", generate_password_hash("password123")),
        )
        db.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            ("User2", "u2@test.com", generate_password_hash("password123")),
        )
        db.commit()
        u1 = db.execute("SELECT id FROM users WHERE email = ?", ("u1@test.com",)).fetchone()["id"]
        u2 = db.execute("SELECT id FROM users WHERE email = ?", ("u2@test.com",)).fetchone()["id"]
        db.execute(
            "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
            (u1, 99.99, "Food", "2026-01-01", "User1 private expense"),
        )
        db.commit()
        db.close()

        c = app.test_client()
        with c.session_transaction() as sess:
            sess["user_id"] = u2
        rv = c.get("/expenses")
        assert b"User1 private expense" not in rv.data


class TestExpenseStubs:
    def test_add_expense_returns_200(self, auth_client):
        rv = auth_client.get("/expenses/add")
        assert rv.status_code == 200

    def test_add_expense_mentions_step_7(self, auth_client):
        rv = auth_client.get("/expenses/add")
        assert b"7" in rv.data

    def test_edit_expense_returns_200(self, auth_client):
        rv = auth_client.get("/expenses/1/edit")
        assert rv.status_code == 200

    def test_edit_expense_mentions_step_8(self, auth_client):
        rv = auth_client.get("/expenses/1/edit")
        assert b"8" in rv.data

    def test_delete_expense_returns_200(self, auth_client):
        rv = auth_client.get("/expenses/1/delete")
        assert rv.status_code == 200

    def test_delete_expense_mentions_step_9(self, auth_client):
        rv = auth_client.get("/expenses/1/delete")
        assert b"9" in rv.data
