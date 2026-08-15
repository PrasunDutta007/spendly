from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash

from database.db import get_db, init_db, seed_db, create_user, get_user_by_email

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

    user = {
        "name": "Priya Sharma",
        "email": "priya.sharma@example.com",
        "member_since": "March 2025",
    }

    stats = {
        "total_spent": 18450.00,
        "transaction_count": 34,
        "top_category": "Food",
    }

    transactions = [
        {"date": "2026-08-10", "description": "Zomato order", "category": "Food", "amount": 420.00},
        {"date": "2026-08-08", "description": "Ola cab", "category": "Transport", "amount": 180.00},
        {"date": "2026-08-05", "description": "Electricity bill", "category": "Bills", "amount": 2100.00},
        {"date": "2026-08-03", "description": "Movie tickets - PVR", "category": "Entertainment", "amount": 600.00},
        {"date": "2026-08-01", "description": "Pharmacy - Apollo", "category": "Health", "amount": 350.00},
    ]

    # bar_height is the category's percent scaled so the largest category
    # reaches 100, rounded to the nearest 5 to match a fixed set of CSS
    # height-bucket classes (.bar-5 ... .bar-100) — keeps the vertical bar
    # chart inline-style-free per the spec's "no inline styles" rule.
    categories = [
        {"name": "Food", "total": 6200.00, "percent": 34, "bar_height": 100},
        {"name": "Bills", "total": 4600.00, "percent": 25, "bar_height": 75},
        {"name": "Transport", "total": 2600.00, "percent": 14, "bar_height": 45},
        {"name": "Shopping", "total": 2350.00, "percent": 13, "bar_height": 40},
        {"name": "Entertainment", "total": 1450.00, "percent": 8, "bar_height": 25},
        {"name": "Health", "total": 1250.00, "percent": 6, "bar_height": 20},
    ]

    return render_template(
        "profile.html",
        user=user,
        stats=stats,
        transactions=transactions,
        categories=categories,
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
