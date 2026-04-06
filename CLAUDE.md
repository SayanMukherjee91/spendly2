# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

**Run the app:**
```bash
python app.py
```
Runs on `http://127.0.0.1:5001` with debug mode enabled.

**Install dependencies:**
```bash
pip install -r requirements.txt
```

**Run tests:**
```bash
pytest
```

**Run a single test:**
```bash
pytest tests/test_filename.py::test_function_name
```

## Architecture

This is **Spendly**, a Flask + SQLite expense tracker built as a step-by-step student project. Features are added incrementally across numbered steps.

**`app.py`** — entry point. All routes are defined here. Placeholder routes (logout, profile, expenses CRUD) return stub strings until their respective steps are implemented.

**`database/db.py`** — SQLite helper module (to be implemented in Step 1). Must expose:
- `get_db()` — returns a connection with `row_factory` set and foreign keys enabled
- `init_db()` — creates tables using `CREATE TABLE IF NOT EXISTS`
- `seed_db()` — inserts sample data

**`templates/`** — Jinja2 templates. `base.html` is the master layout containing the navbar and footer; all other templates extend it via `{% extends "base.html" %}` and fill `{% block content %}`.

**`static/css/style.css`** and **`static/js/main.js`** — frontend assets loaded via `url_for('static', ...)` in `base.html`.

## Incremental Build Steps

The project is structured around numbered steps:
- **Step 1** — `database/db.py` (SQLite setup)
- **Step 3** — logout
- **Step 4** — profile page
- **Steps 7–9** — expense add/edit/delete

When implementing a step, connect the route in `app.py` to the database via `get_db()` and render the appropriate template.
