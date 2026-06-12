#!/usr/bin/env python3
"""Two-pass screening: hard keyword exclusion + heuristic relevance scoring."""

import json, re, math

INPUT = "/opt/data/reviews/gold-nanomaterials-review/data/all_papers.json"
OUTPUT_DIR = "/opt/data/reviews/gold-nanomaterials-review/screening"

# REPLACE THESE for your topic
EXCLUDE_TITLE_TERMS = [
    "cancer", "tumor", "tumour", "therapy", "therapeutic", "drug delivery",
    "diagnostic", "imaging", "biosensor", "SERS", "raman", "photothermal therapy",
    "theranostic", "immunoassay", "bioimaging", "antibacterial", "antimicrobial",
    "antifungal", "antibiotic", "cytotoxicity", "toxicity", "biocompatibility",
    "in vivo", "clinical", "patient", "wound healing", "regenerative medicine",
    "vaccine", "gene delivery", "siRNA", "DNA detection", "protein detection",
    "silver nanoparticle", "silver nanowire", "palladium", "platinum", "copper",
    "iron oxide", "quantum dot", "CdSe", "CdTe", "TiO2", "ZnO", "graphene oxide",
    "carbon nanotube", "magnetic nanoparticle",
    "catalysis", "catalytic", "photocatalytic", "electrocatalysis",
    "fuel cell", "battery", "supercapacitor", "solar cell",
    "water splitting", "CO2 reduction", "hydrogen evolution",
    "sensor", "detection of", "colorimetric detection", "fluorescent detection",
    "nanozyme", "nanozymes", "enzyme mimetic",
    "proton therapy", "radiosensitizer",
    "food safety", "heavy metal", "mercury", "pesticide",
    "drug carrier", "targeted delivery",
]

INCLUDE_TITLE_TERMS = [
    "synthesis", "growth mechanism", "seed-mediated", "Turkevich", "Brust",
    "citrate reduction", "nucleation", "shape control", "shape-controlled",
    "anisotropic", "nanorod", "nanocrystal", "nanostar", "nanoprism",
    "growth of gold", "formation of gold", "preparation of gold",
    "colloidal gold", "gold colloid", "LSPR", "surface plasmon",
    "kinetic", "thermodynamic", "Ostwald", "LaMer",
    "size control", "size-dependent", "morphology control",
    "monodisperse", "aspect ratio", "SPR",
    "growth kinetics", "mechanism of", "in situ", "real-time",
    "TEM", "SAXS", "XAS", "X-ray scattering",
    "optical property", "plasmon resonance",
    "size and shape", "size-", "shape-",
]

EXCLUDE_ABSTRACT_KEYWORDS = [
    "drug delivery", "cancer therapy", "photothermal therapy", "biosensor",
    "SERS substrate", "drug carrier", "clinical application",
    "antibacterial activity", "cytotoxicity", "cell imaging",
    "in vivo study", "clinical trial", "theranostic",
]


def score_title(title: str) -> float:
    t = title.lower()
    for term in EXCLUDE_TITLE_TERMS:
        if term.lower() in t:
            return -100.0
    score = 0.0
    if any(term in t for term in ["synthesis", "preparation", "formation", "growth"]):
        if any(term in t for term in ["gold", "au ", "nanoparticle", "nanorod", "nanocrystal", "colloidal"]):
            score += 50
    if "turkevich" in t: score += 80
    if "brust" in t and "schiffrin" in t: score += 75
    if "seed-mediated" in t: score += 60
    if "growth mechanism" in t: score += 50
    if "shape control" in t or "shape-controlled" in t: score += 45
    if "kinetic" in t or "thermodynamic" in t:
        if any(g in t for g in ["gold", "nanoparticle", "nanocrystal", "growth", "synthesis"]):
            score += 40
    if "nucleation" in t: score += 35
    if "anisotropic" in t: score += 30
    if "in situ" in t and any(g in t for g in ["tem", "growth", "nucleation", "gold"]): score += 30
    if "size control" in t or "monodisperse" in t: score += 25
    if "spr" in t or "lspr" in t or "surface plasmon" in t:
        if any(g in t for g in ["gold", "nanoparticle", "nanorod", "size", "shape"]): score += 25
    if "optical" in t and "gold" in t: score += 15
    for term in ["review", "colloidal", "citrate", "mechanism", "tem", "saxs", "xas"]:
        if term in t: score += 10
    return score


def score_abstract(abstract: str) -> float:
    if not abstract or len(abstract) < 10:
        return -10.0
    a = abstract.lower()
    score = 0.0
    for term in EXCLUDE_ABSTRACT_KEYWORDS:
        if term in a: score -= 20
    synthesis_signals = [
        "synthesis", "synthesized", "prepared", "preparation",
        "nucleation", "growth mechanism", "seed-mediated",
        "citrate reduction", "turkevich", "brust",
        "nanoparticle formation", "nanocrystal growth",
        "kinetic control", "thermodynamic control",
        "shape control", "anisotropic growth",
        "in situ tem", "in situ saxs", "in situ xas",
        "real-time monitoring", "real-time observation",
    ]
    for term in synthesis_signals:
        if term in a: score += 5
    if "gold" in a: score += 3
    if "aunp" in a or "au nanoparticle" in a: score += 5
    if "surface plasmon" in a or "lspr" in a or "plasmon resonance" in a: score += 4
    if "optical property" in a or "extinction" in a or "absorption" in a:
        if "gold" in a or "nanoparticle" in a: score += 3
    return min(score, 40.0)


def main():
    with open(INPUT) as f:
        papers = json.load(f)
    print(f"Screening {len(papers)} papers...")

    included, maybes, excluded = [], [], []
    for p in papers:
        title = p.get("title", "") or ""
        abstract = p.get("abstract", "") or ""
        citation = p.get("cited_by_count", 0) or 0
        year = p.get("year") or 0

        t_score = score_title(title)
        if t_score < -50:
            excluded.append({**p, "screen_score": t_score, "screen_label": "exclude"})
            continue

        a_score = score_abstract(abstract)
        cit_bonus = min(10, math.log10(citation + 1) * 3) if citation > 0 else 0

        if year >= 2020: recency = 5
        elif year >= 2015: recency = 3
        elif year >= 2010: recency = 2
        elif year >= 2000: recency = 1
        elif year >= 1950: recency = 0
        else: recency = -5

        total = t_score + a_score + cit_bonus + recency

        entry = {**p, "screen_score": round(total, 1), "screen_label": ""}
        if total >= 40:
            entry["screen_label"] = "include"
            included.append(entry)
        elif total >= 10:
            entry["screen_label"] = "maybe"
            maybes.append(entry)
        else:
            entry["screen_label"] = "exclude"
            excluded.append(entry)

    for lst in [included, maybes, excluded]:
        lst.sort(key=lambda x: -x["screen_score"])

    print(f"Included: {len(included)}\nMaybes:   {len(maybes)}\nExcluded: {len(excluded)}")

    for name, lst in [("included", included), ("maybes", maybes), ("excluded", excluded)]:
        path = f"{OUTPUT_DIR}/{name}_papers.json"
        with open(path, "w") as f:
            json.dump(lst, f, indent=2, ensure_ascii=False)
        print(f"  -> {path}")

    print("\n=== TOP 20 INCLUDED ===")
    for p in included[:20]:
        print(f"  {p['screen_score']:5.1f} | [{p.get('year','?')}] {p['title'][:85]}")

if __name__ == "__main__":
    main()
