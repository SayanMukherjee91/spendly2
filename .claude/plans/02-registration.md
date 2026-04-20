# Plan: Step 2 — Registration

## Context
The `/register` route in `app.py` currently only handles GET and renders `register.html`. The form already exists with all fields (name, email, password) and error display, but submitting it returns a 405 Method Not Allowed. This step wires up the POST handler, creates a session after successful registration, adds a `/dashboard` route for logged-in users, and makes the navbar context-aware.

---

## Files to Modify

### 1. `app.py`
**Changes:**
- Extend the Flask import to include `request`, `session`, `redirect`
- Set `app.secret_key = "dev-secret-change-me"` immediately after `app = Flask(__name__)`
- Convert `@app.route("/register")` to accept `methods=["GET", "POST"]`
- Add POST logic inside the register view:
  1. Read `name`, `email`, `password` from `request.form`
  2. Basic validation: all fields required, password ≥ 8 characters
  3. Open `get_db()`, try to insert with `generate_password_hash(password)`
  4. Catch `sqlite3.IntegrityError` (UNIQUE constraint on email) → re-render `register.html` with `error="An account with that email already exists."`
  5. On success: fetch the new user's `id`, set `session["user_id"] = id`, redirect to `/dashboard`
- Add `GET /dashboard` route:
  - If `session.get("user_id")` is absent → `redirect(url_for("login"))`
  - Otherwise fetch user row from DB and `render_template("dashboard.html", user=user)`

**Imports to add:** `request`, `session`, `redirect` (from flask); `sqlite3` (stdlib); `generate_password_hash` is already imported in `db.py` — no need to import it in `app.py` since it's called there, but it IS needed here for hashing in the route → import from `werkzeug.security`.

### 2. `templates/base.html`
**Change:** Replace the static `nav-links` div with a conditional block:
```
{% if session.get("user_id") %}
  <a href="{{ url_for('dashboard') }}">Dashboard</a>
  <a href="{{ url_for('logout') }}" class="nav-cta">Logout</a>
{% else %}
  <a href="{{ url_for('login') }}">Sign in</a>
  <a href="{{ url_for('register') }}" class="nav-cta">Get started</a>
{% endif %}
```

---

## Files to Create

### 3. `templates/dashboard.html`
- Extends `base.html`
- Title block: `Dashboard — Spendly`
- Content: a welcome section using existing CSS variables and classes (no new styles needed)
  - Heading: `Welcome back, {{ user["name"] }}!`
  - Subtext: e.g. "Here's your spending overview."
  - Placeholder cards for future steps (expenses list, add expense button) — stub text only

---

## Implementation Order
1. `app.py` — add imports, secret key, POST /register handler, GET /dashboard route
2. `templates/dashboard.html` — create the template
3. `templates/base.html` — update navbar conditional

---

## Key Constraints
- Raw `sqlite3` only — no ORMs
- Parameterised queries only (`?` placeholders)
- `generate_password_hash` from `werkzeug.security` for password storage
- CSS variables only — no hardcoded hex values in dashboard.html
- `SECRET_KEY` hardcoded as `"dev-secret-change-me"` for this dev step

---

## Verification
1. Run `python app.py`
2. Visit `http://127.0.0.1:5001/register` — form renders correctly (GET still works)
3. Submit with a new name/email/password (≥ 8 chars) → redirects to `/dashboard` with welcome message showing the user's name
4. Navbar on dashboard shows "Dashboard" and "Logout" instead of "Sign in" / "Get started"
5. Submit the same email again → error message appears on the register page
6. Navigate to `/dashboard` in a fresh browser (no session) → redirects to `/login`
7. Inspect `spendly.db` with a SQLite viewer → password stored as a hash, not plaintext
