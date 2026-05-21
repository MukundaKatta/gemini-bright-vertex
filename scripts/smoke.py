"""Real Vertex AI smoke test for gemini-bright-vertex (two-stage).

Runs a research question end-to-end through Gemini 2.5 Flash on the
Bright Data + Vertex AI Search MCP stub and verifies the agent walks:

  STAGE 1   SERP search → scrape via Bright Data → "22%" verbatim.
  STAGE 2   index_doc on each scraped page → "indexed" verbatim.
  STAGE 3   vertex_search follow-up → synthesized answer with at least
            one indexed doc_id surfaced in SOURCES.

Usage:
    GOOGLE_CLOUD_PROJECT=careersavvy-mukunda \\
    GOOGLE_GENAI_USE_VERTEXAI=true \\
    GOOGLE_CLOUD_LOCATION=us-central1 \\
    .venv/bin/python scripts/smoke.py
"""
from __future__ import annotations

import os
import sys

os.environ.setdefault("GOOGLE_CLOUD_PROJECT", "careersavvy-mukunda")
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "true")
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "us-central1")

from gemini_bright_vertex.runner import ask  # noqa: E402


QUESTION = (
    "Summarize the Anthropic Claude 4.7 API changes from announcements "
    "in May 2026.\n\n"
    "Walk the two-stage flow:\n"
    "  STAGE 1: call search_engine with the exact query "
    "'Anthropic Claude 4.7 release notes', then scrape_page on the "
    "top 3 anthropic.com results.\n"
    "  STAGE 2: call index_doc on every scraped page into Vertex AI "
    "Search — use stable doc_ids like 'doc_claude_47_release', "
    "'doc_anthropic_changelog', 'doc_prompt_caching'.\n"
    "  STAGE 3: call vertex_search with the exact query "
    "'summarize the API changes' and top_k=3.\n\n"
    "Output the 5 labeled sections from your system prompt with "
    "verbatim quotes and each indexed doc_id paired with its source URL."
)


def main() -> int:
    print("== gemini-bright-vertex smoke (two-stage) ==")
    print(f"project={os.environ.get('GOOGLE_CLOUD_PROJECT')}")
    print(f"location={os.environ.get('GOOGLE_CLOUD_LOCATION')}")
    print(f"vertexai={os.environ.get('GOOGLE_GENAI_USE_VERTEXAI')}")
    print()
    print(f"> {QUESTION}")
    print()

    resp = ask(QUESTION, stub=True)
    print("--- FINAL TEXT ---")
    print(resp.final_text or "(no final text)")
    print("--- END FINAL TEXT ---")
    print(f"events: {len(resp.events)}")

    text = resp.final_text or ""
    upper = text.upper()

    # Look for any of the known canned doc_ids from the Vertex Search stub.
    known_doc_ids = (
        "doc_claude_47_release",
        "doc_anthropic_changelog",
        "doc_prompt_caching",
    )
    has_doc_id = any(did in text for did in known_doc_ids)

    checks = {
        "has ANSWER section":           "ANSWER" in upper,
        "has SOURCES section":          "SOURCES" in upper,
        "has KEY QUOTES section":       "KEY QUOTES" in upper,
        "has CONFIDENCE section":       "CONFIDENCE" in upper,
        "has NEXT STEP section":        "NEXT STEP" in upper,
        "quotes 22% verbatim (Stage1)": "22%" in text,
        "mentions 'indexed' (Stage2)":  "indexed" in text.lower(),
        "surfaces a Vertex doc_id":     has_doc_id,
        "cites anthropic.com":          "anthropic.com" in text.lower(),
        "names Claude 4.7":             "4.7" in text,
    }
    print()
    print("--- CHECKS ---")
    for label, ok in checks.items():
        print(f"  [{'PASS' if ok else 'FAIL'}] {label}")
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
