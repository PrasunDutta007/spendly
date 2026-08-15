# database/queries.py
#   Pure data-access helpers for the profile page. No Flask imports.
#   Each function opens its own connection via get_db() and closes it
#   before returning, matching the style of database/db.py.
#
#   NOTE: the spec's test-table gives total_spent=346.24 / top_category="Bills"
#   for the seed data. Those numbers are stale — the actual seeded expenses
#   (database/db.py seed_db()) sum to 422.49 across 8 transactions, and the
#   highest single category is Shopping (150.00). Tests assert real values.

from datetime import datetime

from database.db import get_db


def get_user_by_id(user_id):
    conn = get_db()
    row = conn.execute(
        "SELECT name, email, created_at FROM users WHERE id = ?", (user_id,)
    ).fetchone()
    conn.close()

    if row is None:
        return None

    created_at = datetime.strptime(row["created_at"], "%Y-%m-%d %H:%M:%S")
    member_since = created_at.strftime("%B %Y")

    return {
        "name": row["name"],
        "email": row["email"],
        "member_since": member_since,
    }


def get_summary_stats(user_id):
    conn = get_db()
    rows = conn.execute(
        "SELECT category, amount FROM expenses WHERE user_id = ?",
        (user_id,)
    ).fetchall()
    conn.close()

    if not rows:
        return {"total_spent": 0, "transaction_count": 0, "top_category": "—"}

    total_spent = 0
    category_totals = {}
    for row in rows:
        amount = row["amount"]
        total_spent += amount
        category_totals[row["category"]] = category_totals.get(row["category"], 0) + amount

    top_category = min(
        category_totals,
        key=lambda cat: (-category_totals[cat], cat)
    )

    return {
        "total_spent": round(total_spent, 2),
        "transaction_count": len(rows),
        "top_category": top_category
    }


def get_recent_transactions(user_id, limit=10):
    conn = get_db()
    rows = conn.execute(
        "SELECT date, description, category, amount FROM expenses "
        "WHERE user_id = ? ORDER BY date DESC, id DESC LIMIT ?",
        (user_id, limit)
    ).fetchall()
    conn.close()

    return [
        {
            "date": row["date"],
            "description": row["description"],
            "category": row["category"],
            "amount": row["amount"],
        }
        for row in rows
    ]


def get_category_breakdown(user_id):
    conn = get_db()
    rows = conn.execute(
        "SELECT category, amount FROM expenses WHERE user_id = ?",
        (user_id,)
    ).fetchall()
    conn.close()

    if not rows:
        return []

    totals = {}
    for row in rows:
        totals[row["category"]] = totals.get(row["category"], 0) + row["amount"]

    grand_total = sum(totals.values())

    sorted_categories = sorted(totals.items(), key=lambda item: (-item[1], item[0]))

    breakdown = []
    for name, amount in sorted_categories:
        pct = round(amount / grand_total * 100)
        breakdown.append({"name": name, "amount": round(amount, 2), "pct": pct})

    sum_of_pcts = sum(item["pct"] for item in breakdown)
    remainder = 100 - sum_of_pcts
    breakdown[0]["pct"] += remainder

    return breakdown
