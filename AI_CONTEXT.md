# `n8n` — AI Context Pack (PRO)

> **Purpose of this file.** Single-source-of-truth context pack for AI coding agents working on this project. Read this **fully** before making changes. If anything contradicts the source code, treat code as authoritative and update this file.
>
> **Audience.** AI agents (Copilot / Claude / Cursor / Aider), engineers onboarding, investors auditing tech due diligence.
>
> **Hard rule.** Default admin credentials are `admin@vnso.vn / Admin@@3224@@`. **NEVER change them** in seeds, fixtures, or env files. This is the unbreakable recovery account.

---

## 0. TL;DR (60 seconds)

- **What.** Open-source workflow automation platform with 400+ integrations, AI-native capabilities, fair-code licensing (Sustainable Use License).
- **Why.** Enable VNSO users to build complex automations without coding; low-code visual workflows + JavaScript/Python when needed.
- **Status.** v2.16.0 production (upstream n8n.io community fork).
- **Stack.** Vue 3 SPA frontend + Node.js/Express backend + PostgreSQL (TypeORM) + Redis (ioredis v5.3.2 + BullMQ job queue) + execution-engine core for workflow state machines.
- **Surface.** REST API, webhook HTTP endpoints, WebSocket for real-time editor sync.
- **Risk class.** **critical-revenue** — automation platform is core to VNSO service delivery; workflow failure = customer SLA breach.

---

## 1. AI Quick Index

| What | Where | Purpose |
|------|-------|---------|
| **Backend entry** | [packages/cli/src/index.ts](packages/cli/src/index.ts) | Express server, API routes, middleware setup |
| **Workflow executor** | [packages/core/src/execution-engine/workflow-execute.ts](packages/core/src/execution-engine/workflow-execute.ts) | State machine: NEW→RUNNING→SUCCESS/ERROR/WAITING |
| **Webhook trigger** | [packages/cli/src/webhooks/webhook-request-handler.ts](packages/cli/src/webhooks/webhook-request-handler.ts) | HTTP POST → execute → enqueue job |
| **Job queue** | [packages/cli/src/scaling/bull-queue-factory.ts](packages/cli/src/scaling/bull-queue-factory.ts) | Redis job persistence + worker dequeue |
| **Execution lifecycle** | [packages/cli/src/execution-lifecycle/](packages/cli/src/execution-lifecycle/) | Hooks: before-run, after-node, on-error, on-finish |
| **i18n system** | [packages/frontend/@n8n/i18n/src/](packages/frontend/@n8n/i18n/src/) | Vue-i18n v11 + custom I18nClass (5000+ keys, en.json only active) |
| **Editor UI** | [packages/frontend/editor-ui/src/](packages/frontend/editor-ui/src/) | Vite + Vue 3 + CodeMirror 6 for code nodes |
| **Node base** | [packages/nodes-base/nodes/](packages/nodes-base/nodes/) | 400+ pre-built nodes (HTTP, Slack, Stripe, etc.) |
| **Database schema** | [packages/cli/src/databases/migrations/](packages/cli/src/databases/migrations/) | 100+ migrations; execution_record, workflow, credential tables |
| **Config loader** | [packages/cli/src/config/](packages/cli/src/config/) | Environment variables + runtime config validation |
| **Docker setup** | [docker-compose.yml](docker-compose.yml) | postgres, redis, api, worker services |
| **Package scripts** | [package.json](package.json) | `pnpm build`, `pnpm dev`, `pnpm test` entry points |

---

## 2. Repo Topology

