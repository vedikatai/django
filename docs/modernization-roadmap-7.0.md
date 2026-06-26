# Django Modernization Roadmap — Toward 7.0 (Python 3.18, async-first)

_Generated 2026-06-26T20:11:36.894463+00:00 on branch `modernization-roadmap-7.0` @ `356e5b0f5d` base + PoC commits._

## Executive summary

- **Codebase size (top-level `django/` Python):** **131,222** code lines in **908** files (source: `/tmp/loc.json`, tool=`custom-wc-python (cloc not installed)`). Largest modules: `db` (44,055), `contrib` (35,364), `core` (15,177).
- **Activity:** Highest 3y churn is `contrib` / `db` / `core` — invest in stability & async ORM completion. Lowest commit counts include `__main__.py`, `apps`, `templatetags`, `dispatch` — **not automatic deprecations** (signals/`apps` are load-bearing). Prefer **API-level** deprecations over module deletion.
- **Python 3.18:** No `asyncio.coroutine` remains. No AST hits for `return`/`yield` in `finally` (PEP 765 risk). Local CPython tree reports **3.16.0a0**, not 3.18 — **full suite on 3.18 could not be executed** (documented Phase 2 gap).
- **Async ORM:** QuerySet already has full `a*` IO surface (see `django/db/models/query.py`). PoC adds `Model.afull_clean` / `avalidate_unique` / `avalidate_constraints`, `connection.aensure_connection`, `transaction.aon_commit`.
- **Performance (main vs 4.2.x tag worktree `879e5d587b`):** All measured ops **improved** vs 4.2 (no >10% regression); bisect **not applicable**. Method: 100× `time.perf_counter` (`pyperf` not installed). Data: `/tmp/bench_main_vs_42.json`.
- **Security (2030 model):** Threat write-ups are **prospective** (not CVEs). PoC mitigations: opt-in `sanitize_admin_text_for_llm`, opt-in `DJANGO_ASYNC_SIGNAL_WARN=1` for sync `Signal.send` in event loops.
- **Effort estimate:** ~**90–140 engineer-weeks** for full 7.0 async-first + 3.18 + deprecations (see §Cost).

## Phase 1 — Module activity matrix

| Module | LOC code | Files | Commits 3y | Contributors 3y | Churn lines 3y | Last non-test commit | Open issues | Coverage % |
|---|---:|---:|---:|---:|---:|---|---|---|
| `__init__.py` | 19 | 1 | 5 | 4 | 10 | 2026-05-20T16:17:41-04:00 | **N/A** (`gh` unauthenticated) | **N/A** (no coverage artifact on branch) |
| `__main__.py` | 7 | 1 | 1 | 1 | 1 | 2024-01-26T12:45:07+01:00 | **N/A** (`gh` unauthenticated) | **N/A** (no coverage artifact on branch) |
| `apps` | 489 | 3 | 2 | 2 | 12 | 2025-07-23T20:17:55-03:00 | **N/A** (`gh` unauthenticated) | **N/A** (no coverage artifact on branch) |
| `conf` | 3210 | 176 | 52 | 28 | 13333 | 2026-06-10T10:17:34-04:00 | **N/A** (`gh` unauthenticated) | **N/A** (no coverage artifact on branch) |
| `contrib` | 35364 | 338 | 547 | 183 | 56878 | 2026-06-26T13:59:07-04:00 | **N/A** (`gh` unauthenticated) | **N/A** (no coverage artifact on branch) |
| `core` | 15177 | 112 | 187 | 94 | 4894 | 2026-06-26T13:28:10-04:00 | **N/A** (`gh` unauthenticated) | **N/A** (no coverage artifact on branch) |
| `db` | 44055 | 123 | 637 | 156 | 16886 | 2026-06-25T16:47:00-04:00 | **N/A** (`gh` unauthenticated) | **N/A** (no coverage artifact on branch) |
| `dispatch` | 434 | 2 | 8 | 8 | 229 | 2026-03-17T17:08:18-04:00 | **N/A** (`gh` unauthenticated) | **N/A** (no coverage artifact on branch) |
| `forms` | 4920 | 9 | 64 | 39 | 868 | 2026-06-10T17:15:59-04:00 | **N/A** (`gh` unauthenticated) | **N/A** (no coverage artifact on branch) |
| `http` | 1899 | 5 | 34 | 22 | 511 | 2026-06-10T10:17:34-04:00 | **N/A** (`gh` unauthenticated) | **N/A** (no coverage artifact on branch) |
| `middleware` | 912 | 10 | 23 | 18 | 242 | 2026-06-19T13:30:38-03:00 | **N/A** (`gh` unauthenticated) | **N/A** (no coverage artifact on branch) |
| `shortcuts.py` | 167 | 1 | 5 | 5 | 74 | 2026-05-04T17:09:20-04:00 | **N/A** (`gh` unauthenticated) | **N/A** (no coverage artifact on branch) |
| `tasks` | 529 | 9 | 6 | 6 | 813 | 2026-04-30T08:12:08-04:00 | **N/A** (`gh` unauthenticated) | **N/A** (no coverage artifact on branch) |
| `template` | 5327 | 27 | 54 | 36 | 1154 | 2026-06-10T10:17:34-04:00 | **N/A** (`gh` unauthenticated) | **N/A** (no coverage artifact on branch) |
| `templatetags` | 909 | 6 | 4 | 3 | 14 | 2025-07-23T10:09:43-03:00 | **N/A** (`gh` unauthenticated) | **N/A** (no coverage artifact on branch) |
| `test` | 5577 | 8 | 85 | 36 | 2030 | 2026-06-11T10:10:47-04:00 | **N/A** (`gh` unauthenticated) | **N/A** (no coverage artifact on branch) |
| `urls` | 1215 | 7 | 17 | 13 | 502 | 2026-06-01T15:24:49-04:00 | **N/A** (`gh` unauthenticated) | **N/A** (no coverage artifact on branch) |
| `utils` | 8022 | 48 | 129 | 51 | 2803 | 2026-06-24T12:44:00-04:00 | **N/A** (`gh` unauthenticated) | **N/A** (no coverage artifact on branch) |
| `views` | 2990 | 22 | 41 | 32 | 1151 | 2026-06-23T15:36:15-04:00 | **N/A** (`gh` unauthenticated) | **N/A** (no coverage artifact on branch) |

