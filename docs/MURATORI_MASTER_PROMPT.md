# Muratori — master planning prompt

Draft for owner review, prepared 2026-09-16. Copy everything after the divider into a new planning conversation, or ask the planning agent to read this file. Recommendations are proposals until approved. This document authorizes planning only.

---

Act as a senior product architect and fullstack technical lead. Help me finalize an implementation-ready specification for **Muratori**, a welcoming social platform for discovering, tracking, rating, and discussing cultural media. Be concrete, question weak assumptions, and keep the design maintainable by a small team.

**1. Working agreement and deliverable**

We are in the planning phase. Do not write application code, scaffold projects, install dependencies, generate migrations, import data, provision infrastructure, or deploy anything. Read-only research and reference inspection are allowed. Produce a detailed specification for my review. Wait for my explicit approval before implementation; approval of the specification alone is not an instruction to implement every future phase.

Distinguish owner requirements, recommended defaults, alternatives, and unresolved decisions. Make reasonable provisional assumptions so unanswered questions do not prevent useful planning, but never present those assumptions as my approval. Ask a short prioritized set of questions at the end, with recommended answers and consequences. Explain technical terms where they affect a decision.

Use current official documentation and release information. State the research date and link sources near claims. Never invent package versions, compatibility, prices, licensing rights, or maintenance status. If something cannot be verified, label it unverified and propose a way to validate it after approval.

**2. Product vision and audience**

Muratori should feel modern, cozy, personal, and inviting. It combines a personal media journal with thoughtful social discussion and optional friendly competitions. Users should be able to discover a title, save it, record their experience, rate it, write a review, and connect around shared interests.

The long-term scope includes movies, TV series, books, and audio. Clarify whether audio means music, podcasts, audiobooks, or several distinct types. Do not treat these as interchangeable domains. The initial recommendation is movies and TV series, with an explicit extension path for other media.

Assume metadata, artwork, links, and user discussion only. Hosting or streaming copyrighted movies, music, ebooks, or audiobooks is outside the proposed scope. Official trailer embeds may be considered separately.

Confirm target countries, languages, age audience, accessibility needs, commercialization plans, and whether the project is primarily a portfolio, community service, or commercial product. Propose Brazilian Portuguese first and English-ready localization as a provisional default, not an established requirement.

Define success around useful engagement: users recording their first title, returning to their journals, meaningful discussions, and manageable moderation load. Avoid making maximum screen time the primary success criterion.

**3. Scope and release boundaries**

Propose these phases with dependencies, acceptance criteria, effort ranges, and scope cuts. Estimates must state team-size and availability assumptions.

Phase 0 — approved specification: architecture decisions, domain model, permission matrix, core journeys, dependency compatibility matrix, provider constraints, operating budget assumptions, and implementation backlog.

Phase 1 — private alpha: account registration and verification; login, logout, recovery; profiles and privacy settings; searchable movie/TV catalog; dynamic title pages; personal library statuses; viewing diary; ratings; one editable review per user/title; review comments with bounded replies; curated/user lists; basic follows and chronological activity; report/block/mute; staff moderation; and catalog synchronization. Start with text reviews and avatars, avoiding arbitrary attachments.

Phase 2 — public beta: small communities with scoped memberships and moderation, posts, in-app notifications, one optional monthly challenge and leaderboard, discovery improvements, and the operational/security/accessibility checks needed for public launch. Communities and competition are part of the intended product, but need not delay a useful private alpha.

Phase 3 — mobile: responsive web and PWA readiness first, then Android/iOS packaging or dedicated clients based on explicit device requirements. Include push notification preferences, deep links, secure authentication, and limited offline behavior.

Phase 4 — expansion: books and specifically defined audio types, Chrome extension, richer recommendations, richer competitions, and additional community features.

Defer direct messaging, live chat, payments, AI recommendations, video/audio uploads, a general-purpose visual page builder, and large realtime infrastructure unless an approved user journey requires them. Record useful ideas in a later backlog: collaborative lists, community watch/read clubs, year-in-review, spoiler-aware episode discussions, taste overlap, and accessible share cards.

