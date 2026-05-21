"""gemini-bright-vertex dashboard (two-stage)."""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from gemini_bright_vertex.runner import ask  # noqa: E402


st.set_page_config(page_title="gemini-bright-vertex", layout="wide", page_icon=":mag_right:")
st.title("gemini-bright-vertex")
st.caption(
    "Bright Data scrape → Vertex AI Search index → synthesized answer. "
    "Two-stage research agent on Google Cloud Agent Builder (ADK) + "
    "Gemini 2.5. Quotes verbatim. Apache 2.0."
)

with st.sidebar:
    st.header("Ask the web (two-stage)")
    question = st.text_area(
        "Your research question",
        value="Summarize the Anthropic Claude 4.7 API changes from announcements in May 2026",
        height=140,
    )
    model = st.selectbox(
        "Gemini model",
        options=["gemini-2.5-flash", "gemini-2.5-pro", "gemini-2.5-flash-lite"],
        index=0,
    )
    stub = st.toggle(
        "Use stub Bright Data + Vertex Search",
        value=True,
        help="On = local stub with canned SERPs + scraped pages + in-memory Vertex Search corpus. "
             "Off = real Bright Data (BRIGHTDATA_API_TOKEN) + real Discovery Engine data store.",
    )
    run = st.button("Run two-stage research", type="primary", use_container_width=True)
    st.divider()
    st.caption(
        f"Project: `{os.getenv('GOOGLE_CLOUD_PROJECT', 'not-set')}`  "
        f"Vertex AI: `{os.getenv('GOOGLE_GENAI_USE_VERTEXAI', 'true')}`"
    )

st.markdown(
    """
The agent walks two stages of tools to answer research questions:

**STAGE 1 — Bright Data MCP (scrape):**
- **search_engine** for the SERP (Google / Bing / DuckDuckGo)
- **scrape_page** for the Web Unlocker fetch (anti-bot bypass + rendered HTML)
- **extract_text** to pull clean text from a previously-scraped page
- **web_data_lookup** for Bright Data's structured datasets

**STAGE 2 — Vertex AI Search / Discovery Engine (index + answer):**
- **index_doc** to ingest every scraped page into the search corpus
- **vertex_search** to answer the user's follow-up question with verbatim quotes
"""
)

if run:
    with st.status("Running two-stage agent on Vertex AI Gemini...", expanded=True) as status:
        t0 = time.perf_counter()
        try:
            resp = ask(question, stub=stub, model=model)
        except Exception as e:  # pragma: no cover
            status.update(label=f"Error: {e}", state="error")
            st.exception(e)
            st.stop()
        elapsed = (time.perf_counter() - t0) * 1000
        status.update(label=f"Done in {elapsed:.0f} ms", state="complete")

    st.subheader("Research answer")
    st.markdown(resp.final_text or "_(no final response)_")

    with st.expander(f"Agent event trace ({len(resp.events)} events)"):
        for i, ev in enumerate(resp.events):
            st.markdown(f"**{i}.** author=`{ev.get('author')}` final=`{ev.get('is_final')}`")
            text = ev.get("text") or ""
            if text:
                st.code(text[:1500], language=None)
else:
    st.info("Use the sidebar to fire a two-stage research question. Stage 1 scrapes through Bright Data; Stage 2 indexes into Vertex AI Search and answers.")
