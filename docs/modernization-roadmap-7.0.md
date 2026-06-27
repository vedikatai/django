# Django Modernization Roadmap — Toward 7.0 (Python 3.18, async-first)

_Regenerated 2026-06-27T06:27:24.388138+00:00 on branch `modernization-roadmap-7.0` @ `848fc648a8`._

## Executive summary

- **Codebase size (top-level `django/` Python):** **131,308** code lines in **908** files (source: `/tmp/loc.json`, tool=`custom-wc-python (cloc not installed)`). Largest: `db` (44,099), `contrib` (35,389), `core` (15,177).
- **Activity:** Highest 3y churn is `contrib` / `db` / `conf` — invest in stability & async ORM completion. Lowest commit counts include `__main__.py`, `apps`, `templatetags` — **not automatic deprecations** (signals/`apps` are load-bearing). Prefer **API-level** deprecations over module deletion.
- **Python 3.18:** No `asyncio.coroutine` remains (0 hits). No AST hits for `return`/`yield` in `finally` (PEP 765; count=0). Local CPython at `/Users/sourabhligade/cpython` reports **3.16.0a0** (`python.exe`), not 3.18 — **full suite on 3.18 could not be executed**. CPython 3.16 smoke blocked: `ModuleNotFoundError: asgiref` in that interpreter env.
- **Async ORM PoCs:** `Model.afull_clean` / `avalidate_unique` / `avalidate_constraints` (`django/db/models/base.py:1474,1702,1753`), `connection.aensure_connection` (`django/db/backends/base/base.py:281`), `transaction.aon_commit` (`django/db/transaction.py:149`).
- **Performance (HEAD vs tag `4.2` @ `879e5d587b`):** `Model.objects.create` median **+30.88%** (regression >10%); other ops improved or within 10%. Bisect first flagged `e1671278` (bulk_create #36490) but **5-run verification shows noise** (parent vs commit overlap); **no safe single-commit fix applied**. Raw: `/tmp/bench_main_vs_42.json`.
- **Security (2030 model):** Prospective threats (not CVEs). Mitigations on branch: opt-in `sanitize_admin_text_for_llm` (`django/contrib/admin/utils.py:637`), opt-in `DJANGO_ASYNC_SIGNAL_WARN=1` (`django/dispatch/dispatcher.py:248`). PoC ran: `/tmp/sec_poc_prompt_injection.py`, signing rotation demo with `SECRET_KEY_FALLBACKS`.
- **Tests this session:** `async` + `asgi` + PoC modules — **139 tests OK** (1 skipped), SQLite. Postgres: local **14.17** rejected (`NotSupportedError: PostgreSQL 15 or later required`).
- **Effort estimate:** ~**90–140 engineer-weeks** for full 7.0 async-first + 3.18 + deprecations (see §Cost).

## Phase 1 — Module activity matrix

| Module | LOC code | Files | Commits 3y | Contributors 3y | Churn lines 3y | Last non-test commit | Open issues | Coverage % |
|---|---:|---:|---:|---:|---:|---|---|---|
| `__init__.py` | 19 | 1 | 5 | 4 | 10 | 2026-05-20T16:17:41-04:00 | **N/A** (`gh` unauthenticated) | **N/A** (no coverage artifact) |
| `__main__.py` | 7 | 1 | 1 | 1 | 1 | 2024-01-26T12:45:07+01:00 | **N/A** (`gh` unauthenticated) | **N/A** (no coverage artifact) |
| `apps` | 489 | 3 | 2 | 2 | 12 | 2025-07-23T20:17:55-03:00 | **N/A** (`gh` unauthenticated) | **N/A** (no coverage artifact) |
| `conf` | 3210 | 176 | 52 | 28 | 13333 | 2026-06-10T10:17:34-04:00 | **N/A** (`gh` unauthenticated) | **N/A** (no coverage artifact) |
| `contrib` | 35389 | 338 | 548 | 184 | 56908 | 2026-06-27T01:42:01+05:30 | **N/A** (`gh` unauthenticated) | **N/A** (no coverage artifact) |
| `core` | 15177 | 112 | 187 | 94 | 4894 | 2026-06-26T13:28:10-04:00 | **N/A** (`gh` unauthenticated) | **N/A** (no coverage artifact) |
| `db` | 44099 | 123 | 638 | 157 | 16946 | 2026-06-27T01:42:00+05:30 | **N/A** (`gh` unauthenticated) | **N/A** (no coverage artifact) |
| `dispatch` | 451 | 2 | 9 | 9 | 252 | 2026-06-27T01:42:01+05:30 | **N/A** (`gh` unauthenticated) | **N/A** (no coverage artifact) |
| `forms` | 4920 | 9 | 64 | 39 | 868 | 2026-06-10T17:15:59-04:00 | **N/A** (`gh` unauthenticated) | **N/A** (no coverage artifact) |
| `http` | 1899 | 5 | 34 | 22 | 511 | 2026-06-10T10:17:34-04:00 | **N/A** (`gh` unauthenticated) | **N/A** (no coverage artifact) |
| `middleware` | 912 | 10 | 23 | 18 | 242 | 2026-06-19T13:30:38-03:00 | **N/A** (`gh` unauthenticated) | **N/A** (no coverage artifact) |
| `shortcuts.py` | 167 | 1 | 5 | 5 | 74 | 2026-05-04T17:09:20-04:00 | **N/A** (`gh` unauthenticated) | **N/A** (no coverage artifact) |
| `tasks` | 529 | 9 | 6 | 6 | 813 | 2026-04-30T08:12:08-04:00 | **N/A** (`gh` unauthenticated) | **N/A** (no coverage artifact) |
| `template` | 5327 | 27 | 54 | 36 | 1154 | 2026-06-10T10:17:34-04:00 | **N/A** (`gh` unauthenticated) | **N/A** (no coverage artifact) |
| `templatetags` | 909 | 6 | 4 | 3 | 14 | 2025-07-23T10:09:43-03:00 | **N/A** (`gh` unauthenticated) | **N/A** (no coverage artifact) |
| `test` | 5577 | 8 | 85 | 36 | 2030 | 2013-11-07T14:30:04-08:00 | **N/A** (`gh` unauthenticated) | **N/A** (no coverage artifact) |
| `urls` | 1215 | 7 | 17 | 13 | 502 | 2026-06-01T15:24:49-04:00 | **N/A** (`gh` unauthenticated) | **N/A** (no coverage artifact) |
| `utils` | 8022 | 48 | 129 | 51 | 2803 | 2026-06-24T12:44:00-04:00 | **N/A** (`gh` unauthenticated) | **N/A** (no coverage artifact) |
| `views` | 2990 | 22 | 41 | 32 | 1151 | 2026-06-23T15:36:15-04:00 | **N/A** (`gh` unauthenticated) | **N/A** (no coverage artifact) |

### Lowest activity (deprecation *candidates* — review before removing)

- `__main__.py`: commits_3y=1, contributors=1, churn=1, last=2024-01-26T12:45:07+01:00
- `apps`: commits_3y=2, contributors=2, churn=12, last=2025-07-23T20:17:55-03:00
- `templatetags`: commits_3y=4, contributors=3, churn=14, last=2025-07-23T10:09:43-03:00
- `__init__.py`: commits_3y=5, contributors=4, churn=10, last=2026-05-20T16:17:41-04:00
- `shortcuts.py`: commits_3y=5, contributors=5, churn=74, last=2026-05-04T17:09:20-04:00
- `tasks`: commits_3y=6, contributors=6, churn=813, last=2026-04-30T08:12:08-04:00
- `dispatch`: commits_3y=9, contributors=9, churn=252, last=2026-06-27T01:42:01+05:30
- `urls`: commits_3y=17, contributors=13, churn=502, last=2026-06-01T15:24:49-04:00
- `middleware`: commits_3y=23, contributors=18, churn=242, last=2026-06-19T13:30:38-03:00
- `http`: commits_3y=34, contributors=22, churn=511, last=2026-06-10T10:17:34-04:00

### Highest churn (stability investment)

- `contrib`: commits_3y=548, contributors=184, churn=56908
- `db`: commits_3y=638, contributors=157, churn=16946
- `conf`: commits_3y=52, contributors=28, churn=13333
- `core`: commits_3y=187, contributors=94, churn=4894
- `utils`: commits_3y=129, contributors=51, churn=2803
- `test`: commits_3y=85, contributors=36, churn=2030
- `template`: commits_3y=54, contributors=36, churn=1154
- `views`: commits_3y=41, contributors=32, churn=1151
- `forms`: commits_3y=64, contributors=39, churn=868
- `tasks`: commits_3y=6, contributors=6, churn=813

### DEPs (django/deps catalog + recent merged PRs)

Catalogued **24** DEP files under status dirs (clone `/tmp/deps-repo`, data `/tmp/deps_catalog.json`).

| DEP | Status | Title | Affected (heuristic) | Impl heuristic |
|---:|---|---|---|---|
| 201 | final | DEP 0201: Simplified routing syntax | django.core, django.urls, ORM, auth | mentioned implemented/landed in text |
| 192 | draft | DEP 192: Standalone Composite Fields | django.db, ORM, auth, migrations | unknown |
| 191 | draft | DEP 191: Composite Fields | ORM, auth | mentioned implemented/landed in text |
| 182 | final | DEP 182: Multiple Template Engines | django.contrib, django.core, django.http, django.template, O | mentioned implemented/landed in text |
| 181 | final | DEP 181: New implementation for ORM expressions | django.db, ORM, auth | mentioned implemented/landed in text |
| 44 | final | DEP 0044: Clarify Release Process | ORM, auth | unknown |
| 18 | accepted | DEP: 0018 | django.db, django.contrib, django.core, ORM, auth, admin | mentioned implemented/landed in text |
| 16 | accepted | DEP 16: Name the main command `django` | auth, admin | unknown |
| 15 | accepted | DEP 15: Improved startproject interface | ASGI, WSGI, auth, admin, migrations | unknown |
| 14 | final | DEP 0014: Background workers | django.tasks, ORM, ASGI, auth, async, email | django.tasks framework in tree (ongoing) |
| 12 | final | DEP 0012: The Steering Council | ORM, auth | unknown |
| 11 | superseded | DEP 11: Accessibility Team | ORM, auth, admin | unknown |
| 10 | final | DEP 0010: New governance for the Django project | ORM, auth, admin | mentioned implemented/landed in text |
| 9 | accepted | DEP 0009: Async-capable Django | django.core, ORM, ASGI, WSGI, auth, admin | partially implemented (async views, ORM a* methods continuing) |
| 8 | final | DEP 0008: Formatting Code with Black | ORM, ASGI, auth, admin, migrations | mentioned implemented/landed in text |
| 7 | final | DEP 0007: Official Django Projects | ORM, auth, admin | unknown |
| 7 | draft | DEP 7: Dependency Policy | django.contrib, ORM, WSGI, auth | mentioned implemented/landed in text |
| 6 | withdrawn | DEP 0006: Channels | ORM, ASGI, WSGI, auth, async, email | mentioned implemented/landed in text |
| 5 | final | DEP 0005: Improved middleware | ORM, WSGI, auth | mentioned implemented/landed in text |
| 4 | final | DEP 4: Release Schedule | ORM, auth | unknown |
| 3 | final | JavaScript Tests & Linting | ORM, auth, admin | unknown |
| 2 | draft | DEP 2: Experimental APIs | ORM, auth | unknown |
| 1 | final | DEP 1: DEP Purpose and Guidelines | ORM, auth, admin, email | mentioned implemented/landed in text |
| None | draft | Content Negotiation Improvements | django.core, ORM, WSGI, auth | unknown |

Recent **merged** PRs on `django/deps` (public GitHub API; not all are DEP text merges):
- PR #111: DEP 0018 Mailers cleanup (f.k.a. email providers) (merged 2026-06-03T17:22:21Z) — https://github.com/django/deps/pull/111
- PR #105: DEP 0018 Dictionary-based EMAIL_PROVIDERS (ticket-35514) (merged 2026-05-13T16:06:05Z) — https://github.com/django/deps/pull/105
- PR #108: Mark DEP 14 as final (merged 2026-04-20T12:11:59Z) — https://github.com/django/deps/pull/108
- PR #98: Add draft for extended project template (merged 2025-11-03T14:06:53Z) — https://github.com/django/deps/pull/98
- PR #100: Add django command (merged 2025-10-11T11:01:20Z) — https://github.com/django/deps/pull/100
- PR #102: Moved DEP 0011 to superseded (merged 2025-08-10T18:45:29Z) — https://github.com/django/deps/pull/102
- PR #95: Update DEPs terminology to match current landscape (merged 2025-01-23T12:02:33Z) — https://github.com/django/deps/pull/95
- PR #91: Update DEP 7 terminology to match current landscape (merged 2025-01-14T02:48:05Z) — https://github.com/django/deps/pull/91
- PR #94: provide a .md template alongside the .rst one (merged 2025-01-14T10:05:24Z) — https://github.com/django/deps/pull/94
- PR #64: Drop 'Last Modified' field (merged 2025-01-07T07:56:47Z) — https://github.com/django/deps/pull/64
- PR #10: Experimental APIs DEP draft (merged 2014-12-06T19:23:20Z) — https://github.com/django/deps/pull/10
- PR #93: Made cosmetic edits to the technical board role description in DEP 10. (merged 2024-09-23T01:03:57Z) — https://github.com/django/deps/pull/93
- PR #92: Moved DEP 44 (clarifying release process) to final. (merged 2024-09-16T08:11:08Z) — https://github.com/django/deps/pull/92
- PR #81: Update DEPs 1, 10, and 12 to reflect current governance (merged 2023-10-30T14:15:41Z) — https://github.com/django/deps/pull/81
- PR #87: Update accessibility team membership (merged 2024-05-28T21:00:33Z) — https://github.com/django/deps/pull/87
- PR #86: Background workers (merged 2024-05-29T11:18:23Z) — https://github.com/django/deps/pull/86
- PR #90: Tidy DEP 14 a bit (merged 2024-06-06T07:01:59Z) — https://github.com/django/deps/pull/90
- PR #89: Update 0014-background-workers.rst (merged 2024-05-31T12:48:06Z) — https://github.com/django/deps/pull/89
- PR #83: Add missing “which” to DEP template (merged 2023-12-19T21:59:33Z) — https://github.com/django/deps/pull/83
- PR #69: DEP 11 -- Create an accessibility team. (merged 2021-02-10T10:43:26Z) — https://github.com/django/deps/pull/69

**Open issues per module / coverage %:** Not retrieved — `gh auth login` required; do not invent counts.

## Phase 2 — Python 3.18 forward compatibility

| Finding | Evidence | 3.18-oriented action | Risk |
|---|---|---|---|
| `asyncio.coroutine` / `@coroutine` | AST/grep under `django/` — **0 matches** (`/tmp/python318_audit.json`) | None | — |
| `return`/`yield` in `finally` (PEP 765) | AST walk — **0 hits** | Re-scan when 3.18 lands | Exception if introduced later |
| Deprecated stdlib patterns | **1** hits (see JSON; includes comments) | Monitor real call sites | Warning/removal |
| `Any` / PEP 604 | AST `Any` name count **4**; `Optional` **0**, `Union` **0** (many annotations already use `X \| Y`) | Prefer `TypeVar`/`Protocol` at public APIs | Silent typing debt |
| CPython 3.18 suite | `/Users/sourabhligade/cpython/python.exe` → **3.16.0a0** | Build 3.18 when tagged | Blocked |

### Representative findings (file:line)

- **Deprecated pattern** `/Users/sourabhligade/django/django/utils/datastructures.py:69` — `This class exists to solve the irritating problem raised by cgi.parse_qs,` → email.message / urllib.parse — risk: exception (removed 3.13)

### CPython suite classification

**Could not run Django full suite on CPython 3.18** — interpreter not present (tree is 3.16.0a0). Attempted `tests/runtests.py` on 3.16.0a0 failed early: `ModuleNotFoundError: No module named 'asgiref'` (deps not installed for that build). No test failures classified as Django bug / CPython regression / undocumented behavior.

## Phase 3 — Async-first redesign

### Gap analysis (`django/db`)

- AST scan of focus files listed in `/tmp/async_orm_gaps.json`: **28** methods already have `a*` twins in same file; **81** IO-ish methods lack same-file `a*` twin (many are sync-only by design: `filter` returns QS, `clean` is CPU-only, schema APIs).
- **QuerySet IO methods:** Full `a*` surface for DB-touching APIs in `django/db/models/query.py` (see twins list in JSON).
- **Model:** PoC adds async validation at lines cited above.
- **Still XL effort:** true async `atomic` context manager with async DB drivers.

### Highest-impact missing APIs (pre-PoC) & effort

| API | File:line (sync) | Async path? | Effort |
|---|---|---|---|
| `Model.full_clean` / `validate_*` | `django/db/models/base.py` (~1448+) | Yes via `sync_to_async` | **S** — PoC `afull_clean` @ 1753 |
| `connections[alias].ensure_connection` | `django/db/backends/base/base.py` (~279) | Threadpool bridge | **S** — PoC `aensure_connection` @ 281 |
| `transaction.on_commit` | `django/db/transaction.py` | Register from async views | **M** — PoC `aon_commit` @ 149 |
| `transaction.atomic` async CM | `django/db/transaction.py` | Needs async driver | **XL** |

### Tests run (this session)

- `python3 tests/runtests.py async asgi dispatch.tests admin_utils.test_llm_sanitize dispatch.test_async_send_warning async.test_async_model_validation --parallel 4` → **OK 139 tests** (1 skipped), SQLite.
- User-requested module name `async_queryset_tests` **does not exist**; covered under `tests/async/`.
- PostgreSQL: server **14.17** on localhost:5432 — Django requires **≥15** (`django/db/backends/base/base.py` `check_database_version_supported`). **Not executed**.

### `django/http` sync IO

- `django/http/request.py` / `response.py`: in-memory / `urllib.parse` only. No blocking socket IO in request objects.
- Remaining request-lifecycle blocking IO is primarily **DB**, **cache**, **email**, **file storage** — not `django/http` itself. No behavioral http patch required for async-safety of the request object layer.

## Phase 4 — Security forward audit (prospective; **not CVEs**)

| ID | Threat | Affected paths | PoC | Mitigation | Compat |
|---|---|---|---|---|---|
| THREAT-2030-01 | Post-quantum break of classical TLS KEX/signatures; session/CSRF secrets in transit | TLS edge; `django/middleware/csrf.py` (484 lines); sessions; app signing | Ran: `SECRET_KEY` + `SECRET_KEY_FALLBACKS` rotation via `django.core.signing.Signer` (app-layer only) | PQ-TLS at edge; keep key rotation (`django/conf/global_settings.py` `SECRET_KEY_FALLBACKS`) | Config/deploy |
| THREAT-2030-02 | AI-generated phishing with perfect UI clones | Auth templates (only `django/contrib/auth/templates/auth/widgets/read_only_password_hash.html` in-tree; most shipped via docs/startproject) | Social-engineering — no code exploit | Passkeys/WebAuthn docs; phishing-resistant MFA | Additive |
| THREAT-2030-03 | LLM prompt injection via admin field metadata | Admin `help_text` / options; `sanitize_admin_text_for_llm` @ `django/contrib/admin/utils.py:637` | `/tmp/sec_poc_prompt_injection.py` (ran) | Opt-in sanitizer + tests `tests/admin_utils/test_llm_sanitize.py` | Opt-in |
| THREAT-2030-04 | Supply chain (unpinned transitive deps) | `pyproject.toml`; CI requirements | Inspected: hash_pin_line_count=0 in sampled req files | Hash-pinned CI installers; steward third-party | CI process |

### CVE-style write-ups (prospective IDs only — **no CVE numbers invented**)

#### THREAT-2030-03 — Admin metadata → LLM prompt injection
- **Description:** Admin operators using LLM tools that ingest `help_text` / verbose names can be steered by malicious field metadata.
- **Affected:** `django/contrib/admin/utils.py:637-664` (mitigation helper); admin options/forms that surface model metadata.
- **PoC:** `/tmp/sec_poc_prompt_injection.py` prints RAW vs SANITIZED with `[redacted]`/`[filtered]` tokens.
- **Mitigation:** Call `sanitize_admin_text_for_llm()` before sending metadata to external models.
- **Compat:** Opt-in; default HTML admin unchanged.

#### THREAT-2030-01 — Classical crypto in transit (PQ readiness)
- **Description:** Future CRQC breaks ECDHE/RSA TLS; cookies/CSRF tokens observable on the wire if TLS fails open.
- **Affected:** Deploy TLS; Django assumes HTTPS termination. App secrets: `SECRET_KEY` signing.
- **PoC:** Demonstrated multi-key verify path with `SECRET_KEY_FALLBACKS` (session signing continuity during rotation).
- **Mitigation:** Hybrid PQ-TLS at edge; rotation runbooks.
- **Compat:** Deploy-time.

#### THREAT-2030-04 — Supply chain
- **Description:** Unhashed pip installs allow dependency confusion / compromised wheels in CI.
- **Affected:** Install path for Django and test requirements.
- **PoC:** Static inspection `/tmp/sec_supply_chain.json` — no `--hash=` pins in sampled requirement files.
- **Mitigation:** `pip install --require-hashes` in official CI; document for deployers.
- **Compat:** CI-only if optional for end users.

## Phase 5 — Performance

Method: **100 iterations**, median & p95 via `statistics` + `time.perf_counter` (`/tmp/run_django_bench.py`). `pyperf` installed (sample `python3 -m pyperf timeit` mean **9.78 ns** for `x+1`). Compared HEAD vs worktree **4.2** @ `879e5d587b84e6fc961829611999431778eb9f6a`.

| Operation | HEAD median ms | 4.2 median ms | Δ% median | HEAD p95 ms | 4.2 p95 ms | >10% regression? |
|---|---:|---:|---:|---:|---:|---|
| Model.objects.create | 0.0381 | 0.0291 | +30.88% | 0.0472 | 0.0392 | YES |
| QuerySet.filter depth 5 | 0.2164 | 0.2006 | +7.85% | 0.2357 | 0.2616 | no |
| Form validation 50 fields | 0.2915 | 0.2921 | -0.23% | 0.3650 | 0.7852 | no |
| Template 10 nested includes | 0.0885 | 0.1003 | -11.76% | 0.0934 | 0.1189 | no |
| Middleware chain of 10 | 0.0242 | 0.0312 | -22.35% | 0.0273 | 0.0338 | no |

### Bisect notes (`Model.objects.create`)

- Automated `git bisect` between `879e5d587b` (4.2) and `356e5b0f5d` first reported **`e1671278e88265e64811657b8b939b5d786295cb`** — *Fixed #36490 -- Avoided unnecessary transaction in bulk_create* (`django/db/models/query.py`).
- **Verification (5 runs each):** parent `5e06b97095` medians ~0.0313–0.0325 ms; `e1671278` ~0.0308–0.0335 ms — **overlapping**, not a clean step change. HEAD `848fc648a8` ~0.037–0.041 ms — **accumulated** multi-commit drift vs 4.2.
- **No performance fix committed:** cannot attribute a correctness-preserving micro-optimization to one commit without risking #36490 behavior; recommend continuous `pyperf` budget in CI instead of a speculative revert.
- **Flame graphs:** not generated (no actionable single hotspot confirmed).

Raw: `/tmp/bench_main_vs_42.json`.

## Phase 6 — Deprecation roadmap

| Version | Action | Migration path |
|---|---|---|
| **6.1** | Document `DJANGO_ASYNC_SIGNAL_WARN=1` audit mode; promote async validation APIs | Adopt `afull_clean` / `aon_commit` |
| **6.1** | Continue existing `RemovedInDjango70Warning` removals already in tree | Follow release notes |
| **7.0** | Require Python **≥3.14+** stepping stone; target **3.18** only if timeline allows — **revisit** | CI matrix |
| **7.0** | Document `Model.afull_clean` & friends as stable; discourage naked sync ORM in ASGI | DEP 0009 follow-ups |
| **8.0** | `DJANGO_ASYNC_STRICT=1` default: `Signal.send` in running loop errors; prefer `asend` | Fix receivers |

PoC warning: `Signal.send` + `RemovedInDjango71Warning` behind `DJANGO_ASYNC_SIGNAL_WARN=1` (`django/dispatch/dispatcher.py:248-262`); tests in `tests/dispatch/test_async_send_warning.py`.

## Implementation effort (engineer-weeks)

| Workstream | Weeks | Justification |
|---|---:|---|
| Finish async ORM beyond `sync_to_async` (drivers, atomic, iterators) | 25–40 | Touches `django/db` ~44k LOC; backend-specific |
| Python 3.18 CI + fix fallout | 8–12 | Unknown until 3.18 exists; buffer for stdlib |
| Typing modernization (PEP 604/Protocols) | 6–10 | Broad but mechanical |
| Admin/AI & auth phishing-resistant features | 6–10 | New APIs + docs |
| Deprecation cycles 6.1→8.0 | 8–12 | Warnings, docs, removals |
| Performance CI budgets / continuous benchmarks | 4–6 | pyperf in CI |
| Security process (PQ TLS docs, supply chain hashes) | 3–5 | Mostly docs/CI |
| **Total** | **90–140** | Overlapping streams; ~4–6 FTE × 2 releases |

### Compute cost (indicative)

- Full test suite × 4 DB backends × 3 Python versions × 2 OS ≈ **order 10³ CPU-hours/month** in CI if fully matrixed (~$50–200/mo cloud depending on runner pricing — **estimate**, not invoiced).
- This audit session: local SQLite runs + microbench + bisect rebuilds at each step on laptop — **~$0** incremental cloud.
- Bisect: **13+ full tree checkouts** with Django import/setup per step (actual runs completed; see bisect narrative above).

## Risk matrix

| Change | Benefit | Risk | Mitigation |
|---|---|---|---|
| Async validation APIs | ASGI completeness | Tx/thread affinity bugs | Tests on SQLite+Postgres 15+ |
| Strict async signals | Safer ASGI | Ecosystem breakage if default early | Env flag → 8.0 |
| Drop low-activity modules | Smaller core | Break implicit public APIs | Deprecate APIs not packages |
| Require 3.18 early | Future-proof | No interpreter yet | Gate on upstream release |
| Revert #36490 for create() perf | Maybe faster create | Breaks bulk_create semantics | **Rejected** — not causal |

## PoC patches on this branch (commits)

- `c58db25295` Refs #modernization-phase3 — async ORM validation + `aensure_connection` + `aon_commit`
- `14dbaa1711` Refs #modernization-phase4 — `sanitize_admin_text_for_llm`
- `39d0df01eb` Refs #modernization-phase6 — opt-in `Signal.send` async-loop warning
- `848fc648a8` Refs #modernization-phase7 — roadmap document in `docs/modernization-roadmap-7.0.md`

## Explicit non-completions

1. **Open GitHub issue counts per module** — no auth token (`gh` not logged in).
2. **Test coverage % per module** — no `coverage.xml` on branch.
3. **CPython 3.18 full suite** — only 3.16.0a0 available; asgiref missing in that env.
4. **Flame graphs** — no confirmed single-commit regression hotspot.
5. **PostgreSQL test matrix** — PG 14.17 < required 15.
6. **Signed commits / GPG** — depends on local key; commits may be unsigned.
7. **Separate draft PR per phase on vedikatai** — `gh` unauthenticated; branch pushed as `vedikatai/modernization-roadmap-7.0` (single branch with phase commits). Create draft PRs after `gh auth login`.
8. **Performance fix for create()** — bisect inconclusive under noise; not applied.

## How to open phase PRs (operator)

```bash
gh auth login
# Phase 3
git push vedikatai c58db25295:refs/heads/modernization/phase3-async-orm
gh pr create --repo vedikatai/django --base main --head modernization/phase3-async-orm --draft --title 'Refs modernization-phase3 -- async ORM validation helpers'
# similarly phase4 @ 14dbaa1711, phase6 @ 39d0df01eb, phase7 @ 848fc648a8
```