**4. Stack and dependency policy**

My preferred frontend is Nuxt 4, Vue, Vuetify 4, Pinia, TypeScript, ESLint, SCSS, Pug, charts, and possibly Vue Flow. My preferred backend is Django, Python, and uv. Evaluate these preferences explicitly; do not silently replace them.

Recommend Nuxt 4 with SSR/hybrid rendering for public discovery and title pages. Use Pinia for client/session-facing state, and Nuxt data fetching for server data. Do not duplicate every API response in a global store. Keep stores and authentication state isolated between SSR requests.

Use Vuetify 4 as the preferred UI baseline, subject to a verified Nuxt/Vite/SSR/i18n integration matrix. Verify whether the chosen Nuxt module release actually supports that combination; an open-ended peer dependency is not sufficient evidence. If a supported module is unavailable, assess documented direct integration or present a supported alternative for approval. Do not automatically fall back to prereleases or downgrade the owner's preferred major version.

Prefer strict TypeScript, ESLint with Nuxt/Vue support, SCSS design tokens, and one JavaScript package manager with a committed lockfile. Propose pnpm, but account for team preferences. Use the supported Node LTS compatible with all selected tools.

Evaluate Pug against Vue template tooling, linting, editor support, contributor readability, and maintenance evidence. The proposed alternative is standard Vue templates; adopting it requires agreement because Pug is an expressed preference. Pug must only compile trusted repository templates, never user-supplied templates.

Assess these candidates without installing them merely because they appear in this list:

| Area | Candidate/default | Admission rule |
| --- | --- | --- |
| UI state | Pinia and its Nuxt integration | Minimal durable client state; no persisted bearer secrets |
| Forms | VeeValidate plus one schema library such as Zod | Demonstrable need for complex reusable forms; verify matching versions |
| Utilities | VueUse | Add for concrete composables, not as a blanket dependency |
| Localization | Nuxt i18n | Confirm locales, SSR, and Vuetify compatibility |
| Images | Nuxt Image or a documented CDN image pipeline | Restrict remote sources; account for transformation cost |
| Charts | Chart.js with vue-chartjs | Lazy-load when an approved statistics screen needs it; accessible text/table fallback |
| Flow editor | Vue Flow | Defer until a real node/edge editing use case exists |
| Rich editor | Tiptap or a restricted Markdown solution | Defer rich content until moderation and sanitization are specified |
| PWA | Maintained Nuxt/Vite PWA integration | Explicit cache/update/offline policy; no private response leakage |
| Frontend checks | Vitest, Vue Test Utils/Nuxt test tools, Playwright, axe-core | Verify contracts, journeys, SSR, and accessibility |
| API | Django REST Framework | One API framework; no parallel DRF/Ninja stack |
| API schema | drf-spectacular and a compatible TypeScript generator | Publish a reviewed OpenAPI contract and detect drift |
| Authentication | Django sessions and django-allauth headless | Confirm DRF integration and chosen browser/mobile flows |
| Database driver | Psycopg 3 | Match Django/Python/PostgreSQL support |
| Filtering | django-filter | Allowlisted, bounded filters and ordering |
| Jobs | Celery plus one supported broker | Imports, notifications, image work, aggregation; retry-safe tasks |
| Cache/broker | Redis, or Valkey after compatibility validation | Separate cache eviction concerns from job delivery; justify license/hosting choice |
| HTTP clients | HTTPX | Timeouts, bounded retries, provider quotas, allowlisted destinations |
| Storage/images | django-storages, compatible S3 client, Pillow | Add with uploads; validate and safely re-encode images |
| Backend checks | pytest, pytest-django, Ruff, optional typing tools | PostgreSQL-backed integration checks for database behavior |
| Monitoring | Structured logs and an error tracker such as Sentry | Minimize personal data and redact secrets |