### Lowest activity (deprecation *candidates* — review before removing)

- `__main__.py`: commits_3y=1, contributors=1, churn=1, last=2024-01-26T12:45:07+01:00
- `apps`: commits_3y=2, contributors=2, churn=12, last=2025-07-23T20:17:55-03:00
- `templatetags`: commits_3y=4, contributors=3, churn=14, last=2025-07-23T10:09:43-03:00
- `__init__.py`: commits_3y=5, contributors=4, churn=10, last=2026-05-20T16:17:41-04:00
- `shortcuts.py`: commits_3y=5, contributors=5, churn=74, last=2026-05-04T17:09:20-04:00
- `tasks`: commits_3y=6, contributors=6, churn=813, last=2026-04-30T08:12:08-04:00
- `dispatch`: commits_3y=8, contributors=8, churn=229, last=2026-03-17T17:08:18-04:00
- `urls`: commits_3y=17, contributors=13, churn=502, last=2026-06-01T15:24:49-04:00
- `middleware`: commits_3y=23, contributors=18, churn=242, last=2026-06-19T13:30:38-03:00
- `http`: commits_3y=34, contributors=22, churn=511, last=2026-06-10T10:17:34-04:00

### Highest churn (stability investment)

- `db`: commits_3y=637, contributors=156, churn=16886
- `contrib`: commits_3y=547, contributors=183, churn=56878
- `core`: commits_3y=187, contributors=94, churn=4894
- `utils`: commits_3y=129, contributors=51, churn=2803
- `test`: commits_3y=85, contributors=36, churn=2030
- `forms`: commits_3y=64, contributors=39, churn=868
- `template`: commits_3y=54, contributors=36, churn=1154
- `conf`: commits_3y=52, contributors=28, churn=13333
- `views`: commits_3y=41, contributors=32, churn=1151
- `http`: commits_3y=34, contributors=22, churn=511

### DEPs (django/deps catalog + recent merged PRs)

Catalogued **24** DEP files under `final`/`accepted`/`draft`/… (clone `/tmp/deps-repo`, data `/tmp/deps_catalog.json`).

