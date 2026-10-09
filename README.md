# LenysPilot (The Lenny Growth Assistant)

This containerized RAG deployment bypasses generic frameworks, utilizing Reciprocal Rank Fusion directly within Postgres (pgvector + TSVECTOR) to guarantee 100% grounded citations. It prioritizes defense-in-depth security by rendering generated artifacts inside an isolated iframe with strict Content-Security-Policies to neutralize XSS risks. The fully decoupled architecture features an idempotent CLI and a zero-dependency Vanilla JS frontend, allowing anyone to boot the entire system with a single `docker compose up -d`.

## Features
- **Local First:** Designed to run entirely offline using Ollama and PostgreSQL `pgvector`.
- **Zero-Code Model Toggle:** Switch between local `ollama` and cloud `anthropic` via `.env`.
- **Hybrid Search:** Combines BM25 Full-Text search with Vector Embeddings via Reciprocal Rank Fusion (RRF).
- **Strict Grounding:** Every claim is cited `[guest-slug · HH:MM:SS]`.
- **Premium Flat UI:** Classic, zero-gradient, serif/sans-serif dark mode UI.
- **Secure Artifacts:** Defense-in-depth HTML rendering with strict Content-Security-Policies.

## Setup & Run (One-Command Startup)

### Prerequisites
- Docker & Docker Compose
- Ollama installed locally (for the local LLM requirement)
- Python 3.11+ (if running tests locally)

### 1. Start the Environment
```bash
# Clone the repository
git clone <repo-url>
cd lenny-growth-assistant

# Create environment file
cp .env.example .env

# Start the database and API
docker compose up -d
```

### 2. Run Database Migrations
```bash
# Apply the schema to the Postgres container
docker compose exec api alembic upgrade head
```

### 3. Ingest Data
Place your markdown transcripts into a folder (e.g., `transcripts/`).
```bash
# Run the idempotent ingestion script
docker compose exec api python ingest.py --dir transcripts
```

### 4. Access the App
Open `http://localhost:8000` in your browser.

## Testing & Evals
We include a Golden Eval script to measure `hit@k` latency and retrieval validity.
```bash
# Run tests
pip install pytest httpx
pytest tests/

# Run Golden Eval
python eval.py
```

## Documentation
- [PRD.md](./PRD.md): User, problem, scope, and trade-offs.
- [architecture.md](./architecture.md): Topology, DB schema, and data flows.
- [design.md](./design.md): UI/UX philosophy and aesthetic rules.
