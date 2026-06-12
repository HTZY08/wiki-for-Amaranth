# PISMA Operational Notes — from 2026-06-03 test run

## Installation

```bash
git clone https://github.com/CarinaSchoppe/PISMA-Literature-Review-Pipeline-Automation-Tool.git /opt/data/pisma
cd /opt/data/pisma
uv pip install -e .[dev]
# If scikit-learn fails to import:
uv pip install scikit-learn --force-reinstall
```

Must use the Hermes venv Python (`source /opt/hermes/.venv/bin/activate` before running). System `/usr/bin/python3` will fail on missing packages.

## Config File Format

PISMA accepts a JSON config via `--config-file`. Critical format rules:

- `search_keywords`, `inclusion_criteria`, `exclusion_criteria` must be **JSON arrays** (`[...]`), not comma-separated strings. The CLI parser passes strings to Pydantic which expects lists.
- `topic_prefilter_keywords` is a single string with semicolons: `"keyword|weight|threshold; keyword2|1.5|70"`
- Boolean flags in CLI: `--feature-enabled` / `--no-feature-enabled`
- API rate limits go under `api_settings: {}` (see fields in config.py lines 72-84)
- `citation_snowballing_enabled` (not `citation_snowballing`) in JSON

## S2 API Key — 2026 Update: Effectively Unobtainable

