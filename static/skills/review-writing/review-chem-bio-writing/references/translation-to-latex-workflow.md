# Chinese Review → English LaTeX Translation Workflow

## ⚠️ Session 2026-06-12 Critical Correction

**The first attempt failed:** one-shot delegate_task produced only 91/367 references.
The user's reaction was strong frustration — the output cut 75% of the content.
**Root cause:** subagents cut scope unless explicitly instructed to preserve all content.

**Lesson:** For massive documents (60K+ Chinese chars, 300+ refs), DO NOT use a single
delegate_task. Use a multi-phase pipeline with independent citation processing.

---

## Completed Example: Gold Nanoparticle Review

**Source:** `gold-nanoparticle-review.md`
- 253KB, 829 lines, 120K characters (≈59K Chinese chars)
- 367 references (numbered [1]–[367])
- 5 major sections, 11 subsections

**Output:** `gold-nanoparticle-review.tex`
- 365KB, 1049 lines
- 5 sections, 11 subsections
- 18 placeholder figures
- 727 superscript citations
- 367 bibitems (211 with full metadata, 156 with DOI links)

---

## Multi-Phase Pipeline

### Phase 0: Assess

```
wc -c -l source.md                           # size + lines
grep -n "^\[" source.md | wc -l             # reference count
grep -n "^#" source.md | head -40           # section structure
```

Calculate: body_lines × ~250 chars/line ≈ total chars.
If >20K chars OR >150 refs → use multi-phase pipeline.
If >100K chars OR >300 refs → MUST use full pipeline below.

### Phase 1: Extract & Build Citation Map

First, extract ALL references and inline citations:

```python
# 1. Parse reference section: [N] DOI:...
ref_dois = {}
for m in re.finditer(r'^\[(\d+)\]\s*DOI:(.*?)$', ref_text, re.MULTILINE):
    ref_dois[int(m.group(1))] = m.group(2).strip()

# 2. Parse inline citations: (Author, Year, *Journal*, DOI:...)
inline_pat = r'\(([^)]+?),\s*(\d{4}),\s*\*([^*]+?)\*,\s*DOI:([^)]+?)\)'
```

Save the DOI-to-reference-number mapping as JSON for later use by translation subagents.

### Phase 2: Resolve DOIs via CrossRef API

For references WITHOUT inline metadata (author, year, journal), resolve via CrossRef:

```python
url = f'https://api.crossref.org/works/{doi}'
# Returns author[], title, container-title, volume, page, year
```

**Rate limit:** ~3 requests/sec — 200 DOIs takes ~1 minute.
**Cache:** Save results to JSON to avoid re-resolving.
**Fallback:** DOIs that fail resolution → use `\href{https://doi.org/{doi}}{doi}` as the bibitem.

**Generation thresholds (2026-06-12 actual):**
- 367 total references
- 99 with inline metadata → formatted from text
- 112 more resolved via CrossRef → 211 with full metadata
- 156 remaining → DOI hyperlink entries

### Phase 3: Split into Translation Chunks

Divide the body text along section boundaries, not arbitrary line counts:

```python
# Sections serve as natural chunk boundaries
sections = [
    (1, 15,    '01_introduction'),
    (16, 61,   '02_spherical'),
    (62, 117,  '03_anisotropic'),
    (118, 163, '04_high_index'),
    (164, 292, '05_nucleation_capping'),
    (293, 366, '06_twinned_insitu'),
    (367, 419, '07_optical_properties'),
    (420, 460, '08_conclusions'),
]
```

Each chunk = one `.md` file in `/tmp/review_chunks/`.

**Chunk size guideline:** Keep each chunk under ~15K chars after translation
to fit in a subagent's context window with room for the DOI mapping.

### Phase 4: Parallel Translation (3 subagents)

Distribute chunks into 3 groups:

