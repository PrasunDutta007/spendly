# Spec: Login and Logout

## Overview
This step implements authentication for Spendly. `GET /login` currently only
renders a static form with no backend handling, and `GET /logout` is an
unimplemented stub that returns a raw string. This step adds a `POST /login`
handler that validates credentials against the `users` table and starts a
server-side session, and implements `GET /logout` to clear that session.
`app.py` currently has no `secret_key` configured and never imports `session`
— this step introduces both, since Flask sessions require a secret key to
sign the session cookie. This is the step that makes `session['user_id']`
a reliable signal for future steps (profile, expenses) to know who is
logged in.

## Depends on
- Step 01 — Database setup (`database/db.py`: `get_db()`, `init_db()`, `users` table) — complete.
- Step 02 — Registration (`database/db.py`: `get_user_by_email()`; `users` table populated with hashed passwords) — complete.

## Routes
- `GET /login` — renders the login form, re-used to redisplay on validation error — public
- `POST /login` — validates credentials, starts session, redirects — public
- `GET /logout` — clears the session, redirects to landing — logged-in

## Database changes
No database changes. The existing `users` table (`id`, `name`, `email`,
`password_hash`, `created_at`) and the existing `get_user_by_email(email)`
helper in `database/db.py` are sufficient to look up a user for login. No new
`database/db.py` helpers are required for this step.

## Templates
- **Create:** none
- **Modify:** `templates/login.html` — change the hardcoded form
  `action="/login"` to `action="{{ url_for('login') }}"`; the existing
  `{% if error %}` block already surfaces errors returned by the route, no
  change needed there.

## Files to change
- `app.py` — import `session` from `flask` and `check_password_hash` from
  `werkzeug.security`; set `app.secret_key` (required for signed session
  cookies); change `@app.route("/login")` to accept
  `methods=["GET", "POST"]` and add credential validation logic that sets
  `session['user_id']` on success; implement `GET /logout` to call
  `session.clear()` (or `session.pop('user_id', None)`) and redirect to
  `landing`, replacing the current stub string return.
- `templates/login.html` — fix hardcoded form action to use `url_for()`.

## Files to create
None.

## New dependencies
No new dependencies. `werkzeug.security` (`check_password_hash`) and
`flask.session` are already available via the existing Flask/Werkzeug
install.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only (`?` placeholders), all SQL lives in `database/db.py`
- Passwords hashed with `werkzeug.security` — use `check_password_hash` to verify against the stored hash, never compare plaintext
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- Use `url_for()` for every internal link/redirect/form action — never hardcode URLs
- Validate on the server even though the form has `required`/`type="email"` attributes (client-side validation is not trustworthy)
- Invalid email or wrong password must be rejected with a single generic friendly error (e.g. "Invalid email or password") re-rendered on `login.html` — do not reveal whether the email exists or the password was wrong, and never a raw 500
- `GET /logout` must actually clear the session — no raw string return now that this step implements it
- Route functions stay thin: parse form, call `db.py` helpers, render/redirect — no SQL inline
- Do not touch `/profile` or `/expenses/*` stub routes — those belong to later steps

## Definition of done
- [ ] Visiting `GET /login` still renders the form unchanged
- [ ] Submitting valid credentials for an existing user (e.g. `demo@spendly.com` / `demo123`) sets `session['user_id']` and redirects away from `/login`
- [ ] Submitting an unknown email re-renders `login.html` with a generic "Invalid email or password" error and does not crash
- [ ] Submitting a known email with the wrong password re-renders `login.html` with the same generic error and does not crash
- [ ] Visiting `GET /logout` after logging in clears the session and redirects to the landing page
- [ ] Visiting `GET /logout` when not logged in does not crash
- [ ] The login form's `action` uses `url_for('login')` instead of a hardcoded `/login` string
- [ ] App starts and runs on port 5001 without errors