Recommend Django 5.2 LTS on its latest supported security patch as a conservative baseline, and compare the latest stable Django series if all dependencies support it. Choose a supported Python minor from the common compatibility set. Use pyproject.toml, uv.lock, normal development sync, and locked synchronization in CI. uv is dependency/environment tooling, not a server or framework.

For every admitted dependency, document purpose, stable version, license, official source, latest meaningful maintenance evidence, runtime/peer requirements, known relevant advisories, SSR/mobile implications, and replacement cost. Infrequent releases alone do not prove abandonment; frequent releases do not prove stability. Explicitly mark what has only been assessed from documentation and what later needs a build/integration check. Schedule controlled upgrades and security patches rather than floating production on latest versions.

**5. Architecture and ownership**

Prefer a modular Django monolith with PostgreSQL and one versioned REST API used by web, mobile, and future extension clients. Organize bounded modules around accounts/access, catalog, personal library, reviews/discussion, social/communities, competitions, moderation, notifications, and integrations.

Django owns business rules, authorization, data validation, transactions, and data persistence. Nuxt owns rendering and presentation; optional server routes may proxy requests or compose presentation data but must not become a second business backend. Only Django and trusted workers access the database.

Recommend a monorepo layout that separates web, backend, documentation, shared API contracts, and operations. Describe future mobile/extension locations without scaffolding empty applications now. Share design tokens, safe UI elements, and API types where useful; do not assume all platform screens or authentication logic can be shared.

Provide one small architecture diagram showing clients, reverse proxy, Nuxt rendering, Django API, PostgreSQL, broker/cache, workers, object storage, and external catalog providers. Explain deployment boundaries and failure behavior. Microservices, Kubernetes, sharding, and event streaming require measured needs before introduction.

**6. Database choice and conceptual relational model**

Recommend PostgreSQL as the primary database. Explain why relational integrity, uniqueness, joins, transactions, and aggregate queries fit the product. MongoDB is capable of serious applications; the decision is about Muratori's relationship-heavy domain, not a claim that MongoDB cannot scale. Use JSONB for bounded provider payloads or genuinely variable metadata, not core permissions, votes, memberships, or relationships. Avoid maintaining both databases without a specific independent need.

Provide a conceptual ER diagram and table dictionary, without SQL or migration code. Mark alpha, beta, and future entities separately. Include cardinalities, ownership, key fields, nullability, constraints, deletion behavior, and indexes for actual access patterns.

Cover these entity groups:

- Accounts: custom user identity planned before initial migrations, profiles, preferences, sessions/devices, role/permission grants, follows, blocks, and mutes.
- Catalog: a stable MediaItem identity with a controlled type; MovieDetails and SeriesDetails; seasons and episodes; translated titles/synopses, aliases, genres, people/credits, artwork references, external provider IDs, provider sync state, and editorial overrides.
- Personal library: one LibraryEntry per user/media item for current status; separate repeatable ConsumptionEvents for rewatches and date history; one current Rating per user/media item; one editable Review per user/media item initially; lists and ordered list items.
- Discussion: review comments first; later community posts and their comments; bounded reply trees, reactions/helpful votes, moderation states, and explicit content ownership.
- Community: community, unique membership, join request/invitation when needed, local role assignments, rules, posts, bans, and moderation actions.
- Competition: challenge definitions, seasons/time windows, eligibility, participation, idempotent score events, score reversals, and rebuildable leaderboard snapshots.
- Operations: reports, moderation history, administrative audit events, notifications/delivery attempts, import runs/checkpoints, and outbox records if needed for reliable post-transaction jobs.

Avoid unchecked generic type/id references for important relationships. For comments or reports spanning several targets, compare explicit foreign keys with an exactly-one-target constraint against a shared content parent with real foreign keys. Select one coherent approach and explain its cost. Do not create a universal entity system purely for hypothetical future content.

Decide whether seasons/episodes are independently rateable MediaItems or child catalog records. Proposed alpha: rate movies and series; episode tracking is optional and later. Future books must distinguish works from editions/ISBNs. Future audio must distinguish recordings/releases, shows/episodes, or audiobook editions as applicable. Adding a media type should reuse reviews/lists but still permit proper new schema and validation.

