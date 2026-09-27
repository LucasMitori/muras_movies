# Containerized frontend for `docker compose up --build`. Local native dev
# (pnpm dev) is unaffected and still the fast-reload path.
#
# Build context is the repo root (see docker-compose.yml) so this Dockerfile
# can also pick up ops/certs/extra-ca.crt: on networks that TLS-intercept
# outbound HTTPS (e.g. an antivirus web shield), Node's fetch needs that root
# CA trusted or `corepack`/`pnpm install` fail with a cert error. It's a
# no-op certificate on a normal network.
FROM node:22-alpine AS base
WORKDIR /app
COPY ops/certs/extra-ca.crt /usr/local/share/ca-certificates/extra-ca.crt
# Bootstrap problem: installing ca-certificates itself needs HTTPS to the apk
# repo, which is exactly what's untrusted before that package exists. Alpine
# publishes the same index over plain HTTP too, so use that just for this one
# install, then switch back to HTTPS for every apk command after.
RUN sed -i 's/https:/http:/' /etc/apk/repositories \
    && apk add --no-cache ca-certificates \
    && sed -i 's/http:/https:/' /etc/apk/repositories \
    && update-ca-certificates
ENV NODE_EXTRA_CA_CERTS=/usr/local/share/ca-certificates/extra-ca.crt
RUN corepack enable

FROM base AS deps
COPY web/package.json web/pnpm-lock.yaml web/pnpm-workspace.yaml ./
# --frozen-lockfile means every version is already pinned/hashed from the
# committed lockfile, so pnpm's minimum-release-age supply-chain gate (which
# guards against freshly-resolving a just-published, possibly-compromised
# version) has nothing left to protect here and only breaks reproducibility
# when a pinned package happened to publish in the last day.
RUN pnpm install --frozen-lockfile --config.minimum-release-age=0

FROM base AS build
# Baked in at build time: Nitro's route-rules proxy target is resolved when
# nuxt.config.ts loads during `nuxt build`, not at container start.
ARG NUXT_API_BASE=http://backend:8000
ENV NUXT_API_BASE=$NUXT_API_BASE
COPY --from=deps /app/node_modules ./node_modules
COPY web/ .
# Same minimum-release-age note as the install step above: `pnpm build`
# re-runs the same lockfile policy check before invoking the "build" script.
RUN pnpm --config.minimum-release-age=0 build

FROM base AS runtime
ENV NODE_ENV=production \
    NITRO_PORT=3000 \
    NITRO_HOST=0.0.0.0
# node:22-alpine already ships an unprivileged "node" user — don't run the
# app process as root inside the container.
COPY --from=build --chown=node:node /app/.output ./.output
USER node
EXPOSE 3000
CMD ["node", ".output/server/index.mjs"]
