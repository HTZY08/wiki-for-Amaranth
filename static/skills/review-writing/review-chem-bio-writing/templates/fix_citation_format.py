#!/usr/bin/env python3
"""
Citation format standardizer for review sections.

Target: (Author, Year, *Journal Abbr*, DOI:10.xxx/xxxxx)
(Author1 & Author2, Year, *Journal Abbr*, DOI:10.xxx/xxxxx)
(Author1 et al, Year, *Journal Abbr*, DOI:10.xxx/xxxxx)

Pitfalls (all verified):
1. YEAR TRUNCATION: [Faraday 1857](doi) → "1857" matches \d+:\d+ page pattern. Fix:
   extract year BEFORE removing page numbers, not after.
2. DOUBLE PARENS: ([text](url)) → ((Author, DOI:...)). Fix: content.replace('((','(')
3. CHINESE BRACKETS: （Willets et al 2005, DOI:[...](url)）. Fix: convert （→( first
4. DOI LOSS: DOI:[text](url) format — must extract DOI from URL after removing
   the DOI: marker, not just drop the marker.
5. 80/20 RULE: Batch scripts cover 80-90%. Always verify 3-5 citations per section
   manually after running. Use patch for edge cases, NOT re-running the script.

USAGE: Copy to review project dir, set SECTIONS_DIR, run.
"""
import re, os, glob

SECTIONS_DIR = "/opt/data/reviews/<project>/sections"
YEAR_RE = re.compile(r'\b(1[6-9]\d{2}|20[0-2]\d)\b')
JOURNAL_RE = re.compile(r'\*([^*]+)\*')

def parse_citation_text(text):
    """Separate author, year, journal — NEVER mix year in author string."""
    text = text.strip()
    year_m = YEAR_RE.search(text)
    year = year_m.group(1) if year_m else ""
    journal_m = JOURNAL_RE.search(text)
    journal = journal_m.group(1).strip() if journal_m else ""
    author = text
    author = JOURNAL_RE.sub('', author)
    if year:
        author = author.replace(year, '', 1)  # remove year safely
    author = re.sub(r'\s*\d+:\d+[-\d,]*\s*', ' ', author)
    author = author.strip().strip(',').strip()
    author = re.sub(r'\s+', ' ', author)
    author = re.sub(r'\s*,\s*', ', ', author)
    author = re.sub(r',\s*$', '', author).strip()
    author = re.sub(r'\s+et\s+al\.?\s*', ' et al', author)
    return author, year, journal

def fix_one_md(match):
    text, url = match.group(1).strip(), match.group(2).strip()
    if not url.startswith("https://doi.org/"):
        return match.group(0)
    doi = "DOI:" + url.replace("https://doi.org/", "").rstrip("/")
    author, year, journal = parse_citation_text(text)
    parts = [author]
    if year: parts.append(year)
    if journal: parts.append(f"*{journal}*")
    parts.append(doi)
    return "(" + ", ".join(parts) + ")"

def fix_chinese_bracket_citations(text):
    """Fix （）with DOI:[...](url) patterns."""
    def handle(m):
        content = m.group(1)
        doi_m = re.search(r'DOI:\[[^\]]*\]\(([^\)]+)\)', content)
        doi_url = doi_m.group(1) if doi_m else ""
        content = re.sub(r',?\s*DOI:\[[^\]]*\]\([^\)]+\)', '', content)
        content = content.replace('**', '')
        author, year, journal = parse_citation_text(content)
        parts = [author]
        if year: parts.append(year)
        if journal: parts.append(f"*{journal}*")
        if doi_url:
            doi = "DOI:" + doi_url.replace("https://doi.org/", "").rstrip("/")
            parts.append(doi)
        return "(" + ", ".join(parts) + ")"
    text = re.sub(r'（([^）]*DOI:\[[^\]]*\]\([^\)]+\)[^）]*)）', handle, text)
    text = re.sub(r'（([^）]{15,})）', lambda m: '(' + m.group(1) + ')', text)
    return text

def process_file(fpath):
    with open(fpath, 'r') as f: content = f.read()
    original = content
    content = fix_chinese_bracket_citations(content)
    md_pat = r'\[([^\]]+)\]\(((https?://doi\.org/[^\)]+))\)'
    content = re.sub(md_pat, fix_one_md, content)
    content = re.sub(r' {2,}', ' ', content)
    content = content.replace('((', '(').replace('))', ')')
    content = re.sub(r'\(\s*\)', '', content)
    if content != original:
        with open(fpath, 'w') as f: f.write(content)
        return True
    return False

def main():
    files = [f for f in sorted(glob.glob(os.path.join(SECTIONS_DIR, "*.md")))
             if not os.path.basename(f).startswith("00-")]
    changed = 0
    for fpath in files:
        if process_file(fpath):
            print(f"  ✓ {os.path.basename(fpath)}")
            changed += 1
    print(f"{changed}/{len(files)} modified. Remember to verify 3-5 citations per section manually.")

if __name__ == "__main__":
    main()
