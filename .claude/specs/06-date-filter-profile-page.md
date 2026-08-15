# Spec: Date Filter for Profile Page

## Overview
The profile page (implemented in steps 04-05) currently shows all-time
stats, recent transactions, and category breakdown for the logged-in
user, sourced from `database/queries.py`. This feature adds a date
range filter to `/profile` so the user can narrow all three sections
(summary stats, recent transactions, category breakdown) to a
specific `start_date`/`end_date` window, using the existing
`expenses.date` column (`"%Y-%m-%d"` string format). No new tables or
columns are needed — this is a query-and-route-layer change plus a
small UI addition.

## Depends on
- `01-database-setup.md` — `expenses` table with `date` column
- `04-profile-page.md` — `profile.html` structure (stats, tx table, breakdown)
- `05-backend-routes-for-profile-page.md` — `database/queries.py` and the
  live `/profile` route this feature extends

## Routes
- `GET /profile` — modify existing route to accept optional
  `start_date` and `end_date` query string params (`?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD`)
  and pass the filtered range through to stats, transactions, and
  category breakdown — logged-in only (unchanged access level)

No new routes.

## Database changes
No database changes. The `expenses.date` column (`TEXT NOT NULL`,
`"%Y-%m-%d"` format) already supports range filtering with `?`
placeholders (e.g. `date >= ? AND date <= ?`). No new index required
at current data volumes.

## Templates
- **Create:** none
- **Modify:** `templates/profile.html` — add a date filter form
  (two date inputs + submit button, likely above "Recent
  transactions") that GETs back to `/profile` with `start_date`/
  `end_date` query params; preserve selected values in the inputs
  after submit; add a "Clear filter" link back to plain `/profile`

## Files to change
- `app.py` — `profile()` route: read `start_date`/`end_date` from
  `request.args`, validate format, pass through to `queries.py`
  functions, pass current filter values to the template
- `database/queries.py` — add optional `start_date`/`end_date`
  parameters to `get_summary_stats()`, `get_recent_transactions()`,
  and `get_category_breakdown()`; append `AND date >= ? AND date <= ?`
  to each query only when both are provided, using parameterized `?`
  placeholders
- `templates/profile.html` — add filter form markup and wire it to
  display currently-applied range
- `static/css/style.css` — styles for the new filter form (reuse
  existing CSS variables, no hardcoded hex values)

## Files to create
None.

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only — never build the date clause with f-strings
- Passwords hashed with werkzeug (unaffected by this feature, but
  don't touch existing auth code)
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- Validate `start_date`/`end_date` format server-side (`YYYY-MM-DD`);
  if invalid or `start_date > end_date`, ignore the filter and show
  all-time data rather than raising a 500
- Keep all DB/filter query logic in `database/queries.py` — none of
  it belongs inline in `app.py`
- If only one of `start_date`/`end_date` is supplied, treat the
  filter as not applied (both-or-nothing) to keep query logic simple

## Definition of done
- [ ] Visiting `/profile` with no query params shows all-time data
      exactly as before (no regression)
- [ ] Visiting `/profile?start_date=2026-08-01&end_date=2026-08-15`
      shows stats, transactions, and category breakdown filtered to
      only expenses with `date` in that inclusive range
- [ ] The filter form's date inputs are pre-filled with the currently
      applied `start_date`/`end_date` after a filtered page load
- [ ] Submitting the filter form navigates via GET to `/profile` with
      the chosen `start_date`/`end_date` in the URL (bookmarkable/shareable)
- [ ] A "Clear filter" control returns to `/profile` with no query
      params and all-time data
- [ ] Supplying an invalid date (e.g. malformed string, or
      `start_date` after `end_date`) does not raise a 500 — the page
      falls back to all-time data
- [ ] Supplying only `start_date` or only `end_date` (not both) falls
      back to all-time data
- [ ] A date range with zero matching expenses renders the page with
      empty/zeroed stats and an empty transactions table, not an error
