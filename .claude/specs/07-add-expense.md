# Spec: Add Expense

## Overview
This feature implements Step 7 of the Spendly roadmap: letting a logged-in
user record a new expense. It replaces the `GET /expenses/add` stub with a
real form page and a `POST` handler that validates input and inserts a row
into the `expenses` table. An entry point is added to the profile page so
users can reach the form, and after a successful submission the user is
returned to their profile where the new expense appears in recent
transactions, summary stats, and the category breakdown.

## Depends on
- Step 1 — Database setup (`users`/`expenses` tables, `get_db()`)
- Step 3 — Login/Logout (session-based auth, `session["user_id"]`)
- Step 4/5/6 — Profile page (entry point lives here; reuses `queries.py` data
  shapes for consistency)

## Routes
- `GET /expenses/add` — render the add-expense form — logged-in only
- `POST /expenses/add` — validate form input, insert expense, redirect to
  profile — logged-in only

If the user is not logged in, redirect to `/login` (same pattern as
`profile()` in `app.py`).

## Database changes
No database changes. The `expenses` table already has the required columns
(`user_id`, `amount`, `category`, `date`, `description`) from
`database/db.py`. No new tables, columns, or constraints needed.

## Templates
- **Create:** `templates/add_expense.html` — form with fields: amount
  (number), category (select, using the fixed category set already seeded:
  Food, Transport, Bills, Health, Entertainment, Shopping, Other), date
  (date input, defaulting to today), description (text, optional). Extends
  `base.html`. Shows validation errors inline, same pattern as
  `register.html`/`login.html`.
- **Modify:** `templates/profile.html` — add an "Add expense" button/link
  near the profile header or above "Recent transactions", pointing to
  `url_for('add_expense')`.

## Files to change
- `app.py` — implement `add_expense()` for both GET and POST, replacing the
  stub
- `templates/profile.html` — add the "Add expense" entry point link
- `static/css/style.css` — styles for the add-expense form and the new
  profile button (reuse existing `.form-input`, `.btn-primary` classes where
  possible; add new rules only if needed)

## Files to create
- `templates/add_expense.html`
- `database/queries.py` — add `create_expense(user_id, amount, category,
  date, description)` function (data-access logic belongs here, not inline
  in the route, matching the pattern already used for profile page queries)

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only (`?` placeholders)
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- DB logic goes in `database/queries.py` (or `database/db.py`), never inline
  in `app.py` routes
- Route function does one thing: fetch/validate, call query helper, render
  or redirect
- Validate on the server: amount must be a positive number, category must be
  one of the fixed set, date must be a valid `YYYY-MM-DD` string, description
  optional
- Use `url_for()` for all internal links — never hardcode URLs
- Redirect unauthenticated users to `/login`, matching the existing
  `profile()` pattern

## Definition of done
- [ ] Visiting `/expenses/add` while logged out redirects to `/login`
- [ ] Visiting `/expenses/add` while logged in renders a form with amount,
      category, date, and description fields
- [ ] Submitting the form with valid data inserts a new row into `expenses`
      for the current user and redirects to `/profile`
- [ ] The newly added expense appears in profile's recent transactions,
      updates the total spent stat, transaction count, and category
      breakdown
- [ ] Submitting with a missing/invalid amount (blank, zero, negative,
      non-numeric) re-renders the form with an inline error and does not
      insert a row
- [ ] Submitting with an invalid category re-renders the form with an
      inline error and does not insert a row
- [ ] Submitting with a missing/invalid date re-renders the form with an
      inline error and does not insert a row
- [ ] Description is optional — submitting without one succeeds
- [ ] Profile page shows a visible "Add expense" link/button that navigates
      to `/expenses/add`
- [ ] All new SQL uses parameterized queries (`?` placeholders)
