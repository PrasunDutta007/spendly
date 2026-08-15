from datetime import datetime, timedelta

import database.db as db_module


def login(client):
    return client.post(
        "/login",
        data={"email": "demo@spendly.com", "password": "demo123"},
    )


def fmt(days_ago):
    return (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")


# Seeded expenses (database/db.py seed_db()), offsets in days-ago from "today":
# 0  Food          Groceries          30.00
# 1  Transport     Bus pass           12.00
# 2  Bills         Electricity bill   89.99
# 3  Health        Pharmacy           25.00
# 5  Entertainment Movie night        60.00
# 7  Shopping      New shoes         150.00
# 9  Other         Misc               10.00
# 11 Food          Restaurant         45.50
# All-time total: 422.49 across 8 transactions.
# Range [today-3 .. today] covers offsets 0,1,2,3: 30 + 12 + 89.99 + 25 = 156.99, 4 txns.


def test_no_query_params_shows_all_time_data(client):
    login(client)
    response = client.get("/profile")
    assert response.status_code == 200
    assert b"422.49" in response.data


def test_valid_range_filters_stats_transactions_and_breakdown(client):
    login(client)
    start = fmt(3)
    end = fmt(0)
    response = client.get(f"/profile?start_date={start}&end_date={end}")
    assert response.status_code == 200
    body = response.data

    # filtered stats total should appear, all-time total should not
    assert b"156.99" in body
    assert b"422.49" not in body

    # transactions inside the range are present
    assert b"Groceries" in body
    assert b"Bus pass" in body
    assert b"Electricity bill" in body
    assert b"Pharmacy" in body

    # transactions outside the range are excluded
    assert b"Movie night" not in body
    assert b"New shoes" not in body
    assert b"Misc" not in body
    assert b"Restaurant" not in body

    # category breakdown reflects only in-range categories
    assert b"Shopping" not in body
    assert b"Entertainment" not in body


def test_date_inputs_prefilled_after_filtered_load(client):
    login(client)
    start = fmt(3)
    end = fmt(0)
    response = client.get(f"/profile?start_date={start}&end_date={end}")
    body = response.data.decode()
    assert f'id="start_date" name="start_date" class="form-input" value="{start}"' in body
    assert f'id="end_date" name="end_date" class="form-input" value="{end}"' in body


def test_clear_filter_link_present_when_filtered(client):
    login(client)
    start = fmt(3)
    end = fmt(0)
    response = client.get(f"/profile?start_date={start}&end_date={end}")
    assert b"Clear filter" in response.data


def test_clear_filter_link_absent_when_not_filtered(client):
    login(client)
    response = client.get("/profile")
    assert b"Clear filter" not in response.data


def test_invalid_date_format_falls_back_to_all_time(client):
    login(client)
    response = client.get(f"/profile?start_date=not-a-date&end_date={fmt(0)}")
    assert response.status_code == 200
    assert b"422.49" in response.data
    assert b"Clear filter" not in response.data


def test_reversed_range_falls_back_to_all_time(client):
    login(client)
    start = fmt(0)
    end = fmt(3)
    response = client.get(f"/profile?start_date={start}&end_date={end}")
    assert response.status_code == 200
    assert b"422.49" in response.data
    assert b"Clear filter" not in response.data


def test_only_start_date_supplied_falls_back_to_all_time(client):
    login(client)
    response = client.get(f"/profile?start_date={fmt(3)}")
    assert response.status_code == 200
    assert b"422.49" in response.data
    assert b"Clear filter" not in response.data


def test_only_end_date_supplied_falls_back_to_all_time(client):
    login(client)
    response = client.get(f"/profile?end_date={fmt(0)}")
    assert response.status_code == 200
    assert b"422.49" in response.data
    assert b"Clear filter" not in response.data


def test_range_with_no_matching_expenses_returns_empty_state(client):
    login(client)
    start = fmt(-20)  # 20 days in the future
    end = fmt(-30)    # 30 days in the future
    response = client.get(f"/profile?start_date={start}&end_date={end}")
    assert response.status_code == 200
    body = response.data

    # no all-time or in-range totals should leak through
    assert b"422.49" not in body
    for desc in (b"Groceries", b"Bus pass", b"Electricity bill", b"Pharmacy",
                 b"Movie night", b"New shoes", b"Misc", b"Restaurant"):
        assert desc not in body


def test_profile_requires_login(client):
    response = client.get("/profile?start_date=2026-08-01&end_date=2026-08-15")
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/login")
