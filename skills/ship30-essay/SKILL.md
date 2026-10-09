---
name: ship30-essay
description: Turns grounded answers from the Lenny's Podcast knowledge base into a Ship 30 for 30-style essay (~1,250 words) with a strong headline, skimmable structure, and per-claim transcript citations. Use whenever the user asks for an essay, article, post, newsletter, thread, or "write this up" based on podcast insights, even if they never say "Ship 30".
---

# Ship 30 for 30 Essay Skill

Source of the principles: the official Ship 30 for 30 guide by Nicolas Cole and Dickie Bush
(https://www.ship30for30.com/post/how-to-start-writing-online-the-ship-30-for-30-ultimate-guide).
This file encodes those principles. Do not improvise a different style.

## Hard rules (grounding comes first)

1. Write ONLY from retrieved transcript chunks for this session. No outside facts.
2. Every factual claim or paraphrased idea gets a citation: `[guest-slug · HH:MM:SS]`.
   Use the speaker-turn timestamp from the chunk metadata.
3. Credibility type is always "I'm curating the experts". Attribute ideas to the guest by name
   ("According to Ada Chen Rekhi on Lenny's Podcast..."). Never present the guest's ideas as the author's own experience.
4. If retrieval returned nothing relevant or too little for ~1,250 words, say so and offer a shorter piece. Do not pad with generic advice.
5. Quote sparingly (under ~15 words per quote). Paraphrase everything else.

## Pipeline (follow in order)

### Step 1. Frame the idea
Decide and write down internally:
- **Reader:** who exactly is this for, and who is it NOT for? Be specific (e.g. "first-time PMs at B2B SaaS startups", not "product people").
- **Content type (the 4 A's):** pick ONE.
  - Actionable (here's how) | Analytical (here are the numbers) | Aspirational (yes, you can) | Anthropological (here's why people behave this way)
- **Proven approach:** pick ONE organizing pattern and keep every main point in it: Steps, Lessons, or Mistakes. Never mix.
  Default: 5 Lessons or 5 Steps (about 5 main points at ~1,250 words).
- **Tequila Test:** list the cliché takes on this topic, then DO NOT use them. Lead with the non-obvious insight the transcripts actually support.

### Step 2. Write the headline
A headline must answer three questions: WHO is it for, WHAT is it about, WHY should they read it (the promise).
Build it from these pieces: a number (the container), a clear WHAT, an optional WHO, a FEEL, and the outcome/PROMISE.
- Create a curiosity gap: give the beginning and the end, withhold the middle.
- Clear beats clever. No puns, no mystery titles.
- You must be able to deliver the promise. If the content can't, change the headline (otherwise it's clickbait).
- Credible names work well here because the guests are the credibility ("what [Guest] taught Lenny about X").

### Step 3. Skeleton before prose
Output order:
1. **Headline** (H1)
2. **Introduction:** restate the headline with slightly more detail, state the credibility ("pulled from Lenny's Podcast"), and use the Golden Intersection: answer the reader's question AND include a short story or concrete scene drawn from the transcript (cited).
3. **Main points** (H2 each, same pattern: "Lesson 1:", "Lesson 2:", ...). Each point = claim + transcript evidence + what the reader should do or take from it.
4. **Conclusion:** one specific, useful takeaway. Not a recap. Say what to do next.

### Step 4. Write with rhythm
- Use 1/3/1 as the default: one-sentence opener, ~3 sentences of substance, one-sentence closer. Use 1/5/1 or 1/2/5/2/1 for heavier sections. You can stack them.
- Alternate short and long. Avoid monotone rhythms: all one-line paragraphs, all two-sentence paragraphs, or all 5+ sentence blocks.
- **Rate of revelation:** every sentence must push something new forward. If a sentence repeats or merely describes something already said, cut it.
- Plain words, active voice, no hedging, no filler.

### Step 5. Format for skimming
- H1 headline, H2 per main point. Add H3 only if a point has real sub-sections.
- Turn any paragraph that lists things into bullets.
- Bold the key sentence in each main point (selectively, not everywhere).
- A reader who only skims headings, bullets, and bold should still get the whole argument.

### Step 6. Self-check, then validate
Before returning, check the draft against `validate_essay.py` rules (or call it as a tool if available):
- 1,100 to 1,400 words (target ~1,250)
- exactly one H1, 3 to 7 H2s, consistent H2 pattern
- at least 1 bullet list and some bold text
- paragraph-length variety (no long runs of same-length paragraphs)
- every main section contains at least one citation
- no citation points to a source outside the retrieved set
If validation fails, fix and re-run once. If it still fails, return the draft with a short note on what's off.

## Output format

Return Markdown only: the essay, then a `## Sources` section listing each cited transcript (guest slug, title, timestamp(s) used, YouTube URL if available). Nothing else (no meta-commentary about the process).

## Anti-patterns (never do)

- Mysterious or "creative" headlines with no WHO / WHAT / WHY
- Generic advice any blog could say; claims with no transcript behind them
- Mixing Steps, Lessons, and Mistakes in one piece
- Blocky paragraphs, no subheads
- Repeating the same point in different words
- Promising something in the headline that the essay doesn't deliver
- Recap-only conclusions
