# lablab.ai submission package — gemini-bright-vertex

Pre-filled fields for the **Web Data UNLOCKED Hackathon** (Bright Data),
ready to paste into the lablab submission form once the application is
approved and the submission portal opens on **May 25 2026 10:00 AM PDT**
(deadline May 29 2026 5:00 PM PDT).

Event: https://lablab.ai/ai-hackathons/brightdata-ai-agents-web-data-hackathon

## 📋 Basic Information

**Project Title**

    gemini-bright-vertex

**Short Description** (one sentence)

    A two-stage Gemini 2.5 research agent for Track 2 Intelligence
    Synthesis: scrape with Bright Data MCP, index into Vertex AI Search,
    then synthesize answers with verbatim quotes from the indexed corpus.

**Long Description**

    gemini-bright-vertex splits research into three stages so the scraped
    corpus becomes durable, queryable knowledge rather than a one-shot
    answer:

    STAGE 1 — Scrape (Bright Data MCP).
      1. search_engine(query, engine) — SERP API pulls top first-party
         results.
      2. scrape_page(url) — Web Unlocker fetches the rendered page
         (anti-bot bypass, returns unlocked_by_brightdata: true).
      3. extract_text(url, css_selector) — clean text per source.
      4. web_data_lookup(dataset, key) — structured datasets (LinkedIn
         companies, Amazon products, etc.).

    STAGE 2 — Index (Vertex AI Search / Discovery Engine).
      5. index_doc(doc_id, title, content, uri) — push every scraped page
         into a Vertex AI Search data store.

    STAGE 3 — Synthesize.
      6. vertex_search(query, top_k=3) — re-query the indexed corpus and
         answer with verbatim snippets, each tagged with its Bright Data
         source URL plus the Vertex doc_id.

    The Stage 2 split is what makes this a Track 2 (Intelligence
    Synthesis) submission instead of a plain scraper: future research
    questions hit the cached corpus first, only fetching new Bright Data
    pages when the index doesn't already have the answer.

    The agent answers in 5 labeled sections:

      ANSWER:     synthesized from vertex_search hits, every
                  number/date/version verbatim from tools.
      SOURCES:    bulleted Bright Data URLs each paired with their
                  Vertex Search doc_id.
      KEY QUOTES: 2-4 verbatim quotes pulled from vertex_search hits;
                  the same string lives in scrape_page output too, so
                  judges can audit byte-for-byte through both stages.
      CONFIDENCE: high / medium / low, grounded in source quality plus
                  cross-doc agreement plus the Bright Data unlock flag.
      NEXT STEP:  one concrete follow-up vertex_search query against the
                  same indexed corpus (no re-scrape needed).

    Strict rule: every quantitative claim must flow through both stages.
    The two-stage contract is pinned by
    test_scrape_index_search_chain_is_consistent.

    Built on Google Cloud Agent Builder (ADK) with Gemini 2.5 Flash on
    Vertex AI, wired to Bright Data's MCP server and Vertex AI Search.
    The repo ships a local stub (canned SERPs + scraped pages + in-memory
    Discovery Engine, no Bright Data account or GCP project required)
    plus two env-var swaps to the real @brightdata/mcp + real Discovery
    Engine data store.

**Technology & Category Tags**

    python, gemini, gemini-2-5, vertex-ai, vertex-ai-search,
    discovery-engine, google-cloud-agent-builder, agent-development-kit,
    mcp, model-context-protocol, bright-data, bright-data-mcp,
    web-unlocker, serp-api, structured-datasets, intelligence-synthesis,
    streamlit, google-cloud-run, apache-2

## 📸 Cover Image and Presentation

**Cover Image**

    /Users/ubl/gemini-bright-vertex/.video-build/cover.png
    (1200x675, 42.5 KB, PNG)

**Video Presentation**

    https://youtu.be/OjcFb89eloY
    (1m51s — intro slide + ~32s real Cloud Run footage + outro slide,
     unlisted, hosted on YouTube)

**Slide Presentation**

    Skipped — the demo video carries the same content.

## 💻 App Hosting & Code Repository

**Public GitHub Repository**

    https://github.com/MukundaKatta/gemini-bright-vertex

**Demo Application Platform**

    Google Cloud Run (us-central1)

**Application URL**

    https://gemini-bright-vertex-1029931682737.us-central1.run.app

## ✅ Bright Data Requirement Check

> Bright Data Requirement: Your submission must demonstrably use at least
> one Bright Data product.

The agent's MCP tool surface is a 1:1 match for the official
`@brightdata/mcp` npm package and uses four Bright Data products:

  - SERP API           — `search_engine(query, engine)`
  - Web Unlocker       — `scrape_page(url)` (returns `unlocked_by_brightdata: true`)
  - extract / scrape   — `extract_text(url, css_selector)` for clean text
  - Structured Datasets — `web_data_lookup(dataset, key)` (LinkedIn companies, etc.)

The demo video shows all four firing through the deployed Streamlit
dashboard, with `unlocked_by_brightdata: true` printed in the event trace
on the verbatim Claude 4.7 release-notes scrape.

## ⏱️ Submission timeline

  - **2026-05-18** — repo + Cloud Run + YouTube + cover all built (today)
  - **2026-05-XX** — lablab moderator approves application (currently
                     "Waiting for approval")
  - **2026-05-25 10:00 AM PDT** — submission portal opens
  - **2026-05-29 05:00 PM PDT** — submission deadline
  - **2026-05-30** — onsite Build Day (SF, The Web Data Loft)
  - **2026-05-31** — Demos & Awards (online + onsite)