Specify invariants: unique external ID per provider and media namespace; one rating and library entry per user/item; no duplicate follow/membership/vote; no self-follow; bounded rating values; unique season/episode numbers within parents; reply belongs to the same discussion; list order is deterministic; self-vote exclusions where applicable. State which invariants use database constraints and which need transactional application logic.

Include transaction boundaries, concurrent updates, conflict handling, migration/backfill plans, deduplication/merging, and rebuildable aggregates. Use UTC timestamps and explicit locale/timezone presentation. Store image objects outside PostgreSQL and retain metadata/keys in relational records. Do not claim UUIDs or nonsequential identifiers replace access control.

**7. Ratings, reactions, diaries, and competitions**

Resolve the meaning of vote. Separate personal ratings of media, helpful votes/reactions on user content, and points earned in challenges. They must have separate models and rules.

Proposed rating scale: 0.5–5 stars in half-star steps, stored as integers 1–10. Unrated means no rating, never zero. Explain the alternative of a 1–10 user-facing scale and ask for a choice. Keep external provider ratings visibly attributed and separate from Muratori ratings.

Define whether rating requires a self-reported watched state, whether in-progress series can be rated, how rewatches work, and whether historical diary entries retain snapshots. Do not pretend consumption can be reliably proven. Propose ratings allowed for watched movies and in-progress/completed series, subject to approval.

For media ranking, show vote counts and an understandable formula, such as a Bayesian adjusted score with documented prior/minimum thresholds. Do not automatically rank a title with one perfect vote above established titles. Define edit/delete effects and stale aggregate behavior.

For friendly competition, propose a narrow first challenge with opt-in participation, published scoring, one eligible completion per distinct title per period, daily caps if justified, deterministic ties, timezone rules, and a correction process. Avoid rewarding raw comments/likes because that encourages spam. Explain how differing media lengths and types affect fairness. Self-reported challenges should have modest rewards and honest limitations.

Use uniquely identified server-recorded score events, retry-safe processing, reversible awards, and reproducible totals. Define handling of removed content, banned users, duplicate events, backdated entries, imported histories, and changed rules. Prefer transparent seasonal/community boards over a permanent popularity contest. Allow users to opt out of public ranking.

**8. Authentication, authorization, and privacy**

My desired permission vocabulary includes perm.admin.access and perm.admin.users.edit. Roles group capabilities, but the backend decides every action. Define an exact permission registry, its mapping to Django permissions/custom policies, and its versioning. Never infer permissions using role-name substrings, prefix matching, or arbitrary client-supplied strings.

Propose visitor, member, community moderator, community owner, platform moderator, administrator, and tightly controlled superuser roles. Community roles apply only to their own community. Platform roles are separate. Use scoped checks and resource ownership along with role-based capabilities.

Provide a role/action/scope matrix. Entering an admin screen does not grant user-edit privileges. A staff user editing ordinary account fields must not be able to grant administrative roles through that same endpoint. Role assignment, moderation, exports, private-data access, and destructive actions need distinct capabilities and audit records.

Default deny. Enforce access on list querysets, detail endpoints, creation, edits, nested objects, search, exports, notifications, background jobs, uploaded media, and cached responses. Frontend route guards and hidden buttons are usability controls only. Do not assume object checks automatically filter DRF list endpoints. Return only authorized fields, not a full record with hidden UI fields.

Proposed browser authentication: same-origin routing to Django, server-issued Secure/HttpOnly session cookies, appropriate SameSite policy, and CSRF protection for state changes. Carefully specify SSR cookie forwarding, trusted proxy behavior, logout/revocation, session expiry, password reset, email verification, and MFA for privileged users. Never serialize session secrets into Nuxt payloads or persist bearer tokens in Pinia/localStorage.

Plan mobile and extension authentication separately using a maintained supported token/public-client flow. Specify revocation, token lifetime, rotation/reuse detection if refresh tokens are selected, secure device storage, and OAuth state/PKCE when OAuth is used. Do not embed confidential client secrets in distributed apps or invent a custom authentication protocol.

