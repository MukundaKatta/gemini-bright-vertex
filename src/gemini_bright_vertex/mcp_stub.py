"""Stub Bright Data + Vertex AI Search MCP server.

Two-stage research surface (Track 2: Intelligence Synthesis):

  STAGE 1 — Bright Data (SERP / unlock / extract / dataset)
    - `search_engine`     — SERP API (Google / Bing / DuckDuckGo)
    - `scrape_page`       — Web Unlocker (anti-bot bypass, rendered HTML)
    - `extract_text`      — clean text from a previously-scraped page
    - `web_data_lookup`   — Bright Data's structured web datasets

  STAGE 2 — Vertex AI Search (Discovery Engine / GenAI App Builder)
    - `index_doc`         — ingest a scraped doc into the search corpus
    - `vertex_search`     — answer follow-ups from the indexed corpus

Returns canned, realistic responses so judges can reproduce the demo
without provisioning Bright Data + Discovery Engine. Real swap is two
env-var changes (BRIGHTDATA_API_TOKEN + GOOGLE_CLOUD_PROJECT) — the
agent code is unchanged.

Run with: python -m gemini_bright_vertex.mcp_stub

Submission: lablab.ai · Bright Data Web Data UNLOCKED Hackathon —
            Track 2 (Intelligence Synthesis), build window
            2026-05-25 → 2026-05-30.
"""

from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent


NOW = datetime.now(timezone.utc)


# ---------------------------------------------------------------------------
# Canned SERP + scrape + dataset data
# ---------------------------------------------------------------------------


# The seeded story chain query: "Anthropic Claude 4.7 release notes".
# Top 3 results scrape cleanly + flow into the Vertex Search corpus.
_SERPS: dict[str, list[dict[str, Any]]] = {
    "Anthropic Claude 4.7 release notes": [
        {
            "rank":    1,
            "title":   "Claude 4.7 release notes — Anthropic",
            "url":     "https://www.anthropic.com/news/claude-4-7-release-notes",
            "snippet": "Claude 4.7 (Sonnet, Haiku, Opus) shipped on 2026-04-21 with extended context, "
                       "improved tool use, and the new agentic mode. Latency drops 22% vs 4.6.",
            "domain":  "anthropic.com",
            "fetched_at": NOW.isoformat(),
        },
        {
            "rank":    2,
            "title":   "What's new in Anthropic's API · May 2026 — Anthropic Engineering Blog",
            "url":     "https://www.anthropic.com/news/api-changelog-may-2026",
            "snippet": "Files API GA, prompt caching defaults to 1h TTL, batch API now supports streaming. "
                       "Memory tool exits preview.",
            "domain":  "anthropic.com",
            "fetched_at": NOW.isoformat(),
        },
        {
            "rank":    3,
            "title":   "Claude 4.7 prompt-caching guide — Anthropic docs",
            "url":     "https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching",
            "snippet": "Cache up to four blocks per request, 1-hour TTL by default, 5-minute TTL on the "
                       "ephemeral tier. New `cache_creation_input_tokens` metric in usage.",
            "domain":  "docs.anthropic.com",
            "fetched_at": NOW.isoformat(),
        },
        {
            "rank":    4,
            "title":   "Claude 4.7 vs GPT-5 head-to-head — Latent Space",
            "url":     "https://www.latent.space/p/claude-4-7-vs-gpt-5-benchmarks",
            "snippet": "Independent benchmark comparing Claude 4.7 Opus and GPT-5 on agent-tool-use tasks. "
                       "Claude leads on long-context retrieval, GPT-5 leads on math.",
            "domain":  "latent.space",
            "fetched_at": NOW.isoformat(),
        },
        {
            "rank":    5,
            "title":   "Built with Opus 4.7 · Cerebral Valley recap",
            "url":     "https://cerebralvalley.ai/posts/built-with-opus-4-7-recap",
            "snippet": "Anthropic's 48-hour hackathon at Cerebral Valley wrapped April 26 with 312 teams "
                       "and a $50K prize pool. Three winners ship next month.",
            "domain":  "cerebralvalley.ai",
            "fetched_at": NOW.isoformat(),
        },
    ],
    "Anthropic CEO Dario Amodei latest interview 2026": [
        {
            "rank":    1,
            "title":   "Dario Amodei on superintelligence timelines — Hard Fork (NYT)",
            "url":     "https://www.nytimes.com/podcasts/hard-fork/dario-amodei-may-2026",
            "snippet": "Anthropic CEO Dario Amodei talks 2027 timelines, the company's $50B-revenue target, "
                       "and why he thinks RSP-level ASL-4 is 18 months out. Interview aired May 12, 2026.",
            "domain":  "nytimes.com",
            "fetched_at": NOW.isoformat(),
        },
    ],
}


