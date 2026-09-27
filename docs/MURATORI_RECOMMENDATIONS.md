# Muratori — findings and recommendations

Prepared 2026-09-16. Planning only; no application code or infrastructure was created. The companion [master prompt](MURATORI_MASTER_PROMPT.md) is the reusable artifact for the next planning discussion.

**Recommended direction**

Use Nuxt 4 + Vuetify 4, Django/DRF, PostgreSQL, object storage, and background workers. Begin as a modular monolith and a responsive web application. Release movies and TV first, then expand the media model and clients in deliberate phases. These are architectural recommendations, not an approved package manifest.

PostgreSQL is the better default for this domain because the central data consists of related identities, titles, ratings, reviews, memberships, and permission grants. Database uniqueness and foreign keys make rules such as one current rating per user/title explicit. JSONB can hold selected variable metadata without sacrificing relational core data. MongoDB can support complex applications, but its flexibility does not give Muratori a clear advantage here. See PostgreSQL's [constraints](https://www.postgresql.org/docs/current/ddl-constraints.html), [JSON types](https://www.postgresql.org/docs/current/datatype-json.html), and [text search](https://www.postgresql.org/docs/current/textsearch.html) documentation.

Images do not drive the PostgreSQL/MongoDB decision: store image files in an object store or use provider-approved image delivery, and keep identities, keys, provenance, and metadata in PostgreSQL.

**Hosting is a separate choice**

| Approach | Why consider it | Main tradeoff |
| --- | --- | --- |
| Hetzner with self-managed services | Control over a conventional Django API, workers, and database deployment | The team owns operations, recovery, upgrades, and capacity |
| Managed application hosting + managed PostgreSQL | Less routine infrastructure work | Higher service costs and provider-specific constraints to evaluate |
| Nuxt on Vercel + backend/workers/database elsewhere | Convenient frontend deployment while retaining backend flexibility | More services, routing/authentication configuration, and possible regional latency |

