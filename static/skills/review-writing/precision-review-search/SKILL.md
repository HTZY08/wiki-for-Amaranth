---
name: precision-review-search
description: >-
  Precision search and screening pipeline for systematic reviews in
  chemistry/materials — when broad database searches (OpenAlex/PubMed/CrossRef)
  return too much noise. Instead of relying on a single pipeline tool (PISMA),
  this skill: (1) decomposes the topic into 10-15 precise sub-topic queries,
  (2) searches OpenAlex + PubMed directly per sub-topic, (3) deduplicates,
  (4) screens with a two-pass keyword+heuristic filter, (5) manually adds
  foundational/classic papers that automated searches miss,
  (6) compiles a final corpus ready for writing.
  Produces 600-1500 papers instead of PISMA's typical ~100.
---

# Precision Review Search Pipeline

## When to use this instead of PISMA

PISMA is great when you have a fairly narrow, focused query where its topic
prefilter and LLM screening work well. But for broad topics where:
- The search query is generic ("gold nanoparticle synthesis")
- Most papers found are about *applications* not *mechanisms*
- You need papers from 1951-2026 (PISMA defaults to ~5 year range)
- The per-source limit (500) is too small

→ Use this precision search + screening pipeline instead.

## Pipeline Overview

```\\nStep 1 ─ DECOMPOSE       Break topic into 10-15 precise sub-topic queries\\nStep 2 ─ SEARCH          For each sub-topic: OpenAlex + PubMed, 1951-2026\\nStep 3 ─ DEDUP           Cross-source deduplication by DOI + normalized title\\nStep 4 ─ SCREEN          Two-pass: hard keyword exclusion → heuristic scoring\\nStep 5 ─ CURATE          Manual addition of classic/foundational papers\\nStep 6 ─ COMPILE         Final corpus\\nStep 7 ─ CLASSIFY        Assign papers to thematic section buckets\\n```

## Corpus Sizing by Review Type

The `final_corpus.json` size directly determines how many citations the final review can carry. Aim for:

| Review Type | Corpus Size | Target Citations in Final Draft | Citation-to-Corpus Ratio |
|-------------|:-----------:|:-------------------------------:|:------------------------:|
| Mini Review | 50-200 | 50-200 | >80% |
| Big Review | 600-1,500 | 250-400 | ~30-50% |
| Mega Review | 1,500-3,000+ | 400-800+ | ~25-35% |

**Warning:** A corpus of 800 papers does NOT automatically produce a well-cited review. Writing typically uses only 10-15% of the corpus in the first pass. The remaining 85-90% must be actively mined and injected in subsequent expansion passes. This is the most common gap between "corpus compiled" and "review written."

After compilation, run the citation density tracking script (see `review-chem-bio-writing` → `references/citation-density-tracking.md`) to measure utilization. If any section has used <20% of its available sub-topic papers, that section needs expansion, not revision.

## Step 1 ─ Decompose the Topic

Do NOT use a single broad query. Break the topic into 10-15 precise sub-topics,
each targeting a specific mechanism, method, or property.

Example for "gold nanomaterial synthesis and growth mechanism":

| # | Sub-topic | Query Focus |
|---|-----------|-------------|
| 1 | Turkevich method | citrate reduction, nucleation mechanism |
| 2 | Brust-Schiffrin | two-phase synthesis, thiol stabilization |
| 3 | Seed-mediated growth | nanorod/anisotropic, Murphy/El-Sayed |
| 4 | Nucleation kinetics | classical vs non-classical, two-step |
| 5 | Anisotropic growth | facet-dependent, capping agent, twin |
| 6 | Shape control | nanocubes, nanostars, nanoprisms |
| 7 | TKD control | thermodynamic vs kinetic, overgrowth |
| 8 | Growth mechanisms | in situ, real-time monitoring |
| 9 | In situ characterization | TEM, SAXS, XAS during growth |
| 10 | SPR/LSPR | size-shape-property relationship |
| 11 | CNT/Ostwald | classical nucleation theory, LaMer |
| 12 | Synthesis scale-up | monodispersity, batch reproducibility |

## Step 2 ─ Search Script

Use the reference script `scripts/search_papers.py`. It:
- Takes a list of (label, openalex_query, pubmed_query, year_start, year_end)
- Searches OpenAlex with cursor-based pagination (200 per sub-topic)
- Searches PubMed via E-utilities (ESearch + EFetch, 100 per sub-topic)
- Deduplicates by DOI + normalized title
- Saves to `all_papers.json`

