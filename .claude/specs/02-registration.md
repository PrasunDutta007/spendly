# Spec: Registration

## Overview
This step implements user registration for Spendly. `GET /register` currently
only renders a static form with no backend handling. This step adds a
`POST /register` handler that validates the submitted form, checks for
duplicate emails, hashes the password, inserts the new user into the
`users` table, and starts a logged-in session for the new user. This is the
first step where the app writes to the database from a route and the first
step where server-side sessions are introduced, laying the groundwork for
login (Step 3 area) and the profile/expense features that depend on
`session['user_id']`.

## Depends on
- Step 01 — Database setup (`database/db.py`: `get_db()`, `init_db()`, `users` table) — complete.

## Routes
- `GET /register` — renders the registration form, re-used to redisplay on validation error — public
- `POST /register` — validates input, creates the user, logs them in, redirects — public

## Database changes
No database changes. The existing `users` table (`id`, `name`, `email`,
`password_hash`, `created_at`) already supports registration. `POST /register`
will use a new `database/db.py` helper (e.g. `create_user(name, email,
password_hash)` and `get_user_by_email(email)`) rather than inline SQL in
`app.py`.

## Templates
- **Create:** none
- **Modify:** `templates/register.html` — change the hardcoded form
  `action="/register"` to `action="{{ url_for('register') }}"`; ensure the
  `{% if error %}` block surfaces validation/duplicate-email errors returned
  by the route.

## Files to change
- `app.py` — add `secret_key` config (required for sessions), change
  `@app.route("/register")` to accept `methods=["GET", "POST"]`, add
  validation + registration logic, set `session['user_id']` on success,
  redirect to `profile` (or `landing` until Step 4 implements `/profile`,
  per the "do not implement a stub route" rule — redirect target should be
  the existing stub route, not a newly built page).
- `database/db.py` — add `create_user(name, email, password_hash)` and
  `get_user_by_email(email)` functions; all SQL stays here, not in `app.py`.
- `templates/register.html` — fix hardcoded form action to use `url_for()`.

## Files to create
None.

## New dependencies
No new dependencies. `werkzeug.security` (`generate_password_hash`) is
already used in `database/db.py`.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only (`?` placeholders), all SQL lives in `database/db.py`
- Passwords hashed with `werkzeug.security.generate_password_hash` before storage — never store plaintext
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- Use `url_for()` for every internal link/redirect/form action — never hardcode URLs
- Validate on the server even though the form has `required`/`type="email"` attributes (client-side validation is not trustworthy)
- Duplicate email must be rejected with a friendly error re-rendered on `register.html`, not a raw 500/IntegrityError
- Route function stays thin: parse form, call `db.py` helpers, render/redirect — no SQL inline

## Definition of done
- [ ] Visiting `GET /register` still renders the form unchanged
- [ ] Submitting the form with a new name/email/password creates a row in `users` with a hashed (non-plaintext) password
- [ ] After successful registration, the user is redirected away from `/register` and `session['user_id']` is set
- [ ] Submitting with an email that already exists (e.g. `demo@spendly.com`) re-renders `register.html` with an error message and does not create a duplicate row
- [ ] Submitting with a missing required field re-renders the form with an error instead of crashing
- [ ] The form's `action` uses `url_for('register')` instead of a hardcoded `/register` string
- [ ] App starts and runs on port 5001 without errors