Hetzner is a reasonable candidate, not an automatic scalability guarantee. Its listed compute regions include Germany, Finland, the USA, and Singapore; a Brazil-focused launch should benchmark candidate regions. It also offers S3-compatible object storage, whose location and delivery costs need separate review. See [Hetzner Cloud](https://www.hetzner.com/cloud/) and [Object Storage](https://www.hetzner.com/storage/object-storage/).

Vercel should not be dismissed as incapable of backend hosting: it currently documents Django deployment, with platform-specific behavior and limits. Muratori's background workers, database, region, operating cost, and reliability requirements should decide the topology. See [Vercel's Django guide](https://vercel.com/docs/frameworks/full-stack/django).

**Stack findings**

| Choice | Finding and recommendation |
| --- | --- |
| Nuxt 4 | Suitable for public SSR/hybrid pages and private application screens. Its server engine supports several deployment targets. [Nuxt documentation](https://nuxt.com/docs/4.x/getting-started/server) |
| Vuetify 4 | Official v4 documentation and release history exist. Retain it as the preference. The Nuxt module documentation still describes Vuetify 3 requirements while its matrix has broader bounds, so verify exact stable module/SSR compatibility before installation. [Vuetify releases](https://github.com/vuetifyjs/vuetify/releases), [integration matrix](https://nuxt.vuetifyjs.com/guide/getting-started/compatibility.html) |
| Pinia | Use its Nuxt integration for selected shared client state, with SSR isolation. [Pinia Nuxt guide](https://pinia.vuejs.org/ssr/nuxt.html) |
| Forms | VeeValidate is a candidate for the dynamic form layer; current v5 documentation describes standard-schema integration. Avoid copying several overlapping validation libraries from the reference. [VeeValidate migration guide](https://vee-validate.logaretm.com/v5/guide/migration/) |
| Charts | Chart.js/vue-chartjs is a concrete candidate for the ambiguous request for “Vue charts.” Defer until statistics screens exist. [vue-chartjs](https://vue-chartjs.org/) |
| Vue Flow | Designed for node-based interfaces. No initial Muratori requirement needs a visual flow editor, so defer it. [Vue Flow](https://vueflow.dev/) |
| Pug | Preserve as an owner preference under review. Standard Vue templates are my maintainability recommendation; Pug integration and maintenance need a separate check before accepting it into the baseline. [Pug documentation](https://pugjs.org/language/plain-text.html) |
| Django | Prefer the latest supported patch of 5.2 LTS for a conservative dependency baseline; compare current stable 6.1 if its features and dependency support justify it. The official table lists 5.2 extended support through April 2028. [Django support table](https://www.djangoproject.com/download/) |
| API | DRF and drf-spectacular are the proposed REST/OpenAPI combination. Validate their selected versions together with Django and Python. [DRF release notes](https://www.django-rest-framework.org/community/release-notes/), [drf-spectacular](https://drf-spectacular.readthedocs.io/en/stable/readme.html) |
| uv | Appropriate for dependency resolution and reproducible environments; commit its lockfile and enforce locked CI synchronization. [uv locking and syncing](https://docs.astral.sh/uv/concepts/projects/sync/) |
| Authentication | Investigate Django sessions for web and allauth headless for account flows and non-browser clients. Select the exact token strategy deliberately. [allauth headless](https://docs.allauth.org/en/latest/headless/index.html) |
| Jobs | Celery is a candidate for imports, notifications, and aggregation. Broker/version choice still needs a compatibility and operations review. [Celery documentation](https://docs.celeryq.dev/en/stable/) |
| Mobile | Capacitor is a reasonable Vue-reuse candidate. It packages built web assets; SSR and device build behavior must be designed separately. [Capacitor workflow](https://capacitorjs.com/docs/basics/workflow) |
| Extension | Plan a future Manifest V3 client with minimal permissions. [Chrome Manifest V3](https://developer.chrome.com/docs/extensions/develop/migrate/what-is-mv3) |

This was a documentation review, not a completed package compatibility or vulnerability audit. Optional packages in the master prompt are candidates, not claims that every package has recently released or works with every other selected version. The approved implementation should resolve and test one exact dependency set before broad development.

**Reference project inspection**

Reviewed selected files under C:\Users\lucas\projetos\Ravena\ravena-v2_essentials. This was a targeted frontend review, not a full repository/backend security audit. The reference was not changed.

- package.json declares Nuxt ^4.0.1 and Vuetify ^3.11.7. It is not an example of a verified Vuetify 4 integration.
- app/components/Form/FormBuilder.vue and app/composables/pages/useUserPage.ts show schema/configuration-driven fields, API endpoints, actions, tabs, and read-only behavior. These are useful design references for Muratori's administrative UI.
- app/components/Table/TableBuilder.vue illustrates reusable tables, but the inspected logic includes columns derived from result data and pagination based on the loaded results. Muratori should define explicit typed columns and server-side pagination.
- nuxt.config.ts has ssr: false and global noindex/nofollow metadata. That may suit a private application, but Muratori's public title pages should be indexable and server-rendered as appropriate.
- stores/authStore.ts writes a token through client-side cookie access and uses cached user permissions for UI state. Muratori should choose and document its browser session/SSR design independently.
- app/plugins/checkPermissions.ts includes roles.some(role => role.includes(permission)). Substring role matching is unsuitable for Muratori's authorization policy. Use exact capabilities plus explicit resource scope, and enforce them in Django.

Frontend builders and permission-aware buttons improve consistency. They do not by themselves secure API access. DRF documents that object-level checks do not automatically filter lists and require explicit consideration during creation. See [DRF permissions](https://www.django-rest-framework.org/api-guide/permissions/).

**Catalog strategy**

TMDB is the recommended first candidate for movie/TV metadata and artwork. Its FAQ allows free non-commercial use with attribution and directs commercial uses to licensing discussions. Plan monetization early enough to choose the right agreement. Its daily ID exports contain identifiers and limited discovery attributes, not the complete catalog metadata. See the [TMDB FAQ](https://developer.themoviedb.org/docs/faq) and [daily exports](https://developer.themoviedb.org/docs/daily-id-exports).

Seed a useful catalog, expand on demand within the provider's terms, and synchronize in the background. Use internal IDs plus namespaced provider IDs; never let an import overwrite user reviews, ratings, or staff corrections. A few dynamic route templates can render arbitrarily many database records without generating a source file for each title.

IMDb's freely available data has non-commercial restrictions and is not a blanket source of artwork rights. Treat it as an alternative requiring a separate rights/coverage review. See [IMDb usage conditions](https://help.imdb.com/article/imdb/general-information/can-i-use-imdb-data-in-my-software/G5JTRESSHJBBHTGX).

For future books, Open Library explicitly distinguishes interactive API use from bulk access and recommends its dumps for bulk needs. Do not design a high-traffic catalog around unlimited per-book API calls. See [Open Library API guidance](https://openlibrary.org/developers/api).

**Decisions still needed from the owner**

| Decision | Proposed answer to review | Why it matters |
| --- | --- | --- |
| Purpose and monetization | Plan for possible future commercial use | Provider licenses and recurring costs |
| Audience and locales | Brazil first; pt-BR with English-ready structure | Region, translations, moderation, privacy review |
| Age audience | Choose explicitly before public launch | Content policy and account/privacy requirements |
| Monthly budget and operations | Provide a budget ceiling and who maintains servers | Self-managed Hetzner versus managed services |
| Team and timeline | State hours/week, team size, and desired beta date | Credible scope and estimates |
| First release | Movies + series; communities/challenge by public beta | Keeps alpha useful and achievable |
| Meaning of vote | Media stars plus helpful votes on user content | Prevents three scoring systems being conflated |
| Rating scale | Half-star steps from 0.5 to 5 | UX and stored rating semantics |
| TV detail | Series-level ratings first | Episode tracking substantially expands UX/import scope |
| Audio meaning | Defer until music/podcasts/audiobooks are specified | Each needs different entities/providers |
| Communities | Open discovery with scoped moderators; private groups later | Membership/privacy/moderation complexity |
| Competition | Optional monthly discovery challenge with modest rewards | Fairness, abuse controls, and scoring rules |
| Visibility | Choose explicit defaults; make diary/list privacy easy | Affects feeds, caching, search, and leaderboards |
| Mobile | Responsive web first; investigate Capacitor next | Avoids promising native reuse without device requirements |
| Pug | Confirm Pug or approve standard Vue templates | Tooling, onboarding, and template conventions |
| Brand | Confirm Muratori, domain, and visual direction | Prevents carrying the legacy workspace name into product design |

All of these questions are incorporated into the master prompt. They are review decisions; no answer is required merely to read or revise the draft.
