# Gold Style Writing Conventions

A writing mode for academic reviews that produces dense, flowing prose with embedded journal-abbreviated citations. Named after the gold nanomaterials review (55K Chinese chars, 1,026 DOIs) whose style the user requested for all reviews.

## Style Rules

### Prose Form
- **Flowing academic paragraphs, no bullet-point structure inside sections.** Each paragraph should carry 3-6 data points connected by narrative logic.
- **No structural markers in the output.** No "C:", "E:", "L:", "T:", "关键观察:", "数据来源:", or any other thinking-scaffold artifacts. The structure should be invisible to the reader.
- **Open each section with a concrete data point** (the "钉子开门" technique). First paragraph should contain at least one specific number from a specific paper — not a general statement about the field.
- **Transition naturally** between paragraphs using content-appropriate connectors, not formulaic transitions like "此外" or "另一方面".

### Citation Format
- **Inline (Author, Year, *Journal Abbrev*, DOI:xxx)** — the journal abbreviation is mandatory. It adds density and allows readers to assess source credibility without clicking.
- Examples: `(Sidstedt, 2018, *Anal Bioanal Chem*, DOI:10.1007/s00216-018-0931-z)`, `(Tan, 2024, *J Med Virol*, DOI:10.1002/jmv.29624)`
- Multiple citations in one parenthetical: `(Smithgall, 2020, *J Clin Microbiol*, DOI:10.1128/JCM.00958-20; Basu, 2020, *J Clin Microbiol*, DOI:10.1128/JCM.01136-20)`
- Chinese context: use "等人" not "et al.": `(Tan等人, 2024, *J Med Virol*, DOI:10.1002/jmv.29624)`
- Do NOT use markdown hyperlinks for citations. Plain text is more portable.

### Information Density Rules

| Dimension | Requirement | Example |
|-----------|-------------|---------|
| Per-paragraph data points | ≥3 specific numbers | "470 μM Hb: 410→58 positive rxns; 620 μM: complete inhibition; IC₅₀: 39-470 μM" |
| Comparison scope | Multi-method, not single-method | "LAMP NTC false positive: 5-30%; RPA: >40%; PCR: <1%" |
| Range honesty | Report best-case AND typical | "LAMP LOD: 22-1,000 copies/reaction" not just "22 copies/reaction" |
| Source proximity | Primary data preferred over reviews | "(Tan, 2024, J Med Virol, DOI:...)" over "(Tan, as cited in Kim 2023)" |

### Output Format
- **Markdown (.md) only.** Do not auto-compile to HTML or PDF. The user edits prose directly in markdown.
- Clean enough to copy-paste into a research note or manuscript.

## When to Use This Mode

Trigger: The user explicitly asks for the "金风格" (gold style), or says "像第三个那样写" / "改成金纳米那种风格" / "以第三个为模板".

This mode supersedes C-E-L-T paragraph structure for the final output — C-E-L-T can still be used as a thinking tool during drafting but MUST be stripped before delivery.

## Relationship to C-E-L-T

- C-E-L-T is a THINKING structure for paragraph construction
- Gold style is a WRITING mode for the deliverable
- Use C-E-L-T to organize thoughts during Phase 6 drafting, then strip all markers before delivery
- Gold style prose already has implicit claim (opening sentence) + evidence (data + citations) + limitation (transition sentence) — no need for explicit labels
