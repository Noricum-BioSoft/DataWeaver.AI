---
name: Noricum scientific context layer (DataWeaver side)
overview: DataWeaver.AI's share of the Noricum scientific orchestration platform — the persistent scientific context and memory layer that Helix.AI reasons over. Derived from the master plan in the Helix.AI repo; this file is the working plan for anyone operating in the DataWeaver workspace.
status: proposed (derived from master plan rev 2, 2026-10-07)
master_plan: Helix.AI/.cursor/plans/noricum-scientific-orchestration-platform.md
gap_analysis: Helix.AI/docs/architecture/NORICUM_PLATFORM_GAP_ANALYSIS.md (§3 DataWeaver current state, §5 decisions D1–D2)
todos:
  - id: p5-knowledge-model
    content: "P5: canonical knowledge tables (caller-supplied UUIDs, trace_id, schema_version) + relationships + provenance_events; compatibility adapters over legacy Design/Build/Test/File; additive Alembic migration only"
    status: pending
  - id: p6-context-api
    content: "P6: /api/context routers — idempotent PUT-by-domain-id writes, read endpoints incl. /traces/{trace_id}; analysis services persist AnalysisResult/Artifact/ProvenanceEvent; X-Service-Key auth; deps/Docker/CI; OpenAPI snapshot"
    status: pending
  - id: p7-dw-side
    content: "P7 (DW side): serve Helix's dual-mode parity checks; recorded-response fixtures; contract test against docs/openapi.yaml"
    status: pending
  - id: p9-dw-docs
    content: "P9 (DW side): docs/API.md for the Context API; ORCH-001 assertions that depend on DataWeaver"
    status: pending
---

# Noricum Scientific Context Layer — DataWeaver.AI plan

> **Helix owns reasoning and orchestration. DataWeaver owns persistent scientific context and memory.**
> Helix never gets raw database access; it talks to DataWeaver only through the Scientific Context API.

This is the DataWeaver.AI slice of the cross‑repo master plan. The master plan is the source of truth for sequencing, contracts and acceptance criteria; when the two disagree, update **both** (the master plan carries a review‑feedback mapping that must stay accurate). Phase numbers are kept identical to the master plan so cross‑references work.

Repo layout assumption: both repos are checked out as siblings under `~/git/Noricum/` (`Helix.AI/`, `DataWeaver.AI/`).

## Principles that bind this repo

1. **Strangler, not rewrite — inside DataWeaver too.** Introduce the canonical model beside the legacy tables; serve legacy rows through compatibility adapters; **no data migration and no table retirement** in P5/P6. Existing `/api/bio/*`, `/api/workflows/*`, `/api/files/*` endpoints keep working unchanged.
2. **IDs originate in Helix.** Every shared domain object (objective, plan, assessment, authorization, intent, approval, execution request/run, observation, decision, artifact, provenance event) arrives with its UUID. DataWeaver **never mints IDs for shared objects**; a duplicate ID is an integrity error, not a silent new row.
3. **One `trace_id` per scientific loop.** Every canonical row carries `trace_id`; `GET /api/context/traces/{trace_id}` returns the whole loop.
4. **Writes are idempotent upserts.** `PUT /api/context/<type>/{domain_id}`: same body twice → `200`, no duplicate; conflicting body for an immutable type (intent, approval, assessment, provenance event) → `409`; conflicting body for a versioned type (objective, plan) → new version with `supersedes`.
5. **Every write produces provenance.** Each `PUT` creates its `ProvenanceEvent` and `relationships` edges in the same transaction.
6. **Structured rationale, not reasoning traces.** Store `rationale: list[RationaleItem{evidence_refs, statement, conclusion, confidence}]` as JSONB; never a free‑text "reasoning" column.
7. **Postgres + JSONB, no graph DB.** `relationships` is a polymorphic edge table (decision D1). SQLite stays the dev/test default; Postgres via `docker-compose.test.yml` before merging any migration.
8. **Safe data only.** Fixtures and `sample_data/` only; never production data; no credentials in code or YAML.

## Shared contracts (defined in Helix, mirrored here)

Pydantic sources of truth live in `Helix.AI/backend/contracts/` and `Helix.AI/shared/` (P0 of the master plan). Until a shared package exists (revisit at P7), DataWeaver keeps **JSON‑schema snapshots** in `backend/app/schemas/contracts/*.json`, exported from Helix (`test_platform_contracts.py` emits them), and validates request bodies against them. Field names below are normative.

