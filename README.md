# Muratori

A cozy, personal-journal-meets-social platform for discovering, tracking, rating, and discussing
movies and TV series (Phase 1 alpha scope — see `docs/MURATORI_MASTER_PROMPT.md` for the full
product spec this was built from).

This repository currently implements the **Phase 1 core slice**: accounts, catalog (TMDB-backed),
personal library, ratings, and reviews — end-to-end, with the acceptance path proven working:
register → browse an imported title → rate/track it → data persists in PostgreSQL → another user is
correctly denied access to your rating.

## Stack

- **Backend**: Django 5.2 + Django REST Framework + PostgreSQL, managed with `uv`.
- **Frontend**: Nuxt 4 + Vuetify 4 (via `vuetify-nuxt-module`, currently at `1.0.0-rc.6`) + Pinia +
  TypeScript, using standard Vue templates (not Pug — see decision note below).
- **Auth**: same-origin Django session cookies + CSRF, proxied through Nuxt's dev/route-rules proxy
  so the browser only ever talks to one origin.
- **Catalog source**: TMDB (non-commercial use per their terms; revisit licensing before any
  commercial launch).

## Repo layout

```
backend/   Django project (apps/accounts, apps/catalog, apps/library)
web/       Nuxt 4 frontend
ops/       docker-compose.dev.yml (local Postgres only)
docs/      Original planning prompt and findings this build followed
```

## Running it locally

### Option A: full Docker stack

```
docker compose up --build
```

Builds and runs Postgres, the Django backend, and the Nuxt frontend together. On every start the
backend container automatically runs migrations and seeds one admin account via
`manage.py ensure_admin` (idempotent — safe to rebuild/restart repeatedly):

- email: `devmitori@gmail.com`
- password: `Admin@Movies2026`

Visit http://localhost:3000 for the app or http://localhost:8000/admin for the Django admin.
Override the seeded credentials with the `DJANGO_SUPERUSER_EMAIL` / `DJANGO_SUPERUSER_PASSWORD` /
`DJANGO_SUPERUSER_USERNAME` environment variables on the `backend` service in `docker-compose.yml`.

### Option B: native dev (fast reload)

1. **Database** (containerized so nobody has to guess a native Postgres password):
   ```
   docker compose -f ops/docker-compose.dev.yml up -d
   ```
   Exposes Postgres on host port **5433** (5432 was already taken by a native install on this
   machine — adjust `ops/docker-compose.dev.yml` and `backend/.env` if yours is free).

2. **Backend**:
   ```
   cd backend
   cp .env.example .env      # already done in this checkout; edit TMDB_API_KEY if you have one
   uv run manage.py migrate
   uv run manage.py createsuperuser
   uv run manage.py runserver 8000
   ```

3. **Frontend**:
   ```
   cd web
   pnpm install
   pnpm dev
   ```
   Visit http://localhost:3000. API calls proxy to `http://localhost:8000` (override with
   `NUXT_API_BASE`).

4. **Seed the catalog** (requires a free TMDB API key — https://www.themoviedb.org/settings/api):
   ```
   cd backend
   uv run manage.py import_tmdb_popular --pages 2
   # or a single title:
   uv run manage.py import_tmdb_movie 27205
   ```
   Without a key, you can still smoke-test by creating a `MediaItem` via `manage.py shell` or the
   Django admin at `/admin/`.

## Testing / linting

```
cd backend && uv run pytest && uv run ruff check .
cd web && pnpm lint
```

12 backend tests currently cover: rating/library/review uniqueness constraints, the Bayesian rating
aggregate, cross-user permission denial (a user cannot edit another user's review or see their
private library/rating rows), and the register/login/logout session flow.

## What's deliberately not built yet

Per the phased scope in `docs/MURATORI_MASTER_PROMPT.md`: communities, competitions/challenges,
Celery/background jobs, mobile/Capacitor, the Chrome extension, books/audio media types, and
episode-level tracking. The `library.ReviewComment` model exists (bounded one-level reply tree) but
has no frontend UI yet.

## Decisions made without a live approval round

This was built directly from the planning doc's own **recommended defaults**, since the doc was fed
into an active build request rather than a separate planning-only conversation. Flagging the calls
that matter most in case any should be revisited:

- **Standard Vue templates, not Pug** — user confirmed this trade-off explicitly when asked.
- **Rating scale**: 0.5–5 stars in half-star steps, stored as integers 1–10 (spec's proposed default).
- **`vuetify-nuxt-module@1.0.0-rc.6`**: verified via published npm metadata that it declares
  `vuetify: '^3.4.0 || ^4.0.0'` as a peer dependency — genuine v4 support, but it's still a
  release-candidate, not a final 1.0. Revisit once it ships stable.
- **Auth**: hand-rolled session endpoints (register/login/logout/me) rather than django-allauth
  headless, to keep the first slice small. Revisit allauth if email verification / social login /
  password reset flows are needed — those aren't implemented yet.
- **No Celery/Redis yet**: the rating aggregate recomputes synchronously (via `transaction.on_commit`)
  since alpha-scale traffic doesn't need a queue yet. TMDB imports run as management commands, not
  background jobs.
- **Postgres dev port 5433, not 5432**: this machine already had a native PostgreSQL service bound
  to 5432. `ops/docker-compose.dev.yml` and `backend/.env` are wired to 5433 consistently — adjust
  both together if you move it.
- **Node 22.18.0 vs Nuxt 4.5.2's declared `engines` requirement (`^22.19.0`)**: one patch below what
  Nuxt's package.json asks for. Nothing broke in testing, but worth upgrading Node before relying on
  this long-term.
