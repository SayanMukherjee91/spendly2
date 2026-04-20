# Plan: Step 1 — Database Setup (`database/db.py`)

## Context
Spendly is a Flask + SQLite expense tracker built as an incremental student project. Step 1 requires implementing `database/db.py`, which is currently a stub with placeholder comments. This module is the foundation for all future steps — authentication (Step 3), profile (Step 4), and expense CRUD (Steps 7–9) all depend on it.

---

## Schema

### `users` table
| Column | Type | Notes |
|---|---|---|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT |
| name | TEXT | NOT NULL |
| email | TEXT | NOT NULL UNIQUE |
| password_hash | TEXT | NOT NULL |
| created_at | TEXT | DEFAULT CURRENT_TIMESTAMP |

### `expenses` table
| Column | Type | Notes |
|---|---|---|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT |
| user_id | INTEGER | NOT NULL, FK → users(id) |
| title | TEXT | NOT NULL |
| amount | REAL | NOT NULL |
| category | TEXT | NOT NULL |
| date | TEXT | NOT NULL (ISO format YYYY-MM-DD) |
| created_at | TEXT | DEFAULT CURRENT_TIMESTAMP |

---

## Implementation

### `database/db.py`

#### `get_db()`
- Connect to `database/spendly.db` using `os.path` relative to the module file
- Set `conn.row_factory = sqlite3.Row`
- Execute `PRAGMA foreign_keys = ON`
- Return the connection

#### `init_db()`
- Call `get_db()`, run `CREATE TABLE IF NOT EXISTS` for `users` and `expenses`, commit and close

#### `seed_db()`
- Call `init_db()`, insert 1 sample user and 3 sample expenses using `INSERT OR IGNORE`, commit and close

---

## Verification
1. `python -c "from database.db import init_db, seed_db; init_db(); seed_db(); print('OK')"` → prints `OK`
2. `database/spendly.db` is created
3. `sqlite3 database/spendly.db ".tables"` → shows `users expenses`
4. `sqlite3 database/spendly.db "SELECT * FROM users;"` → shows seeded user
5. `pytest` → all tests pass
