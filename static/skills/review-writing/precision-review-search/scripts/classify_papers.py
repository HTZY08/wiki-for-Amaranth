#!/usr/bin/env python3
"""Phase 4: Classify final corpus into thematic buckets → feeds Phase 5 outline.

Usage: edit BUCKETS list for your review's sections, then run.
Output: classification.json (papers with bucket assignments + bucket summary)
"""

import json, re

INPUT = "data/final_corpus.json"          # From Step 6
OUTPUT = "data/classification.json"       # Feeds Phase 5

# === DEFINE YOUR BUCKETS HERE ===
# Each bucket maps to one review section.
# title_keywords: words that strongly signal this bucket (title match = 20pts)
# abstract_signals: weaker signals (abstract match = 5pts)
# weight: 0.5 (peripheral) to 1.0 (core topic)

BUCKETS = [
    {
        "id": "section_placeholder",
        "section": "X.X Example Section",
        "title_keywords": ["example", "placeholder"],
        "abstract_signals": ["example", "placeholder"],
        "weight": 1.0,
    },
]


def classify_paper(paper: dict) -> list[tuple]:
    """Return list of (bucket_id, score, section_name) sorted by score desc."""
    title = (paper.get("title") or "").lower()
    abstract = (paper.get("abstract") or "").lower()
    combined = f"{title} {abstract}"

    scores = []
    for bucket in BUCKETS:
        score = 0.0
        for kw in bucket["title_keywords"]:
            if kw.lower() in title:
                score += 20 * bucket["weight"]
            elif kw.lower() in combined:
                score += 8 * bucket["weight"]
        for sig in bucket["abstract_signals"]:
            if sig.lower() in abstract:
                score += 5 * bucket["weight"]
        if score > 0:
            scores.append((bucket["id"], score, bucket["section"]))
    return sorted(scores, key=lambda x: -x[1])


def main():
    import os, sys
    base = os.path.dirname(os.path.abspath(__file__))
    input_path = os.path.join(base, "..", INPUT)
    output_path = os.path.join(base, "..", OUTPUT)

    if not os.path.exists(input_path):
        print(f"Error: {input_path} not found. Run compile_corpus.py first.")
        sys.exit(1)

    with open(input_path) as f:
        papers = json.load(f)

    bucket_counts = {b["id"]: {"count": 0, "papers": [], "section": b["section"]}
                     for b in BUCKETS}
    bucket_counts["unclassified"] = {"count": 0, "papers": [], "section": "Unclassified"}

    for p in papers:
        scores = classify_paper(p)
        if scores:
            primary = scores[0]
            p["classification"] = {
                "primary_bucket": primary[0],
                "primary_score": round(primary[1], 1),
                "primary_section": primary[2],
                "all_buckets": [(s[0], round(s[1], 1)) for s in scores],
            }
            if primary[0] in bucket_counts:
                bucket_counts[primary[0]]["count"] += 1
                bucket_counts[primary[0]]["papers"].append(p["title"][:80])
        else:
            p["classification"] = {"primary_bucket": "unclassified", "primary_score": 0,
                                   "primary_section": "Unclassified"}
            bucket_counts["unclassified"]["count"] += 1
            bucket_counts["unclassified"]["papers"].append(p["title"][:80])

    output = {"papers": papers, "bucket_summary": {}, "total": len(papers)}
    for bid, info in sorted(bucket_counts.items()):
        output["bucket_summary"][bid] = {
            "section": info["section"],
            "count": info["count"],
            "sample_papers": info["papers"][:5],
        }

    with open(output_path, "w") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"Classified {len(papers)} papers into "
          f"{len([b for b in bucket_counts.values() if b['count'] > 0])} buckets")
    for bid, info in sorted(bucket_counts.items(), key=lambda x: -x[1]["count"]):
        if info["count"] > 0:
            print(f"  {bid:35s} {info['count']:4d}  {info['section'][:45]}")
    print(f"\nOutput: {output_path}")


if __name__ == "__main__":
    main()
