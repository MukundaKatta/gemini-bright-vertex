# gemini-bright-vertex

A two-stage research agent built on **Google Cloud Agent Builder (ADK)**,
**Gemini 2.5**, the **Bright Data MCP server**, and **Vertex AI Search**
(Discovery Engine / GenAI App Builder). Submission for the **Bright Data
Web Data UNLOCKED Hackathon** on lablab.ai (build window 2026-05-25 →
2026-05-30) — **Track 2: Intelligence Synthesis**.

## What it does

The user gives the agent a research question. The agent answers it with
a two-stage flow:

1. **STAGE 1 — Scrape.** Walk the Bright Data MCP tools (SERP API → Web
   Unlocker → text extract → dataset lookup) to gather the top first-party
   sources for the question.
2. **STAGE 2 — Index.** Push every scraped page into a Vertex AI Search
   data store via `index_doc`.
3. **STAGE 3 — Synthesize.** Re-query the indexed corpus with
   `vertex_search` and answer the user's question with verbatim quotes
   pulled byte-for-byte from the indexed docs.

The Stage 2 split is what makes this a Track 2 (Intelligence Synthesis)
submission rather than a plain scraper: the scraped corpus becomes a
durable, queryable knowledge base that the same agent (or future agents)
can keep mining without re-scraping.

## Tool surface

The agent uses the standard Bright Data MCP tool surface — same as the
official [`@brightdata/mcp`](https://github.com/brightdata/mcp) npm
package — extended with two Vertex AI Search tools. Stub for demos, real
account is two env-var swaps (BRIGHTDATA_API_TOKEN + GOOGLE_CLOUD_PROJECT).

**Stage 1 (Bright Data):**
- `search_engine(query, engine)` — SERP API (Google / Bing / DuckDuckGo)
- `scrape_page(url)` — Web Unlocker, anti-bot bypass, rendered HTML + text
- `extract_text(url, css_selector)` — clean text from a previously-scraped page
- `web_data_lookup(dataset, key)` — structured datasets (LinkedIn companies, Amazon products, etc.)

**Stage 2 (Vertex AI Search / Discovery Engine):**
- `index_doc(doc_id, title, content, uri)` — ingest a scraped doc into the search corpus
- `vertex_search(query, top_k=3)` — query the indexed corpus, returns verbatim snippets + doc URIs

## Architecture

```
┌──────────────────────┐   ┌───────────────────────┐   ┌──────────────────────────┐   ┌──────────────────────────┐
│ Streamlit dashboard  │──▶│  ADK LlmAgent          │──▶│  STAGE 1: Bright Data     │──▶│  STAGE 2: Vertex AI       │
│ on Cloud Run         │   │  Gemini 2.5 on Vertex  │   │  MCP (SERP / Unlocker /   │   │  Search (Discovery        │
│                      │   │  AI                    │   │  extract / dataset)       │   │  Engine) index + query    │
│ "research my Q ..."  │   │                        │   │                           │   │                           │
└──────────────────────┘   └───────────────────────┘   └──────────────────────────┘   └──────────────────────────┘
```

## Output contract

The system prompt requires EXACTLY these labeled sections per answer:

```
ANSWER:      synthesized from vertex_search hits, every number/date/version verbatim from tools.
SOURCES:     bulleted Bright Data URLs each paired with their Vertex Search doc_id.
KEY QUOTES:  2-4 verbatim quotes pulled from vertex_search hits; same string lives in scrape_page too.
CONFIDENCE:  high / medium / low, grounded in source quality + cross-doc agreement + Bright Data unlock flag.
NEXT STEP:   one concrete follow-up vertex_search query against the same indexed corpus.
```

Strict rule: every quantitative claim must come from a tool result that
flowed through both stages. The agent cites byte-for-byte; never
paraphrases inside KEY QUOTES.

## Try it against a real Bright Data + Discovery Engine

```sh
export BRIGHTDATA_API_TOKEN="brd_..."
export GOOGLE_CLOUD_PROJECT="your-project"
export GOOGLE_GENAI_USE_VERTEXAI=true
export GOOGLE_CLOUD_LOCATION=us-central1
pip install -e .
streamlit run app/dashboard.py
```

Untick "Use stub Bright Data + Vertex Search" in the sidebar. The agent
now spawns the official `@brightdata/mcp` server via `npx` and (with a
small `index_doc` / `vertex_search` wrapper around the
`google-cloud-discoveryengine` client) talks to a real Discovery Engine
data store you create in the GenAI App Builder console.

## Tests

```sh
pip install -e ".[dev]"
pytest -q
```

The suite pins the two-stage chain contract: the same scraped content
survives Stage 1 → Stage 2 → Stage 3 byte-for-byte, so the agent's
KEY QUOTES are auditable. See
`test_scrape_index_search_chain_is_consistent`.

## License

Apache 2.0. Standalone repo created during the Bright Data Web Data
UNLOCKED Hackathon contest period (2026-05-25 → 2026-05-30).