Address account enumeration, login throttling, credential abuse, spam, IDOR, mass assignment, stored XSS, CSRF, unsafe redirects, malicious imports/URLs, SSRF, and upload abuse. Use bounded request sizes and query limits. Secrets stay server-side; deployment, database, storage, and provider credentials use least privilege.

Define library/list/profile visibility; what follows versus blocks mean; whether blocked users can still see public content anonymously; privacy defaults for diary dates and activity; and whether private activity contributes to a public board. Do not promise stronger blocking privacy than public access permits.

Plan data export, deletion/anonymization, retention, backup expiry, report evidence access, and removal from search/cache. Distinguish content moderation soft deletion from erasure obligations. Identify applicable jurisdictions and age rules for later qualified review; do not claim that an architecture or host automatically guarantees LGPD/GDPR compliance.

**9. Reusable frontend architecture and reference project**

You may inspect C:\Users\lucas\projetos\Ravena\ravena-v2_essentials strictly as a read-only reference. Do not modify it or copy its implementation, assets, secrets, dependencies, or business-specific logic. The Muratori workspace is C:\Users\lucas\projetos\Fullstack\muras_movies.

Learn from configuration-driven forms, tables, action menus, modal/page editing, composables, and permissions. Design typed FieldSchema, FormSchema, TableSchema, and ResourceDefinition concepts with an allowlisted component registry, stable identifiers, safe attributes, accessibility, validation/error mapping, and explicit escape hatches for custom components. Keep schema definitions in version control initially. Do not evaluate code/templates received from a server or user.

Form requirements: create/edit/read-only modes; defaults; nested fields where needed; dependent fields; async choices with cancellation; loading/empty/error states; server validation; unsaved-change handling; keyboard support; and permission-aware actions backed by API enforcement.

Table requirements: typed explicit columns, server-side pagination/filtering/sorting, bounded exports, accessible actions, persisted harmless preferences, and predictable empty/error states. Do not infer all visible columns from arbitrary API response fields or download entire datasets to paginate in the browser.

Separate reusable administrative CRUD screens from carefully designed public product screens. A movie page and a community page can share components without being forced into one generic table/page framework.

Define route templates such as movies/[id]-[slug], series/[id]-[slug], users/[handle], lists/[id]-[slug], and communities/[id]-[slug]. A template serves many records; do not generate source files or rebuild the entire site for each imported title. Resolve records by stable IDs and redirect obsolete slugs to canonical URLs.

Use SSR or suitable hybrid rendering for public pages, canonical metadata, Open Graph cards, sitemaps, and appropriate indexing policies. Private, settings, and admin routes must not be indexed. Public cached catalog data must be separated from user-specific watch status, ratings, and actions. Never cache personalized HTML for other users. Plan meaningful 404s, unavailable titles, provider outages, loading skeletons, and empty states.

Design a restrained visual system: warm neutrals, clear typography, poster-rich cards, comfortable spacing, light/dark themes, restrained motion, clear focus states, spoiler controls, and mobile touch targets. Target WCAG 2.2 AA and specify checks; no automatic conformance claim. Charts need readable summaries and keyboard alternatives where relevant.

**10. Catalog sources and ingestion**

Evaluate TMDB as the first movie/TV metadata and artwork source. Compare alternatives only where they improve coverage, licensing, cost, or resilience. IMDb downloadable datasets have non-commercial restrictions; do not assume they include poster rights or authorize a commercial catalog. Later evaluate Open Library bulk data for books and separately chosen sources for each audio type.

Create a provider matrix covering available fields, translations, identifiers, metadata/image rights, attribution, commercial licensing, retention/cache rules, quotas, costs, completeness, reliability, and deletion/update requirements. An API key is not unlimited redistribution permission. Verify actual terms rather than inventing cache durations or import rights.

Begin with a useful curated/popular seed and on-demand expansion, subject to terms. TMDB daily ID exports are discovery inputs, not full metadata dumps. Do not promise instant full-catalog coverage or download every image upfront.

