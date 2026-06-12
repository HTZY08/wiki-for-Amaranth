#!/usr/bin/env python3
"""Precision search for gold nanoparticle synthesis & mechanism papers.

Searches OpenAlex + PubMed for each sub-topic query, collects metadata,
deduplicates by DOI, saves to JSON for review.
"""

import json, time, sys, re
from urllib.request import Request, urlopen
from urllib.parse import quote
from urllib.error import HTTPError

# NOTE: Before running, set OUTPUT to your project path:
# /opt/data/reviews/<your-project>/data/all_papers.json
OUTPUT = "/opt/data/reviews/gold-nanomaterials-review/data/all_papers.json"

# === SUB-TOPIC QUERIES ===
# Each: (label, openalex_query, pubmed_query, year_start, year_end)
# REPLACE THESE for your topic
QUERIES = [
    ("turkevich_citrate",
     'title_and_abstract.search:"Turkevich method" AND (gold OR colloidal gold OR citrate reduction)',
     "Turkevich method gold citrate", 1951, 2026),

    ("brust_schiffrin",
     'title_and_abstract.search:"Brust-Schiffrin" AND gold',
     "Brust Schiffrin gold nanoparticle", 1994, 2026),

    ("seed_mediated_growth",
     'title_and_abstract.search:"seed-mediated" AND gold AND (nanorod OR nanoparticle OR growth)',
     "seed-mediated gold nanorod growth", 2000, 2026),

    ("nucleation_kinetics",
     'title_and_abstract.search:(nucleation OR kinetics) AND ("gold nanoparticle" OR "gold nanocrystal") AND (synthesis OR formation OR growth)',
     "gold nanoparticle nucleation kinetics synthesis", 1951, 2026),

    ("anisotropic_growth",
     'title_and_abstract.search:"anisotropic growth" AND gold AND (nanoparticle OR nanorod OR nanocrystal)',
     "anisotropic growth gold nanoparticle", 2000, 2026),

    ("shape_control",
     'title_and_abstract.search:("shape control" OR "shape-controlled") AND gold AND (nanoparticle OR nanocrystal OR nanorod OR nanostar OR nanoprism)',
     "shape control gold nanoparticle", 2000, 2026),

    ("thermodynamic_kinetic_control",
     'title_and_abstract.search:(thermodynamic* OR kinetic*) AND (control OR growth) AND ("gold nanoparticle" OR "gold nanocrystal") AND (synthesis OR formation)',
     "thermodynamic kinetic control gold nanoparticle synthesis", 2000, 2026),

    ("growth_mechanism",
     'title_and_abstract.search:("growth mechanism" AND ("gold nanoparticle" OR "gold nanorod" OR "gold nanocrystal"))',
     "growth mechanism gold nanoparticle", 1951, 2026),

    ("in_situ_characterization",
     'title_and_abstract.search:("in situ" OR "in-situ" OR "real-time") AND (TEM OR microscopy OR SAXS OR XAS) AND ("gold nanoparticle" OR "gold nanorod" OR "gold nanocrystal") AND (growth OR nucleation OR formation)',
     "in situ TEM gold nanoparticle growth", 2000, 2026),

    ("spr_lspr",
     'title_and_abstract.search:(SPR OR LSPR OR "surface plasmon") AND ("gold nanoparticle" OR "gold nanorod") AND (size OR shape OR aspect ratio OR optical property)',
     "SPR LSPR gold nanoparticle size shape optical", 1990, 2026),

    ("classical_nucleation",
     'title_and_abstract.search:("classical nucleation theory" OR "LaMer" OR "Ostwald ripening" OR "two-step nucleation") AND (gold OR nanoparticle OR nanocrystal)',
     "classical nucleation theory gold nanoparticle", 1950, 2026),
]


def openalex_search(query: str, per_page: int = 50, max_results: int = 200) -> list[dict]:
    results = []
    cursor = "*"
    base = "https://api.openalex.org/works"
    params = f"?filter={quote(query)}&per_page={per_page}&sort=relevance_score:desc&cursor="
    attempt = 0
    while cursor and len(results) < max_results and attempt < 20:
        url = f"{base}{params}{cursor}"
        try:
            req = Request(url, headers={"User-Agent": "ReviewBot/1.0"})
            resp = urlopen(req, timeout=30)
            data = json.loads(resp.read())
            works = data.get("results", [])
            if not works:
                break
            for w in works:
                results.append({
                    "id": w.get("id"),
                    "title": w.get("title", ""),
                    "abstract": w.get("abstract_inverted_index", ""),
                    "year": w.get("publication_year"),
                    "doi": (w.get("doi") or "").lower().strip(),
                    "source": "openalex",
                    "query_label": query[:60],
                    "cited_by_count": w.get("cited_by_count", 0),
                    "authors": [a.get("author", {}).get("display_name", "")
                                for a in w.get("authorships", [])[:5]],
                    "venue": (w.get("primary_location") or {}).get("source", {}).get("display_name", ""),
                })
            cursor = data.get("meta", {}).get("next_cursor")
            attempt += 1
            time.sleep(0.2)
        except HTTPError as e:
            if e.code == 429:
                time.sleep(2)
                continue
            break
        except Exception as e:
            print(f"  OpenAlex error: {e}", file=sys.stderr)
            break
    return results


