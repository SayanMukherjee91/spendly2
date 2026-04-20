# Plan: Login and Logout (Step 3)

## Context
Step 2 (registration) wired up user creation and sessions. Step 3 completes the auth loop by implementing the login POST handler and the logout route. Without this, users who navigate away after registering have no way to sign back in, and the Logout link in the navbar is broken.

---

## Changes Required

### 1. `app.py`

**Add `check_password_hash` to the werkzeug import (line 4):**
```python
from werkzeug.security import generate_password_hash, check_password_hash
```

**Replace the stubbed `/login` route (lines 67–69) with a full GET/POST handler:**
```python
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    email    = request.form.get("email", "").strip()
    password = request.form.get("password", "")

    db   = get_db()
    user = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    db.close()

    if user is None or not check_password_hash(user["password_hash"], password):
        return render_template("login.html", error="Invalid email or password.")

    session["user_id"] = user["id"]
    return redirect(url_for("dashboard"))
```

**Replace the stubbed `/logout` route (lines 86–88):**
```python
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("landing"))
```

---

## Files to Change
| File | What changes |
|------|-------------|
| `app.py` | Add `check_password_hash` import; implement POST `/login`; implement `/logout` |

## Files to Create
None.

## Files Left Unchanged
| File | Why |
|------|-----|
| `templates/login.html` | Already POSTs to `/login` and renders `{{ error }}` — no changes needed |
| `templates/base.html` | Navbar conditional already complete from Step 2 |
| `templates/dashboard.html` | No changes for this step |
| `database/db.py` | No schema changes needed |

---

## Key Implementation Rules
- Use `check_password_hash(user["password_hash"], password)` — never compare plaintext
- Single error message `"Invalid email or password."` for both unknown email and wrong password (do not leak which field is wrong)
- `session.clear()` in logout (not `session.pop`) to wipe the whole session
- Redirect logout to `url_for('landing')`, not `/login`
- Query uses parameterised `?` placeholder — no string interpolation

---

## Verification (Definition of Done)
1. `GET /login` — renders form without errors
2. POST valid credentials (`demo@spendly.com` / `demo123`) → redirected to `/dashboard`, user name shown
3. POST unknown email → login page re-renders with "Invalid email or password."
4. POST correct email + wrong password → same error message
5. Click Logout → session cleared, redirected to landing page `/`
6. After logout, `GET /dashboard` → redirects to `/login`
7. Navbar shows "Sign in" / "Get started" after logout; "Dashboard" / "Logout" when logged in