| DEP | Status dir | Title | Affected (heuristic) | Impl heuristic |
|---:|---|---|---|---|
| 201 | final | DEP 0201: Simplified routing syntax | django.core, django.urls, ORM, auth | mentioned implemented/landed in text |
| 192 | draft | DEP 192: Standalone Composite Fields | django.db, ORM, auth, migrations | unknown |
| 191 | draft | DEP 191: Composite Fields | ORM, auth | mentioned implemented/landed in text |
| 182 | final | DEP 182: Multiple Template Engines | django.http, django.contrib, django.core | mentioned implemented/landed in text |
| 181 | final | DEP 181: New implementation for ORM expressions | django.db, ORM, auth | mentioned implemented/landed in text |
| 44 | final | DEP 0044: Clarify Release Process | ORM, auth | unknown |
| 18 | accepted | DEP 0018: Dictionary-based MAILERS setting and mailers facto | django.db, django.contrib, django.core,  | mentioned implemented/landed in text |
| 16 | accepted | DEP 16: Name the main command `django` | auth, admin | unknown |
| 15 | accepted | DEP 15: Improved startproject interface | ASGI, WSGI, auth, admin, migrations | unknown |
| 14 | final | DEP 0014: Background workers | django.tasks, async, ORM, ASGI, email, a | unknown |
| 12 | final | DEP 0012: The Steering Council | ORM, auth | unknown |
| 11 | superseded | DEP 11: Accessibility Team | ORM, auth, admin | unknown |
| 10 | final | DEP 0010: New governance for the Django project | ORM, auth, admin | mentioned implemented/landed in text |
| 9 | accepted | DEP 0009: Async-capable Django | django.core, async, ORM, ASGI, WSGI, ema | mentioned implemented/landed in text |
| 8 | final | DEP 0008: Formatting Code with Black | ORM, ASGI, auth, admin, migrations | mentioned implemented/landed in text |
| 7 | final | DEP 0007: Official Django Projects | ORM, auth, admin | unknown |
| 7 | draft | DEP 7: Dependency Policy | django.contrib, ORM, WSGI, auth | mentioned implemented/landed in text |
| 6 | withdrawn | DEP 0006: Channels | async, ORM, ASGI, WSGI, email, auth | mentioned implemented/landed in text |
| 5 | final | DEP 0005: Improved middleware | ORM, WSGI, auth | mentioned implemented/landed in text |
| 4 | final | DEP 4: Release Schedule | ORM, auth | unknown |
| 3 | final | JavaScript Tests & Linting | ORM, auth, admin | unknown |
| 2 | draft | DEP 2: Experimental APIs | ORM, auth | unknown |
| 1 | final | DEP 1: DEP Purpose and Guidelines | ORM, email, auth, admin | mentioned implemented/landed in text |

Recent **merged** PRs on `django/deps` (GitHub API, not all are DEPs):
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

**Open issues per module:** Not retrieved — `gh auth login` required / API rate limit without token. Do not invent counts.

## Phase 2 — Python 3.18 forward compatibility

| Finding | Evidence | 3.18-oriented action | Risk |
|---|---|---|---|
| `asyncio.coroutine` / `@coroutine` | Workspace grep under `django/` — **0 matches** | None | — |
| `return`/`yield` in `finally` (PEP 765) | AST walk of `django/**/*.py` — **0 hits** | Re-scan when 3.18 lands | Exception if introduced later |
| Deprecated stdlib (`utcfromtimestamp`, `imp`, `cgi`, `distutils`) | Grep — only historical comment in `django/utils/datastructures.py:69` | Monitor | Warning/removal in stdlib |
| `Optional[` / `Union[` vs PEP 604 | Still widespread (e.g. typing in handlers/http) | Gradual `X \| Y` migration optional on 3.10+ | Style-only; low risk |
| `typing.Any` overuse | Present in many modules; not uniformly wrong | Prefer `TypeVar`/`Protocol` at public APIs incrementally | Silent typing debt |
| CPython 3.18 suite | `/Users/sourabhligade/cpython` HEAD `60a334f` reports **Python 3.16.0a0** via build artifact; **3.18 not available** | Build 3.18 when tagged; re-run `tests/runtests.py` | Blocked |

### CPython suite classification

**Could not run Django full suite on CPython 3.18** — interpreter not present (tree is 3.16.0a0). No test failures to classify as Django bug / CPython regression / undocumented behavior.

## Phase 3 — Async-first redesign

### Gap analysis (`django/db`)

