# Architecture & System Design

## Deployment Topology
The system is designed to be "trivially easy for a stranger to run."
- **Docker Compose:** Manages the entire stack.
- **Service 1 (db):** `pgvector/pgvector:pg16` - PostgreSQL with native vector extensions.
- **Service 2 (api):** FastAPI backend, serving both the REST API and the static vanilla HTML/JS frontend.
- **Host System:** Ollama runs natively on the host machine to leverage local GPU/CPU optimally (configured via `OLLAMA_BASE_URL=http://host.docker.internal:11434`).

## Database Schema (PostgreSQL)
- **`documents`**: Stores transcript metadata (guest slug, title) and a `content_hash` for idempotent updates.
- **`chunks`**: Stores individual speaker turns. Contains a `vector(768)` column indexed via `HNSW` for semantic search, and a `TSVECTOR` column indexed via `GIN` for full-text search.
- **`sessions`**: Tracks chat instances.
- **`messages`**: Stores conversation history and a `metadata_json` column that logs the Retrieval Traces (which chunks were pulled) for observability.
- **`artifacts`**: Stores generated Markdown/HTML payloads to decouple large documents from the chat feed.

## Ingestion Flow
1. The CLI (`ingest.py`) reads local markdown files.
2. Parses YAML frontmatter for metadata.
3. Uses Regex to split the body by speaker turns (`Speaker (HH:MM:SS):`).
4. Checks `content_hash`. If unchanged, skips.
5. If changed, deletes old chunks, calls the embedding service, and inserts new chunks.

## Retrieval Flow (Hybrid RRF)
Instead of relying solely on vector search (which can miss exact keywords), we use Reciprocal Rank Fusion:
1. Embed the user query.
2. Execute a single Postgres query that runs both an `HNSW` vector distance check and a `ts_rank` text search.
3. Calculate `1 / (60 + rank)` for both sets.
4. Merge and return the top 5 chunks.

## Agent Routing & Provider Toggle
- **Provider Abstraction:** The `AgentService` uses a strategy pattern. The `LLM_PROVIDER` env var seamlessly toggles between `OllamaProvider` and `AnthropicProvider` without changing application logic.
- **Routing:** The agent inspects the prompt. If the user requests an essay/Ship30, it appends strict formatting instructions to the prompt and intercepts the response to generate an Artifact.

## Security (Defense in Depth)
- All generated HTML is treated as hostile.
- Endpoint: `GET /artifacts/{id}`
- Headers injected: `Content-Security-Policy: default-src 'none'; style-src 'unsafe-inline'; sandbox;`
- This entirely neutralizes XSS execution in the browser.