def pubmed_search(query: str, max_results: int = 100) -> list[dict]:
    results = []
    esearch_url = (
        f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        f"?db=pubmed&term={quote(query)}&retmax={max_results}&retmode=json&sort=relevance"
    )
    try:
        req = Request(esearch_url, headers={"User-Agent": "ReviewBot/1.0"})
        resp = urlopen(req, timeout=30)
        search_data = json.loads(resp.read())
    except Exception as e:
        print(f"  PubMed search error: {e}", file=sys.stderr)
        return results

    ids = search_data.get("esearchresult", {}).get("idlist", [])
    if not ids:
        return results

    for i in range(0, len(ids), 50):
        batch = ids[i:i + 50]
        efetch_url = (
            f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
            f"?db=pubmed&id={','.join(batch)}&retmode=xml&rettype=abstract"
        )
        try:
            req = Request(efetch_url, headers={"User-Agent": "ReviewBot/1.0"})
            resp = urlopen(req, timeout=30)
            xml = resp.read().decode("utf-8")
            articles = xml.split("<PubmedArticle>")[1:]
            for art in articles:
                title = _extract_xml(art, "ArticleTitle")
                abstract = _extract_xml(art, "AbstractText")
                year = _extract_xml(art, "PubDate")
                doi = _extract_xml(art, "ELocationID")
                if not doi or "doi" not in doi.lower()[:10]:
                    doi = _extract_xml_attr(art, "ArticleId", "IdType", "doi")
                year_num = None
                if year:
                    m = re.search(r"(\d{4})", year)
                    if m:
                        year_num = int(m.group(1))
                results.append({
                    "id": _extract_xml(art, "PMID"),
                    "title": title.strip() if title else "",
                    "abstract": abstract.strip() if abstract else "",
                    "year": year_num,
                    "doi": ("https://doi.org/" + doi.strip()) if doi and doi.strip() else "",
                    "source": "pubmed",
                    "query_label": query[:60],
                    "cited_by_count": 0,
                    "authors": [],
                    "venue": _extract_xml(art, "Journal") or "",
                })
            time.sleep(0.4)
        except Exception as e:
            print(f"  PubMed fetch error: {e}", file=sys.stderr)
            time.sleep(1)
    return results


def _extract_xml(text: str, tag: str) -> str:
    parts = text.split(f"<{tag}>")
    if len(parts) < 2:
        return ""
    parts2 = parts[1].split(f"</{tag}>")
    return parts2[0].strip() if len(parts2) > 1 else ""


def _extract_xml_attr(text: str, tag: str, attr: str, attr_val: str) -> str:
    import html
    pattern = re.compile(
        rf'<{tag}[^>]*{re.escape(attr)}\s*=\s*["\']?{re.escape(attr_val)}["\']?[^>]*>(.*?)</{tag}>',
        re.DOTALL
    )
    m = pattern.search(text)
    return html.unescape(m.group(1).strip()) if m else ""


def deduplicate(papers: list[dict]) -> list[dict]:
    seen_dois: set = set()
    seen_titles: set = set()
    unique = []
    for p in papers:
        doi = p.get("doi", "").strip().lower().rstrip("/")
        if doi and doi in seen_dois:
            continue
        title = p.get("title", "").strip().lower()
        title_simple = re.sub(r"[^a-z0-9]", "", title)[:80]
        if title_simple and title_simple in seen_titles:
            continue
        if doi:
            seen_dois.add(doi)
        if title_simple:
            seen_titles.add(title_simple)
        unique.append(p)
    return unique


def abstract_inverted_to_text(inverted_index) -> str:
    if isinstance(inverted_index, str):
        return inverted_index
    if not isinstance(inverted_index, dict):
        return ""
    word_positions = []
    for word, positions in inverted_index.items():
        for pos in positions:
            word_positions.append((pos, word))
    word_positions.sort()
    return " ".join(w for _, w in word_positions)


def main():
    import os
    os.makedirs(os.path.dirname(OUTPUT) or ".", exist_ok=True)

    all_papers = []
    print(f"Searching {len(QUERIES)} sub-topics over OpenAlex + PubMed...")

    for label, oa_query, pm_query, y_start, y_end in QUERIES:
        print(f"[{label}] OpenAlex: {oa_query[:60]}...")
        oa_results = openalex_search(oa_query)
        for p in oa_results:
            if isinstance(p.get("abstract"), dict):
                p["abstract"] = abstract_inverted_to_text(p["abstract"])
            elif not isinstance(p.get("abstract"), str):
                p["abstract"] = ""
        print(f"  -> {len(oa_results)} from OpenAlex")
        all_papers.extend(oa_results)

        print(f"[{label}] PubMed: {pm_query[:60]}...")
        pm_results = pubmed_search(pm_query)
        print(f"  -> {len(pm_results)} from PubMed")
        all_papers.extend(pm_results)

        time.sleep(0.5)

    print(f"Total before dedup: {len(all_papers)}")
    all_papers = deduplicate(all_papers)
    print(f"Total after dedup: {len(all_papers)}")

    with open(OUTPUT, "w") as f:
        json.dump(all_papers, f, indent=2, ensure_ascii=False)

    by_source = {}
    for p in all_papers:
        s = p.get("source", "unknown")
        by_source[s] = by_source.get(s, 0) + 1
    print(f"\nSaved to {OUTPUT}")
    print(f"By source: {by_source}")
    pre_2000 = sum(1 for p in all_papers if p.get("year") and p["year"] < 2000)
    post_2000 = sum(1 for p in all_papers if p.get("year") and p["year"] >= 2000)
    print(f"  <2000: {pre_2000}, >=2000: {post_2000}")


if __name__ == "__main__":
    main()