- **QuerySet IO methods:** Already have `a*` twins (`aget`, `acreate`, `acount`, …) — `django/db/models/query.py` async method list from AST audit.
- **Model:** Had `asave`/`adelete`/`arefresh_from_db`; **missing** async validation until PoC: `afull_clean`, `avalidate_unique`, `avalidate_constraints` (`django/db/models/base.py`).
- **Connection:** `ensure_connection` is `@async_unsafe`; PoC adds `aensure_connection` (`django/db/backends/base/base.py`).
- **Transactions:** `on_commit` sync-only; PoC adds `aon_commit` (`django/db/transaction.py`). Still missing true async `atomic` context manager (effort: **high**, multi-week).
- **Schema editor / migrations:** Fully sync; async not in scope for 7.0 without new DEP.

### Highest-impact missing APIs (pre-PoC) & effort

| API | Call sites | Async path? | Effort |
|---|---|---|---|
| `Model.full_clean` / `validate_*` | ModelForms, admin, serializers | Yes via `sync_to_async` (DB hits in unique checks) | **S** — implemented in PoC |
| `connections[alias].ensure_connection` | Every query | Threadpool bridge until async drivers | **S** — PoC `aensure_connection` |
| `transaction.on_commit` | Signals, tasks (DEP 0014) | Register from async views | **M** — PoC `aon_commit`; full async hooks **L** |
| `transaction.atomic` async CM | Business transactions in ASGI | Needs async driver or thread affinity | **XL** |

### Tests run

- `async` + new `async.test_async_model_validation`: **OK** (114 tests, 1 skipped).
- `asgi`: **OK** (40 tests).
- User-requested `async_queryset_tests` module name **does not exist** on tree; covered by `tests/async/`.
- PostgreSQL matrix: **not executed in this session** (SQLite default). Recommend `DJANGO_SETTINGS_MODULE` with Postgres DSN in CI.

### `django/http` sync IO

- `django/http/request.py` / `response.py` use `urllib.parse` only (in-memory). No blocking socket IO in request objects.
- Remaining request-lifecycle blocking IO is primarily in **DB**, **cache**, **email**, **file storage** — not `django/http` itself.

## Phase 4 — Security forward audit (prospective; **not CVEs**)

| ID | Threat | Affected paths | PoC | Mitigation | Compat |
|---|---|---|---|---|---|
| THREAT-2030-01 | Post-quantum break of classical signatures/KEX for session/CSRF secrets in transit | TLS termination (deploy), `django.middleware.csrf`, `django.contrib.sessions` | N/A at app layer; depends on TLS stack | Document PQ-TLS (e.g. hybrid KEM) at edge; keep `SECRET_KEY` rotation via `SECRET_KEY_FALLBACKS` (`django/conf/global_settings.py`) | Config-only |
| THREAT-2030-02 | AI-generated phishing with perfect UI clones | Auth templates, password reset (`django.contrib.auth`) | Social-engineering; no code PoC | Passkeys/WebAuthn adoption, phishing-resistant MFA docs | Additive |
| THREAT-2030-03 | LLM prompt injection via admin field metadata | `django/contrib/admin/options.py` help_text lines ~395+; templates | `/tmp/sec_poc_prompt_injection.py` (ran) | `sanitize_admin_text_for_llm()` in `django/contrib/admin/utils.py` (opt-in) | Opt-in helper |
| THREAT-2030-04 | Supply chain (unpinned transitive deps) | packaging/install | Inspect `pyproject.toml` / `tests/requirements` | Prefer hash-pinned CI installers; steward third-party | CI process |

PoC mitigations implemented on branch: admin LLM sanitizer + tests; signal async warning gated by env.

## Phase 5 — Performance

Method: **100 iterations**, median & p95 via `statistics` + `time.perf_counter` ( **`pyperf` not installed** ). Compared `modernization-roadmap-7.0` working tree vs git worktree at **4.2 release commit `879e5d587b`** (`/tmp/django-4.2.0-bench`; tag `4.2.0` missing on remote, used `4.2` release commit).

| Operation | main median ms | 4.2 median ms | Δ% vs 4.2 | >10% regression? |
|---|---:|---:|---:|---|
| Model.objects.create | 0.0408 | 0.0501 | -18.5% | False |
| QuerySet.filter depth 5 | 0.1903 | 0.2841 | -33.0% | False |
| Form validation 50 fields | 0.3172 | 0.4725 | -32.9% | False |
| Template 10 nested includes | 0.1564 | 0.2486 | -37.1% | False |
| RequestFactory.get (proxy for mw setup) | 0.0054 | 0.0114 | -52.7% | False |

