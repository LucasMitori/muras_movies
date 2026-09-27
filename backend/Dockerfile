# Containerized backend for `docker compose up --build`. Local native dev
# (uv run manage.py ...) is unaffected and still the fast-reload path.
#
# Build context is the repo root (see docker-compose.yml) so this Dockerfile
# can also pick up ops/certs/extra-ca.crt: on networks that TLS-intercept
# outbound HTTPS (e.g. an antivirus web shield), uv's own HTTPS client needs
# that root CA trusted or `uv sync` fails with a cert error. It's a no-op
# certificate on a normal network.
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_NATIVE_TLS=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

COPY ops/certs/extra-ca.crt /usr/local/share/ca-certificates/extra-ca.crt
RUN update-ca-certificates

# Install dependencies in their own layer so code-only changes don't bust the cache.
COPY backend/pyproject.toml backend/uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev

COPY backend/ .
RUN uv sync --frozen --no-dev

RUN chmod +x docker-entrypoint.sh

# Don't run the app process as root inside the container.
RUN groupadd -r app && useradd -r -g app -d /app -s /usr/sbin/nologin app \
    && mkdir -p media staticfiles \
    && chown -R app:app /app
USER app

EXPOSE 8000

ENTRYPOINT ["./docker-entrypoint.sh"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
