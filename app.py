import os
import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from youtubelink import YOUTUBE_EMBED_URL
from database.db import get_db, init_db, seed_db

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, template_folder=os.path.join(BASE_DIR, "templates"),
            static_folder=os.path.join(BASE_DIR, "static"))
app.secret_key = "dev-secret-change-me"

_MONTHS = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
app.jinja_env.filters['month_name'] = lambda n: _MONTHS[int(n) - 1]

with app.app_context():
    init_db()
    seed_db()


@app.context_processor
def inject_nav_user():
    name = session.get("user_name")
    if not name and session.get("user_id"):
        db = get_db()
        row = db.execute("SELECT name FROM users WHERE id = ?", (session["user_id"],)).fetchone()
        db.close()
        if row:
            name = row["name"]
            session["user_name"] = name
    return {"nav_user_name": name or ""}


# ------------------------------------------------------------------ #
# Routes                                                              #
# ------------------------------------------------------------------ #

@app.route("/")
def landing():
    return render_template("landing.html", youtube_embed_url=YOUTUBE_EMBED_URL)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")

    if not name or not email or not password:
        return render_template("register.html", error="All fields are required.")
    if len(password) < 8:
        return render_template("register.html", error="Password must be at least 8 characters.")

    db = get_db()
    try:
        db.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            (name, email, generate_password_hash(password)),
        )
        db.commit()
        user_id = db.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()["id"]
        session["user_id"]   = user_id
        session["user_name"] = name
        return redirect(url_for("dashboard"))
    except sqlite3.IntegrityError:
        return render_template("register.html", error="An account with that email already exists.")
    finally:
        db.close()


@app.route("/dashboard")
def dashboard():
    if not session.get("user_id"):
        return redirect(url_for("login"))
    user_id = session["user_id"]
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()

    summary = db.execute(
        "SELECT COALESCE(SUM(amount), 0) AS total, COUNT(*) AS cnt FROM expenses WHERE user_id = ?",
        (user_id,)
    ).fetchone()
    total_spend = float(summary["total"] or 0)
    tx_count    = int(summary["cnt"])
    avg_spend   = total_spend / tx_count if tx_count else 0.0

    monthly_rows = db.execute(
        "SELECT strftime('%Y-%m', date) AS month, SUM(amount) AS total "
        "FROM expenses WHERE user_id = ? GROUP BY month ORDER BY month ASC",
        (user_id,)
    ).fetchall()
    monthly = [{"month": r["month"], "total": float(r["total"])} for r in monthly_rows]

    cat_rows = db.execute(
        "SELECT category, SUM(amount) AS total "
        "FROM expenses WHERE user_id = ? GROUP BY category ORDER BY total DESC",
        (user_id,)
    ).fetchall()
    by_category = [{"category": r["category"], "total": float(r["total"])} for r in cat_rows]

    db.close()
    return render_template("dashboard.html", user=user,
        total_spend=total_spend, tx_count=tx_count, avg_spend=avg_spend,
        monthly=monthly, by_category=by_category)


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

    session["user_id"]   = user["id"]
    session["user_name"] = user["name"]
    return redirect(url_for("dashboard"))


# ------------------------------------------------------------------ #
# Placeholder routes — students will implement these                  #
# ------------------------------------------------------------------ #

@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("landing"))


@app.route("/profile", methods=["GET", "POST"])
def profile():
    if not session.get("user_id"):
        return redirect(url_for("login"))

    user_id = session["user_id"]
    db = get_db()
    name_error = pw_error = None

    if request.method == "POST":
        action = request.form.get("action")

        if action == "update_name":
            new_name = request.form.get("name", "").strip()
            if not new_name:
                name_error = "Name cannot be blank."
            else:
                db.execute("UPDATE users SET name = ? WHERE id = ?", (new_name, user_id))
                db.commit()
                db.close()
                session["user_name"] = new_name
                return redirect(url_for("profile"))

        elif action == "change_password":
            current = request.form.get("current_password", "")
            new_pw  = request.form.get("new_password", "")
            row = db.execute("SELECT password_hash FROM users WHERE id = ?", (user_id,)).fetchone()
            if not check_password_hash(row["password_hash"], current):
                pw_error = "Current password is incorrect."
            elif len(new_pw) < 8:
                pw_error = "New password must be at least 8 characters."
            else:
                db.execute("UPDATE users SET password_hash = ? WHERE id = ?",
                           (generate_password_hash(new_pw), user_id))
                db.commit()
                db.close()
                return redirect(url_for("profile"))

    user = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()

    try:
        dt = datetime.strptime(user["created_at"], "%Y-%m-%d %H:%M:%S")
    except (ValueError, TypeError):
        dt = datetime.now()
    member_since = dt.strftime("%B %Y")

    db.close()

    return render_template("profile.html",
        user=user, member_since=member_since,
        name_error=name_error, pw_error=pw_error,
    )


@app.route("/expenses")
def expenses():
    if not session.get("user_id"):
        return redirect(url_for("login"))
    user_id = session["user_id"]
    db = get_db()
    expense_rows = db.execute(
        "SELECT * FROM expenses WHERE user_id = ? ORDER BY date DESC",
        (user_id,)
    ).fetchall()
    months = [r["month"] for r in db.execute(
        "SELECT DISTINCT strftime('%Y-%m', date) AS month FROM expenses "
        "WHERE user_id = ? ORDER BY month DESC",
        (user_id,)
    ).fetchall()]
    categories = [r["category"] for r in db.execute(
        "SELECT DISTINCT category FROM expenses WHERE user_id = ? ORDER BY category",
        (user_id,)
    ).fetchall()]
    by_category = [{"category": r["category"], "total": r["total"]} for r in db.execute(
        "SELECT category, SUM(amount) AS total FROM expenses "
        "WHERE user_id = ? GROUP BY category ORDER BY total DESC",
        (user_id,)
    ).fetchall()]
    db.close()
    return render_template("expenses.html",
        expenses=expense_rows, months=months, categories=categories,
        by_category=by_category)


@app.route("/expenses/add")
def add_expense():
    return "Add expense — coming in Step 7"


@app.route("/expenses/<int:id>/edit")
def edit_expense(id):
    return "Edit expense — coming in Step 8"


@app.route("/expenses/<int:id>/delete")
def delete_expense(id):
    return "Delete expense — coming in Step 9"


if __name__ == "__main__":
    app.run(debug=True, port=5001, use_reloader=False)
