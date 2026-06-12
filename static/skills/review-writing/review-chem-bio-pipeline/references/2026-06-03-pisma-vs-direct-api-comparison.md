# PISMA vs Direct API Search — Comparison Data (2026-06-03)

## Context

Gold nanomaterials review — "synthesis, growth mechanism and intrinsic properties"
Niche topic within nanomaterial chemistry. Exclusion criteria: biosensing, drug delivery, SERS, therapy applications.

## Results Comparison

| Metric | PISMA (3 sources) | Direct API (11 sub-topics) |
|--------|-------------------|---------------------------|
| Sources used | OpenAlex, PubMed, CrossRef | OpenAlex + PubMed |
| Total before dedup | 106 | 1,779 |
| After dedup | 106 | 1,479 |
| After screening | 95 (all excluded at default 70 threshold) | 731 included + 264 maybes |
| Final corpus | 0 usable | 855 (731 auto + 115 top maybes + 9 classics) |
| Pipeline runtime | ~3 min + 5s screening | ~5 min search + 30s screening |

## Key Learnings

### 1. PISMA's Query Construction is the Problem

PISMA concatenates `research_topic + search_keywords + boolean_operators` into a single query per source. For the gold review, the S2 query was:

```
Gold nanomaterials — synthesis, growth mechanism... ("gold nanoparticle" OR...) AND (synthesis OR growth...)
  gold nanoparticle synthesis Turkevich method Brust-Schiffrin seed-mediated gold nanorod...
```

This is treated as a single bag-of-words query. It returns papers that mention *any* of these terms, dominated by high-citation papers in adjacent fields (SERS at 3701 citations, drug delivery at 2117 citations).

### 2. Sub-Topic Decomposition Fixes This

Instead of one broad query, decompose into 11 targeted queries, each searching a specific mechanism or method:

| Sub-topic | Query | Papers |
|-----------|-------|--------|
| Turkevich/citrate | "Turkevich method" AND gold | 59 |
| Brust-Schiffrin | "Brust-Schiffrin" AND gold | 41 |
| Seed-mediated growth | "seed-mediated" AND gold AND nanorod | 288 |
| Nucleation/kinetics | (nucleation OR kinetics) AND gold nanoparticle | 153 |
| Anisotropic growth | "anisotropic growth" AND gold | 180 |
| Shape control | "shape control" AND gold | 113 |
| Growth mechanism | "growth mechanism" gold nanoparticle | 231 |
| In situ characterization | in situ TEM gold nanoparticle growth | 253 |
| Thermodynamic/kinetic control | (thermodynamic* OR kinetic*) gold nanoparticle | 231 |
| SPR/LSPR properties | SPR LSPR gold nanoparticle size shape | 34 |
| Classical nucleation theory | "classical nucleation theory" gold | 185 |

### 3. User Validation

User explicitly agreed this approach is correct for niche fields:
> "对，我觉得这是可以的，在应对小众研究领域这是必要的"

### 4. Heuristic Screening Thresholds

Default exclude threshold was calibrated too high. Real distribution of scores:
- 2 papers scored > 60
- 14 papers scored > 50
- 45 papers scored > 40
- 51 papers scored > 30

With `relevance_threshold: 50` in PISMA: 14 papers included, but 9 of those were noise.
With custom heuristic at threshold 40: 731 included, ~500 of which are genuinely relevant.

### 5. Manual Classics Are Essential

PISMA's year range (default 2021-2026) misses ALL foundational papers. Required additions:
- Faraday 1857 — first colloidal gold
- Turkevich 1951 — citrate reduction method
- Brust 1994 — two-phase synthesis
- Natan 1998 — seeded growth
- Murphy 1999/2001 — seed-mediated AuNRs
- El-Sayed 2005 — shape-dependent properties
- Astruc 2004 — comprehensive review
- Dreaden 2011 — anisotropic applications

These must be added manually regardless of search strategy.

### 6. Pipeline Scripts

Created and stored under `scripts/`:

```
search_papers.py     → all_papers.json (1,779 before dedup)
screen_papers.py     → {included,maybes,excluded}_papers.json
compile_corpus.py    → final_corpus.json (855 papers)
```

All URLs and absolute paths are relative-friendly (set `INPUT_INCLUDED`, etc. when running).
