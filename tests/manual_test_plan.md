# Manual UI Test Plan

## Pre-requisites
1. Ensure the stack is running: `docker compose up -d`
2. Ensure data is ingested: `docker compose exec api python ingest.py --dir transcripts`
3. Navigate to `http://localhost:8000`

## Test Cases

### 1. The Empty State
- **Action:** Open the app.
- **Expected:** A pure black loading screen plays the `opening.mp4` video. Exactly 3 seconds later, it fades out.
- **Expected:** The chat area is empty except for the perfectly centered "Lenozen Logo" and the "The Lenny Growth Assistant" text in Merriweather font.

### 2. Conversational RAG & Grounding
- **Action:** Type "What are some common mistakes founders make?" and hit enter.
- **Expected:** The empty state greeting vanishes. A loading indicator `...` appears.
- **Expected:** The assistant replies with a grounded answer.
- **Verification:** Read the answer. Verify that it contains strict citations in the format `[guest-slug · HH:MM:SS]`.

### 3. Ship 30 for 30 Essay Generation & Artifact Viewer
- **Action:** Type "Write a Ship 30 essay about finding product-market fit based on the transcripts."
- **Expected:** The assistant recognizes the intent and triggers the Ship 30 skill.
- **Expected:** Instead of dumping 1,250 words into the chat feed, the assistant replies with a link: `[View Artifact X](/artifacts/X)`.
- **Expected:** The UI intercepts the link, splits the screen in half, and opens the essay in the right-side `iframe`.
- **Verification:** Check the iframe content. Ensure it follows the 1/3/1 rhythm, contains headings, and has a `## Sources` block at the bottom.

### 4. Artifact Security (XSS Prevention)
- **Action:** Inspect the `iframe` network tab or source code.
- **Expected:** The iframe is served with `Content-Security-Policy: default-src 'none'; style-src 'unsafe-inline'; sandbox;`.
- **Verification:** Any malicious `<script>` tags the LLM might have hallucinated will be entirely blocked from executing.

### 5. Session Isolation
- **Action:** Click "New chat" in the left sidebar.
- **Expected:** The screen clears, the centered empty state returns, and the artifact viewer (if open) cleanly closes.
- **Expected:** Sending a new message creates a brand new `session_id` in the database without previous context.
