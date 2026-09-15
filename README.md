# School Management System — Backend (Phase 1: accounts + academics)

Django 5.2 + DRF backend. This phase scaffolds `accounts` and `academics`
per the build spec's Section 10 phasing, plus a minimal `students.Student`
stub so `Enrollment`/`Grade` have something to reference. `attendance`,
`activities`, `communications`, and `reporting` are stubbed (app configs
only, no models yet) so `INSTALLED_APPS` resolves — they're the next phase.

**Dependencies are pinned to the latest stable release of each package as
of this writing (Django 6.1.1, DRF 3.18, etc — see `requirements.txt`).**
Verified with a clean-room `pip install -r requirements.txt` into a fresh
virtualenv, followed by `check` / `migrate` / `seed_data` / the full API
smoke test — all passing. Re-run `pip list --outdated` periodically and
re-verify with `smoke_test.py` before bumping further, since Django major
version bumps (5→6) have changed model API surface before (e.g.
`CheckConstraint` moved from `check=` to `condition=` in 5.1+).

## Setup

```bash
cp .env.example .env          # edit values — SECRET_KEY must be 32+ bytes (djangorestframework-simplejwt
                               # warns/HMAC-weakens below that; the .env.example placeholder is NOT production-safe)
docker compose up --build     # web (8000), worker, beat, db, redis
docker compose exec web python manage.py migrate
docker compose exec web python manage.py seed_data
```

Local (non-Docker) dev:

```bash
pip install -r requirements.txt --break-system-packages
# point DATABASE_URL at sqlite:///db.sqlite3 in .env for a quick start
python manage.py migrate
python manage.py seed_data
python manage.py runserver
```

Seed data creates three users (password `ChangeMe123!` for all):
`admin@school.example.com`, `teacher@school.example.com`,
`student@school.example.com`, plus one `Subject` (MATH101) and one
`Class` (G8B, 2025-2026).

API docs: `/api/docs/` (Swagger) and `/api/redoc/` once the server is running.

## RBAC design

- **No custom user model.** `accounts.Profile` is a 1:1 extension of
  Django's built-in `User` carrying `role` (admin/teacher/student/parent)
  + contact fields. This keeps `django.contrib.auth`'s admin, password
  validators, and permission plumbing stock. A `post_save` signal
  (`accounts/signals.py`) guarantees every `User` gets a `Profile` even if
  created outside `RegisterSerializer` (e.g. `createsuperuser`), so
  `request.user.profile` never raises `DoesNotExist` inside a permission
  class.
- **Permission classes live in one place** (`accounts/permissions.py`) and
  are composed per-viewset rather than duplicated: `IsAdmin`, `IsTeacher`,
  `IsStudent`, `IsParent`, `IsAdminOrTeacher` (staff-facing writes —
  grades, attendance), `ReadOnlyOrAdmin` (reference data like Subjects
  that everyone reads but only admins curate), `IsOwnerOrAdmin`
  (object-level: a user can act on their own record, admin can act on
  any).
- **Role is read-only on the self-service profile endpoint.** A user can
  PATCH their own phone/address/photo via `/api/accounts/profiles/me/`,
  but can't promote themselves — role changes are intentionally left as a
  separate admin-only action for a later phase.

## JWT design

- `djangorestframework-simplejwt`, access token 15 min / refresh 7 days
  (both from `.env`, not hardcoded), rotation + blacklist-after-rotation
  enabled so a leaked refresh token can't be replayed indefinitely.
- `RoleAwareTokenObtainPairSerializer` embeds `role` and `email` directly
  in the access token payload. The React app can pick the correct
  dashboard immediately after login without a second round-trip to
  `/me/` — this was a deliberate latency trade-off given Section 4.2's
  "role-based redirect" requirement.
- Auth endpoints (`/api/auth/login/`, `/api/auth/register/`) are throttled
  at 100/hour via DRF's `ScopedRateThrottle` (`throttle_scope = "auth"`),
  matching Section 3's rate-limit requirement. The throttle cache is
  Redis-backed (`django-redis`), so the limit is enforced consistently
  across all Gunicorn workers, not per-process.

## Business rules enforced at two layers

Per Section 5, each rule is enforced both at the DB level (so it holds
even under a race condition or a direct DB write) and re-validated in the
serializer (so the API returns a clean 400 instead of a raw
`IntegrityError`):

| Rule | DB constraint | Serializer check |
|---|---|---|
| Grade score 0–100 | `CheckConstraint` on `Grade` | `validate_score` |
| No duplicate enrollment (student+class+year) | `UniqueConstraint` on `Enrollment` | `validate()` |
| Class code unique per academic_year | `UniqueConstraint` on `Class` | `validate()` |

Grade creates/updates also write to `accounts.AuditLog` via the
`accounts.audit.record(...)` helper, capturing actor, old/new value, and
resolved client IP (`accounts/middleware.py` resolves `X-Forwarded-For`
consistently behind a proxy).

## Sample API calls
```bash
# Register (role picks which extra fields the React multi-step form should show)
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"email":"t@school.example.com","password":"SuperSecret123!","first_name":"Nina","last_name":"Newteacher","role":"teacher"}'

# Login — response includes access/refresh JWTs; access token payload has `role`
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"t@school.example.com","password":"SuperSecret123!"}'

# Authenticated request
curl http://localhost:8000/api/accounts/profiles/me/ \
  -H "Authorization: Bearer <access_token>"

# Create a grade (admin/teacher only; 0-100 enforced both layers)
curl -X POST http://localhost:8000/api/academics/grades/ \
  -H "Authorization: Bearer <access_token>" -H "Content-Type: application/json" \
  -d '{"enrollment": 1, "subject": 1, "score": 87.5}'
```

All of the above (register, duplicate-email rejection, unauthenticated
401, role-based 403s, duplicate-class 400, out-of-range-score 400, audit
log writes) are exercised in `smoke_test.py` using DRF's `APIClient` —
run it against a fresh `migrate` + `seed_data` to verify the scaffold.

## Assumptions / open questions (per spec Section 10, item 6)

- **Single-school deployment.** Multi-tenancy would need a `School` FK on
  `Profile`/`Class`/etc. and isolation middleware/queryset scoping — not
  built here.
- **Real-time features** (live notifications, chat) would mean adding
  Django Channels + a Redis-backed channel layer; none of the current
  models assume it.
- **Threaded/inbox messaging** (Section 3's `communications` app) isn't
  scaffolded yet — the `Message`/`Announcement` models and recipient
  scoping logic are next-phase work.

## Next phases (not built yet)

1. `students` app: full admission workflow, document uploads, DOB
   validation (currently a minimal stub lives in `students/models.py`).
2. `attendance`, `activities` (assignments + Celery due-date reminders),
   `communications` (recipient-scoped messaging + rate limiting),
   `reporting` (Redis-cached aggregate endpoints).
3. OpenAPI-generated TypeScript client + the React/Figma frontend
   (Section 4).
4. Tests (pytest-django + factory_boy, ≥85% coverage), GitHub Actions
   CI/CD, Sentry wiring.