_SCRAPED_PAGES: dict[str, dict[str, Any]] = {
    "https://www.anthropic.com/news/claude-4-7-release-notes": {
        "url":     "https://www.anthropic.com/news/claude-4-7-release-notes",
        "title":   "Claude 4.7 release notes",
        "status":  200,
        "rendered_chars": 8421,
        "text_excerpt": (
            "We're shipping Claude 4.7 today, an across-the-board upgrade to our model family. "
            "Three SKUs ship simultaneously: Sonnet, Haiku, and Opus. All three include extended "
            "context to 1M tokens with prompt caching, improved structured-tool-use accuracy, and "
            "a new 'agentic mode' that automatically retries failed tool calls with a self-repair "
            "step. Latency on Sonnet is 22% lower than 4.6 at the p95 measured across 100k "
            "production requests. Opus 4.7 ships with the new 'thinking' budget controls — "
            "developers can cap reasoning tokens per turn. Pricing is unchanged from 4.6."
        ),
        "fetched_at": NOW.isoformat(),
        "unlocked_by_brightdata": True,
    },
    "https://www.anthropic.com/news/api-changelog-may-2026": {
        "url":     "https://www.anthropic.com/news/api-changelog-may-2026",
        "title":   "What's new in the Anthropic API · May 2026",
        "status":  200,
        "rendered_chars": 5612,
        "text_excerpt": (
            "The Files API is now generally available. Upload up to 100 MB per file, share files "
            "across requests, automatic 30-day retention. The Memory tool exits preview today; "
            "developers can give Claude a persistent scratchpad bounded by a token budget. "
            "Prompt caching defaults to a 1-hour TTL across all tiers. The Batch API now supports "
            "streaming partial results back as each batched request completes."
        ),
        "fetched_at": NOW.isoformat(),
        "unlocked_by_brightdata": True,
    },
    "https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching": {
        "url":     "https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching",
        "title":   "Prompt caching — Anthropic docs",
        "status":  200,
        "rendered_chars": 4204,
        "text_excerpt": (
            "Prompt caching lets you cache up to four content blocks per request. The default TTL "
            "is 1 hour across all tiers as of May 2026; the ephemeral tier still offers a 5-minute "
            "TTL for short-lived sessions. Every cached response now surfaces a "
            "`cache_creation_input_tokens` metric in the usage payload so you can verify cache hits "
            "without scraping logs. Caching applies across both Sonnet and Opus 4.7 with no "
            "additional configuration."
        ),
        "fetched_at": NOW.isoformat(),
        "unlocked_by_brightdata": True,
    },
}


_DATASETS: dict[str, list[dict[str, Any]]] = {
    # Bright Data has dataset endpoints for, e.g., LinkedIn company pages.
    "linkedin_company:Anthropic": [
        {
            "company":         "Anthropic",
            "linkedin_url":    "https://www.linkedin.com/company/anthropicresearch",
            "headquarters":    "San Francisco, CA, United States",
            "industry":        "AI / Research",
            "employee_count":  1_842,
            "founded":         2021,
            "specialties":     ["LLMs", "AI Safety", "Constitutional AI", "RLHF"],
            "fetched_at":      NOW.isoformat(),
        },
    ],
}


# ---------------------------------------------------------------------------
# Vertex AI Search (Discovery Engine) stub corpus
# ---------------------------------------------------------------------------


# Process-level in-memory corpus. Stage 2 ingests scraped pages here; the
# follow-up `vertex_search` call answers from this corpus. Mirrors the shape
# of `google.cloud.discoveryengine_v1.DocumentService.create_document` and
# `SearchService.search` so the swap to a real Discovery Engine data store
# is one client call.
_VERTEX_CORPUS: dict[str, dict[str, Any]] = {}