The import design must include provider adapters, normalized records, provenance, external namespaces, checkpoints, bounded concurrency, quota budgets, retries/backoff, idempotent upserts, import previews, malformed-record quarantine, update detection, deleted/merged records, and sync monitoring. Preserve editorial overrides and user ratings/reviews when metadata refreshes.

Use provider change mechanisms when available. Deduplicate by external identity and carefully reviewed cross-provider mappings, not title alone. Store translations and original titles separately. Permit moderated missing-title requests and staff-created provisional records with safe later merging.

Serve existing local catalog records during provider outages. Bound upstream work caused by searches to prevent a public endpoint from exhausting quotas. Use approved provider artwork delivery/caching policies. User avatars and future uploads belong in object storage with a separate validation and moderation path.

**11. API, jobs, search, and performance**

Produce endpoint families, payload descriptions, pagination/filter conventions, error formats, and auth requirements without implementation code. Include API versioning, stable IDs, timestamps, documented enum values, bounded field expansion, and backward compatibility for mobile versions.

Use idempotent rating/library mutations and deduplication keys where retries could duplicate diary events, competition points, or notifications. Define 401/403/404 semantics, optimistic UI rollback, and conflict responses. The API schema is the source for generated client types; frontend validation supplements backend validation.

Begin with PostgreSQL search, language-aware full-text search and/or trigram matching as justified by titles, aliases, and accents. Specify filters and ranking. Add a dedicated search engine only after measured shortcomings, with a plan for indexing lag and permission-aware results.

Use bounded queries, appropriate indexes, select/prefetch strategies, query-count budgets, and pagination. Start social feeds with a clear chronological model and explain how follows, blocks, and visibility are applied.

Queue ingestion, email, notifications, image processing, and expensive leaderboard work. Tasks must tolerate duplicate delivery, crashes, restarts, and partial failure. Schedule after database commit; evaluate a transactional outbox when lost delivery is unacceptable. Define retry limits, failed-job inspection, and reconciliation. Cache/broker contents must not be the only durable record of votes or points.

State provisional load scenarios, not promises: for example 1,000, 10,000, and 100,000 registered users, each with separately stated daily activity, peak concurrent users, requests/sec, catalog size, review volume, uploads, and queue load. Registration totals alone do not size infrastructure.

Propose measurable targets under an explicit load profile: cached/local API reads p95 around 300 ms excluding provider calls, simple writes p95 around 500 ms, and mobile web performance targets based on Core Web Vitals. Treat these as proposed budgets to benchmark, not current achieved performance. Define capacity triggers using DB saturation, memory, latency, queue delay, and cost.

**12. Hosting, storage, and operations**

Compare self-managed Hetzner, a managed platform/database, and a hybrid with Nuxt on Vercel and Django/workers/PostgreSQL elsewhere. Database choice does not force a hosting provider. Vercel can host Django under its supported platform model; verify current limits instead of repeating outdated claims about serverless platforms.

Recommend Hetzner only if the team accepts OS maintenance, firewalling, patches, monitoring, database operation, backups, and incident response. A single VPS may be acceptable for an alpha, but is a single failure domain and does not provide high availability. Managed PostgreSQL may be worth the cost when operating capacity is limited.

Show an inexpensive alpha topology and a growth topology. Prefer a reverse proxy, containerized Nuxt/Django/worker processes, private database/broker networking, object storage, TLS, transactional email, separate staging, and secret management. Choose Docker Compose or an equivalent simple deployment approach initially. Do not invent a requirement for Kubernetes.

Compare regions against the actual audience. If Brazil is primary, measure latency from Brazil to candidate locations and colocate app/database where possible. A CDN helps assets and cached pages but does not remove latency from authenticated writes. Check object-storage location separately from compute availability.

Provide a cost worksheet with compute, database, storage, requests/egress, backups, email, monitoring, domains, staging, licensing, and an operating-effort estimate. Quote prices only with dated provider sources and assumptions; otherwise leave them as explicit variables. No infrastructure purchases in this phase.

