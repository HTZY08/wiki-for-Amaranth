#!/usr/bin/env python3
"""Sub-topic precision search: OpenAlex + PubMed across multiple targeted queries.

Used when PISMA's flat queries return too much noise for niche topics.
Decompose your field into 8-12 sub-topics, each as a separate query.
"""

import json, time, sys, re, os
from urllib.request import Request, urlopen
from urllib.parse import quote

CACHE_DIR = "/opt/data/review_cache"
OUTPUT = "./all_papers.json"

# === EXAMPLE QUERIES (gold nanoparticle synthesis) ===
# Replace with your own sub-topic queries
QUERIES = [
    ("turkevich_citrate",
     'title_and_abstract.search:"Turkevich method" AND gold',
     "Turkevich method gold citrate",
     1950, 2026),
    ("brust_schiffrin",
     'title_and_abstract.search:"Brust-Schiffrin" AND gold',
     "Brust Schiffrin gold nanoparticle",
     1990, 2026),
    ("seed_mediated_growth",
     'title_and_abstract.search:"seed-mediated" AND gold AND nanorod',
     "seed-mediated gold nanorod growth",
     1995, 2026),
]


def openalex_search(query: str, max_results: int = 200) -> list[dict]:
    results = []
    cursor = "*"
    base = "https://api.openalex.org/works"
    params = f"?filter={quote(query)}&per_page=50&sort=relevance_score:desc&cursor="
    attempt = 0
    while cursor and len(results) < max_results and attempt < 20:
        url = f"{base}{params}{cursor}"
        try:
            req = Request(url, headers={"User-Agent": "ReviewBot/1.0"})
            resp = urlopen(req, timeout=30)
            data = json.loads(resp.read())
            if not data or "results" not in data:
                break
            works = data.get("results", [])
            if not works:
                break
            for w in works:
                doi = (w.get("doi") or "").lower().strip()
                results.append({
                    "id": w.get("id"),
                    "title": w.get("title", ""),
                    "abstract": _parse_abstract(w.get("abstract_inverted_index", "")),
                    "year": w.get("publication_year"),
                    "doi": doi,
                    "source": "openalex",
                    "cited_by_count": w.get("cited_by_count", 0),
                    "authors": [a.get("author", {}).get("display_name", "")
                                for a in w.get("authorships", [])[:5]],
                    "venue": (w.get("primary_location") or {}).get("source", {}).get("display_name", ""),
                })
            cursor = data.get("meta", {}).get("next_cursor")
            attempt += 1
            time.sleep(0.2)
        except Exception as e:
            print(f"  OA error: {e}", file=sys.stderr)
            break
    return results


def pubmed_search(query: str, max_results: int = 100) -> list[dict]:
    results = []
    esearch_url = (f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
                   f"?db=pubmed&term={quote(query)}&retmax={max_results}&retmode=json&sort=relevance")
    try:
        req = Request(esearch_url, headers={"User-Agent": "ReviewBot/1.0"})
        resp = urlopen(req, timeout=30)
        search_data = json.loads(resp.read())
    except Exception as e:
        print(f"  PM error: {e}", file=sys.stderr)
        return results

    ids = search_data.get("esearchresult", {}).get("idlist", [])
    if not ids:
        return results

    for i in range(0, len(ids), 50):
        batch = ids[i:i + 50]
        efetch_url = (f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
                      f"?db=pubmed&id={','.join(batch)}&retmode=xml&rettype=abstract")
        try:
            req = Request(efetch_url, headers={"User-Agent": "ReviewBot/1.0"})
            resp = urlopen(req, timeout=30)
            xml = resp.read().decode("utf-8")
            for art in xml.split("<PubmedArticle>")[1:]:
                title = _xml_tag(art, "ArticleTitle")
                abstract = _xml_tag(art, "AbstractText")
                year = _xml_tag(art, "PubDate")
                doi = _xml_tag(art, "ELocationID")
                if doi and "doi" not in doi[:6].lower():
                    doi = ""
                year_num = int(re.search(r"(\d{4})", year).group(1)) if year else None
                results.append({
                    "title": title.strip(),
                    "abstract": abstract.strip(),
                    "year": year_num,
                    "doi": f"https://doi.org/{doi.strip()}" if doi.strip() else "",
                    "source": "pubmed",
                    "id": _xml_tag(art, "PMID"),
                    "cited_by_count": 0,
                    "authors": [],
                })
            time.sleep(0.4)
        except Exception as e:
            print(f"  PM error: {e}", file=sys.stderr)
            time.sleep(1)
    return results


def _parse_abstract(inv) -> str:
    if isinstance(inv, str):
        return inv
    if not isinstance(inv, dict):
        return ""
    wps = [(pos, word) for word, positions in inv.items() for pos in positions]
    wps.sort()
    return " ".join(w for _, w in wps)


def _xml_tag(text: str, tag: str) -> str:
    parts = text.split(f"<{tag}>")
    if len(parts) < 2:
        return ""
    return parts[1].split(f"</{tag}>")[0].strip()


def deduplicate(papers: list[dict]) -> list[dict]:
    seen_dois, seen_titles = set(), set()
    unique = []
    for p in papers:
        doi = p.get("doi", "").strip().lower().rstrip("/")
        if doi and doi in seen_dois:
            continue
        title = re.sub(r"[^a-z0-9]", "", p.get("title", "").lower())[:80]
        if title and title in seen_titles:
            continue
        if doi:
            seen_dois.add(doi)
        if title:
            seen_titles.add(title)
        unique.append(p)
    return unique


def main():
    os.makedirs(CACHE_DIR, exist_ok=True)
    all_papers = []
    print(f"Searching {len(QUERIES)} sub-topics across OpenAlex + PubMed...")
    for label, oa_q, pm_q, _, _ in QUERIES:
        print(f"[{label}] OA...", end=" ")
        oa = openalex_search(oa_q)
        print(f"{len(oa)}  PM...", end=" ")
        pm = pubmed_search(pm_q)
        print(f"{len(pm)}")
        all_papers.extend(oa + pm)
        time.sleep(0.5)
    print(f"\nBefore dedup: {len(all_papers)}")
    all_papers = deduplicate(all_papers)
    print(f"After dedup:  {len(all_papers)}")
    with open(OUTPUT, "w") as f:
        json.dump(all_papers, f, indent=2, ensure_ascii=False)
    print(f"Saved to {OUTPUT}")


if __name__ == "__main__":
    main()
