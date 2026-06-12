# Fast-Track Workflow: Thesis Chapter → Review

> When the user already has a thesis Chapter 1 with ~100-150 curated references covering 3-5 years, the full Phase 2-4 (Search + Dedup + Classify) pipeline is overkill. Use this fast-track instead.

## Trigger Condition

Use this workflow when ALL of the following are true:
- The source material is a thesis Chapter 1 (or equivalent comprehensive literature review)
- The thesis references cover the core literature (within ~2 years of submission)
- The review aims to reorganize + reframe existing content, not to discover entirely new literature
- The user confirms they want to "拆成综述" (decompose into reviews)

## Fast-Track Pipeline

```
Phase 0 ─ DECOMPOSE (from main skill SKILL.md)
  → Map thesis sections → identify 2-3 separable reviews
  → Allocate thesis references per review
  → Confirm split with user BEFORE proposing your own structure

Phase 1 ─ SCOPE (use full Phase 1 from SKILL.md)
  → Five questions + intellectual genealogy + argument map
  → This phase is NOT skippable — the review needs its own critical claim

Phase 1.5 ─ SUPPLEMENTAL SEARCH (replaces Phase 2-4)
  → Do NOT run PISMA or full database search
  → Use targeted Perplexity / AnySearch / web_search for:
    - Foundational papers older than the thesis's time window
    - Very recent papers (post-thesis-finalization, last 6-12 months)
    - One cross-check: verify there's no major review on the same topic
      published after the thesis was completed
  → 3-5 targeted queries, not 50+

Phase 5 ─ OUTLINE (use full Phase 5 from SKILL.md)
  → Map thesis section content to new review structure
  → Each section gets a C-E-L-T skeleton

Phase 6 ─ WRITE (use full Phase 6 from SKILL.md)
  → Write sections from thesis content with C-E-L-T restructuring
  → Keep thesis DOI references; verify DOIs resolve during write
  → Add supplemental papers inline where needed

Phase 6.5 ─ QUICK PDF (replaces Phase 7 figures)
  → Generate a readable draft PDF from markdown (see below)
  → Figures are placeholder descriptions for now
  → This is a submission-ready draft, not final camera-ready
```

## Phase 1.5: Supplemental Search Protocol

### What to Search For

| Gap Type | Query Pattern | Tool |
|----------|--------------|------|
| Foundational classics | "[concept] first discovered/reported" | Perplexity or web_search |
| Post-thesis (last 6mo) | "[topic] 2025 2026 review" | Perplexity (better recency) |
| Overlap check | "[exact review title] review" | web_search — check no identical review exists |
| Missing modality | "[method] AND [topic] 2024 2025" | Perplexity |

### What NOT to Do
- Do NOT run PISMA — thesis references already filtered for relevance
- Do NOT run 50+ database queries — you'll waste time rediscovering the thesis
- Do NOT cite AI search results without DOI verification

## Phase 6.5: Quick PDF Generation

### Prerequisites
```bash
uv run --with weasyprint --with markdown-it-py python3 build_pdf.py
```

### Build Script Template

Copy from `review-chem-bio-writing/skills/templates/build_chinese_pdf.py`, adapting:
- `BASE` → project directory path
- `SECTIONS` → ordered list of section files
- `TITLE` / `SUBTITLE` → review title

### When to Skip This Phase
- If the user only wants draft markdown sections (not a PDF)
- If the user plans to submit to a journal that requires a specific template

## Pitfalls

1. **Thesis content is not review content.** A thesis Chapter 1 describes "what is known"; a review argues "why it matters and where we should go." Every paragraph must be rewritten with a C-E-L-T structure, not copy-pasted.
2. **Old references.** If the thesis is >1 year old, up to 30% of its references may be outdated. The supplemental search should catch the most important recent work.
3. **Over-familiarity.** Writing from your own thesis risks missing important papers that contradict your argument. The supplemental search should explicitly look for dissenting views.
4. **Artificial splitting.** A thesis chapter often interweaves topics. Don't force a clean split that breaks the narrative. If two candidate reviews share >30% of references, they should be one review.
