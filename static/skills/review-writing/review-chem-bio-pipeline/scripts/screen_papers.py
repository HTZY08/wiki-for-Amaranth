#!/usr/bin/env python3
"""Two-pass heuristic screening for gold nanoparticle synthesis papers.

Pass 1: Hard exclusion (biosensor, drug delivery, SERS, cancer, etc.)
Pass 2: Composite scoring: title signals + abstract signals + citation + recency

Outputs: included_papers.json, maybes_papers.json, excluded_papers.json
"""

import json, re, math

INPUT = "./all_papers.json"
OUTPUT_DIR = "."

# === CUSTOMIZE THESE LISTS FOR YOUR TOPIC ===
# Terms that trigger instant exclusion
EXCLUDE_TITLE_TERMS = [
    "cancer", "tumor", "therapy", "drug delivery", "diagnostic",
    "biosensor", "SERS", "photothermal", "theranostic",
    "antibacterial", "toxicity", "in vivo", "clinical",
    "drug carrier", "nanozyme", "vaccine", "gene delivery",
    "palladium", "platinum", "silver nanoparticle", "iron oxide",
    "quantum dot", "carbon nanotube",
    "catalysis", "fuel cell", "battery", "solar cell",
    "food safety", "pesticide", "heavy metal",
]

# Terms that signal strong relevance
INCLUDE_TITLE_TERMS = [
    "synthesis", "growth mechanism", "seed-mediated", "turkevich", "brust",
    "citrate reduction", "nucleation", "shape control",
    "anisotropic", "nanorod", "nanocrystal",
    "colloidal gold", "lspr", "surface plasmon",
    "kinetic", "thermodynamic", "ostwald",
    "size control", "monodisperse",
    "in situ", "real-time", "saxs", "tem",
]


def score_paper(p: dict) -> dict:
    title = (p.get("title") or "").lower()
    abstract = (p.get("abstract") or "").lower()
    cit = p.get("cited_by_count", 0) or 0
    year = p.get("year") or 0

    # Hard exclusion
    for term in EXCLUDE_TITLE_TERMS:
        if term in title:
            return {**p, "screen_score": -100.0, "screen_label": "exclude"}

    score = 0.0

    # Title signals
    if "synthesis" in title or "preparation" in title or "formation" in title:
        if "gold" in title or "au " in title:
            score += 50
    if "turkevich" in title: score += 80
    if "brust" in title: score += 75
    if "seed-mediated" in title: score += 60
    if "growth mechanism" in title: score += 50
    if "shape control" in title or "shape-controlled" in title: score += 45
    if ("kinetic" in title or "thermodynamic" in title) and ("gold" in title or "nanoparticle" in title): score += 40
    if "nucleation" in title: score += 35
    if "anisotropic" in title: score += 30
    if "in situ" in title and ("tem" in title or "growth" in title): score += 30
    if "spr" in title or "lspr" in title or "surface plasmon" in title: score += 25
    if "size control" in title or "monodisperse" in title: score += 25
    if "optical" in title and "gold" in title: score += 15

    # Abstract signals
    if abstract and len(abstract) > 10:
        for term in ["drug delivery", "cancer therapy", "photothermal", "biosensor", "clinical"]:
            if term in abstract: score -= 20
        for term in ["synthesis", "nucleation", "growth mechanism", "seed-mediated",
                     "citrate reduction", "turkevich", "in situ tem"]:
            if term in abstract: score += 5
        if "gold" in abstract: score += 3
        if "surface plasmon" in abstract or "lspr" in abstract: score += 4

    # Citation bonus
    score += min(10, math.log10(cit + 1) * 3) if cit > 0 else 0

    # Recency
    if year >= 2020: score += 5
    elif year >= 2015: score += 3
    elif year >= 2010: score += 2
    elif year >= 2000: score += 1

    label = "include" if score >= 40 else ("maybe" if score >= 10 else "exclude")
    return {**p, "screen_score": round(score, 1), "screen_label": label}


def main():
    with open(INPUT) as f:
        papers = json.load(f)
    print(f"Screening {len(papers)} papers...")
    scored = [score_paper(p) for p in papers]

    inc = sorted([p for p in scored if p["screen_label"] == "include"], key=lambda x: -x["screen_score"])
    may = sorted([p for p in scored if p["screen_label"] == "maybe"], key=lambda x: -x["screen_score"])
    exc = sorted([p for p in scored if p["screen_label"] == "exclude"], key=lambda x: -x["screen_score"])

    print(f"Included: {len(inc)}")
    print(f"Maybes:   {len(may)}")
    print(f"Excluded: {len(exc)}")

    for name, lst in [("included", inc), ("maybes", may), ("excluded", exc)]:
        with open(f"{OUTPUT_DIR}/{name}_papers.json", "w") as f:
            json.dump(lst, f, indent=2, ensure_ascii=False)
        print(f"  -> {name}_papers.json")

    print("\n=== Top 20 Included ===")
    for p in inc[:20]:
        print(f"  {p['screen_score']:5.1f} | [{p.get('year','?')}] {p['title'][:80]}")


if __name__ == "__main__":
    main()