| Contract | Key fields DataWeaver must store |
|---|---|
| `ScientificObjective` | `objective_id, trace_id, version, objective, question, constraints, desired_evidence[], success_criteria[], status: proposed\|active\|answered\|abandoned, parent_decision_id?` |
| `ScientificPlan` | `plan_id, trace_id, version, objective_id, plan_hash, plan_rationale[], steps[], required_capabilities[], status, supersedes?` (full JSON stored) |
| `SecurityAssessment` | `assessment_id, trace_id, plan_id, plan_hash, assessment_hash, outcome, rationale[], applied_policies[], screening_results[], policy_envelope{}` |
| `ExecutionRecommendation` | `recommendation_id, trace_id, plan_id, provider_id, capability_id, candidate_set[], criteria_scores{}, rationale[]` |
| `ProviderAuthorization` | `authorization_id, trace_id, recommendation_id, assessment_id, provider_id, result, checks[]` |
| `ExecutionIntent` (immutable) | `execution_intent_id, trace_id, plan_id, plan_hash, assessment_id?, recommendation_id?, authorization_id?, provider_id, capability_id, input_manifest_hash, execution_parameters_hash, execution_intent_hash` |
| `HumanApproval` (immutable) | `approval_id, trace_id, execution_intent_id, execution_intent_hash, decision, principal{subject_id, identity_provider, roles[], tenant_id?}, timestamp, selected_recommendation_id?` |
| `ExecutionRequest` / `ExecutionRun` | `execution_request_id, execution_intent_id, approval_id, idempotency_key (unique), provider_id, provider_handle?` / `execution_run_id, status, cost_actual?, outputs[]` |
| `Observation` / `Interpretation` / `NextDecision` | observation has **no claims** (metric/value/unit/artifact_refs); decision has `kind`, `rationale[]`, `evidence_ids[]`, `proposed_objective?` |
| `ProvenanceRecord` | `event_id, trace_id, event_type, actor{kind,id}, tool, tool_version, model_version?, agent_id?, agent_version?, prompt_template_id?, prompt_template_version?, prompt_template_hash?, code_commit?, schema_version, parameters{}, execution_backend?, provider_id?, inputs[], outputs[], timestamp` |
| `CapabilityDescriptor` | stored in `capabilities` with `source: manual\|generated\|provider`, `catalog_sha?`, `pinned_release?`, `promoted_by/at` |

---

## Phase 5 — Knowledge model v1 (~5 days) — MUST

**Package** `backend/app/models/knowledge/` (one module per aggregate; all tables: UUID PK supplied by caller, `trace_id`, `schema_version int`, `attrs JSONB`, `created_at/updated_at`, `created_by`).

Tables: `scientific_objectives`, `hypotheses`, `experiment_plans`, `experiments`, `experimental_conditions`, `samples`, `biological_entities` (`entity_type`, `sequence?`, `lineage_hash`, `parent_id`), `artifacts` (`uri`, `content_hash`, `format`, `supersedes_id`), `measurements` (`value`, `unit`, `method`, `sample_id`, `entity_id`, `confidence`), `observations`, `analysis_results`, `conclusions`, `decisions`, `capabilities`, `execution_providers`, `execution_intents`, `execution_requests` (`idempotency_key` unique), `security_assessments` (`policy_envelope JSONB`), `provider_authorizations`, `human_approvals`, `execution_runs`, `provenance_events`.

`relationships`: `subject_type, subject_id, predicate, object_type, object_id, confidence?, provenance_event_id?, attrs JSONB`; unique on the 5‑tuple; indexes `(subject_type, subject_id)` and `(object_type, object_id)`. Predicates v1: `motivated, produced, analyzed_by, supports, contradicts, based_on, generated, derived_from, measured_on, part_of, executed_by, assessed_by, authorized_by, approved_by, supersedes`.

**Compatibility adapters** `backend/app/services/compat/`: read‑only adapters presenting legacy rows in canonical shape — `Design/Build (models/bio_entities.py) → BiologicalEntity`, `Test → Measurement`, `File/FileMetadata → Artifact`, `FileRelationship → relationships(derived_from)`. SQL views where the dialect allows (Postgres), Python adapters for SQLite. Context API reads union canonical + compat results, tagged `origin: canonical|legacy`. `workflow_phases` tables (`app/models/workflow_phases.py`): leave untouched, mark legacy in docstrings.

**Migration:** one additive Alembic revision chained after `f7c123bd3c74` (new tables and indexes only). `app/database.py::create_tables()` imports the knowledge metadata. Legacy data migration and table retirement → LATER (master plan priorities), after Helix↔DW parity is proven in P7.

Tests (`backend/tests/knowledge/`, SQLite + optional Postgres compose): round‑trips with caller‑supplied IDs; duplicate ID → `IntegrityError`; edge uniqueness; recursive `get_provenance(type, id, depth)`; compat adapters return seeded legacy rows as canonical shapes; `alembic upgrade head` on empty and seeded DBs; **all existing tests stay green**.

Exit: new tables present; legacy endpoints unchanged; compat views serve seeded legacy data.

---

## Phase 6 — Scientific Context API (~5 days) — MUST

Router package `backend/app/api/context/` mounted at `/api/context` in `backend/main.py`; service auth `X-Service-Key` (constant‑time compare against `DATAWEAVER_SERVICE_KEYS` env, one key per caller) + `project_id` scoping; `backend/app/auth.py`. Note: the two colliding `/api/bio` routers (`app/api/bio_matcher.py`, `api/bio_entities.py`) are **not** touched here — tracked as a separate issue.