### Key parameters to adjust per topic:

```python
# OpenAlex filter syntax
"title_and_abstract.search:(nucleation OR kinetics) AND (\"gold nanoparticle\" OR \"gold nanocrystal\")"

# PubMed query
"gold nanoparticle nucleation kinetics synthesis"
```

### Rate limits (hard-coded in script):
- OpenAlex: 0.2s delay (5 req/s, but $1/day free budget)
- PubMed: 0.4s delay (3 req/s without key)

### Output:
```json
[
  {
    "id": "https://openalex.org/W...",
    "title": "...",
    "abstract": "...",
    "year": 2023,
    "doi": "https://doi.org/...",
    "source": "openalex",
    "cited_by_count": 145,
    "authors": ["Author A", "Author B"],
    "venue": "Journal Name",
    "query_label": "turkevich_citrate"
  },
  ...
]
```

## Step 3 ─ Dedup

Built into the search script. DOI matching (preferred) + title normalization as fallback.

## Step 4 ─ Screen (Two-Pass)

Use the reference script `scripts/screen_papers.py`.

### Pass 1: Hard Title Exclusion

Papers with any of these in the title are immediately excluded (`score = -100`):
- Application keywords: cancer, therapy, drug delivery, biosensor, SERS,
  antibacterial, cytotoxicity, in vivo, clinical, vaccine, gene delivery
- Non-gold materials: silver, palladium, platinum, iron oxide, quantum dot,
  TiO2, ZnO, graphene oxide, carbon nanotube
- Non-synthesis focus: catalysis, sensor, detection of, nanozyme,
  food safety, heavy metal, pesticide, drug carrier

### Pass 2: Heuristic Scoring

Score = `title_score + abstract_score + citation_bonus + recency_bonus`

| Component | Range | Description |
|-----------|-------|-------------|
| Title score | -100 to +100 | Strong signals: Turkevich +80, Brust +75, seed-mediated +60, growth mechanism +50, kinetic/thermodynamic +40, nucleation +35 |
| Abstract score | -20 to +40 | Penalty for application language, bonus for synthesis/nucleation/growth terms |
| Citation bonus | 0 to +10 | log10(citations+1) × 3, capped |
| Recency bonus | -5 to +5 | 2020+ = 5, 2015-2019 = 3, 2010-2014 = 2, 2000-2009 = 1, classics = 0, unknown = -5 |

### Output tiers:

| Score | Label | Action |
|-------|-------|--------|
| ≥ 40 | include | Core corpus |
| 10-39 | maybe | Review manually |
| < 10 | exclude | Discard |

Typical results: 1479 raw → 731 included + 264 maybes + 484 excluded

## Step 5 ─ Manual Classic Addition

Automated search misses foundational papers because:
- They're too old (Faraday 1857, Turkevich 1951 are not in OpenAlex/PubMed)
- They don't match search filters (DOI not indexed)
- They're known by name not by keyword match

### Standard classics for gold nanomaterial reviews:

| Paper | Year | Why essential |
|-------|------|---------------|
| Faraday — "The color of colloidal gold" | 1857 | First AuNP report |
| Turkevich — citrate reduction method | 1951 | The method everyone uses |
| Frens — size control by citrate/Au ratio | 1973 | Size tuning |
| Brust-Schiffrin — two-phase synthesis | 1994 | Thiol-stabilized AuNPs |
| Natan — seeded growth | 1998 | Seed method origin |
| Jana/Murphy — seed-mediated AuNRs | 1999-2001 | Anisotropic growth |
| El-Sayed — shape-dependent SPR | 2003 | Fundamental property link |
| Burda/El-Sayed — nanocrystal shape chemistry | 2005 | Comprehensive shape review |
| Sau/Murphy — anisotropic assembly | 2005 | Assembly + properties |

Add these to `scripts/compile_corpus.py` as a CLASSICS list.

## Step 6 ─ Compile + Output → PDF Delivery

Script: `scripts/compile_corpus.py`

### Final delivery: markdown + PDF

After writing all sections and running mandatory Post-Processing (strip C-E-L-T labels, de-AI):
- **Markdown** stays in `sections/` for computer-side editing and journal submission conversion
- **PDF** is generated for clean WeChat delivery (no encoding issues)

See `review-chem-bio-writing` → Phase 8 for the build workflow. Novels/daily reads skip the PDF step.

Output: `final_corpus.json` — typically 800-900 papers.

### Writing in Chinese

