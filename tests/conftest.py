import pytest
import database.db as db_module
from werkzeug.security import generate_password_hash
from app import app as flask_app


@pytest.fixture()
def app(monkeypatch, tmp_path):
    db_path = str(tmp_path / "test.db")
    monkeypatch.setattr(db_module, "DB_PATH", db_path)
    db_module.init_db()
    flask_app.config["TESTING"] = True
    yield flask_app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def auth_client(app):
    """Test client with a registered and logged-in user (Alice)."""
    db = db_module.get_db()
    db.execute(
        "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
        ("Alice", "alice@test.com", generate_password_hash("password123")),
    )
    db.commit()
    row = db.execute("SELECT id FROM users WHERE email = ?", ("alice@test.com",)).fetchone()
    user_id = row["id"]
    db.close()

    c = app.test_client()
    with c.session_transaction() as sess:
        sess["user_id"] = user_id
    return c


@pytest.fixture()
def seeded_client(app):
    """Test client with demo seed data and demo user logged in."""
    db_module.seed_db()
    db = db_module.get_db()
    row = db.execute("SELECT id FROM users WHERE email = ?", ("demo@spendly.com",)).fetchone()
    user_id = row["id"]
    db.close()

    c = app.test_client()
    with c.session_transaction() as sess:
        sess["user_id"] = user_id
    return c
