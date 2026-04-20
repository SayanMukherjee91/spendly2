# Spec: Login and Logout

## Overview
This step wires up the login and logout flows. The `/login` route currently only handles GET; this step adds the POST handler that validates credentials, checks the password hash, stores the user's `user_id` in the Flask session, and redirects to `/dashboard`. The `/logout` route clears the session and redirects to the landing page. Together these steps complete the core authentication loop started in Step 2 (registration).

## Depends on
- **Step 1** — `database/db.py` must be complete (`users` table, `get_db()`)
- **Step 2** — Registration must be complete (session setup, `/dashboard` route, navbar conditional links)

## Routes
- `POST /login` — validate credentials, set session, redirect to `/dashboard` — public
- `GET /logout` — clear session, redirect to `/` — logged-in (safe to call when logged out too)

## Database changes
No database changes. The `users` table already has `id`, `email`, and `password_hash`.

## Templates
- **Create:** none
- **Modify:** `templates/login.html` — no structural changes needed; the form already POSTs to `/login` and renders `{{ error }}`

## Files to change
- `app.py` — add `check_password_hash` import, add POST method to `/login` route, implement `/logout` route

## Files to create
No new files.

## New dependencies
No new dependencies. `werkzeug.security.check_password_hash` is already available via Flask's Werkzeug dependency.

## Rules for implementation
- No SQLAlchemy or ORMs — use raw `sqlite3` via `get_db()`
- Parameterised queries only — never interpolate user input into SQL strings
- Passwords verified with `werkzeug.security.check_password_hash` — never compare plaintext
- Use CSS variables — never hardcode hex values in any template or stylesheet
- All templates extend `base.html`
- On unknown email OR wrong password, re-render `login.html` with `error="Invalid email or password."` (do not distinguish which field was wrong)
- After successful login set `session["user_id"] = <user id>` and redirect to `/dashboard`
- `/logout` must call `session.clear()` then redirect to `url_for('landing')`

## Definition of done
- [ ] Visiting `GET /login` renders the login form (no regression)
- [ ] Submitting correct email + password sets a session and redirects to `/dashboard`
- [ ] `/dashboard` shows the correct user's name after login
- [ ] Submitting an unknown email shows "Invalid email or password." on the login page
- [ ] Submitting a known email with the wrong password shows "Invalid email or password." on the login page
- [ ] Clicking Logout clears the session and redirects to the landing page (`/`)
- [ ] After logout, navigating to `/dashboard` redirects to `/login`
- [ ] The navbar shows "Sign in" and "Get started" after logout (session gone)