# Canned ranked answers for known follow-up queries. The agent calls these
# after Stage 2 ingest so the demo finishes with a search-grounded synthesis.
_VERTEX_QUERIES: dict[str, list[str]] = {
    "summarize the API changes": [
        "doc_anthropic_changelog",
        "doc_claude_47_release",
        "doc_prompt_caching",
    ],
    "what changed in the Anthropic API in May 2026": [
        "doc_anthropic_changelog",
        "doc_prompt_caching",
        "doc_claude_47_release",
    ],
    "what is new with prompt caching": [
        "doc_prompt_caching",
        "doc_anthropic_changelog",
        "doc_claude_47_release",
    ],
}


# Stable doc_id mapping per URL — keeps Stage 1 → Stage 2 → Stage 3 traceable.
_URL_TO_DOC_ID: dict[str, str] = {
    "https://www.anthropic.com/news/claude-4-7-release-notes":               "doc_claude_47_release",
    "https://www.anthropic.com/news/api-changelog-may-2026":                 "doc_anthropic_changelog",
    "https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching":   "doc_prompt_caching",
}


def doc_id_for_url(url: str) -> str:
    """Stable doc_id for a scraped URL. Used by agent + tests to bridge stages."""
    return _URL_TO_DOC_ID.get(url, f"doc_{abs(hash(url)) % 10_000_000:07d}")


# ---------------------------------------------------------------------------
# Response builders — Bright Data (Stage 1)
# ---------------------------------------------------------------------------


# SERP query aliasing — common rewordings the agent might pick for the
# Claude 4.7 release-notes story chain. Keeps the demo robust against the
# LLM rephrasing the user's question before calling `search_engine`.
_SERP_ALIASES: dict[str, str] = {
    "anthropic claude 4.7 api changes may 2026":              "Anthropic Claude 4.7 release notes",
    "anthropic claude 4.7 api changes":                       "Anthropic Claude 4.7 release notes",
    "anthropic claude 4.7 api changelog":                     "Anthropic Claude 4.7 release notes",
    "anthropic claude 4.7 release":                           "Anthropic Claude 4.7 release notes",
    "anthropic claude 4.7 release notes 2026":                "Anthropic Claude 4.7 release notes",
    "anthropic claude latest release notes 2026":             "Anthropic Claude 4.7 release notes",
    "anthropic claude latest release notes":                  "Anthropic Claude 4.7 release notes",
    "claude 4.7 release notes":                               "Anthropic Claude 4.7 release notes",
    "claude 4.7 api changes":                                 "Anthropic Claude 4.7 release notes",
    "anthropic api changes may 2026":                         "Anthropic Claude 4.7 release notes",
    "anthropic api changelog may 2026":                       "Anthropic Claude 4.7 release notes",
    "claude api changes may 2026":                            "Anthropic Claude 4.7 release notes",
}


def _resolve_serp_query(query: str) -> str:
    """Map common rewordings to the canonical seeded SERP key."""
    if query in _SERPS:
        return query
    alias = _SERP_ALIASES.get(query.strip().lower())
    return alias if alias else query


def search_engine_response(query: str, engine: str = "google") -> dict[str, Any]:
    canonical = _resolve_serp_query(query)
    results = _SERPS.get(canonical, [])
    if not results:
        # Soft fallback so the agent can still reason about an unknown query.
        results = [{
            "rank":    1,
            "title":   f"(stub) no canned SERP for {query!r}",
            "url":     "",
            "snippet": "Bright Data stub: this query has no canned results. "
                       "In production the real Bright Data SERP API would return "
                       "live results from the chosen engine.",
            "domain":  "stub",
            "fetched_at": NOW.isoformat(),
        }]
    return {
        "query":     query,
        "engine":    engine,
        "result_count": len(results),
        "results":   results,
    }


def scrape_page_response(url: str) -> dict[str, Any]:
    rec = _SCRAPED_PAGES.get(url)
    if rec is None:
        return {
            "url":    url,
            "status": 200,
            "rendered_chars": 0,
            "text_excerpt": (
                f"(stub) no canned scrape for {url}. In production the real "
                "Bright Data Web Unlocker would return the rendered page text "
                "after bypassing any anti-bot defences."
            ),
            "unlocked_by_brightdata": True,
            "fetched_at": NOW.isoformat(),
        }
    return rec