**The S2 API key registration process is broken.** The "Request an API Key" link on the API page is a same-page anchor that does not trigger any email or form submission. Multiple GitHub issues confirm the same (SakanaAI/AI-Scientist #104: "applied 5 days ago, no response").

**Without a key, S2 is essentially unusable.** Even at 0.1 req/s, every request after the first returns 429. The shared pool (originally stated as 1000 req/s globally) is completely exhausted by automated tooling in 2026.

**Impact on PISMA:** Enabling `semantic_scholar_enabled: true` without a key wastes 1-2 minutes per query on exponential backoff retries that all fail with 429. Total pipeline runtime increases ~2-3 minutes with zero results from S2.

**Recommendation:** Set `semantic_scholar_enabled: false` in PISMA config. The remaining sources (OpenAlex, PubMed, Crossref, Unpaywall) produce sufficient results for a review. Verified: a gold nanomaterials search with S2 disabled produced 106 publications from non-S2 sources in ~3 minutes.

If you absolutely need S2's citation graph data, consider using OpenAlex's `cited_by_api_url` and `related_works` fields as a substitute.

## Topic Prefilter

Default model: `BAAI/bge-small-en-v1.5` (~33MB safetensors). Loads on CUDA automatically if available. First run downloads from HuggingFace.

Strongly recommended to set `topic_prefilter_keywords` with explicit weight|threshold triplets. These define what "relevant" means. Example:
```
"gold nanoparticle|1.5|70; gold nanorod|1.5|70; anisotropic growth|1.8|75"
```

## Rate Limiting

PISMA has built-in rate limiting per source via env vars:
- `OPENALEX_CALLS_PER_SECOND=5.0`
- `SEMANTIC_SCHOLAR_CALLS_PER_SECOND=0.3` (be conservative without key!)
- `CROSSREF_CALLS_PER_SECOND=2.5`
- `PUBMED_CALLS_PER_SECOND=3.0`
- `ARXIV_CALLS_PER_SECOND=0.34`

S2 also has dedicated retry settings:
```
semantic_scholar_retry_attempts: 5
semantic_scholar_retry_backoff_strategy: "exponential"
semantic_scholar_retry_backoff_base_seconds: 5.0
```

## Performance

| Stage | Time (106 papers, S2 disabled) | Notes |
|-------|-------------------------------|-------|
| Topic prefilter model load | ~20s first run | Cached after; fails if transformers/torch missing |
| Discovery (3 sources, S2 disabled) | ~3 min | S2+ArXiv disabled → pipeline completes cleanly |
| Discovery (4 sources, S2 enabled, no key) | ~5+ min | S2 adds 2-3 min of useless retries (all 429) |
| Citation expansion | ~6s per paper | Linear in paper count |
| Dedup + output | <1s | |

## Output Files

All written to `results/` in the PISMA working directory:
- `papers.csv` — full dump
- `included_papers.csv` / `excluded_papers.csv` — prefilter-split
- `top_papers.json` — ranked
- `citation_graph.json` — for Phase 5 ORGANIZE
- `prisma_flow.md` — PRISMA count for Phase 8
- `review_summary.md` — narrative summary
- `pipeline.log` — full run log

## Relevance Threshold — Critical Tuning Parameter

**Default `relevance_threshold` is 70.0** (config.py line 204). In `decision_mode: strict` (also the default), any paper scoring below 70 is excluded regardless of topic match quality.

This is the #1 reason PISMA produces `included_papers.csv` with only headers and no rows. The composite score combines topic match (40%), methodology (20%), theoretical contribution (15%), recency (10%), and citation count (15%) minus penalties. Even papers with "gold nanoparticle" in the title score 50-60 because they're penalized for low theoretical contribution or methodology classification.

**Fix:** Add to your JSON config:
```json
{
  "relevance_threshold": 50,
  "decision_mode": "triage"
}
```
- `decision_mode: strict` → binary include/exclude at threshold
- `decision_mode: triage` → uses `maybe_threshold_margin` (±10) for three-way classification

Also lower keyword thresholds in `topic_prefilter_keywords`:
```json
"topic_prefilter_keywords": "gold nanoparticle|1.5|60; gold nanorod|1.5|60; Turkevich|1.8|65; ..."
```
Each triplet is `keyword|weight|threshold` — the third number is the per-keyword match threshold.

## AI Screening — What Actually Runs

When no LLM client is configured (no OpenAI/Gemini/Ollama API key), PISMA falls back to **heuristic screening** via `RelevanceScorer.deep_score()` (relevance_scoring.py). This is a weighted formula, NOT an LLM:

```
topic_score (40%) = 0.65 × keyword_topic_score + 0.35 × semantic_topic_score
methodology_score (20%) = 90 if classified else 35
theoretical_contribution (15%) = 15 × theory terms detected
recency (10%) = position in year range
citation_count (15%) = log-scaled
final = weighted_sum - exclusion_penalties - banned_penalties
```

**Key flags that control screening behavior:**

| Config Field | Default | Effect |
|-------------|---------|--------|
| `ai_evaluation_enabled` | `true` | Must be `true` for screening to run at all. When false → `collect` mode, no screening. |
| `topic_prefilter_enabled` | `true` | Enables the BGE-small semantic model. Without it, screening is purely keyword-based. |
| `topic_prefilter_filter_low_relevance` | `false` | When `true`, uses semantic similarity thresholds to filter. When `false`, only keyword-based filtering applies. |
| `topic_prefilter_high_threshold` | `0.7` | Cosine similarity threshold (0-1). 0.7 is strict for BGE-small. |
| `topic_prefilter_low_threshold` | `0.3` | Below this → auto-exclude. Only active if `filter_low_relevance: true`. |
| `relevance_threshold` | `70.0` | Composite score threshold (0-100). Papers below this → exclude in strict mode. |
| `decision_mode` | `strict` | `strict` → binary include/exclude. `triage` → three-way with margin. |

### Hard Exclusions (Always Applied)

These run BEFORE topic prefilter and ignore all thresholds:

| Source | What triggers it |
|--------|-----------------|
| `banned_topics` | Keywords in title+abstract → hard exclude |
| `excluded_title_terms` | Keywords in title only → hard exclude |
| `exclusion_criteria` | Keywords → soft penalty (-20 each) |

If a paper matches a banned topic or excluded title term, it's excluded regardless of score.

### Performance on GPU

| Hardware | Papers/sec | Notes |
|----------|-----------|-------|
| RTX 5070 Ti (12GB) | ~20 papers/s | BGE-small loads in ~5s, screening 95 papers in ~5s |
| CPU only | ~2-3 papers/s | Use only if GPU unavailable |

## The `--active` Flag for Hermes Environment

In the Hermes Docker environment, the active venv is `/opt/hermes/.venv`. When running `uv run` inside a project directory (like PISMA's), uv creates its own `.venv` by default. Use `--active` to force uv to use the Hermes venv instead:

```bash
cd /opt/data/pisma
uv run --active python main.py --config gold_review_config.json
```

Without `--active`, uv creates a fresh virtual environment, installing all dependencies again. With `--active`, it uses the already-configured Hermes venv where packages like `transformers`, `torch`, and `accelerate` are installed.

## Known Issues (Verified 2026-06)

- **S2 without API key = completely unusable.** Do not enable `semantic_scholar_enabled` unless you have a working key. Every request returns 429 regardless of rate limit settings. See "S2 API Key — 2026 Update" above.
- arXiv also rate-limited through mihomo proxy. May or may not work depending on proxy node. Disable if not needed.
- Google Scholar HTML scraping is extremely slow (0.2 req/s). Disable for automated runs.
- The `from_cli` method passes string args to Pydantic list fields — JSON config file is the reliable path.
- Topic prefilter fails if `transformers` and `torch` are not installed. Pipeline will still run but screening falls back to keyword-only heuristic.
- CrossRef and Unpaywall are the most reliable sources — no API key needed, no proxy issues.
