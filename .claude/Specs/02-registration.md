# Spec: Registration

## Overview
This step wires up the registration form so new users can create an account. The `/register` route currently only handles GET; this step adds the POST handler that validates input, hashes the password, inserts the user into the database, stores their `user_id` in a Flask session, and redirects them to a new `/dashboard` page. It also sets a `SECRET_KEY` on the app so sessions work, and updates the navbar in `base.html` to show context-aware links (Sign in / Get started when logged out; Dashboard / Logout when logged in).

## Depends on
- **Step 1** — `database/db.py` must be complete (users table, `get_db()`)

## Routes
- `POST /register` — process registration form, insert user, set session, redirect to `/dashboard` — public
- `GET /dashboard` — render the logged-in home page — logged-in only (redirect to `/login` if no session)

## Database changes
No database changes. The `users` table (`id`, `name`, `email`, `password_hash`, `created_at`) already exists in `database/db.py`.

## Templates
- **Create:** `templates/dashboard.html` — logged-in home page with a welcome message and placeholder links for future steps
- **Modify:** `templates/base.html` — update `nav-links` block to conditionally show Dashboard + Logout links when `session.user_id` is set, otherwise Sign in + Get started

## Files to change
- `app.py` — add `SECRET_KEY`, import `request`/`session`/`redirect`/`url_for` from flask, add POST method to `/register` route, add `GET /dashboard` route

## Files to create
- `templates/dashboard.html`

## New dependencies
No new dependencies. `werkzeug.security.generate_password_hash` / `check_password_hash` are already available via Flask's dependency on Werkzeug.

## Rules for implementation
- No SQLAlchemy or ORMs — use raw `sqlite3` via `get_db()`
- Parameterised queries only — never interpolate user input into SQL strings
- Passwords hashed with `werkzeug.security.generate_password_hash` before inserting
- Use CSS variables — never hardcode hex values in any template or stylesheet
- All templates extend `base.html`
- `SECRET_KEY` must be set before any session usage; use a hard-coded dev string (e.g. `"dev-secret-change-me"`) — do NOT read from env for this step
- On duplicate email, re-render `register.html` with `error="An account with that email already exists."`
- On any other DB error, re-render with a generic error message
- After successful registration set `session["user_id"] = <new user id>` and redirect to `/dashboard`
- `/dashboard` must redirect to `/login` if `session.get("user_id")` is absent

## Definition of done
- [ ] Visiting `GET /register` renders the registration form (no regression)
- [ ] Submitting the form with valid name, email, and password (≥ 8 chars) creates a new row in the `users` table
- [ ] After successful registration the browser is redirected to `/dashboard`
- [ ] `/dashboard` displays a welcome message that includes the logged-in user's name (fetched from DB via session)
- [ ] Submitting the form a second time with the same email shows the error "An account with that email already exists." on the register page
- [ ] The navbar on `/dashboard` shows "Dashboard" and "Logout" links instead of "Sign in" and "Get started"
- [ ] Navigating to `/dashboard` without a session redirects to `/login`
- [ ] Passwords are stored as hashes (not plaintext) — verifiable by inspecting `spendly.db` with a SQLite viewer
