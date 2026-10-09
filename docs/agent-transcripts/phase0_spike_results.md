# Phase 0 Spike Results

## Spike 1: Transcript Format Analysis
**Goal:** Determine the structure of Lenny's Podcast transcripts.
**Result:** 
- The transcripts are stored as Markdown files.
- They contain standard YAML frontmatter (`---` blocks) with metadata such as `guest`, `title`, `youtube_url`, `publish_date`, etc.
- The body is plain text, with speaker turns formatted as `Speaker Name (HH:MM:SS):`.
**Conclusion:** We can reliably parse this format using a combination of `pyyaml` for the frontmatter and a simple Regex (e.g., `^(.*?)\s*\((\d{2}:\d{2}:\d{2})\):\n`) for the chunks, splitting by speaker. This chunking strategy naturally preserves the context and timestamp for citations.

## Spike 2: Agent Layer -> Ollama Integration
**Goal:** Confirm how the Anthropic Claude Agent SDK talks to a local Ollama instance.
**Result:** 
- Ollama natively exposes an OpenAI-compatible endpoint (`/v1/chat/completions`), but does NOT natively expose an Anthropic-compatible endpoint.
- The Anthropic Python SDK is strictly typed and validates payloads against the Anthropic API schema (e.g. `messages`, specific `tools` formatting).
- Direct connection from the Anthropic SDK to Ollama will fail because of payload mismatch and endpoint mismatch.
**Trade-off & Design Decision:**
If we rely strictly on the Anthropic SDK, we would have to force users to run a proxy container (like LiteLLM) to translate Anthropic calls into OpenAI-compatible calls for Ollama. This violates the goal of a simple "trivially easy for a stranger to run" setup.
**Solution:** We will build a **Provider Abstraction Layer** (Strategy Pattern) in our backend. 
- `AgentService` will define the core chat and tool-routing loop.
- `AnthropicProvider` will implement this using the `anthropic` SDK.
- `OllamaProvider` will implement this using the `openai` SDK (pointing to `localhost:11434/v1`).
This way, the app logic is agnostic, requires zero code changes to toggle, and local inference works flawlessly out of the box without requiring extra Docker containers just for translation.