**Writes (idempotent upserts by domain id):** `PUT /objectives/{objective_id}`, `PUT /plans/{plan_id}`, `PUT /assessments/{assessment_id}`, `PUT /recommendations/{recommendation_id}`, `PUT /authorizations/{authorization_id}`, `PUT /intents/{execution_intent_id}`, `PUT /approvals/{approval_id}`, `PUT /executions/{execution_request_id}` + `PATCH /executions/{id}` (status, handle, results), `PUT /runs/{execution_run_id}`, `PUT /observations/{id}`, `PUT /analysis-results/{id}`, `PUT /conclusions/{id}`, `PUT /decisions/{id}`, `PUT /provenance-events/{event_id}`, `PUT /relationships` (natural key). Semantics per principle 4. Bodies validated against the contract JSON schemas.

**Reads:** `GET /objectives/{id}/context` (objective, hypotheses, prior experiments, evidence summary, prior decisions, open uncertainties — one bounded payload for Helix's planner), `GET /objectives/{id}/hypotheses`, `GET /evidence?objective_id|entity_id|dataset_id`, `GET /experiments?objective_id`, `GET /measurements?experiment_id|entity_id|sample_id`, `GET /provenance/{type}/{id}?depth=`, `GET /decisions?objective_id`, `GET /relationships?subject=|object=|predicate=`, `GET /traces/{trace_id}` (every record of one loop, ordered by `created_at`).

**Analysis integration:** `DataAnalyzer`, `simple_visualizer`, `IntelligentMerger`, `DataQAService` gain `persist(project_id, inputs[]) -> AnalysisResult + Artifact(s) + ProvenanceEvent(tool, tool_version, parameters, code_commit)`; `bio_matcher` session endpoints call it when `project_id` is supplied (session memory stays for UI continuity but is no longer the record). Ingest `POST /api/context/datasets/ingest` (CSV/Excel via existing loaders); PDF/report/image adapters as documented extension points under `app/services/ingest/`.

**Housekeeping (in scope, small):** declare `plotly`, `openpyxl`, `numpy` in `backend/requirements.txt`; drop unused `celery`, `redis`, `python-jose`; make the OpenAI model configurable (`DATAWEAVER_LLM_MODEL`, default unchanged) instead of hard‑coded `gpt-3.5-turbo`; add `backend/Dockerfile`; GitHub Actions workflow running `backend/tests` on SQLite; export OpenAPI snapshot to `docs/openapi.yaml` (regenerate via `scripts/convert_openapi.py`).

Tests: per‑endpoint (TestClient + SQLite); idempotency (double `PUT` → 200/no duplicate; conflicting `PUT` on immutable → 409; on versioned → new version); unauthenticated/foreign‑project → 401/403; `/traces/{trace_id}` returns the full seeded loop; contract test that responses validate against `docs/openapi.yaml`; analysis persistence links result → input dataset via `analyzed_by`.

Exit: OpenAPI snapshot committed; Helix consumes it as `Helix.AI/tests/fixtures/dataweaver_openapi.json`.

---

## Phase 7 — Integration (DataWeaver side; ~1 day of the 4) — MUST

Helix implements `KnowledgeStore` with a `dataweaver` backend and a `dual` mode that writes to both its local ledger and DataWeaver and asserts **id and hash parity** per object. DataWeaver's obligations:

- Recorded‑response fixtures for Helix's `respx` contract tests (`scripts/record_context_fixtures.py` → `docs/fixtures/context_api/*.json`).
- `GET /traces/{trace_id}` and `GET /provenance/measurement/{id}` must reach back to the objective for a full mock‑lab loop.
- Any schema change → regenerate `docs/openapi.yaml` and notify the Helix side (fixture refresh).

Exit (shared): closed‑loop mock‑lab demo persists the whole loop here and `/traces/{trace_id}` returns objective → plan → assessment → authorization → intent → approval → run → measurements → observation → decision.

---

## Phase 9 — Docs and acceptance (DataWeaver side) — MUST

- `docs/API.md`: Context API section (auth, idempotency semantics, trace queries, error codes).
- ORCH‑001 (`Helix.AI/tests/acceptance/test_orch_001_golden_path.py`) assertions that depend on this repo: "DataWeaver contains the resulting scientific context", "domain ids identical across stores", "provenance reaches from final decision to original inputs", "`/traces/{trace_id}` returns the loop".

## Verification (standing)

1. `cd backend && pytest tests/ -q` on SQLite — no regressions.
2. `docker compose -f backend/docker-compose.test.yml up` + `alembic upgrade head` + tests on Postgres before merging any migration.
3. OpenAPI snapshot regenerated and diffed when routers change.
4. Record results in `artifacts/test_results/<phase>.md` and notes in `artifacts/worklog.md` (create `artifacts/` in this repo on first use).

## Out of scope here (tracked in master plan / gap analysis)

- Resolving the duplicate `/api/bio` routers; in‑memory `WorkflowStateManager`/`DataContextManager` persistence; frontend changes; legacy data migration and table retirement (LATER); multi‑tenant auth beyond service keys.
