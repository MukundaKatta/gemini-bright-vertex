from gemini_bright_vertex.mcp_stub import (
    _SERPS,
    _SCRAPED_PAGES,
    _DATASETS,
    _VERTEX_CORPUS,
    _reset_corpus,
    doc_id_for_url,
    extract_text_response,
    index_doc_response,
    scrape_page_response,
    search_engine_response,
    vertex_search_response,
    web_data_lookup_response,
)


# ---------------------------------------------------------------------------
# STAGE 1: Bright Data SERP / scrape / extract / dataset
# ---------------------------------------------------------------------------


def test_serps_seeded():
    assert "Anthropic Claude 4.7 release notes" in _SERPS
    assert len(_SERPS["Anthropic Claude 4.7 release notes"]) == 5


def test_search_engine_known_query():
    payload = search_engine_response("Anthropic Claude 4.7 release notes")
    assert payload["engine"] == "google"
    assert payload["result_count"] == 5
    titles = [r["title"] for r in payload["results"]]
    assert any("4.7" in t for t in titles)


def test_search_engine_unknown_query_fallback():
    payload = search_engine_response("some unrelated query")
    assert payload["result_count"] == 1
    assert "stub" in payload["results"][0]["title"].lower()


def test_scrape_page_known_url_carries_22_percent():
    payload = scrape_page_response(
        "https://www.anthropic.com/news/claude-4-7-release-notes"
    )
    assert payload["status"] == 200
    assert payload["unlocked_by_brightdata"] is True
    assert "Claude 4.7" in payload["text_excerpt"]
    # The 22% latency drop is the load-bearing verbatim claim.
    assert "22%" in payload["text_excerpt"]


def test_extract_text_requires_prior_scrape():
    payload = extract_text_response("https://example.com/never-fetched")
    assert "error" in payload


def test_web_data_lookup_returns_anthropic_record():
    payload = web_data_lookup_response("linkedin_company", "Anthropic")
    assert payload["count"] == 1
    rec = payload["records"][0]
    assert rec["company"] == "Anthropic"
    assert rec["employee_count"] == 1842


# ---------------------------------------------------------------------------
# STAGE 2: Vertex AI Search ingest
# ---------------------------------------------------------------------------


def test_index_doc_returns_indexed_status():
    _reset_corpus()
    out = index_doc_response(
        doc_id="doc_test_1",
        title="Test page",
        content="some verbatim content with the 22% claim.",
        uri="https://example.com/test",
    )
    assert out["status"] == "indexed"
    assert out["doc_id"] == "doc_test_1"
    assert out["indexed_at"].startswith("2026-")
    assert out["corpus_size"] == 1


def test_index_doc_accumulates_corpus():
    _reset_corpus()
    index_doc_response("d1", "T1", "c1", "u1")
    index_doc_response("d2", "T2", "c2", "u2")
    assert len(_VERTEX_CORPUS) == 2
    assert {"d1", "d2"}.issubset(_VERTEX_CORPUS.keys())


# ---------------------------------------------------------------------------
# STAGE 3: Vertex AI Search retrieval
# ---------------------------------------------------------------------------


def test_vertex_search_canned_followup_returns_top_k():
    _reset_corpus()
    # Seed the corpus the way the agent would in Stage 2.
    for url in (
        "https://www.anthropic.com/news/claude-4-7-release-notes",
        "https://www.anthropic.com/news/api-changelog-may-2026",
        "https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching",
    ):
        scrape = scrape_page_response(url)
        index_doc_response(
            doc_id=doc_id_for_url(url),
            title=scrape["title"],
            content=scrape["text_excerpt"],
            uri=url,
        )
    out = vertex_search_response("summarize the API changes", top_k=3)
    assert out["result_count"] == 3
    doc_ids = [h["doc_id"] for h in out["results"]]
    assert "doc_anthropic_changelog" in doc_ids
    assert "doc_claude_47_release" in doc_ids
    assert "doc_prompt_caching" in doc_ids


def test_vertex_search_substring_fallback_for_unknown_query():
    _reset_corpus()
    index_doc_response("d1", "Files API", "Files API is now generally available.", "u1")
    index_doc_response("d2", "Other",     "Totally unrelated content here.",       "u2")
    out = vertex_search_response("files api", top_k=5)
    assert out["result_count"] >= 1
    assert out["results"][0]["doc_id"] == "d1"


def test_vertex_search_empty_corpus_returns_zero_hits():
    _reset_corpus()
    out = vertex_search_response("anything", top_k=3)
    assert out["result_count"] == 0
    assert out["corpus_size"] == 0


# ---------------------------------------------------------------------------
# End-to-end chain: Stage 1 content survives Stage 2 → 3 unchanged.
# ---------------------------------------------------------------------------


def test_scrape_index_search_chain_is_consistent():
    """The Track 2 killer move: scraped content survives Stage 1 -> 2 -> 3 unchanged.

    SERP picks the top URL. scrape_page returns text containing "22%".
    index_doc ingests that exact text. vertex_search returns the same
    doc with the same text intact, so the agent can quote verbatim and
    the user can audit byte-for-byte.
    """
    _reset_corpus()

    # STAGE 1: SERP → scrape.
    serp = search_engine_response("Anthropic Claude 4.7 release notes")
    top_url = serp["results"][0]["url"]
    assert top_url == "https://www.anthropic.com/news/claude-4-7-release-notes"
    scrape = scrape_page_response(top_url)
    stage1_content = scrape["text_excerpt"]
    assert "22%" in stage1_content
    assert scrape["unlocked_by_brightdata"] is True

    # Also index the other two top results so vertex_search has the full corpus.
    for url in (
        "https://www.anthropic.com/news/api-changelog-may-2026",
        "https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching",
    ):
        sc = scrape_page_response(url)
        index_doc_response(
            doc_id=doc_id_for_url(url),
            title=sc["title"],
            content=sc["text_excerpt"],
            uri=url,
        )

    # STAGE 2: index the top doc with its scraped content verbatim.
    doc_id = doc_id_for_url(top_url)
    indexed = index_doc_response(
        doc_id=doc_id,
        title=scrape["title"],
        content=stage1_content,
        uri=top_url,
    )
    assert indexed["status"] == "indexed"
    assert indexed["doc_id"] == doc_id

    # STAGE 3: ask the follow-up; the same doc + content must come back.
    out = vertex_search_response("summarize the API changes", top_k=3)
    matching = [h for h in out["results"] if h["doc_id"] == doc_id]
    assert len(matching) == 1, "indexed doc must show up in vertex_search results"
    hit = matching[0]

    # The contract: byte-for-byte content survives all three stages.
    assert hit["content"] == stage1_content
    assert "22%" in hit["content"]
    assert hit["uri"] == top_url