```
n8n/
├── packages/
│   ├── cli/                              # Main API server + worker entrypoint
│   │   ├── src/
│   │   │   ├── index.ts                  # Express app + server startup
│   │   │   ├── active-executions.ts      # In-memory execution tracking + response modes
│   │   │   ├── active-workflow-manager.ts # Workflow activation + trigger registration
│   │   │   ├── config/                   # Runtime config + env parsing
│   │   │   ├── controllers/              # API route handlers (REST endpoints)
│   │   │   ├── databases/                # TypeORM + migrations
│   │   │   ├── execution-lifecycle/      # Execution hooks + error handlers
│   │   │   ├── executions/               # Execution record CRUD
│   │   │   ├── scaling/                  # BullMQ queue + worker process
│   │   │   ├── webhooks/                 # Webhook request handler + manager
│   │   │   ├── workflows/                # Workflow repo + execution service
│   │   │   └── [15+ feature dirs]        # auth, credentials, events, push, etc.
│   │   ├── test/                         # Integration + E2E tests (jest)
│   │   ├── Dockerfile                    # node:18-alpine
│   │   └── package.json                  # express, pg, redis, bullmq, etc.
│   ├── core/                             # Workflow execution engine (no Node.js dependency)
│   │   ├── src/
│   │   │   ├── execution-engine/
│   │   │   │   ├── workflow-execute.ts   # Core: PCancelable<IRun> run()
│   │   │   │   ├── node-execution-context.ts # Node runtime context
│   │   │   │   ├── partial-execution-utils.ts # DAG graph for partial reruns
│   │   │   │   └── requests-response.ts  # Request/response handling
│   │   │   ├── credentials.ts            # Credential loading + decryption
│   │   │   ├── node-execute-functions.ts # IExecuteFunctions, IPollFunctions, etc.
│   │   │   └── [storage, errors, utils]
│   │   └── package.json
│   ├── frontend/
│   │   ├── @n8n/i18n/                    # Translation system (separate package)
│   │   │   ├── src/
│   │   │   │   ├── index.ts              # I18nClass + createI18n instance
│   │   │   │   ├── locales/
│   │   │   │   │   └── en.json           # 5000+ translation keys (master)
│   │   │   │   └── types.ts              # BaseTextKey type (generated from en.json)
│   │   │   └── package.json
│   │   ├── @n8n/design-system/           # UI component library
│   │   │   ├── src/
│   │   │   │   ├── components/           # Buttons, modals, dropdowns, etc.
│   │   │   │   └── locale/               # Design-system translations (flat keys)
│   │   │   └── package.json
│   │   ├── editor-ui/                    # Main editor app (Vite SPA)
│   │   │   ├── src/
│   │   │   │   ├── main.ts               # Vue 3 app bootstrap + i18nInstance plugin
│   │   │   │   ├── components/           # Editor canvas, node panels, etc.
│   │   │   │   ├── views/                # Pages: workflows, executions, credentials
│   │   │   │   ├── stores/               # Pinia stores (workflow, execution state)
│   │   │   │   ├── app/dev/i18nHmr.ts   # HMR for locale files during dev
│   │   │   │   └── [plugins, router, utils]
│   │   │   ├── index.html                # Entry HTML + theme meta tags
│   │   │   ├── vite.config.ts            # Vite build config + i18n plugin
│   │   │   └── package.json
│   │   └── [3+ other frontend packages]
│   ├── nodes-base/                       # Built-in node collection (400+ nodes)
│   │   ├── nodes/
│   │   │   ├── [Category]/
│   │   │   │   ├── [NodeName]/
│   │   │   │   │   ├── [NodeName].node.ts # INodeType definition
│   │   │   │   │   └── descriptions/     # Parameter descriptions
│   │   │   │   └── ...
│   │   └── credentials/                  # Built-in credential types
│   ├── workflow/                         # n8n-workflow npm package (types + DAG logic)
│   └── [extensions, testing, node-dev]
├── docker-compose.yml                    # postgres, redis, api, worker, frontend services
├── package.json                          # Root monorepo + pnpm workspaces
├── pnpm-workspace.yaml                   # Workspace config
├── turbo.json                            # Turbo build orchestration
└── docs/                                 # Generated API docs + guides
```

---

## 3. Boundaries & Ownership

| Component | Owner | Constraints | Safe to modify |
|-----------|-------|-----------|-----------------|
| **Workflow executor (core)** | Core team | State machine must have zero data loss | Only with tests |
| **Webhook handler** | Core team | Must not drop events | Only with E2E tests |
| **Job queue (Redis)** | DevOps | Atomicity on enqueue/dequeue | Only with queue perf tests |
| **Credential encryption** | Security team | No plaintext in logs/UI | Never solo; coordinate |
| **Database schema** | DBA | Backward-compatible migrations only | Migration strategy reviewed |
| **Editor UI (Vue)** | Frontend team | i18n + theme-contract compliance | Freely, with e2e tests |
| **i18n system** | Frontend team | 5000+ keys, single active locale | Add keys in en.json + tests |
| **Node types** | Community/Core | Plugin architecture via node loader | Freely; register in loader |
| **Config + env** | DevOps | No secrets in code; .env only | Only after env validation |

---

## 4. Golden Path (Rapid Build & Deploy)

### Developer setup (5 min)

```bash
cd /root/n8n
pnpm install

# Generate TypeORM types
pnpm build

# Start dev mode (watch + reload)
pnpm dev:be &                    # Backend on :5678
pnpm dev:fe:editor &             # Frontend on :8080
# Or all at once:
# pnpm dev
```

