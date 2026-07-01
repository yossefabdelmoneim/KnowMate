# Back_End — KnowMate Data Analyst Agent

Layered FastAPI backend that hosts the KnowMate Data Analyst Agent

This brings up Postgres + Ollama + the API on port 8000. Open
http://localhost:8000/docs for the OpenAPI spec.

The first run pulls the qwen2.5:7b model into the Ollama container
(several GB — be patient on first boot).

## Quick start (local dev)

```bash
# 1. Create a venv + install deps
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2. Start Postgres + Ollama separately (or via `docker compose up postgres ollama`)

# 3. Run Alembic migrations
alembic upgrade head

# 4. Run the API
uvicorn main:app --reload
```

## API surface

### Public
- `GET /health` — liveness check (reports Ollama availability)

### Auth
- `POST /auth/register` — `{email, password, full_name?}` → `UserPublic`
- `POST /auth/login` — `{email, password}` → `{access_token, ...}`

### Chat sessions (JWT-protected)
- `POST /sessions` — create a chat
- `GET /sessions` — list your chats
- `GET /sessions/{id}` — get one chat (with dataset info)
- `PATCH /sessions/{id}` — update title/description, close
- `DELETE /sessions/{id}` — delete a chat
- `POST /sessions/{id}/dataset` — attach a dataset (**one-file-per-chat enforced**)
- `GET /sessions/_meta/supported-types` — list supported file extensions
- `GET /sessions/{id}/messages` — chat history
- `POST /sessions/{id}/messages` — send a question → agent runs analysis

### Backwards-compatible
- `POST /analyze` — file + question in, analysis out (creates an
  ephemeral session + dataset under the caller). Accepts JWT or API key.

### Memory (stub)
- `GET /memory` — returns empty lists for now (extraction is a stub)

### API keys (DEFERRED — uncomment in `main.py` to enable)
- `POST /api-keys` — issue a new API key (plaintext returned once)
- `GET /api-keys` — list your keys (no plaintext)
- `DELETE /api-keys/{id}` — revoke a key

## Key design decisions

### One file per chat
Enforced in `services/session_service.py` and at the DB level (the
`datasets` table has a UNIQUE constraint on `session_id`). To analyze
a different file, the user opens a new chat.

### Short-term memory
The most recent `SHORT_TERM_MEMORY_WINDOW` (default 6) prior messages
in the same chat are fed into the code-generation prompt as
"Conversation so far" so follow-ups like *"now sort that descending"*
resolve correctly.

### Long-term memory (cross-chat)
The `UserPreference` and `LongTermMemory` tables + repositories +
extraction logic in `services/memory_service.py` are **fully
implemented**. After every successful analysis, the agent triggers two
best-effort LLM calls:

1. **Preference extraction** — scans the Q&A pair for explicit user
   preferences ("I always want bar charts", "show values in EGP",
   "I work in retail"). Upserts into `UserPreference` rows with a
   confidence score. Lower-confidence extractions cannot overwrite
   higher ones already stored.

2. **Fact extraction** — scans for durable facts worth remembering
   across chats (topics of interest, skill gaps, context). Inserts
   into `LongTermMemory` rows with an importance score. Identical
   content is deduped (importance ratchets up only).

Before every agent run, the user's top N preferences (above a
confidence threshold) and top M memories are pulled and injected into
the code-gen prompt as a "User context" section, so the agent
personalizes its output to each user.

Disable via `LONG_TERM_MEMORY_ENABLED=false` in `.env` if you need
max speed (it adds 2 LLM calls per analysis).

Endpoints:
- `GET /memory` — list the user's stored preferences + memories
  (with optional `?category=` and `?kind=` filters)

### Multi-agent interface (stub)
`services/agent_service.py` defines an `AgentService` protocol with
`can_handle()` + `handle()`. The `AnalystAgent` is the first
registered implementation. When you add more agents (SQL agent, viz
agent, etc.), register them the same way and build an orchestrator
that picks among them.


### Supported file formats
CSV, TSV, plain text, XLSX, XLS (legacy), ODS, JSON, JSON Lines,
Parquet, Stata `.dta`. Adding a format is one new loader function in
`services/dataset_loader.py` + one entry in the `_LOADERS` dict.

## Environment variables

See `.env.example`. Critical ones:
- `DATABASE_URL` — Postgres connection string
- `LLM_OLLAMA_BASE_URL` — Ollama server URL
- `LLM_MODEL` — Ollama model tag (default `qwen2.5:7b`)
- `JWT_SECRET` — **change in production**
- `MAX_UPLOAD_SIZE_BYTES` — per-file upload cap
- `SHORT_TERM_MEMORY_WINDOW` — number of prior turns fed into the prompt

## Migrations

Alembic migrations live in `migrations/versions/`. To create a new one:

```bash
alembic revision --autogenerate -m "describe your change"
alembic upgrade head
```

The initial migration creates all tables for the current model set.
