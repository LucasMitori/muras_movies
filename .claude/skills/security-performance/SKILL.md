---
name: security-performance
description: Run a combined security and performance audit of Muratori (Django backend, Nuxt frontend, Docker/infra), then fix what's found rather than only reporting it. Use when asked to audit, scan, harden, or check the project for security or performance problems.
---

# Security & performance audit — Muratori

Two passes over the current working tree, then fix, then verify. Don't stop at a report —
the point of this skill is a codebase that's measurably better after it runs, not a list.

## 1. Security pass

Invoke the `maruth-security` skill first for the general OWASP-style sweep (secrets, injection,
supply chain, headers). On top of that, specifically check this project's own risk areas:

- **`backend/config/settings/base.py`, `dev.py`, `prod.py`**: `SECRET_KEY` default, `DEBUG`
  default, `ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS` / `CSRF_TRUSTED_ORIGINS`, session/CSRF cookie
  flags (`SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`, `SESSION_COOKIE_SAMESITE`). Confirm `prod.py`
  can't accidentally run with dev-safe (insecure) values.
- **`docker-compose.yml`**: hardcoded `DJANGO_SECRET_KEY` and the seeded superuser password
  (`DJANGO_SUPERUSER_EMAIL`/`PASSWORD`). These are deliberate for local/dev seeding — flag if
  anything suggests this compose file might be reused as-is for a real deployment, and confirm the
  README is explicit that these are dev-only defaults to override.
- **`backend/apps/accounts/management/commands/ensure_admin.py`**: confirm it can't be triggered
  with an empty/weak password via unset env vars, and that it only ever grants staff/superuser to
  the one configured account.
- **DRF views/serializers** (`apps/*/views.py`, `apps/*/serializers.py`): every viewset's
  `get_queryset`/permission classes actually scope to the requesting user where the data is
  private (library entries, ratings, reviews) — re-check `apps/library` privacy rules specifically,
  since that's the app with the most cross-user access-control surface.
- **Auth throttling**: `DEFAULT_THROTTLE_RATES["auth"]` in `base.py` is actually applied to
  login/register/password-adjacent views, not just declared.
- **Nuxt** (`web/app/composables/useApi.ts`, any `v-html` usage): CSRF token is only echoed on
  mutating requests, cookies aren't logged, no raw HTML interpolation of user-supplied content.
- **Docker images**: containers don't run unnecessarily as root where avoidable, no secrets appear
  in image layers (check `docker history`), `ops/certs/extra-ca.crt` stays documented as a
  local-network dev artifact and isn't presented as something every deployment needs.
- **Dependencies**: skim `backend/uv.lock` and `web/pnpm-lock.yaml` for pinned versions with known
  CVEs.

## 2. Performance pass

- **N+1 queries**: grep `apps/*/views.py` and `serializers.py` for foreign-key/related-field access
  without `select_related`/`prefetch_related` — the catalog list/detail and library endpoints are
  the highest-traffic paths.
- **Missing indexes**: check `apps/*/models.py` for fields used in frequent `filter()`/`order_by()`
  (catalog search, library-by-user lookups) that lack `db_index=True` or a model-level index.
- **Rating aggregation** (`apps/library/signals.py`): confirm the synchronous
  `transaction.on_commit` recompute is still O(1)-ish per write and won't degrade as review counts
  grow; note if it should move to async/batched before that becomes a problem, without adding
  Celery speculatively.
- **Pagination**: `DEFAULT_PAGINATION_CLASS`/`PAGE_SIZE` in `base.py` actually applies to every
  list endpoint that could return unbounded rows.
- **Nuxt bundle**: no accidental duplicate client-side fetch of data already provided by SSR;
  `nuxt build` output size is reasonable for what's shipped (`web/.output`).
- **Docker build**: layer order in `backend/Dockerfile` / `web/Dockerfile` still installs
  dependencies before copying source (cache-friendly); image sizes aren't bloated by leftover
  build artifacts in the final stage.

## 3. Fix and verify

- Apply fixes directly, smallest correct change first — this is a small alpha-scope app; don't
  introduce Celery/Redis/new infra to fix a performance issue that a query change or index solves.
- After fixing, run: `cd backend && uv run pytest && uv run ruff check .` and
  `cd web && pnpm lint`.
- If the Docker stack is running (`docker compose ps`), re-check the affected endpoints respond
  correctly after the fix (`curl` through both `localhost:8000` directly and `localhost:3000/api/**`
  via the Nuxt proxy).
- Close with a concise before/after: what was found, what was fixed, and what was deliberately left
  alone (with the reason — e.g. "not worth Celery at alpha scale").
