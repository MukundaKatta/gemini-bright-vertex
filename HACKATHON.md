# Bright Data Web Data UNLOCKED Hackathon — lablab.ai submission

**Track 2: Intelligence Synthesis.**

Lablab event: https://lablab.ai/ai-hackathons/brightdata-web-data-unlocked
Build window: 2026-05-25 → 2026-05-30
Demos: 2026-05-31

## Elevator pitch
A two-stage Gemini research analyst. STAGE 1 walks Bright Data MCP
(SERP API + Web Unlocker + structured datasets) to scrape the top
first-party sources for a question. STAGE 2 indexes every scraped
page into a Vertex AI Search corpus and synthesizes the final answer
from that corpus with verbatim quotes. Stage 1 unlocks the web; Stage 2
turns the unlocked content into a durable, queryable knowledge base.

## Why Track 2 (Intelligence Synthesis)

A plain scrape-and-cite agent (Track 1) answers one question and throws
the page away. Track 2 demands turning unlocked web data into
intelligence — something the team can re-query later without scraping
again. We do that by piping every Bright Data scrape straight into
Vertex AI Search (Discovery Engine), then answering the user's question
from the indexed corpus. Same agent, same prompt, durable corpus.

## Rule compliance

| Rule | How we meet it |
|---|---|
| Uses Bright Data | MCP tool surface matches the official `@brightdata/mcp` (SERP, Web Unlocker, structured datasets); stub for demos, real account via `BRIGHTDATA_API_TOKEN` |
| Track 2 — Intelligence Synthesis | Stage 2 indexes every scraped page into Vertex AI Search (Discovery Engine) and the final answer is synthesized from the indexed corpus, not the raw scrape |
| AI agent (not just a script) | `google.adk.agents.LlmAgent` with Gemini 2.5 Flash on Vertex AI walks 6 MCP tools across both stages and self-evaluates source quality |
| Newly created during the contest period | Repo init within the build window (2026-05-25 → 2026-05-30) |
| Original work | Standalone repo, Apache 2.0 |
| Runs on the web | Streamlit dashboard, Cloud Run deployable |

## Description

`gemini-bright-vertex` treats every research question as a
**scrape → index → synthesize** loop. You ask "Summarize the Anthropic
Claude 4.7 API changes from announcements in May 2026" and the agent:

**STAGE 1 — Scrape (Bright Data MCP):**
1. `search_engine(query, engine)` — pull the top SERP results.
2. Pick the most authoritative (prefer first-party).
3. `scrape_page(url)` — fetch the rendered page through the Web
   Unlocker (anti-bot bypass, returns `unlocked_by_brightdata: true`).
4. `extract_text(url, css_selector)` — clean text for citation.
5. `web_data_lookup(dataset, key)` — if the question touches a structured
   record (company, profile, product), pull the canonical row.

**STAGE 2 — Index (Vertex AI Search / Discovery Engine):**
6. `index_doc(doc_id, title, content, uri)` for every scraped page.
   Returns `{"status": "indexed", "doc_id": ..., "indexed_at": ...}`.
   This burns GenAI App Builder credits — the durable corpus is the
   submission's "intelligence synthesis" layer.

**STAGE 3 — Synthesize (Vertex AI Search):**
7. `vertex_search(query, top_k=3)` against the indexed corpus.
8. Quote verbatim from the returned snippets in KEY QUOTES.

The agent's answer is a 5-section report (ANSWER / SOURCES / KEY
QUOTES / CONFIDENCE / NEXT STEP). Every number, date, version string,
and quoted line must be copied verbatim from a tool result that flowed
through both stages — the system prompt rejects paraphrasing inside
KEY QUOTES. SOURCES pairs each Bright Data URL with the Vertex Search
doc_id it was indexed as, so the audit trail is end-to-end.

## Built with
python, gemini, gemini-2-5, vertex-ai, vertex-ai-search, discovery-engine,
genai-app-builder, google-cloud-agent-builder, agent-development-kit,
mcp, model-context-protocol, bright-data, bright-data-mcp, web-unlocker,
serp-api, streamlit, google-cloud-run, apache-2

## Try it out
- Code repo: https://github.com/MukundaKatta/gemini-bright-vertex
- Live demo (Cloud Run): pinned after deploy
- Demo video (YouTube unlisted): pinned after upload
