# Product Requirements Document (PRD)

## 1. Discovery Brief

### User and Problem
**Primary User:** Product Managers, Growth Engineers, and Marketers.
**Problem:** The user needs highly specific, operator-vetted product advice from Lenny's Podcast, but they lack the time to manually search through hours of audio transcripts. They need actionable answers, directly cited from experts, and the ability to instantly format those insights into shareable artifacts (like a Ship 30 for 30 essay).
**Pain Removed:** Eliminates the manual labor of synthesizing scattered podcast knowledge and guarantees that generated advice is grounded in actual expert testimony rather than generic LLM training data.

### Success Metric
**Operational Metric:** `hit@k` (retrieval success). The system must reliably retrieve the correct podcast chunk in the top 5 results for answerable queries.
**Product Metric:** Zero hallucinations. 100% of factual claims in the generated essays must contain a valid `[guest-slug · HH:MM:SS]` citation.

### Assumptions
1. Transcripts are relatively static and updated in batches, so a CLI ingestion tool is sufficient (real-time ingestion via webhooks is not required).
2. Users prefer local execution for data privacy, meaning Ollama is the primary deployment target, but Anthropic is available for cloud deployment.
3. Generated HTML/Markdown artifacts can be hostile; strict frontend security (CSP/sandbox) is non-negotiable.

### Scope Choices
**In Scope:**
- Full-stack chat interface with side-by-side artifact viewer.
- Hybrid search (BM25 + pgvector) using Reciprocal Rank Fusion.
- Strict Ship 30 for 30 essay generation.
- Defense-in-depth HTML rendering.

**Out of Scope:**
- User authentication (SSO/OAuth). To simplify the take-home deployment, session IDs are generated per client silently.
- Audio playback. While we cite the timestamp, syncing an actual audio player is excluded to focus on the core RAG logic.

### Risks and Trade-offs
1. **Local Model Quality:** Ollama models (like `llama3`) may struggle with complex prompt adherence compared to Claude 3.5 Sonnet. *Mitigation:* We use a highly structured system prompt and explicit routing.
2. **XSS in Artifacts:** LLMs generating HTML can inject malicious scripts. *Mitigation:* We use a strict `default-src 'none'` Content Security Policy and a sandboxed iframe.
3. **Latency:** Local embeddings and local LLM generation can be slow on older machines. *Mitigation:* We implemented UI loading states and async Postgres calls.