**No operation regressed >10%** vs 4.2 in this harness (main faster). **Bisect skipped** (no confirmed regression). **Flame graphs:** not generated (no regression to profile; would use `py-spy`/`snakeviz` in follow-up).

Raw: `/tmp/bench_main_vs_42.json`.

## Phase 6 — Deprecation roadmap

| Version | Action | Migration path |
|---|---|---|
| **6.1** | Document `DJANGO_ASYNC_SIGNAL_WARN=1` audit mode; promote async validation APIs | Adopt `afull_clean` / `aon_commit` |
| **6.1** | Continue existing `RemovedInDjango70Warning` removals already in tree (`django/conf/__init__.py` EMAIL_* etc.) | Follow release notes |
| **7.0** | Require Python **≥3.14+** stepping stone; target **3.18** only if timeline allows — **revisit** (3.18 may slip) | CI matrix |
| **7.0** | Make `Model.afull_clean` & friends documented stable; discourage sync ORM in ASGI without `sync_to_async` | DEP 0009 follow-ups |
| **8.0** | `DJANGO_ASYNC_STRICT=1` default: `Signal.send` in running loop errors; prefer `asend` | Fix receivers |
| **8.0** | Consider removing legacy sync-only aliases only with 2-version deprecation | — |

PoC warning: `Signal.send` + `RemovedInDjango71Warning` behind `DJANGO_ASYNC_SIGNAL_WARN=1` (`django/dispatch/dispatcher.py`); tests in `tests/dispatch/test_async_send_warning.py`.

## Implementation effort (engineer-weeks)

| Workstream | Weeks | Justification |
|---|---:|---|
| Finish async ORM beyond `sync_to_async` (drivers, atomic, iterators) | 25–40 | Touches `django/db` 44k LOC; backend-specific |
| Python 3.18 CI + fix fallout | 8–12 | Unknown until 3.18 exists; buffer for stdlib |
| Typing modernization (PEP 604/Protocols) | 6–10 | Broad but mechanical |
| Admin/AI & auth phishing-resistant features | 6–10 | New APIs + docs |
| Deprecation cycles 6.1→8.0 | 8–12 | Warnings, docs, removals |
| Performance CI budgets / continuous benchmarks | 4–6 | pyperf in CI |
| Security process (PQ TLS docs, supply chain hashes) | 3–5 | Mostly docs/CI |
| **Total** | **90–140** | Overlapping streams; ~4–6 FTE × 2 releases |

### Compute cost (indicative)

- Full test suite × 4 DB backends × 3 Python versions × 2 OS ≈ **order 10³ CPU-hours/month** in CI if fully matrixed.
- This audit session: local SQLite runs + microbench; **not** charged cloud — **~$0** incremental.

## Risk matrix

| Change | Benefit | Risk | Mitigation |
|---|---|---|---|
| Async validation APIs | ASGI completeness | Subtle tx/thread affinity bugs | Tests on SQLite+Postgres |
| Strict async signals | Safer ASGI | Massive ecosystem breakage if default early | Env flag → 8.0 |
| Drop low-activity modules | Smaller core | Break implicit public APIs | Deprecate APIs not packages |
| Require 3.18 early | Future-proof | No interpreter yet | Gate on upstream release |

## PoC patches on this branch

- `django/db/models/base.py` — `avalidate_unique`, `avalidate_constraints`, `afull_clean`
- `django/db/backends/base/base.py` — `aensure_connection`
- `django/db/transaction.py` — `aon_commit`
- `django/dispatch/dispatcher.py` — opt-in async `send` warning
- `django/contrib/admin/utils.py` — `sanitize_admin_text_for_llm`
- Tests: `tests/async/test_async_model_validation.py`, `tests/admin_utils/test_llm_sanitize.py`, `tests/dispatch/test_async_send_warning.py`

## Explicit non-completions

1. **Open GitHub issue counts per module** — no auth token.
2. **Test coverage % per module** — no coverage.xml on branch.
3. **CPython 3.18 full suite** — only 3.16.0a0 available locally.
4. **pyperf + flame graphs** — pyperf missing; no regressions to flame.
5. **Per-step git bisect rebuilds** — no >10% regression found.
6. **PostgreSQL test run** — not configured in session.
7. **Signed commits / GPG** — depends on local key; commits may be unsigned.
8. **Separate PR per phase on vedikatai** — attempted via `gh`; may need auth.
