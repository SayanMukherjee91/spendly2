import sqlite3
import database.db as db_module


def test_get_db_returns_connection(app):
    conn = db_module.get_db()
    assert isinstance(conn, sqlite3.Connection)
    conn.close()


def test_get_db_row_factory(app):
    conn = db_module.get_db()
    conn.execute("INSERT INTO users (name, email, password_hash) VALUES ('X', 'x@x.com', 'h')")
    conn.commit()
    row = conn.execute("SELECT name FROM users").fetchone()
    assert row["name"] == "X"
    conn.close()


def test_get_db_foreign_keys_enabled(app):
    conn = db_module.get_db()
    result = conn.execute("PRAGMA foreign_keys").fetchone()
    assert result[0] == 1
    conn.close()


def test_init_db_creates_users_table(app):
    conn = db_module.get_db()
    tables = [r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()]
    assert "users" in tables
    conn.close()


def test_init_db_creates_expenses_table(app):
    conn = db_module.get_db()
    tables = [r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()]
    assert "expenses" in tables
    conn.close()


def test_init_db_idempotent(app):
    db_module.init_db()
    db_module.init_db()
    conn = db_module.get_db()
    tables = [r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()]
    assert "users" in tables
    conn.close()


def test_seed_db_creates_demo_user(app):
    db_module.seed_db()
    conn = db_module.get_db()
    row = conn.execute("SELECT * FROM users WHERE email = ?", ("demo@spendly.com",)).fetchone()
    assert row is not None
    assert row["name"] == "Demo User"
    conn.close()


def test_seed_db_creates_eight_expenses(app):
    db_module.seed_db()
    conn = db_module.get_db()
    cnt = conn.execute("SELECT COUNT(*) FROM expenses").fetchone()[0]
    assert cnt == 8
    conn.close()


def test_seed_db_is_idempotent(app):
    db_module.seed_db()
    db_module.seed_db()
    conn = db_module.get_db()
    user_cnt = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    assert user_cnt == 1
    conn.close()


def test_expenses_foreign_key_enforced(app):
    import pytest as _pytest
    conn = db_module.get_db()
    with _pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO expenses (user_id, amount, category, date) VALUES (?, ?, ?, ?)",
            (9999, 10.0, "Food", "2026-01-01"),
        )
        conn.commit()
    conn.close()