### Environment (`.env` or env vars)

```bash
# Database
DB_TYPE=postgresdb
DB_POSTGRESDB_HOST=localhost
DB_POSTGRESDB_USER=postgres
DB_POSTGRESDB_PASSWORD=postgres
DB_POSTGRESDB_DATABASE=n8n

# Redis (for job queue + scaling)
REDIS_HOST=localhost
REDIS_PORT=6379

# Encryption (generate via: openssl rand -base64 32)
N8N_ENCRYPTION_KEY=<base64-32-chars>

# Admin user
N8N_DEFAULT_USER_PASSWORD=Admin@@3224@@

# Webhook base URL
WEBHOOK_URL=http://localhost:5678/webhook

# Log level
N8N_LOG_LEVEL=info
```

### Build for production

```bash
pnpm build                       # Compiles TS + frontend bundle
npm start                        # Starts API on :5678
```

### Run worker (separate process)

```bash
# In container or separate terminal:
node dist/packages/cli/bin/n8n.js worker
```

### Docker Compose (full stack)

```bash
docker-compose up -d
# Starts: postgres, redis, api (wait 10s), worker, frontend
```

### Test (check before commit)

```bash
pnpm test                        # Run all tests (slow: 5+ min)
pnpm test:backend                # CLI tests only
pnpm test:frontend               # Frontend tests only
```

---

## 5. Environment Variables

### Core

| Variable | Type | Default | Notes |
|----------|------|---------|-------|
| `DB_TYPE` | enum | postgresdb | Only postgresdb supported in prod |
| `DB_POSTGRESDB_HOST` | host | localhost | Fails if not reachable; test at startup |
| `DB_POSTGRESDB_PORT` | int | 5432 | |
| `DB_POSTGRESDB_USER` | string | postgres | |
| `DB_POSTGRESDB_PASSWORD` | secret | — | Never log this |
| `DB_POSTGRESDB_DATABASE` | string | n8n | |
| `N8N_ENCRYPTION_KEY` | secret | — | Base64(32 bytes); used for credential encryption |
| `N8N_LOG_LEVEL` | enum | info | debug/info/warn/error; debug = verbose |
| `WEBHOOK_URL` | url | http://localhost | Base URL for public webhook endpoint |
| `REDIS_HOST` | host | localhost | Job queue; required for scaling mode |
| `REDIS_PORT` | int | 6379 | |

### Admin Recovery

| Variable | Type | Default | Notes |
|----------|------|---------|-------|
| `N8N_DEFAULT_USER_PASSWORD` | secret | Admin@@3224@@ | Sets admin@vnso.vn password on first run |
| `N8N_USER_FOLDER` | path | ~/.n8n | Local credential/history storage |

### Feature flags

| Variable | Type | Default | Notes |
|----------|------|---------|-------|
| `N8N_PUBLIC_SIGNUP_ENABLED` | bool | false | Allow new user registration (UI only) |
| `N8N_PUBLIC_WEBHOOKS_ENABLED` | bool | true | Accept webhook triggers |
| `N8N_LOG_EXECUTION_TIMEOUT` | ms | 30000 | Force-kill execution if timeout exceeded |
| `N8N_SCALING_ENABLED` | bool | false | Enable multi-worker scaling mode |
| `N8N_BINARY_DATA_STORAGE` | enum | filesystem | or `db` or `s3` |

---

## 6. Data Model (PostgreSQL Schema)

### Key tables (100+ total)

| Table | Columns | Purpose | Indexes |
|-------|---------|---------|---------|
| **workflow** | id, name, nodes, connections, active, project_id, created_at, updated_at | Workflow definition (DAG) | PK(id), IX(project_id, active) |
| **workflow_execute** | id, workflow_id, execution_data, started_at, finished_at, status | Execution record (immutable after finish) | PK(id), IX(workflow_id, status) |
| **webhook** | id, workflow_id, path, method, static_data, test_data | Webhook registration; static = public (e.g., `/webhook/{uuid}`), test = preview trigger | PK(id), IX(workflow_id, path) |
| **credential** | id, name, type, data (encrypted), project_id | Encrypted OAuth token / API key | PK(id), IX(project_id, type) |
| **user** | id, email, password (hash + salt), first_name, project_id | Admin/Editor/Viewer | PK(id), UX(email) |
| **project** | id, name, project_type, sso_config | Multi-tenancy scope | PK(id) |
| **binary_data** | id, workflow_id, execution_id, data (blob) | File/image storage for large payloads | PK(id), IX(execution_id) |
| **execution_history** | execution_id, node_name, input, output, error, duration_ms | Per-node execution audit (denormalized for perf) | IX(execution_id, node_name) |
| **activation_error** | workflow_id, error_message, error_timestamp | Why workflow failed to activate (webhook conflict, etc.) | PK(workflow_id) |

