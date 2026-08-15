from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash

from database.db import get_db, init_db, seed_db, create_user, get_user_by_email
from database import queries

app = Flask(__name__)
app.secret_key = "dev-secret-key-change-in-production"

with app.app_context():
    init_db()
    seed_db()


# ------------------------------------------------------------------ #
# Routes                                                              #
# ------------------------------------------------------------------ #

@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")

    if not name or not email or not password:
        return render_template("register.html", error="All fields are required.")

    if "@" not in email or "." not in email.split("@")[-1]:
        return render_template("register.html", error="Please enter a valid email address.")

    if len(password) < 8:
        return render_template("register.html", error="Password must be at least 8 characters.")

    if get_user_by_email(email):
        return render_template("register.html", error="An account with this email already exists.")

    password_hash = generate_password_hash(password)
    create_user(name, email, password_hash)

    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")

    user = get_user_by_email(email)

    if not user or not check_password_hash(user["password_hash"], password):
        return render_template("login.html", error="Invalid email or password.")

    session["user_id"] = user["id"]
    session["user_name"] = user["name"]

    return redirect(url_for("landing"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("landing"))


@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


@app.route("/profile")
def profile():
    if not session.get("user_id"):
        return redirect(url_for("login"))

    user_id = session["user_id"]

    start_date, end_date = queries.parse_date_range(
        request.args.get("start_date", ""), request.args.get("end_date", "")
    )
    start_date = start_date or ""
    end_date = end_date or ""

    user = queries.get_user_by_id(user_id)
    stats = queries.get_summary_stats(user_id, start_date, end_date)
    transactions = queries.get_recent_transactions(
        user_id, start_date=start_date, end_date=end_date
    )
    raw_categories = queries.get_category_breakdown(user_id, start_date, end_date)

    # profile.html expects `total`/`percent`/`bar_height`/`name`; queries.py
    # returns `name`/`amount`/`pct`. Map names and compute bar_height here
    # (nearest-5 CSS bucket, largest category = 100) — this is presentation
    # logic, not data access, so it stays out of queries.py.
    categories = []
    if raw_categories:
        max_pct = raw_categories[0]["pct"]
        for c in raw_categories:
            scaled = (c["pct"] / max_pct) * 100 if max_pct else 0
            bucket = min(max(5, round(scaled / 5) * 5), 100)
            categories.append({
                "name": c["name"],
                "total": c["amount"],
                "percent": c["pct"],
                "bar_height": bucket,
            })

    return render_template(
        "profile.html",
        user=user,
        stats=stats,
        transactions=transactions,
        categories=categories,
        start_date=start_date,
        end_date=end_date,
    )


# ------------------------------------------------------------------ #
# Placeholder routes — students will implement these                  #
# ------------------------------------------------------------------ #

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
    app.run(debug=True, port=5001)