| Agent | Chunks | Sections | Expected size |
|-------|--------|----------|--------------|
| A | 01-03 | Introduction + Spherical + Anisotropic | ~70KB |
| B | 04-06 | High-index + Nucleation/Capping + Twinned/In-situ | ~170KB |
| C | 07-08 | Optical Properties + Conclusions | ~70KB |

Each agent receives:
- Its chunk markdown files
- The DOI-to-ref mapping JSON
- Clear instructions: translate to academic English, convert ALL citations,
  add 5-7 placeholder figures, do NOT shorten content

**CRITICAL:** The subagent prompt must explicitly say:
- "Preserve ALL content — do NOT shorten or summarize"
- "Every inline citation MUST be converted — verify none remain in the output"
- "The output should match the original content density exactly"

### Phase 5: Assemble

After all 3 chunks complete:

1. **Read all chunk outputs** — verify each file exists and has reasonable size
2. **Read bibliography** — `\begin{thebibliography}{367}` ... `\end{thebibliography}`
3. **Write preamble** — elsarticle documentclass, packages, frontmatter, abstract
4. **Concatenate:** preamble + chunk_A + chunk_B + chunk_C + bibliography + `\end{document}`

### Phase 6: Structural Verification

```python
# Check begin/end balance
begins = full.count(r'\begin{')
ends = full.count(r'\end{')
assert begins == ends, f"Unbalanced: {begins} begin vs {ends} end"

# Check brace balance
depth = 0
for line in full:
    for c in line:
        if c == '{': depth += 1
        elif c == '}': depth -= 1
assert depth == 0, f"Final brace depth: {depth}"

# Check citation coverage
ref_count = full.count(r'\textsuperscript{[')
```

### Phase 7: Add abstract & frontmatter

Generate abstract from the key themes:
- Hook: gap between synthetic capability and mechanistic understanding
- Roadmap: what each section covers
- Emphasis: unresolved contradictions identified by the review
- Keywords: 6-10 relevant terms

---

## LaTeX Template Requirements

### Preamble
```latex
\documentclass[review]{elsarticle}
\usepackage{amsmath,amssymb}
\usepackage{graphicx}
\usepackage{hyperref}
\usepackage{cite}
\usepackage[margin=2.5cm]{geometry}
\usepackage{float}
\usepackage{booktabs}
\usepackage{array}
```

### Citation Conversion Rules

| Source format | Target format |
|--------------|--------------|
| `(Faraday, 1857, *Phil Trans*, DOI:10.1098/rstl.1857.0011)` | `\textsuperscript{[351]}` |
| `(Turkevich, 1951, DOI:10.1039/DF9511100055)` (no journal) | `\textsuperscript{[267]}` |
| Section `# 2.1 标题` | `\subsection{Title}` |
| Chinese `*Journal Name*` | Remove asterisks, keep as `\emph{Journal}` |
| DOI `10.1002/adma.202102514` | Used only for bibitem lookup key |

### Placeholder Figures

Insert 15-20 figures throughout the document. Each should have:
- A descriptive scientific caption (what data/concept it should show)
- A unique label (`fig:topic-name`)
- Standard size: `width=0.85\textwidth`

**Suggested placement:** 1 figure per major subsection + 2-3 in the conclusions section.

Common figure types:
- Historical timelines
- TEM/SEM images of representative morphologies
- Schematics of synthesis mechanisms
- Optical property tuning maps (LSPR wavelength vs aspect ratio)
- Comparison plots (ensemble vs single-particle)
- Unresolved contradictions diagrams
- Future roadmap / unified framework

### Bibliography Generation

For references with metadata:
```latex
\bibitem{N} Author, A. B.; Author, C. D. Title. \emph{Journal} \textbf{Year}, \emph{Volume}, Pages.
```

For references without metadata (DOI-only):
```latex
\bibitem{N} \href{https://doi.org/{DOI}}{DOI}.
```

**Order:** Must match the citation number (not alphabetical).

---

## Common Pitfalls

