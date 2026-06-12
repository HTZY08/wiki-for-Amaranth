#!/usr/bin/env python3
"""Compile final corpus: auto-included + top maybes + manual classic additions."""

import json

INPUT_DIR = "/opt/data/reviews/gold-nanomaterials-review"
OUTPUT = f"{INPUT_DIR}/data/final_corpus.json"

# REPLACE THESE for your topic — foundational papers for your field
CLASSICS = [
    {"title": "The color of colloidal gold", "year": 1857, "authors": "Faraday M",
     "journal": "Philosophical Transactions of the Royal Society of London",
     "doi": "10.1098/rstl.1857.0011", "cited_by_count": 2000},

    {"title": "A study of the nucleation and growth processes in the synthesis of colloidal gold",
     "year": 1951, "authors": "Turkevich J, Stevenson PC, Hillier J",
     "journal": "Discussions of the Faraday Society", "doi": "10.1039/DF9511100055",
     "cited_by_count": 8500},

    {"title": "Synthesis of thiol-derivatised gold nanoparticles in a two-phase liquid-liquid system",
     "year": 1994, "authors": "Brust M, Walker M, Bethell D, Schiffrin DJ, Whyman R",
     "journal": "Journal of the Chemical Society, Chemical Communications",
     "doi": "10.1039/C39940000801", "cited_by_count": 18000},

    {"title": "Seeded Growth of Colloidal Gold Nanoparticles",
     "year": 1998, "authors": "Brown KR, Natan MJ",
     "journal": "Langmuir", "doi": "10.1021/la9702799", "cited_by_count": 1500},

    {"title": "Seeded High Yield Synthesis of Short Au Nanorods in Aqueous Solution",
     "year": 1999, "authors": "Jana NR, Gearheart L, Murphy CJ",
     "journal": "Langmuir", "doi": "10.1021/la990556r", "cited_by_count": 2000},

    {"title": "Wet Chemical Synthesis of High Aspect Ratio Cylindrical Gold Nanorods",
     "year": 2001, "authors": "Jana NR, Gearheart L, Murphy CJ",
     "journal": "Journal of Physical Chemistry B", "doi": "10.1021/jp0101864",
     "cited_by_count": 3000},

    {"title": "Chemistry and Properties of Nanocrystals of Different Shapes",
     "year": 2005, "authors": "Burda C, Chen X, Narayanan R, El-Sayed MA",
     "journal": "Chemical Reviews", "doi": "10.1021/cr030063a", "cited_by_count": 4500},

    {"title": "Gold nanoparticles: Assembly, supramolecular chemistry, quantum-size-related properties, and applications toward biology, catalysis, and nanotechnology",
     "year": 2004, "authors": "Daniel MC, Astruc D",
     "journal": "Chemical Reviews", "doi": "10.1021/cr030698+", "cited_by_count": 12000},

    {"title": "Anisotropic gold nanoparticles: Synthesis, properties, applications, and toxicity",
     "year": 2011, "authors": "Dreaden EC, Alkilany AM, Huang X, Murphy CJ, El-Sayed MA",
     "journal": "Chemical Society Reviews", "doi": "10.1039/C0CS00215A",
     "cited_by_count": 2500},
]


def main():
    with open(f"{INPUT_DIR}/included_papers.json") as f:
        included = json.load(f)
    with open(f"{INPUT_DIR}/maybes_papers.json") as f:
        maybes = json.load(f)

    top_maybes = [p for p in maybes if p.get("screen_score", 0) >= 20]
    top_maybes.sort(key=lambda x: -x["screen_score"])

    corpus = []
    seen_dois = set()

    for p in included:
        doi = (p.get("doi") or "").lower().strip().rstrip("/")
        if doi and doi not in seen_dois:
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

    print(f"Final corpus: {len(corpus)} papers")
    by_type = {}
    for p in corpus:
        t = p.get("source_type", "unknown")
        by_type[t] = by_type.get(t, 0) + 1
    for t, c in sorted(by_type.items()):
        print(f"  {t}: {c}")

    years = {}
    for p in corpus:
        y = p.get("year")
        if y:
            years[y] = years.get(y, 0) + 1
    print(f"\nYear distribution:")
    print(f"  pre-2000: {sum(c for y,c in years.items() if y < 2000)}")
    print(f"  2000-2010: {sum(c for y,c in years.items() if 2000 <= y < 2010)}")
    print(f"  2010-2020: {sum(c for y,c in years.items() if 2010 <= y < 2020)}")
    print(f"  2020-2026: {sum(c for y,c in years.items() if y >= 2020)}")


if __name__ == "__main__":
    main()
