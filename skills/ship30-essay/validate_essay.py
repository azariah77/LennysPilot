"""Validate a generated essay against the ship30-essay skill rules.

Usage:
    python validate_essay.py essay.md [--allowed-sources slug1,slug2,...]
    cat essay.md | python validate_essay.py -

Exit code 0 = pass, 1 = fail. Prints a JSON report so an agent/tool can parse it.
"""
from __future__ import annotations

import argparse
import json
import re
import sys

CITATION_RE = re.compile(r"\[([a-z0-9][a-z0-9\-]*)\s*·\s*(\d{1,2}:\d{2}:\d{2}|\d{1,2}:\d{2})\]")
H1_RE = re.compile(r"^#\s+(?!#)(.+)$", re.M)
H2_RE = re.compile(r"^##\s+(?!#)(.+)$", re.M)
BULLET_RE = re.compile(r"^\s*(?:[-*+]|\d+\.)\s+\S", re.M)
BOLD_RE = re.compile(r"\*\*[^*\n]+\*\*")
PATTERN_RE = re.compile(r"^(lesson|step|mistake|tip|reason)\s*#?\d+", re.I)

MIN_WORDS, MAX_WORDS = 1100, 1400


def split_body_and_sources(text: str) -> tuple[str, str]:
    m = re.search(r"^##\s+Sources\b", text, re.M | re.I)
    if not m:
        return text, ""
    return text[: m.start()], text[m.start():]


def sections(body: str) -> list[tuple[str, str]]:
    """Return (heading, content) for each H2 section in the body."""
    parts = re.split(r"^##\s+(?!#)(.+)$", body, flags=re.M)
    # parts = [preamble, h1, c1, h2, c2, ...]
    return [(parts[i].strip(), parts[i + 1]) for i in range(1, len(parts) - 1, 2)]


def paragraph_lengths(body: str) -> list[int]:
    paras = []
    for block in re.split(r"\n\s*\n", body):
        block = block.strip()
        if not block or block.startswith("#") or BULLET_RE.match(block):
            continue
        paras.append(len(re.findall(r"[.!?](?:\s|$)", block)) or 1)
    return paras


def longest_equal_run(vals: list[int]) -> int:
    best = run = 1 if vals else 0
    for a, b in zip(vals, vals[1:]):
        run = run + 1 if a == b else 1
        best = max(best, run)
    return best


def validate(text: str, allowed_sources: set[str] | None = None) -> dict:
    body, sources_block = split_body_and_sources(text)
    checks: dict[str, dict] = {}

    def add(name: str, ok: bool, detail: str) -> None:
        checks[name] = {"ok": bool(ok), "detail": detail}

    words = len(re.findall(r"\b[\w'’-]+\b", re.sub(r"\[[^\]]*\]", "", body)))
    add("word_count", MIN_WORDS <= words <= MAX_WORDS, f"{words} words (target {MIN_WORDS}-{MAX_WORDS})")

    h1s = H1_RE.findall(body)
    add("single_h1", len(h1s) == 1, f"{len(h1s)} H1 found")

    secs = sections(body)
    heads = [h for h, _ in secs]
    add("h2_count", 3 <= len(heads) <= 7, f"{len(heads)} H2 sections")

    kinds = {(PATTERN_RE.match(h).group(1).lower() if PATTERN_RE.match(h) else None) for h in heads}
    add(
        "consistent_pattern",
        len(heads) >= 3 and len(kinds) == 1 and None not in kinds,
        "main-point headings should all be the same type (e.g. 'Lesson 1', 'Lesson 2'). Found: "
        + ", ".join(sorted(str(k) for k in kinds)),
    )

    add("has_bullets", len(BULLET_RE.findall(body)) >= 3, f"{len(BULLET_RE.findall(body))} bullet lines")
    add("has_bold", len(BOLD_RE.findall(body)) >= 3, f"{len(BOLD_RE.findall(body))} bold spans")

    lens = paragraph_lengths(body)
    run = longest_equal_run(lens)
    add("rhythm_variety", run <= 3 and len(set(lens)) >= 3, f"longest same-length run={run}, distinct lengths={len(set(lens))}")

    # citations
    cites = CITATION_RE.findall(text)
    add("has_citations", len(cites) >= 5, f"{len(cites)} citations")
    missing = [h for h, c in secs if h.lower() != "sources" and not CITATION_RE.search(c)]
    add("every_section_cited", not missing, "uncited sections: " + (", ".join(missing) or "none"))
    if allowed_sources is not None:
        bad = sorted({slug for slug, _ in cites if slug not in allowed_sources})
        add("citations_in_retrieved_set", not bad, "unknown sources: " + (", ".join(bad) or "none"))

    add("sources_section", bool(sources_block.strip()), "## Sources section present" if sources_block else "missing ## Sources section")

    # headline answers WHO/WHAT/PROMISE (heuristic: has a number or a 'how/why' promise and is not too short)
    if h1s:
        h = h1s[0]
        add("headline_specific", len(h.split()) >= 8, f"{len(h.split())} words (descriptive headlines run 8+)")
    else:
        add("headline_specific", False, "no headline")

    return {"passed": all(c["ok"] for c in checks.values()), "checks": checks}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("path", help="markdown file, or - for stdin")
    ap.add_argument("--allowed-sources", default=None, help="comma-separated guest slugs retrieved for this answer")
    args = ap.parse_args()
    text = sys.stdin.read() if args.path == "-" else open(args.path, encoding="utf-8").read()
    allowed = set(args.allowed_sources.split(",")) if args.allowed_sources else None
    report = validate(text, allowed)
    print(json.dumps(report, indent=2))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