def extract_text_response(url: str, css_selector: str | None = None) -> dict[str, Any]:
    """Convenience tool: extract clean text from a previously-scraped page."""
    page = _SCRAPED_PAGES.get(url)
    if page is None:
        return {"error": f"page not scraped yet: {url!r} — call scrape_page first"}
    return {
        "url":          url,
        "css_selector": css_selector or "body",
        "text":         page["text_excerpt"],
        "char_count":   len(page["text_excerpt"]),
    }


def web_data_lookup_response(dataset: str, key: str) -> dict[str, Any]:
    lookup_key = f"{dataset}:{key}"
    rec = _DATASETS.get(lookup_key)
    if rec is None:
        return {"error": f"unknown dataset entry {lookup_key!r}",
                "known": list(_DATASETS.keys())}
    return {"dataset": dataset, "key": key, "records": rec, "count": len(rec)}


# ---------------------------------------------------------------------------
# Response builders — Vertex AI Search (Stage 2)
# ---------------------------------------------------------------------------


def index_doc_response(
    doc_id: str,
    title: str,
    content: str,
    uri: str,
) -> dict[str, Any]:
    """Simulate `DocumentService.create_document` on a Discovery Engine data store.

    Stores the doc in the process-level `_VERTEX_CORPUS` so a follow-up
    `vertex_search` call can return it verbatim. The agent calls this once
    per scraped page in Stage 2.
    """
    indexed_at = datetime.now(timezone.utc).isoformat()
    _VERTEX_CORPUS[doc_id] = {
        "doc_id":      doc_id,
        "title":       title,
        "content":     content,
        "uri":         uri,
        "indexed_at":  indexed_at,
    }
    return {
        "status":     "indexed",
        "doc_id":     doc_id,
        "title":      title,
        "uri":        uri,
        "indexed_at": indexed_at,
        "corpus_size": len(_VERTEX_CORPUS),
    }


def vertex_search_response(query: str, top_k: int = 3) -> dict[str, Any]:
    """Simulate `SearchService.search` on the Discovery Engine corpus.

    For known follow-up queries we use a canned ranking that picks the most
    relevant indexed docs. For unknown queries we fall back to substring
    matching across the corpus so the demo still degrades gracefully.
    """
    ranking = _VERTEX_QUERIES.get(query)
    if ranking is None:
        # Substring fallback so judges can fire any follow-up question.
        q = query.lower()
        scored = []
        for doc_id, rec in _VERTEX_CORPUS.items():
            text = (rec.get("title", "") + " " + rec.get("content", "")).lower()
            score = sum(1 for tok in q.split() if tok in text)
            if score:
                scored.append((score, doc_id))
        scored.sort(reverse=True)
        ranking = [doc_id for _score, doc_id in scored]

    hits: list[dict[str, Any]] = []
    for doc_id in ranking[: max(top_k, 0)]:
        rec = _VERTEX_CORPUS.get(doc_id)
        if rec is None:
            continue
        content = rec["content"]
        # First two sentences as a "snippet" — verbatim, no paraphrase.
        snippet = ". ".join(content.split(". ")[:2]).strip()
        if snippet and not snippet.endswith("."):
            snippet += "."
        hits.append({
            "doc_id":  rec["doc_id"],
            "title":   rec["title"],
            "uri":     rec["uri"],
            "snippet": snippet,
            "content": content,
            "indexed_at": rec["indexed_at"],
        })

    return {
        "query":       query,
        "top_k":       top_k,
        "result_count": len(hits),
        "corpus_size":  len(_VERTEX_CORPUS),
        "results":     hits,
    }


# ---------------------------------------------------------------------------
# Test/helper utilities
# ---------------------------------------------------------------------------


def _reset_corpus() -> None:
    """Clear the in-memory Vertex Search corpus. For test isolation only."""
    _VERTEX_CORPUS.clear()


# ---------------------------------------------------------------------------
# MCP server wiring
# ---------------------------------------------------------------------------


