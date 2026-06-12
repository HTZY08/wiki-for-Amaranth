#!/usr/bin/env python3
"""Compile final corpus from auto-screened papers + manually added classics.

Merges included_papers.json + top maybes + CLASSICS list.
Handles DOI dedup across all sets. Outputs sorted final_corpus.json.
"""

import json

INPUT_INCLUDED = "./included_papers.json"
INPUT_MAYBES = "./maybes_papers.json"
OUTPUT = "./final_corpus.json"

# === EDIT THIS LIST for your topic's foundational papers ===
# Add the absolute classics that automated search doesn't capture
CLASSICS = [
    {"title": "The color of colloidal gold", "year": 1857,
     "authors": "Faraday M", "journal": "Phil Trans R Soc Lond",
     "doi": "10.1098/rstl.1857.0011", "cited_by_count": 2000},

    {"title": "A study of the nucleation and growth processes in the synthesis of colloidal gold",
     "year": 1951, "authors": "Turkevich J, Stevenson PC, Hillier J",
     "journal": "Discussions Faraday Soc", "doi": "10.1039/DF9511100055",
     "cited_by_count": 8500},

    {"title": "Synthesis of thiol-derivatised gold nanoparticles in a two-phase liquid-liquid system",
     "year": 1994, "authors": "Brust M et al.",
     "journal": "J Chem Soc Chem Commun", "doi": "10.1039/C39940000801",
     "cited_by_count": 18000},
]


def main():
    with open(INPUT_INCLUDED) as f: included = json.load(f)
    with open(INPUT_MAYBES) as f: maybes = json.load(f)

    top_maybes = sorted([p for p in maybes if p.get("screen_score", 0) >= 20],
                         key=lambda x: -x["screen_score"])

    corpus = []
    seen_dois = set()

    for p in included:
        doi = (p.get("doi") or "").lower().strip().rstrip("/")
        if doi:
            seen_dois.add(doi)
        corpus.append({**p, "source_type": "auto_included"})

    for p in top_maybes:
        doi = (p.get("doi") or "").lower().strip().rstrip("/")
        if doi and doi in seen_dois:
            continue
        if doi:
            seen_dois.add(doi)
        corpus.append({**p, "source_type": "auto_maybe"})

    for c in CLASSICS:
        doi = c.get("doi", "").lower().strip().rstrip("/")
        if doi and doi in seen_dois:
            continue
        if doi:
            seen_dois.add(doi)
        corpus.append({**c, "source": "manual", "source_type": "manual_classic"})

    def sort_key(p):
        if p.get("source_type") == "manual_classic":
            return (0, -(p.get("cited_by_count", 0) or 0))
        return (1, -(p.get("screen_score", 0) or 0))

    corpus.sort(key=sort_key)

    with open(OUTPUT, "w") as f:
        json.dump(corpus, f, indent=2, ensure_ascii=False)

    by_type = {}
    for p in corpus:
        t = p.get("source_type", "unknown")
        by_type[t] = by_type.get(t, 0) + 1

    print(f"Final corpus: {len(corpus)} papers")
    for t, c in sorted(by_type.items()):
        print(f"  {t}: {c}")
    print(f"\nYear distribution:")
    years = [p.get("year", 0) or 0 for p in corpus]
    print(f"  <2000: {sum(1 for y in years if 0 < y < 2000)}")
    print(f"  2000-2010: {sum(1 for y in years if 2000 <= y < 2010)}")
    print(f"  2010-2020: {sum(1 for y in years if 2010 <= y < 2020)}")
    print(f"  2020+: {sum(1 for y in years if y >= 2020)}")


if __name__ == "__main__":
    main()