### Credential encryption

```
┌─────────────────────────────────────────┐
│  credential.data (DB encrypted column)  │
├─────────────────────────────────────────┤
│  AES-256-GCM(                           │
│    plaintext_json,                      │
│    key=N8N_ENCRYPTION_KEY,              │
│    iv=random_per_credential             │
│  )                                      │
│  → Base64 + IV + Tag stored in DB       │
└─────────────────────────────────────────┘
```

**Decryption only happens server-side** during node execution; never in frontend or logs.

---

## 7. State Machines

### Workflow execution lifecycle

```
┌─────────────────────────────────────────────────────────────────────┐
│  EXECUTION STATE MACHINE (n8n-core)                                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  NEW                                                                  │
│   └─→ ┌──────────────────────────────────────────┐                 │
│       │ RUNNING (execution_data.status = active) │                 │
│       └──────────┬─────────────────────────────┬──┘                 │
│                  │                             │                    │
│             ┌─ YES                        NO ─┤                     │
│             │    (all nodes done)          (at a waiting node)      │
│             │                                  │                    │
│             v                                  v                    │
│        ┌─────────────────────┐         ┌──────────────┐             │
│        │ SUCCESS / ERROR     │         │   WAITING    │             │
│        │ (status terminal)   │         │ (paused at   │             │
│        └─────────────────────┘         │  webhook/   │             │
│             ^                          │  form node) │             │
│             │                          └──────────┬──┘             │
│       (all nodes resolved)                        │                 │
│             │                    webhook/form filled in             │
│             └────────────────────────────────────┘                 │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
```

**Execution statuses (IRun.status):**
- `new` — Created but not started
- `running` — Currently executing nodes
- `success` — Completed without errors
- `error` — Halted due to node error (caught + logged)
- `waiting` — Paused at webhook/waiting trigger node (resumable)
- `crashed` — Unexpected worker failure (mark for retry on next activation)

**Node execution statuses (IRunData[node_name][index].status):**
- `success` — Node completed without error
- `error` — Node threw error (execution continues to error handler or stops)
- `running` — Still executing (long HTTP request, etc.)
- `waiting` — Node paused awaiting external input

