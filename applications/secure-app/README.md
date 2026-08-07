# secure-app

Functionally identical to [`vulnerable-app`](../vulnerable-app) — same
auth, file upload, and notes endpoints. Each of `vulnerable-app`'s three
planted flaws is fixed here, with nothing else changed, so the diff between
the two apps is the fix itself.

## Fixes

| # | Flaw in `vulnerable-app` | Fix here |
|---|---|---|
| 1 | SQL injection via `q` splice in `GET /notes/search` | `q` and `user_id` are passed as bound parameters (`?` placeholders) — user input can no longer change the shape of the query. |
| 2 | Hardcoded `SECRET_KEY` in source | `SECRET_KEY` is read from the environment (`os.environ["SECRET_KEY"]`); the app raises and refuses to start if it isn't set — fails closed instead of falling back to a guessable default. |
| 3 | `Werkzeug==3.0.1` (CVE-2024-34069) | Pinned to `Werkzeug==3.0.3`, the patched release. |
| 4 | Unpinned base image + root user in `Dockerfile` | Pinned to `python:3.12.6-slim-bookworm`; dedicated `appuser` created and switched to via `USER` before the app runs (verified: `uid=999`). |

## Verified

Running the exact SQLi payload that dumps user data against
`vulnerable-app` (`q=zzz' UNION SELECT id, username, password_hash FROM
users -- `) returns `[]` here — the injection has no effect. Normal
register/login/notes/search functionality is unchanged.