### 1. Subagent scope cutting (MOST CRITICAL)
Single-pass delegate_task WILL produce an acceptably-looking but
incomplete result. The subagent will naturally compress content and
select a subset of references to save tokens.
**Fix:** Use multi-phase pipeline with DOI processing first, then
explicit per-chunk instructions to preserve ALL content.

### 2. DOI truncation in source file
The reference section may have truncated DOIs:
```
[1] DOI:10.1002/1521-4095(200109
```
The full DOI is `10.1002/1521-4095(200109)13:18<1389::AID-ADMA1389>3.0.CO;2-F`.
Prefix matching with the first 20 chars of the DOI works for CrossRef lookup.

### 3. Missing journal abbreviations
Inline citations may omit the journal for well-known works:
`(Brust, 1994, DOI:10.1039/C39940000801)` — no journal field.
CrossRef API will supply the journal name.

### 4. Duplicate DOIs
Some references with identical DOIs appear as separate entries
(different citation locations pointing to the same work).
Deduplicate in the bibliography but keep both citation numbers.

### 5. Special characters in LaTeX
Chinese text may contain:
- `&` → `\&`
- `%` → `\%`
- `#` → `\#`
- `_` → `\_`
- `~` → `\textasciitilde{}`
- Em-dashes `—` → `---`
- Chinese quotes `""` → ``` ''`
- Non-breaking hyphens in DOIs

### 6. Section 5/6/7 merging
The Chinese review may have separate sections for "Thermal/Electronic Properties,"
"Unified Structure-Property Map," and "Three Bottlenecks." These often get
merged into a single "Conclusions and Outlook" section in translation.
**Check with the user** if they want sections preserved faithfully or merged.

---

## Verification Checklist

After assembly, verify:

- [ ] `\begin{}` count == `\end{}` count
- [ ] Brace depth == 0 (balanced)
- [ ] Section count matches original (or user-approved structure)
- [ ] Citation count: expected ≈ inline_citations in source
- [ ] Bibliography count matches reference section in source
- [ ] No remaining Chinese characters (grep for 汉字)
- [ ] All DOIs in the source are accounted for
- [ ] All `\textsuperscript{[N]}` have N in 1..max_ref
- [ ] Figure count matches expected (15-20 for major review)
- [ ] Abstract + keywords present
- [ ] `\end{document}` present
- [ ] No `\bibitem{0}` or empty bibitems

### Phase 8: .tex → .docx via pandoc

After generating the .tex file, convert to Word using the pandoc binary:

```bash
# Install pandoc if not present
cd /tmp
curl -sL https://github.com/jgm/pandoc/releases/download/3.6.4/pandoc-3.6.4-linux-amd64.tar.gz -o pandoc.tar.gz
tar xzf pandoc.tar.gz
cp pandoc-3.6.4/bin/pandoc /opt/data/bin/

# Convert
cd /opt/data/reviews/gold-nanoparticle-review/
/opt/data/bin/pandoc gold-nanoparticle-review.tex \
  -f latex -t docx \
  --resource-path=. \
  --wrap=preserve \
  -o gold-nanoparticle-review.docx
```

**pandoc image handling:** If `\includegraphics` references missing files, pandoc warns but still outputs the docx with "[image]" placeholders. For true placeholders, generate 1×1 PNGs for each figure name referenced in the .tex.

### Phase 9: Placeholder Image Generation

```python
import base64, os
# Minimal 1×1 white PNG
png_data = base64.b64decode(
    'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=='
)
figs = ['placeholder-fig-1', 'placeholder-fig-2', 'fig_timeline', ...]
for fig in figs:
    with open(f'/path/to/figures/{fig}.png', 'wb') as f:
        f.write(png_data)

# Update .tex to reference .png
sed -i 's/\.pdf}/.png}/g' review.tex
```

### Phase 10: python-docx Post-Processing (fix pandoc reference blob + preserve formatting)