When writing sections from the compiled corpus, default to Chinese.
See the full "Writing in Chinese (Default)" section below for style rules
and the "Post-Processing: Cleanup" section for the mandatory stripping pass.

## Citation Snowballing (Optional Extension)

After compiling the final corpus, classify papers into section-level buckets.
This maps papers to review sections before writing begins.

Script: `scripts/classify_papers.py`

**How it works:**
- Define N buckets in the BUCKETS list, each with `title_keywords` (strong signals),
  `abstract_signals` (weaker), and `weight` (core = 1.0, peripheral = 0.5-0.8)
- Each paper gets scored against all buckets; highest-scoring bucket wins
- Unclassified papers fall into a catch-all bucket for manual distribution

**Typical output (calibrated on gold nanomaterials, 855 papers):**

| Bucket | Papers | Becomes Section |
|--------|--------|----------------|
| Seed-mediated synthesis | 216 | §2.2 Anisotropic Growth |
| Nucleation mechanisms | 129 | §3.1 Nucleation |
| Optical properties | 127 | §4.2 Size-Shape LSPR |
| In situ characterization | 81 | §3.4 In Situ |
| Capping agents | 78 | §3.2 Capping Agents |
| Turkevich/Brust | 61 | §2.1 Spherical |
| Scalability | 29 | §2.4 Scalability |
| Twin vs single-crystal | 23 | §3.3 Crystal Growth |
| Smaller buckets | 38 | §§2.3, 4.1, 4.3, 5, 6 |
| Unclassified | 73 | Distribute manually |

The classification JSON is the bridge between this skill (search/screening)
and `review-chem-bio-pipeline` Phase 5 (outline building → writing).

## Writing in Chinese (Default)

**All sections MUST be written in Chinese.** This is the user's explicit preference
("用中文写，便于看"). The user reads Chinese academic text faster and more naturally.

- Write in formal Chinese academic style — concise, precise, neutral
- Preserve all English technical terms (SPR, AuNP, TEM, etc.) as-is; do not translate
- Place DOIs inline using markdown: `([Author Year](https://doi.org/10.XXXX/XXXXXX))`
- Use **C-E-L-T paragraph structure (Claim → Evidence → Limitation → Transition) INTERNALLY only** — this framework guides paragraph flow but its labels (`**C：**`, `**E：**`, `**L：**`, `**T：**`) must NEVER appear in the visible output
- Keep paragraphs focused: one claim per paragraph, support with DOI'd evidence

## Post-Processing: Cleanup (Mandatory)

After writing all sections, run a mandatory cleanup pass on every file:

### Step 1: Strip Framework Labels

Search for and remove all `**C：**`, `**E：**`, `**L：**`, `**T：**` markers from the body text.
The text that follows each label should remain — just drop the bold label prefix.
Verify the paragraphs flow naturally after removal (no orphaned sentences).

```python
import re
content = re.sub(r'\*\*[CELT]：\*\*\s*', '', content)
content = re.sub(r'\n{3,}', '\n\n', content)
```

### Step 2: De-AI the Language

Load and apply `review-chem-bio-writing` (which in turn delegates to `chinese-thesis-language-editor` as the authoritative Chinese academic language style source). See that skill's language section for the full rule set.

Key targets for the cleanup pass:
- Remove judgment markers: don't write "这表明/这意味着/这说明/这反映了" — let data speak for itself
- Kill "每个实践者都学过/众所周知" style openings — start with the fact, not the framing
- Remove formulaic transitions — facts should drive the narrative, not transition sentences
- Then run `chinese-thesis-language-editor` for the full 18-rule check

### Step 3: Verify Flow

Read through each section one more time with labels removed. If a paragraph
used to start with `**C：**`, its topic sentence should still read naturally
as the start of a paragraph. If it doesn't, add bridging words.

## Phase 6 Integration: Writing with Inline DOIs

The final corpus feeds directly into writing. Each paper in `final_corpus.json` carries its DOI. Follow the writing and post-processing steps above, then Phase 7-8 (figures, verification). Include the DOI inline with every citation using markdown link format:

```markdown
([Author Year](https://doi.org/10.XXXX/XXXXXX))
```

This preserves the machine-readable citation for downstream bibliography generation while keeping the text self-contained.

## File Structure

Project files go under `/opt/data/reviews/<project-name>/`:

```
/opt/data/reviews/<project-name>/
  ├── scripts/
  │   ├── search_papers.py         # Step 2: Multi-sub-topic search
  │   ├── screen_papers.py         # Step 4: Two-pass screening
  │   └── compile_corpus.py        # Steps 5-6: Classic addition + compilation
  ├── data/
  │   ├── all_papers.json          # Raw collected papers
  │   └── final_corpus.json        # Final curated corpus
  ├── screening/
  │   ├── included_papers.json     # Pass 2 output: included
  │   ├── maybes_papers.json       # Pass 2 output: borderline
  │   └── excluded_papers.json     # Pass 2 output: excluded
  ├── sections/                    # Phase 6: drafted section files
  └── cache/                       # API response cache
```
```

## Adapting to Other Topics

Change three things to adapt this pipeline:

### 1. Sub-topic queries (search_papers.py)
Replace the QUERIES list. Each entry:
```python
("label", "openalex_title_abstract_query", "pubmed_query", year_start, year_end)
```

### 2. Exclusion/inclusion keywords (screen_papers.py)
Update:
- `EXCLUDE_TITLE_TERMS` — anything off-topic
- `INCLUDE_TITLE_TERMS` — strong on-topic signals
- `EXCLUDE_ABSTRACT_KEYWORDS` — abstract-level noise

### 3. Classic papers (compile_corpus.py)
Update the `CLASSICS` list with the field's foundational papers.

## Pitfalls

1. **Don't be too aggressive with exclusion terms.** A paper about "gold
   nanoparticle synthesis for cancer therapy" might have great mechanistic
   content in the first half — the title-based exclusion will lose it.
   Better to include and let abstract-level scoring sort it out.

2. **OpenAlex has ~3-5 day indexing delay.** Hot-off-the-press papers
   (last week) won't appear. Use PubMed first for latest papers.

3. **PubMed abstracts are sometimes truncated.** The EFetch API returns
   the first ~2500 chars. Some longer abstracts get cut. This affects
   abstract-based scoring.

4. **Classic papers may have broken DOIs.** Faraday 1857's DOI differs
   between OpenAlex and CrossRef. Always include title + year as fallback.

5. **The $1/day OpenAlex budget runs out fast.** 100K calls ≈ $1.
   At 11 queries × 200 results each, we use ~2200 calls. Fine for a
   single review but don't iterate unnecessarily.

6. **Forgetting to strip C-E-L-T labels is the most common writing-phase error.** The cleanup pass is mandatory. See `review-chem-bio-writing` Phase 7 for the full protocol.

7. **De-AI the Chinese prose.** The authoritative language style source is `chinese-thesis-language-editor`, not `humanizer` or `user-writing-style` (those are for creative/historical writing, not reviews). Load `review-chem-bio-writing` → Phase 7 → Step 2 for the procedure.

8. **Corpus under-utilization is the #1 gap between a 'corpus compiled' and 'review written'.** The user expects ALL usable papers in the corpus to be cited — not just 10-15%. A corpus of 800 papers should produce 250-800 citations depending on review type, not 60-80. Active mining of unused papers from the corpus is mandatory after the first writing pass, not optional. See `review-chem-bio-writing` → Phase 6 → 大规模引用注入 for the workflow.

## Comparison: PISMA vs Precision Search

| Aspect | PISMA | Precision Search |
|--------|-------|------------------|
| Best for | Narrow, well-defined topics | Broad, noisy topics |
| Sources | 8+ databases | OpenAlex + PubMed (intentional) |
| Typical yield | 50-200 papers | 600-1500 papers |
| Time window | Configurable, default ~5yr | Full 1951-2026 |
| Classic papers | Missed (too old) | Added manually |
| Screening | BGE topic prefilter + LLM | Keyword-based heuristic |
| Screening speed | ~5s for 100 papers (GPU) | <1s for 1500 papers |
| False positive rate | Low (with tuned threshold) | Moderate (compensate with volume) |
| Needs S2 API key | Yes (broken in 2026) | No |

This skill is the search/screening counterpart to `review-chem-bio-writing` — use `precision-review-search` for Phases 2-4, then hand the final corpus to `review-chem-bio-writing` for Phases 5-8 (write, post-process, figures, verify).

## Project Organization Convention

Keep skill and project files separate:

```
/opt/data/
  ├── skills/research/precision-review-search/   ← Methodology + script templates
  └── reviews/<project-name>/                      ← Project data (one project per review)
      ├── scripts/     ← Copied from skill, then customized
      ├── data/        ← all_papers.json, final_corpus.json
      ├── screening/   ← included/maybe/excluded splits
      └── cache/       ← API response cache
```