def _make_server() -> Server:
    server = Server("bright-data-vertex-stub")

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [
            Tool(name="search_engine",
                 description=("STAGE 1 (Bright Data SERP API). Run a SERP query "
                              "and get the top results with rank, title, url, "
                              "snippet, and domain. Engine defaults to google."),
                 inputSchema={"type": "object",
                              "properties": {
                                  "query":  {"type": "string"},
                                  "engine": {"type": "string",
                                              "enum": ["google", "bing", "duckduckgo"],
                                              "default": "google"},
                              },
                              "required": ["query"]}),
            Tool(name="scrape_page",
                 description=("STAGE 1 (Bright Data Web Unlocker). Fetch a URL "
                              "through Bright Data's anti-bot bypass. Returns "
                              "rendered text + status + the "
                              "`unlocked_by_brightdata` flag."),
                 inputSchema={"type": "object",
                              "properties": {"url": {"type": "string"}},
                              "required": ["url"]}),
            Tool(name="extract_text",
                 description=("STAGE 1 (Bright Data). Extract clean text from a "
                              "previously-scraped page. Optionally narrow by "
                              "CSS selector."),
                 inputSchema={"type": "object",
                              "properties": {
                                  "url":          {"type": "string"},
                                  "css_selector": {"type": "string"},
                              },
                              "required": ["url"]}),
            Tool(name="web_data_lookup",
                 description=("STAGE 1 (Bright Data datasets). Look up a "
                              "structured record from Bright Data's web "
                              "datasets (LinkedIn companies, Amazon products, "
                              "etc.). Returns canonical fields verbatim."),
                 inputSchema={"type": "object",
                              "properties": {
                                  "dataset": {"type": "string"},
                                  "key":     {"type": "string"},
                              },
                              "required": ["dataset", "key"]}),
            Tool(name="index_doc",
                 description=("STAGE 2 (Vertex AI Search / Discovery Engine). "
                              "Ingest a scraped doc into the search corpus. "
                              "Pass a stable doc_id, the page title, the full "
                              "page content, and the source URI. Returns "
                              "{status: 'indexed', doc_id, indexed_at}. Call "
                              "once per scraped page before vertex_search."),
                 inputSchema={"type": "object",
                              "properties": {
                                  "doc_id":  {"type": "string"},
                                  "title":   {"type": "string"},
                                  "content": {"type": "string"},
                                  "uri":     {"type": "string"},
                              },
                              "required": ["doc_id", "title", "content", "uri"]}),
            Tool(name="vertex_search",
                 description=("STAGE 2 (Vertex AI Search / Discovery Engine). "
                              "Query the indexed corpus for the user's "
                              "follow-up question. Returns top_k matching "
                              "docs with verbatim snippets + full content + "
                              "the source URI. Use this to synthesize the "
                              "final answer with quotes."),
                 inputSchema={"type": "object",
                              "properties": {
                                  "query": {"type": "string"},
                                  "top_k": {"type": "integer", "default": 3},
                              },
                              "required": ["query"]}),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
        a = arguments
        if name == "search_engine":
            payload = search_engine_response(a.get("query", ""),
                                              a.get("engine", "google"))
        elif name == "scrape_page":
            payload = scrape_page_response(a.get("url", ""))
        elif name == "extract_text":
            payload = extract_text_response(a.get("url", ""),
                                            a.get("css_selector"))
        elif name == "web_data_lookup":
            payload = web_data_lookup_response(a.get("dataset", ""),
                                                a.get("key", ""))
        elif name == "index_doc":
            payload = index_doc_response(
                doc_id=a.get("doc_id", ""),
                title=a.get("title", ""),
                content=a.get("content", ""),
                uri=a.get("uri", ""),
            )
        elif name == "vertex_search":
            payload = vertex_search_response(
                query=a.get("query", ""),
                top_k=int(a.get("top_k", 3)),
            )
        else:
            payload = {"error": f"unknown tool {name!r}"}
        return [TextContent(type="text", text=json.dumps(payload, indent=2, default=str))]

    return server


async def _main() -> None:
    server = _make_server()
    async with stdio_server() as (read, write):
        await server.run(read, write, server.create_initialization_options())


def main() -> None:
    asyncio.run(_main())


if __name__ == "__main__":
    main()
