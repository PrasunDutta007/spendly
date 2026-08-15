# tests/test_backend_connection.py
#
# NOTE: the spec (.claude/specs/05-backend-routes-for-profile-page.md) states
# expected seed-data values of total_spent=346.24 and top_category="Bills".
# Those numbers are stale. The actual seeded expenses (database/db.py
# seed_db()) sum to 422.49 across 8 transactions, and the highest single
# category is Shopping (150.00). These tests assert against the real,
# computed seed values.

from datetime import datetime

import database.db as db_module
import database.queries as queries


def _seed_user_id():
    return db_module.get_user_by_email("demo@spendly.com")["id"]


def _new_user_id(client, email):
    client.post(
        "/register",
        data={"name": "New User", "email": email, "password": "password123"},
    )
    return db_module.get_user_by_email(email)["id"]


# ---------------------------------------------------------------- #
# get_user_by_id
# ---------------------------------------------------------------- #

def test_get_user_by_id_valid(client):
    user_id = _seed_user_id()
    result = queries.get_user_by_id(user_id)
    assert result == {
        "name": "Demo User",
        "email": "demo@spendly.com",
        "member_since": datetime.now().strftime("%B %Y"),
    }


def test_get_user_by_id_nonexistent(client):
    assert queries.get_user_by_id(999999) is None


# ---------------------------------------------------------------- #
# get_summary_stats
# ---------------------------------------------------------------- #

def test_get_summary_stats_with_expenses(client):
    user_id = _seed_user_id()
    stats = queries.get_summary_stats(user_id)
    assert stats["total_spent"] == 422.49
    assert stats["transaction_count"] == 8
    assert stats["top_category"] == "Shopping"


def test_get_summary_stats_no_expenses(client):
    user_id = _new_user_id(client, "nostats@example.com")
    assert queries.get_summary_stats(user_id) == {
        "total_spent": 0,
        "transaction_count": 0,
        "top_category": "—",
    }


# ---------------------------------------------------------------- #
# get_recent_transactions
# ---------------------------------------------------------------- #

def test_get_recent_transactions_with_expenses(client):
    user_id = _seed_user_id()
    result = queries.get_recent_transactions(user_id)
    assert len(result) == 8
    for item in result:
        assert set(item.keys()) == {"date", "description", "category", "amount"}
    dates = [item["date"] for item in result]
    assert dates == sorted(dates, reverse=True)
    assert result[0]["description"] == "Groceries"


def test_get_recent_transactions_no_expenses(client):
    user_id = _new_user_id(client, "notx@example.com")
    assert queries.get_recent_transactions(user_id) == []


# ---------------------------------------------------------------- #
# get_category_breakdown
# ---------------------------------------------------------------- #

def test_get_category_breakdown_with_expenses(client):
    user_id = _seed_user_id()
    result = queries.get_category_breakdown(user_id)
    assert len(result) == 7
    assert result[0]["name"] == "Shopping"
    amounts = [item["amount"] for item in result]
    assert amounts == sorted(amounts, reverse=True)
    assert sum(item["pct"] for item in result) == 100
    for item in result:
        assert isinstance(item["pct"], int)


def test_get_category_breakdown_no_expenses(client):
    user_id = _new_user_id(client, "nocat@example.com")
    assert queries.get_category_breakdown(user_id) == []


# ---------------------------------------------------------------- #
# GET /profile
# ---------------------------------------------------------------- #

def test_profile_redirects_when_not_logged_in(client):
    response = client.get("/profile")
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/login")


def test_profile_authenticated_renders_seed_user(client):
    client.post("/login", data={"email": "demo@spendly.com", "password": "demo123"})
    response = client.get("/profile")

    assert response.status_code == 200
    assert b"Demo User" in response.data
    assert b"demo@spendly.com" in response.data
    assert "₹".encode("utf-8") in response.data
    assert b"422.49" in response.data
    assert b"Shopping" in response.data
    for category in ["Food", "Transport", "Bills", "Health", "Entertainment", "Shopping", "Other"]:
        assert category.encode("utf-8") in response.data


def test_profile_new_user_zero_expenses(client):
    client.post(
        "/register",
        data={"name": "Fresh User", "email": "fresh@example.com", "password": "password123"},
    )
    client.post("/login", data={"email": "fresh@example.com", "password": "password123"})
    response = client.get("/profile")

    assert response.status_code == 200
    assert "₹0.00".encode("utf-8") in response.data