### Webhook → execution trigger pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│  WEBHOOK TRIGGER → EXECUTION QUEUE → WORKER DEQUEUE → RUN      │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  1. HTTP POST /webhook/{uuid}                                   │
│     ↓ (webhook-request-handler.ts)                              │
│     • Validate method (GET/POST/PUT/PATCH/DELETE)               │
│     • Parse body (JSON, form-data, raw)                          │
│     • Setup CORS headers                                         │
│                                                                   │
│  2. webhookManager.executeWebhook(req)                           │
│     ↓ (webhook.service.ts → findWebhook)                         │
│     • Lookup webhook in DB: path + method + project_id           │
│     • If static: trigger immediately                             │
│     • If test: inject test data instead of real                  │
│                                                                   │
│  3. Enqueue job to Redis                                         │
│     ↓ (BullMQ job)                                               │
│     Job: {                                                        │
│       type: 'WORKFLOW_EXECUTE',                                  │
│       workflow_id: uuid,                                          │
│       execution_id: uuid,                                         │
│       trigger_data: { body, query, headers },                    │
│       run_index: 1,                                              │
│       execute_at: now(),                                          │
│     }                                                             │
│                                                                   │
│  4. Return 200 OK to caller (async, don't wait for execution)    │
│     └─ Response mode (JSON, redirect, webhook, None)             │
│                                                                   │
│  5. Worker dequeues job (async, separate process)                │
│     ↓ (scaling/job-queue-worker.ts)                              │
│     • Load workflow definition from DB                           │
│     • Load credentials (decrypt)                                 │
│     • Instantiate WorkflowExecute with trigger data              │
│     • Invoke run() → PCancelable<IRun>                           │
│                                                                   │
│  6. Execute DAG of nodes (workflow-execute.ts)                   │
│     ↓ State: NEW → RUNNING → SUCCESS/ERROR/WAITING              │
│     • Find start nodes (webhook trigger node, etc.)              │
│     • For each node: execute in order, await results             │
│     • Pass output data to dependent nodes via connections        │
│     • On node error: call errorHandler, mark execution FAILED    │
│                                                                   │
│  7. Persist execution_data to DB                                 │
│     ↓ (execution.service.ts)                                     │
│     • Status, duration, output, error, logs                      │
│     • Mark job COMPLETED in Redis                                │
│                                                                   │
│  8. Emit execution:finished event                                │
│     ↓ (WebSocket → frontend)                                     │
│     • UI updates workflow history in real-time                   │
│     • Show execution result (success/error/waiting)              │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### Waiting node resumption flow

```
Execution WAITING @ webhook-trigger-node (awaiting external data)
  ↓
User (or external service) sends webhook: POST /webhook/{new_uuid}
  ↓
Lookup webhook by path → finds WAITING execution
  ↓
Resume execution from waiting node with fresh input data
  ↓
Continue downstream nodes
  ↓
Final status: SUCCESS or ERROR
```

---

## 8. API Endpoints (Selection)

### Core workflow endpoints

```
POST   /workflows/create            # New workflow (multipart: definition)
GET    /workflows                   # List workflows (paginated)
GET    /workflows/:id               # Get workflow def + metadata
PUT    /workflows/:id               # Update workflow nodes/connections
DELETE /workflows/:id               # Soft delete (archive)

PUT    /workflows/:id/activate      # Activate (register webhook, schedule triggers)
PUT    /workflows/:id/deactivate    # Deactivate
```

### Execution endpoints

```
POST   /workflows/:id/execute       # Manual trigger (real-time, blocking)
GET    /executions                  # List past executions (filtered by workflow)
GET    /executions/:id              # Get single execution (full output + logs)
DELETE /executions/:id              # Hard delete execution history
```

### Webhook endpoints

```
POST   /webhooks/create             # Register webhook for workflow
GET    /webhooks/test/:uuid         # Test webhook (dry-run, use test data)
DELETE /webhooks/:id                # Unregister webhook

POST   /webhook/{uuid}              # Public endpoint (triggered by external)
```

### Credential endpoints

```
POST   /credentials/create          # New credential (encrypted storage)
GET    /credentials                 # List credentials (names only, no values)
PUT    /credentials/:id             # Update credential
DELETE /credentials/:id             # Delete credential

POST   /credentials/:type/test      # Test if credential is valid (e.g., test Stripe key)
```

### Execution monitoring

```
GET    /workflows/:id/history       # Execution timeline (paginated)
GET    /workflows/:id/logs          # Combined logs from all executions
WS     /workflow/:id/stream         # WebSocket: real-time execution updates
```

---

## 9. Architecture & Data Flow

```mermaid
flowchart TB
  user["👤 User (Browser)"]
  nginx["🔀 Nginx (Reverse Proxy)"]
  editor["📝 Editor UI (Vue 3 SPA)"]
  api["⚙️ API Server (Express + Node.js)"]
  postgres[("🗄️ PostgreSQL<br/>(Workflow Defs +<br/>Credentials)")]
  redis["📋 Redis<br/>(Job Queue +<br/>Pub/Sub)"]
  worker["🏃 Worker<br/>(Execution Core)"]
  webhook["🪝 Webhook Listener<br/>(HTTP POST)"]
  external["🌐 External APIs<br/>(Slack, Stripe,<br/>400+ integrations)"]
  eventbus["🚌 Event Bus<br/>(execution:finished,<br/>node:executed)"]

  user -->|Browser (HTTPS)| nginx
  nginx -->|:5678/api| api
  nginx -->|:8080| editor
  
  editor -->|REST/WS| api
  api -->|SQL| postgres
  api -->|enqueue job| redis
  api -->|publish event| eventbus
  
  eventbus -->|subscribe| editor
  eventbus -->|subscribe| worker
  
  webhook -->|listen| redis
  api -->|register webhook| webhook
  
  redis -->|dequeue| worker
  worker -->|load creds| postgres
  worker -->|call node| external
  worker -->|persist execution| postgres
  worker -->|emit event| eventbus
```

### Critical data invariants

| Invariant | Why | Enforcement |
|-----------|-----|------------|
| **No credential leakage** | Plaintext credential in logs → breach | Encrypt in DB; decrypt only server-side during node run |
| **At-least-once execution** | Workflow not running = silent customer failure | Each execution has unique `execution_id` + `runIndex`; retry on worker crash (max 5 times) |
| **Webhook deduplication** | External event fires 2× → double execution | Store webhook UUID in execution_data; duplicate POST rejected |
| **User data isolation** | User A sees User B's workflows = CRITICAL | FK project_id on all tables; RBAC enforced in API middleware |
| **Deterministic node order** | Nodes execute out of order → non-deterministic output | Single-threaded executor; queue FIFO per workflow |

---

## 10. Failure Modes & Mitigations (≥8 critical)

| # | Failure | Trigger | Impact | Mitigation today | Future fix |
|----|---------|---------|--------|-----------------|------------|
| **1** | **Execution stuck in RUNNING** | Timeout (30min default; HTTP node hangs) | Queue blocked; resource leak; new triggers pile up | Timeout enforcement + watchdog timer | Graceful node termination via isolates |
| **2** | **Credential decryption fails** | DB corruption or encryption key rotated | Cannot auth external APIs; workflow errors | Fallback to cached cipher if available | Versioned encryption keys + rotation ceremony |
| **3** | **Node module import error** | npm package missing/version mismatch | Workflow fails at node instantiation | Error logged; operator manual fix required | Dynamic node loader + fallback stub |
| **4** | **Queue back-pressure** | Worker slower than trigger rate | Redis queue grows unbounded; OOM risk | Alert on queue depth (>10k); manual scale-up | Adaptive concurrency + DLQ for poison jobs |
| **5** | **Infinite loop in workflow** | User constructs loop without exit | Runaway CPU; timeout after 5min | Hard timeout (5min); max loop iterations (1000) | Static cycle detection in editor (DAG analysis) |
| **6** | **Database migration drift** | Operator rolls back mid-flight | Table structure mismatch; ORM query failures | Pre-migration backup; rollback procedure documented | Immutable migration history + version lock |
| **7** | **Public webhook abuse / DDoS** | Attacker discovers webhook URL | Queue flooded; legitimate webhooks delayed | Rate limiting (100 req/min per webhook); Cloudflare WAF | HMAC signature validation on webhook payload |
| **8** | **Worker process OOM** | Workflow with huge dataset (100MB+ in memory) | Worker crashes mid-execution; RUNNING state orphaned | Node enforces maxDataSize (32MB); early kill allows restart | Streaming data via pipes instead of memory buffer |
| **9** | **Silent execution failure** | Node completes without output (null) | Downstream nodes skip; no alert | Execution marked UNKNOWN_ERROR if no output | Mandatory output schema per node + validation |
| **10** | **Webhook listener crashes** | Unhandled exception in express middleware | Incoming webhooks fail with 500 | Supervisor restarts process (systemd/Docker/PM2) | Middleware error trap + DLQ for unparseable payloads |

---

## 11. SLO (Service Level Objectives)

| Metric | Target | Measurement | Alert threshold |
|--------|--------|-------------|-----------------|
| **Workflow execution success rate** | 99.9% | (successful_executions / total_executions) × 100 | < 99% |
| **Webhook trigger latency (p99)** | <5s | Time from POST /webhook to job enqueued | > 10s |
| **Worker job processing latency (p95)** | <30s | Time from dequeue to execution finished | > 60s |
| **API endpoint latency (p95)** | <500ms | GET /workflows, POST /workflows/:id/execute | > 1s |
| **Queue backlog** | <1000 jobs | Redis LLEN bull:workflow:execution | > 10000 |
| **Database uptime** | 99.95% | PostgreSQL availability (RTO: 5min) | Connection failures |
| **Credential freshness** | <5min | Max age of decrypted credentials in memory | > 10min |

---

## 12. Deployment Stages

### Stage 1: Local development

```bash
docker-compose -f docker-compose.dev.yml up
# postgres, redis, api (watch), worker, frontend (watch)
```

### Stage 2: Staging (pre-prod test)

```bash
docker build -t n8n:staging .
docker-compose -f docker-compose.staging.yml up -d
# Test webhook abuse, large executions, credential rotation
```

### Stage 3: Production

**Prerequisites:**
- [ ] All tests passing (unit + integration + e2e)
- [ ] Database backup taken
- [ ] N8N_ENCRYPTION_KEY rotated (no plaintext logs)
- [ ] Webhook URL hardened (HMAC validation in place)
- [ ] Cluster reconciliation running (5min health check)

**Deploy:**

```bash
# Blue-green: start new version, switch traffic, kill old
docker pull n8n:v2.16.0
docker-compose -f docker-compose.prod.yml up -d api-new
# Healthcheck api-new for 1 min
nginx -s reload  # Switch traffic
kill api-old
```

**Post-deploy:**

```bash
# Verify admin user auto-recovery
curl -X POST http://localhost:5678/auth/login \
  -d '{"email":"admin@vnso.vn","password":"Admin@@3224@@'}'

# Check queue depth
redis-cli LLEN bull:workflow:execution

# Tail logs
docker logs n8n-api -f --tail=100
```

---

## 13. Security & Admin Recovery

### Default admin

```
Email:    admin@vnso.vn
Password: Admin@@3224@@
```

**Never change** in seeds or migrations. This account is unbreakable recovery lever.

### Credential encryption

1. **At-rest:** AES-256-GCM in DB; key = `N8N_ENCRYPTION_KEY` (from env, never in code).
2. **In-flight:** TLS 1.2+ on all API calls; WS secure (wss://).
3. **Decryption:** Server-side only, during node execution; never log plaintext.

### RBAC (role-based access control)

| Role | Workflow | Credentials | Executions | Admin |
|------|----------|-------------|-----------|-------|
| **Viewer** | Read | Read (names) | Read | — |
| **Editor** | Create/Edit/Activate | Create/Use | Read | — |
| **Owner** | Full | Full | Full | Delete |
| **Admin** | Full | Full | Full | Yes |

### Key rotation

**Encryption key rotation (N8N_ENCRYPTION_KEY):**

1. Generate new key: `openssl rand -base64 32`
2. Run migration: re-encrypt all credentials with new key
3. Update `.env` with new key
4. Restart API + worker (must use same key)
5. **Old key becomes unrecoverable** — backup first

---

## 14. Observability

### Logging

| Channel | Level | Example |
|---------|-------|---------|
| **Application logs** | info/debug | `Execution ${id} started`, `Node "HTTP Request" executed in 250ms` |
| **Error logs** | error/warn | `CredentialDataError: Failed to decrypt`, `TimeoutExecutionCancelledError` |
| **Audit logs** | info | `User ${id} created workflow`, `Credential ${id} accessed` |

**Log aggregation:** stdout → docker logs (docker compose) or ELK stack (production).

### Metrics

- **Prometheus client** exports:
  - `n8n_workflow_execution_duration_ms` (histogram)
  - `n8n_workflow_execution_count` (counter, by status)
  - `n8n_node_execution_count` (by node type)
  - `n8n_webhook_requests_total` (by method + status)

### Traces (OpenTelemetry ready)

- **Trace per execution:** execution_id as context
- **Span per node:** node_name + duration + status
- **Export to:** Jaeger, Datadog, NewRelic (TODO: impl)

---

## 15. Testing

### Unit tests (no external deps)

```bash
pnpm test:unit
# Tests: credentials.ts, node-execute-functions.ts, expression evaluator
```

### Integration tests (real DB + Redis)

```bash
pnpm test:backend
# Starts postgres container; tests workflow execution, webhook trigger, etc.
```

### E2E tests (full stack)

```bash
# Start docker-compose first
docker-compose -f docker-compose.test.yml up -d
# Then run
pnpm test:e2e
# Tests: user login, create workflow, activate, trigger webhook, check execution result
```

### Load testing (queue saturation)

```bash
# Simulate 1000 webhook fires in 10s
apache-bench -n 1000 -c 100 http://localhost:5678/webhook/{uuid}

# Monitor queue depth
watch -n1 'redis-cli LLEN bull:workflow:execution'
```

---

## 16. Runbook (Production Response)

| Scenario | Symptoms | First action | Escalation | Rollback |
|----------|----------|--------------|------------|----------|
| **Workflows not triggering** | No new executions for 5 min | Check Redis queue: `redis-cli LLEN bull:workflow:execution` | Worker logs: `docker logs n8n-worker` for crashes | Restart worker; check DB for trigger registration |
| **High API latency (>5s)** | `/workflows` endpoint slow | Check slow queries: `SELECT * FROM pg_stat_statements WHERE mean_exec_time > 5000` | DBA: Add missing index on workflow(project_id, active) | Add index; replan queries; scale API |
| **Credential decryption errors** | Log: `CredentialDataError` in executions | Verify `N8N_ENCRYPTION_KEY` matches across API + workers | Check if key was rotated; try cached cipher | Restore from backup; re-encrypt all credentials |
| **Webhook URL spoofing (DDoS)** | Queue depth > 50000; egress spike | Block via Cloudflare WAF: rate limit `/webhook/*` to 100 req/min per IP | Regenerate webhook secret; add HMAC validation | Implement HMAC signature check on payload |
| **DB disk full (>90%)** | Executions insert failing | Identify largest table: `SELECT tablename, pg_size_pretty(...) ORDER BY size DESC` | DBA: Archive old execution logs to S3; purge; expand | Reduce retention window; compress execution_history |
| **Worker process OOM** | Worker restarts every 5 min; logs show "SIGKILL" | Increase node memory: `--max-old-space-size=16000` (default: 4000) | Heap dump: `node --inspect dist/worker.js`; Chrome DevTools | Restart worker; investigate node type memory leak |
| **Queue poison job (infinite retry)** | Single job stuck in bull:active for hours | Inspect job: `redis-cli HGETALL bull:workflow:execution:jobid` | Move to DLQ; log for manual review | Delete from queue; fix workflow; restart worker |
| **Admin account locked (MFA broken)** | Cannot login as `admin@vnso.vn` | SSH to DB: `DELETE FROM user_mfa WHERE user_id = (SELECT id FROM user WHERE email = 'admin@vnso.vn')` | Re-authenticate admin via backup code or new TOTP setup | Use recovery credential (N8N_USER_FOLDER backup) |

---

## 17. Pitch (Investor Lens)

**Problem:** VNSO customers need to orchestrate complex automations across 400+ SaaS tools (Slack, Stripe, CRM) without managing custom code or point integrations.

**Solution:** Self-hosted n8n platform with 400+ pre-built integrations, visual no-code workflow editor, JavaScript/Python for custom logic, and fair-code licensing (customer can self-host if needed).

**Business model:** [TBD] Usage-based: per-execution, per-node, per-API-call, per-GB-storage.

**Market wedge:** Fair-code licensing (source available, self-hostable) reduces vendor lock-in fear vs. Zapier/Make; appeals to enterprise buyers.

**Revenue mechanics:**
- Workflow execution: $0.01–$0.10 per execution
- External API call tax: $0.0001 per 100 calls (pass-through to customer)
- Storage: $0.10 per GB·month (binary data, execution logs)

**Growth loop:** Free trial (100 execs) → first workflow → daily schedule → add integrations → paid plan.

---

## 18. Key Files for AI

| File | Purpose | Read when... |
|------|---------|-------------|
| [packages/cli/src/index.ts](packages/cli/src/index.ts) | Express app bootstrap | Understanding API startup flow |
| [packages/core/src/execution-engine/workflow-execute.ts](packages/core/src/execution-engine/workflow-execute.ts) | Execution state machine | Implementing execution logic; state transitions |
| [packages/cli/src/active-workflow-manager.ts](packages/cli/src/active-workflow-manager.ts) | Trigger registration + webhook activation | Webhook setup; workflow activation lifecycle |
| [packages/cli/src/webhooks/webhook-request-handler.ts](packages/cli/src/webhooks/webhook-request-handler.ts) | HTTP webhook entry point | Webhook trigger pipeline |
| [packages/cli/src/scaling/bull-queue-factory.ts](packages/cli/src/scaling/bull-queue-factory.ts) | Job queue setup | Job enqueueing; worker scaling |
| [packages/cli/src/execution-lifecycle/](packages/cli/src/execution-lifecycle/) | Hooks: before-run, after-node, on-error | Execution lifecycle integration |
| [packages/frontend/@n8n/i18n/src/index.ts](packages/frontend/@n8n/i18n/src/index.ts) | i18n system entry | Adding translations; see `/memories/repo/n8n-i18n-system.md` |
| [packages/frontend/editor-ui/src/main.ts](packages/frontend/editor-ui/src/main.ts) | Vue 3 app bootstrap | Frontend initialization; plugin setup |
| [packages/nodes-base/nodes/](packages/nodes-base/nodes/) | Built-in node collection | Creating new node type |

---

## 19. Roadmap & Change Log

### Roadmap (v2–v3 timeline)

| Phase | Target | Focus | Risk |
|-------|--------|-------|------|
| **v2.16→v2.20** | Q2 2026 | Bug fixes, performance, VNSO i18n integration | Low |
| **v3.0** | Q4 2026 | Multi-tenant SaaS, custom node marketplace, distributed workers (100+) | High; requires schema redesign |
| **v3.2** | Q1 2027 | External credential stores (Vault, AWS Secrets), edge workers (SG, US latency), LLM workflow suggestions | Very high; new services |

### Change log

| Date | Version | Author | Change |
|------|---------|--------|--------|
| 2026-05-01 | AI_CONTEXT v2 | AI (Copilot) | Rewrite to 19-section PRO structure; emphasize execution state machine + webhook pipeline |
| 2026-04-01 | n8n v2.16.0 | n8n upstream | Upstream release |

---