**Problem:** pandoc concatenates all `thebibliography` entries into ONE paragraph when converting `.tex → .docx`. The output docx has a single massive reference blob paragraph containing all 367 references, completely unreadable.

**Fix:** Replace the blob with individual entries from the pre-built `bibliography.tex` file.

```python
import re
from docx import Document
from docx.shared import Pt, Cm

doc = Document('pandoc-output.docx')

# 1. Find and remove the reference blob paragraph
for i, p in enumerate(doc.paragraphs):
    if re.match(r'^36[0-7]\s+10\.\d+', p.text.strip()):
        p._element.getparent().remove(p._element)
        break

# 2. Read the bibliography.tex file (generated during Phase 2)
with open('/tmp/bibliography.tex') as f:
    bib_text = f.read()

# 3. Extract bibitem entries
bib_entries = []
for m in re.finditer(r'\\bibitem\{(\d+)\}\s*(.+?)(?=\\bibitem\{\d+\}|\Z)', bib_text, re.DOTALL):
    num = int(m.group(1))
    content = m.group(2).strip()
    content = content.replace('\\emph{', '').replace('\\textbf{', '')
    content = re.sub(r'\s+', ' ', content).strip()
    bib_entries.append((num, content))

# 4. Add individual reference entries with hanging indent
for num, content in bib_entries:
    p = doc.add_paragraph()
    run = p.add_run(f'[{num}] ')
    run.font.name = 'Times New Roman'
    run.font.size = Pt(9)
    run = p.add_run(content)
    run.font.name = 'Times New Roman'
    run.font.size = Pt(9)
    p.paragraph_format.space_after = Pt(1)
    p.paragraph_format.first_line_indent = Cm(-0.4)
    p.paragraph_format.left_indent = Cm(0.4)

doc.save('review-formatted.docx')
```

**Citation superscript verification:** After pandoc conversion, verify that `\textsuperscript{[N]}` became Word superscript:

```python
cite_count = sum(
    1 for p in doc.paragraphs 
    for r in p.runs 
    if r.font.superscript and re.search(r'\[\d+\]', r.text)
)
print(f'Superscript citations: {cite_count}')
```

For the gold nanoparticle review (727 citations total): pandoc preserved 699 as superscript. The remaining 28 may be in figure captions or special environments — acceptable for a first pass.

### Key Formatting Principle (User Correction 2026-06-12)

When the user says "保留格式转成word啊", they mean:
1. ✅ Superscript citations must remain superscript — pandoc handles `\textsuperscript{}` natively
2. ✅ Section headings become Heading 1/2/3 in Word — pandoc handles `\section`/`\subsection`
3. ❌ The reference section is a single blob → must post-process to individual entries (Phase 10)
4. ❌ Keywords are embedded in a generic paragraph → should have a "Keywords: " label
5. ✅ Figure captions remain as descriptive text
6. ✅ All body content is preserved (not shortened)

**DO NOT** use python-docx to build the document from scratch when you already have pandoc. Parsing LaTeX back to structured content is fragile and will lose citations, equations, and formatting. Always start with pandoc, then post-process with python-docx for the reference section.

### User's Institutional Defaults (Session 2026-06-12)

- School: School of Chemical Engineering and Technology, Tiangong University, Tianjin 300387, China
- Author name: leave blank `\author[1]{}`
- Email: leave blank `\ead{}`
- Journal preset: Journal of Materials Chemistry A (override as needed)

---

## Session History

- **2026-06-12:** First successful full pipeline run on gold nanoparticle review
  (253KB → 365KB LaTeX, 367 refs, 727 citations, 18 figures)
- **Failure mode 1 attempted:** Single delegate_task → only 91/367 refs produced
- **Failure mode 2 avoided:** Manual translation without DOI resolution →
  156 refs would have no metadata
- **Success achieved via:** Multi-phase + CrossRef + chunked parallel translation
