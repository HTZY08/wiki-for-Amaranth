"""Cold-start bootstrap helpers for resonance matrices."""

from __future__ import annotations

import os
import re
import sqlite3
from itertools import combinations

import numpy as np
import yaml

from resonance.node_registry import NodeRegistry, PlaneType


def load_skill_manifest(path: str) -> dict:
    """Load a skill manifest YAML file."""

    if not os.path.exists(path):
        return {"skills": {}}
    with open(path, "r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    skills = data.get("skills")
    if not isinstance(skills, dict):
        data["skills"] = {}
    return data


def bootstrap_W_raw(
    manifest: dict,
    registry: NodeRegistry,
    explicit_weight: float = 1.0,
    tag_weight: float = 0.2,
    generic_skills: list[str] = None,
) -> np.ndarray:
    """Initialize W_raw from manifest metadata."""

    n = registry.size()
    W = np.zeros((n, n), dtype=np.float64)
    skills = manifest.get("skills", {}) if isinstance(manifest, dict) else {}
    generic_skills = generic_skills or [
        "codex",
        "web_search",
        "research",
        "obsidian",
    ]

    def idx_for_skill(name: str):
        idx = registry.get_idx(name)
        if idx is not None:
            return idx
        return registry.get_idx(f"skill:{name}")

    for skill_name, metadata in skills.items():
        if not isinstance(metadata, dict):
            continue
        i = idx_for_skill(skill_name)
        if i is None:
            continue
        for related in metadata.get("related_skills") or []:
            j = idx_for_skill(str(related))
            if j is not None and i != j:
                W[i, j] += explicit_weight
                W[j, i] += explicit_weight

    tagged: list[tuple[int, set[str]]] = []
    for skill_name, metadata in skills.items():
        if not isinstance(metadata, dict):
            continue
        idx = idx_for_skill(skill_name)
        if idx is None:
            continue
        tags = {
            str(tag).strip().lower()
            for tag in (metadata.get("domain_tags") or [])
            if str(tag).strip()
        }
        if tags:
            tagged.append((idx, tags))

    for (i, tags_i), (j, tags_j) in combinations(tagged, 2):
        shared = tags_i.intersection(tags_j)
        if shared:
            weight = tag_weight * len(shared)
            W[i, j] += weight
            W[j, i] += weight

    generic_indices = [
        idx for name in generic_skills if (idx := idx_for_skill(name)) is not None
    ][:3]
    if generic_indices:
        for i in range(n):
            if np.isclose(W[i].sum() + W[:, i].sum(), 0.0):
                for j in generic_indices:
                    if i != j:
                        W[i, j] += 0.1
                        W[j, i] += 0.1

    np.fill_diagonal(W, 0.0)
    return W


def generate_manifest_from_skills(
    cooc_db_path: str,
    output_path: str,
) -> None:
    """Generate an initial manifest from skill_cooc.db."""

    names: set[str] = set()
    if os.path.exists(cooc_db_path):
        with sqlite3.connect(cooc_db_path) as conn:
            cur = conn.cursor()
            for table in ("skills", "cooc"):
                exists = cur.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
                    (table,),
                ).fetchone()
                if exists is None:
                    continue
                if table == "skills":
                    rows = cur.execute("SELECT name FROM skills").fetchall()
                    names.update(row[0] for row in rows if row[0])
                else:
                    rows = cur.execute("SELECT skill_a, skill_b FROM cooc").fetchall()
                    for a, b in rows:
                        if a:
                            names.add(a)
                        if b:
                            names.add(b)

    manifest = {"skills": {}}
    for name in sorted(names):
        manifest["skills"][name] = {
            "domain_tags": _infer_domain_tags(name),
            "related_skills": [],
        }

    out_dir = os.path.dirname(output_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as handle:
        yaml.safe_dump(manifest, handle, sort_keys=True, allow_unicode=True)


def _infer_domain_tags(name: str) -> list[str]:
    tokens = {
        token
        for token in re.split(r"[^a-zA-Z0-9]+", name.lower())
        if token and len(token) > 1
    }
    rules = [
        ("coding", {"codex", "code", "python", "dev", "software", "plugin"}),
        ("research", {"search", "arxiv", "paper", "zhihu", "web"}),
        ("writing", {"obsidian", "wiki", "note", "author", "content"}),
        ("chemistry", {"chem", "orca", "xtb", "dft", "quantum"}),
        ("data", {"data", "db", "sql", "analysis", "pipeline"}),
        ("automation", {"cron", "monitor", "orchestration", "workflow"}),
    ]
    tags = [tag for tag, needles in rules if tokens.intersection(needles)]
    return tags or ["general"]