Define encrypted off-host backups, restoration drills, retention, provider independence where justified, and recovery objectives. Propose alpha RPO of 24 hours and RTO of one working day as initial discussion points; tighter requirements require a different backup/availability budget. Explain point-in-time recovery and how to add it before stronger promises.

Plan health/readiness checks, structured logs, request IDs, error tracking, uptime alerts, queue monitoring, slow-query visibility, disk alarms, security updates, CI/CD, reproducible builds, migration ordering, and rollbacks. Database restoration is not a routine substitute for a backward-compatible migration plan.

**13. Mobile and future Chrome extension**

Compare PWA, Capacitor with shared Vue UI, and a dedicated mobile framework only against concrete needs. Prefer investigating Capacitor for Vue reuse, but document constraints before committing. A packaged app needs bundled client assets and a reachable API; a Nuxt SSR server does not run inside the mobile bundle. Plan separate build configurations and platform adapters.

Specify safe-area layouts, back navigation, keyboard behavior, app links, image caching, notification permissions, device token management, logout cleanup, and secure token storage. Start offline behavior with read-only cached public catalog data; an offline mutation queue needs conflict resolution and idempotency before adoption. iOS signing/builds require the appropriate Apple tooling and account; account for that later.

Reserve a future Chrome Manifest V3 extension for user-initiated actions such as saving a supported page's title to a list. Minimize host permissions, validate messages and detected IDs, isolate tokens from page scripts, and respect remote-code and store policies. Do not collect browsing history by default. Reuse the versioned API and public-client authentication design; do not build the extension in the first release.

**14. Quality and release acceptance**

Plan tests for meaningful behavior and risk: domain invariants, concurrent rating/vote updates, duplicate jobs, authorization matrices, list-query privacy, cross-community isolation, role escalation, session/CSRF flows, catalog retries/merges, provider failure, upload validation, and score reconciliation. Test database semantics with PostgreSQL rather than relying only on SQLite.

Plan frontend component checks where valuable, API contract checks, and end-to-end journeys: register/verify/sign in; discover a title; save/track/rate/review; edit one's own content; report/moderate; exercise permission denial; opt into a challenge. Include SSR/hydration, responsive layouts, accessibility, and cache isolation checks.

Public release requires tested account recovery, privacy controls, reporting/moderation workflows, provider attribution, dependency/security review, a successful backup restoration, usable error/empty states, monitoring ownership, and load results at the approved target. Do not claim security, scalability, or accessibility from tool selection alone.

The first proposed implementation slice, after approval, should demonstrate one complete path: user authentication → imported movie → dynamic public page → authorized library/rating mutation → persisted PostgreSQL data → verified denied access for another user. Add schema-driven administration incrementally around real resources after proving that path.

**15. Required planning response**

Return a self-contained specification containing:

1. Product summary, assumptions, target audience, and key user journeys.
2. Recommended stack and concise decision records for database, hosting, API/authentication, rendering, media modeling, and mobile.
3. Dependency compatibility/maintenance matrix with current official sources and unresolved verification items.
4. Alpha/beta/future scope, proposed improvements, exclusions, milestones, and acceptance criteria.
5. Architecture diagram, conceptual ER diagram, entity dictionary, integrity rules, and prioritized indexes.
6. Permission matrix, browser/mobile auth flows, privacy rules, abuse controls, and moderation workflow.
7. Reusable component and route design, design-system principles, and SEO/accessibility strategy.
8. Provider/licensing comparison and import/sync lifecycle.
9. API contract outline, asynchronous work, search, cache boundaries, and provisional performance/load targets.
10. Hosting comparison, cost worksheet, backups/recovery, observability, and deployment approach.
11. Risks, tradeoffs, unresolved decisions, and a prioritized implementation backlog with dependencies and realistic effort ranges.
12. A concise owner approval checklist and the highest-impact questions with recommended answers.

End at the review checkpoint. Do not begin implementation.
