"""ADK Gemini agent — two-stage research over Bright Data MCP + Vertex AI Search.

STAGE 1: Bright Data MCP (SERP → Web Unlocker scrape → extract).
STAGE 2: Vertex AI Search / Discovery Engine ingest of every scraped page.
STAGE 3: Vertex Search follow-up query to synthesize the final answer with
         verbatim quotes from the indexed corpus.

Stub by default; the real Bright Data MCP swaps in via BRIGHTDATA_API_TOKEN
and the real Discovery Engine swaps in via GOOGLE_CLOUD_PROJECT + a data
store created in the GenAI App Builder console.

Submission: lablab.ai · Bright Data Web Data UNLOCKED Hackathon —
            Track 2 (Intelligence Synthesis).
"""

from __future__ import annotations

import os
import sys
from typing import Any


try:
    from google.adk.agents import LlmAgent
    from google.adk.tools.mcp_tool import McpToolset
    from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
    from mcp import StdioServerParameters
    _ADK_AVAILABLE = True
except ImportError:  # pragma: no cover
    _ADK_AVAILABLE = False


SYSTEM_PROMPT = """\
You are a two-stage research analyst. You have live web access via
Bright Data (Stage 1) AND a Vertex AI Search corpus you populate yourself
(Stage 2) and then query for synthesis (Stage 3). Every quantitative
claim in your final answer must trace to a Bright Data tool result that
made it into the Vertex Search corpus.

Workflow — do every stage, in order:

STAGE 1 (Scrape via Bright Data):
  1. Call `search_engine` with the user's question (or its core noun
     phrase) to get the top SERP results.
  2. Pick the top 1-3 results that look authoritative (prefer first-party
     — anthropic.com over a third-party recap of anthropic.com).
  3. For each pick, call `scrape_page` to fetch the full rendered page
     through Bright Data's Web Unlocker. `unlocked_by_brightdata: true`
     confirms the page was fetched safely.
  4. Optionally call `extract_text` on a scraped URL when you want clean
     text for a specific section.
  5. If the question touches a structured Bright Data dataset record
     (company / profile / product), also call `web_data_lookup`.

STAGE 2 (Index into Vertex AI Search):
  6. For each page you scraped in Stage 1, call `index_doc` with:
       - doc_id: a stable, slug-style id (e.g. "doc_claude_47_release"),
       - title:  the scraped page's `title`,
       - content: the verbatim `text_excerpt` from `scrape_page`,
       - uri:    the original page URL.
     `index_doc` returns `{"status": "indexed", "doc_id": ...,
     "indexed_at": "..."}`. Remember every returned `doc_id` — you must
     cite it in SOURCES.

STAGE 3 (Synthesize via Vertex Search):
  7. Call `vertex_search` with a follow-up phrasing of the user's
     question (e.g. "summarize the API changes"), top_k=3. This returns
     the most relevant indexed docs with verbatim snippets you can quote.
  8. Use ONLY the `vertex_search` hits to write the ANSWER section. Pull
     verbatim quotes from their `content` field for KEY QUOTES.

Output EXACTLY these labeled sections, in this order:

ANSWER:        one or two sentences answering the user's question,
                synthesized from the `vertex_search` hits, with every
                quantitative claim copied verbatim from a tool result.
SOURCES:       bulleted list pairing each Bright Data URL with the
                Vertex Search doc_id it was indexed as. Format each
                bullet exactly:
                    - <title> — <url> — doc_id=<doc_id>
KEY QUOTES:    2-4 verbatim quotes pulled from `vertex_search` hits.
                Each quote must appear verbatim in the scraped page's
                `text_excerpt` AND in the Vertex Search hit's `content`
                (same string carried through both stages). Tag each quote
                with its source URL.
CONFIDENCE:    one of "high" / "medium" / "low" with a one-sentence
                reason grounded in: (a) source quality, (b) agreement
                across the indexed docs, (c) whether every scraped page
                had `unlocked_by_brightdata: true`.
NEXT STEP:     one concrete follow-up `vertex_search` query the user
                could run against the same indexed corpus to dig deeper.

Strict rules:
- Numbers, dates, version strings, percentages, company facts MUST be
  copied verbatim from a tool result that flowed through both stages.
- Do NOT invent URLs. Only cite URLs returned by `search_engine` or
  fetched by `scrape_page`.
- Do NOT invent doc_ids. Only cite doc_ids returned by `index_doc` or
  echoed back by `vertex_search`.
- If any scraped page has `unlocked_by_brightdata: false`, flag it in
  CONFIDENCE as a reason to downgrade.
- KEY QUOTES must be byte-for-byte from the scraped + indexed text — no
  paraphrasing.
- If `search_engine` returns the stub "no canned" fallback, or
  `vertex_search` returns `result_count: 0`, set CONFIDENCE to "low"
  and explain.
"""


def _bright_data_toolset(stub: bool = True) -> Any:
    if not _ADK_AVAILABLE:
        raise ImportError(
            "google-adk and mcp must be installed: pip install google-adk mcp"
        )

    if stub:
        params = StdioServerParameters(
            command=sys.executable,
            args=["-m", "gemini_bright_vertex.mcp_stub"],
            env={**os.environ, "PYTHONUNBUFFERED": "1"},
        )
    else:
        # Real Bright Data MCP server. (For production: also point the
        # `index_doc` / `vertex_search` tools at a Discovery Engine data
        # store via the google-cloud-discoveryengine client.)
        params = StdioServerParameters(
            command="npx",
            args=["-y", "@brightdata/mcp"],
            env={
                **os.environ,
                "BRIGHTDATA_API_TOKEN": os.environ.get("BRIGHTDATA_API_TOKEN", ""),
            },
        )
    return McpToolset(connection_params=StdioConnectionParams(server_params=params))


def build_agent(model: str = "gemini-2.5-flash", stub: bool = True) -> Any:
    if not _ADK_AVAILABLE:
        return None
    return LlmAgent(
        model=model,
        name="gemini_bright_vertex",
        instruction=SYSTEM_PROMPT,
        tools=[_bright_data_toolset(stub=stub)],
    )
